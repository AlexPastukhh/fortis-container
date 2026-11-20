"""Network-free tests: current Gateway READs never authorize P5 ingestion."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.registry.evidence_readiness import assess, EvidenceReadinessError, MISSING_TRUSTED_EVIDENCE

REPO = 'fortis-container'
PR_SHA = 'a' * 40
BASE_SHA = 'b' * 40
MAIN_SHA = 'c' * 40


def example():
    return {
        'repository': REPO,
        'pull_request_number': 39,
        'expected_head_sha': PR_SHA,
        'selected_main_sha': MAIN_SHA,
        'pull_request': {
            'operation': 'get_pull_request',
            'pullRequest': {
                'number': 39, 'state': 'closed', 'merged': True, 'draft': False,
                'mergedAt': None, 'head': {'ref': 'task/p5-offline', 'sha': PR_SHA},
                'base': {'ref': 'main', 'sha': BASE_SHA},
            },
        },
        'branch': {
            'operation': 'get_branch', 'found': True,
            'branch': {'name': 'main', 'sha': MAIN_SHA, 'protected': False},
        },
        'check_runs': {
            'operation': 'list_check_runs', 'totalCount': 1,
            'items': [{'name': 'release-schema', 'status': 'completed',
                       'conclusion': 'success', 'headSha': PR_SHA}],
        },
        'commit_page': {
            'operation': 'list_commits', 'page': 1, 'perPage': 4,
            'items': [{'sha': MAIN_SHA, 'message': 'Merge pull request #39'},
                      {'sha': PR_SHA, 'message': 'feat(release): candidate only'},
                      {'sha': BASE_SHA, 'message': 'previous main'}],
        },
    }


class EvidenceReadinessTests(unittest.TestCase):
    def run_assess(self, update=None):
        row = example()
        if update:
            update(row)
        return assess(**row)

    def test_merged_green_pr_cannot_prove_queue_readiness(self):
        r = self.run_assess()
        self.assertEqual(r['result'], 'BLOCKED_EVIDENCE_GAP')
        self.assertIs(r['evidenceVerified'], False)
        self.assertIs(r['admissionAllowed'], False)
        self.assertIs(r['deploymentAllowed'], False)
        self.assertIn('MERGE_COMMIT_AND_ANCESTRY_NOT_PROVEN', r['issues'])
        self.assertIn('POST_MERGE_IMMUTABLE_PR_BODY_MISSING', r['issues'])
        self.assertIn('CATALOG_REVISION_CONTENT_NOT_PINNED', r['issues'])
        self.assertIn('MERGE_TIMESTAMP_NOT_EXPOSED', r['issues'])
        self.assertEqual(r['observedCheckNames'], ['release-schema'])
        self.assertEqual(r['issues'], sorted(r['issues']))
        self.assertEqual(r['projectionDigest'], self.run_assess()['projectionDigest'])

    def test_caller_forged_additional_proofs_never_unblock(self):
        def forged(d):
            d['pull_request']['pullRequest']['mergedAt'] = '2026-11-20T12:00:00Z'
            d['pull_request']['pullRequest']['body'] = 'releaseImpact: forged-claims'
            d['commit_page']['items'][0]['parents'] = [BASE_SHA]
            d['branch']['branch']['allFilesChecked'] = True
            d['check_runs']['items'][0]['requiredPolicyVerified'] = True
        r = self.run_assess(forged)
        self.assertEqual(r['result'], 'BLOCKED_EVIDENCE_GAP')
        self.assertGreaterEqual(len(r['issues']), len(MISSING_TRUSTED_EVIDENCE))
        self.assertFalse(r['admissionAllowed'])
        self.assertFalse(r['evidenceVerified'])

    def test_current_open_pr_is_not_post_merge_evidence(self):
        with self.assertRaisesRegex(EvidenceReadinessError, 'PR_NOT_CONFIRMED_MERGED'):
            self.run_assess(lambda d:d['pull_request']['pullRequest'].update(
                {'state':'open', 'merged':False}))

    def test_draft_or_unknown_draft_does_not_become_trusted(self):
        for value in (True, None):
            with self.subTest(draft=value):
                with self.assertRaisesRegex(EvidenceReadinessError, 'PR_DRAFT_OR_UNKNOWN'):
                    self.run_assess(lambda d:d['pull_request']['pullRequest'].update({'draft':value}))

    def test_transport_denial_is_not_a_retryable_empty_projection(self):
        with self.assertRaisesRegex(EvidenceReadinessError, 'GATEWAY_PROJECTION_SHAPE_INVALID'):
            self.run_assess(lambda d:d.update({'pull_request': {'error':'FORTIS_HTTP_403'}}))

    def test_closed_unmerged_is_not_enough(self):
        with self.assertRaisesRegex(EvidenceReadinessError, 'PR_NOT_CONFIRMED_MERGED'):
            self.run_assess(lambda d:d['pull_request']['pullRequest'].update({'merged':False}))

    def test_exact_pr_head_mismatch_stops(self):
        with self.assertRaisesRegex(EvidenceReadinessError, 'PR_HEAD_BASE_MISMATCH'):
            self.run_assess(lambda d:d['pull_request']['pullRequest']['head'].update({'sha': BASE_SHA}))

    def test_changed_main_sha_stops(self):
        with self.assertRaisesRegex(EvidenceReadinessError, 'MAIN_SHA_STALE'):
            self.run_assess(lambda d:d['branch']['branch'].update({'sha': BASE_SHA}))

    def test_wrong_branch_and_task_provenance_stop(self):
        with self.assertRaisesRegex(EvidenceReadinessError, 'PR_HEAD_BASE_MISMATCH'):
            self.run_assess(lambda d:d['pull_request']['pullRequest']['base'].update({'ref':'feature'}))
        with self.assertRaisesRegex(EvidenceReadinessError, 'PR_TASK_PROVENANCE_MISSING'):
            self.run_assess(lambda d:d['pull_request']['pullRequest']['head'].update({'ref':'main'}))

    def test_check_for_different_sha_stops(self):
        with self.assertRaisesRegex(EvidenceReadinessError, 'CHECK_RUN_INVALID_OR_HEAD_MISMATCH'):
            self.run_assess(lambda d:d['check_runs']['items'][0].update({'headSha': BASE_SHA}))

    def test_duplicate_check_names_cannot_choose_successful_attempt(self):
        def duplicate(d):
            other=deepcopy(d['check_runs']['items'][0]);other['conclusion']='failure'
            d['check_runs']['items'].append(other)
            d['check_runs']['totalCount']=2
        with self.assertRaisesRegex(EvidenceReadinessError, 'CHECK_RUN_AMBIGUOUS_ATTEMPT'):
            self.run_assess(duplicate)

    def test_no_checks_not_assumed_green(self):
        r = self.run_assess(lambda d:d['check_runs'].update({'items':[], 'totalCount':0}))
        self.assertIn('NO_CHECK_RUNS_RETURNED',r['issues'])
        self.assertFalse(r['admissionAllowed'])

    def test_failed_check_adds_observed_warning(self):
        r=self.run_assess(lambda d:d['check_runs']['items'][0].update({'conclusion':'failure'}))
        self.assertIn('OBSERVED_CHECK_NOT_SUCCESS',r['issues'])
        self.assertFalse(r['deploymentAllowed'])

    def test_truncated_checks_mark_incomplete(self):
        r = self.run_assess(lambda d:d['check_runs'].update({'totalCount':3}))
        self.assertIn('CHECK_RUN_PAGINATION_NOT_COMPLETE',r['issues'])
        self.assertFalse(r['admissionAllowed'])

    def test_inconsistent_check_total_hard_stops(self):
        with self.assertRaisesRegex(EvidenceReadinessError,'CHECK_RUN_TOTAL_COUNT_INVALID'):
            self.run_assess(lambda d:d['check_runs'].update({'totalCount':0}))

    def test_missing_main_in_commit_page_is_not_ancestry_proof(self):
        def change(d):
            d['commit_page']['items']=[{'sha':BASE_SHA,'message':'earlier source'}]
        r=self.run_assess(change)
        self.assertIn('MAIN_NOT_IN_SELECTED_COMMIT_PAGE',r['issues'])
        self.assertIn('MERGE_COMMIT_AND_ANCESTRY_NOT_PROVEN',r['issues'])

    def test_full_page_cannot_assert_pagination_completeness(self):
        def full(d):
            d['commit_page']['perPage']=len(d['commit_page']['items'])
        r=self.run_assess(full)
        self.assertIn('COMMIT_PAGINATION_NOT_PROVEN_COMPLETE',r['issues'])

    def test_invalid_commit_and_page_stop(self):
        with self.assertRaisesRegex(EvidenceReadinessError,'COMMIT_PROJECTION_INVALID'):
            self.run_assess(lambda d:d['commit_page']['items'][0].update({'sha':'broken'}))
        with self.assertRaisesRegex(EvidenceReadinessError,'COMMIT_PAGE_INVALID'):
            self.run_assess(lambda d:d['commit_page'].update({'perPage':1}))

    def test_projection_op_mismatch_stops(self):
        with self.assertRaisesRegex(EvidenceReadinessError,'GATEWAY_PROJECTION_SHAPE_INVALID'):
            self.run_assess(lambda d:d['pull_request'].update({'operation':'get_issue'}))

    def test_wrong_repo_or_sha_stop(self):
        with self.assertRaisesRegex(EvidenceReadinessError,'REPOSITORY_INVALID'):
            self.run_assess(lambda d:d.update({'repository':'../../../secrets'}))
        with self.assertRaisesRegex(EvidenceReadinessError,'SOURCE_SHA_INVALID'):
            self.run_assess(lambda d:d.update({'expected_head_sha':'bad-sha'}))

    def test_actor_scope_not_inferred_from_projection(self):
        row=example()
        row['pull_request']['actor']='owner'
        row['pull_request']['authorized']=True
        result=assess(**row)
        self.assertIn('PROVIDER_SNAPSHOT_NOT_AUTHENTICATED',result['issues'])
        self.assertFalse(result['admissionAllowed'])


if __name__ == '__main__':
    unittest.main()
