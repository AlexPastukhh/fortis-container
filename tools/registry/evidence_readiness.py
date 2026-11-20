"""Offline P5 post-merge Gateway READ gap assessor; never admission authority.

Known current Gateway projections cannot prove immutable merge history, complete
paths, retained exact PR-body Release Impact, pinned catalog or CI policy.
Even perfect-looking input must return BLOCKED_EVIDENCE_GAP. No HTTP/SQL/I/O.
"""
from __future__ import annotations

import re
from .store import digest

SHA = re.compile(r"[0-9a-f]{40}\Z")
REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}\Z")


class EvidenceReadinessError(ValueError):
    """Invalid projection/metadata; fail closed at the caller."""


def _need(valid, code):
    if not valid:
        raise EvidenceReadinessError(code)


def _sha(value):
    return type(value) is str and SHA.fullmatch(value) is not None


def _read(row, operation):
    _need(type(row) is dict and row.get('operation') == operation,
          'GATEWAY_PROJECTION_SHAPE_INVALID')
    return row


# An unconditional gate for the *current* bounded typed READ contract. These
# facts require independently reviewed future typed operations. Merely adding
# plausible dict fields in a fixture does not turn them into authenticated
# evidence or an install-state proof.
MISSING_TRUSTED_EVIDENCE = (
    'POST_MERGE_IMMUTABLE_PR_BODY_MISSING',
    'MERGE_COMMIT_AND_ANCESTRY_NOT_PROVEN',
    'COMPLETE_CHANGED_PATHS_NOT_PROVEN',
    'CATALOG_REVISION_CONTENT_NOT_PINNED',
    'PR_RELEASE_IMPACT_RECALCULATION_MISSING',
    'CI_REQUIRED_CHECK_POLICY_NOT_PINNED',
    'CI_ATTEMPT_AND_RESULT_PROVENANCE_INCOMPLETE',
    'DEPENDENCY_CLOSURE_NOT_VERIFIED',
    'PROVIDER_SNAPSHOT_NOT_AUTHENTICATED',
)


def assess(*, repository, pull_request_number, expected_head_sha,
           selected_main_sha, pull_request, branch, check_runs,
           commit_page):
    """Assess current Gateway READ *projections*, never report ADMISSIBLE.

    Inputs must come from separate exact scoped authenticated Gateway READs
    in a real caller; offline fixture fields are still completely untrusted.
    Read results cannot independently establish installed state or permission.
    """
    _need(type(repository) is str and REPO.fullmatch(repository) is not None,
          'REPOSITORY_INVALID')
    _need(type(pull_request_number) is int and 0 < pull_request_number <= 1000000,
          'PR_NUMBER_INVALID')
    _need(_sha(expected_head_sha) and _sha(selected_main_sha), 'SOURCE_SHA_INVALID')
    pr = _read(pull_request, 'get_pull_request').get('pullRequest')
    _need(type(pr) is dict, 'PR_PROJECTION_INVALID')
    _need(pr.get('number') == pull_request_number and
          pr.get('state') == 'closed' and pr.get('merged') is True,
          'PR_NOT_CONFIRMED_MERGED')
    _need(pr.get('draft') is False, 'PR_DRAFT_OR_UNKNOWN')
    head, base = pr.get('head'), pr.get('base')
    _need(type(head) is dict and type(base) is dict and
          head.get('sha') == expected_head_sha and base.get('ref') == 'main'
          and _sha(base.get('sha')), 'PR_HEAD_BASE_MISMATCH')
    _need(type(head.get('ref')) is str and head['ref'].startswith('task/'),
          'PR_TASK_PROVENANCE_MISSING')
    main = _read(branch, 'get_branch').get('branch')
    _need(branch.get('found') is True and type(main) is dict and
          main.get('name') == 'main' and main.get('sha') == selected_main_sha,
          'MAIN_SHA_STALE')
    projection = _read(check_runs, 'list_check_runs')
    runs = projection.get('items')
    _need(type(runs) is list and len(runs) <= 100,
          'CHECK_RUNS_INCOMPLETE_OR_INVALID')
    count = projection.get('totalCount')
    _need(type(count) is int and len(runs) <= count,
          'CHECK_RUN_TOTAL_COUNT_INVALID')
    checks = set()
    for run in runs:
        _need(type(run) is dict and type(run.get('name')) is str and
              len(run['name']) <= 128 and run.get('headSha') == expected_head_sha and
              run.get('status') in ('queued', 'in_progress', 'completed') and
              run.get('conclusion') in (None, 'success', 'failure', 'cancelled',
                                        'timed_out', 'skipped', 'neutral', 'action_required'),
              'CHECK_RUN_INVALID_OR_HEAD_MISMATCH')
        _need(run['name'] not in checks, 'CHECK_RUN_AMBIGUOUS_ATTEMPT')
        checks.add(run['name'])
    commits = _read(commit_page, 'list_commits')
    page = commits.get('page')
    limit = commits.get('perPage')
    items = commits.get('items')
    _need(type(page) is int and page >= 1 and type(limit) is int and
          1 <= limit <= 100 and type(items) is list and len(items) <= limit,
          'COMMIT_PAGE_INVALID')
    for item in items:
        _need(type(item) is dict and _sha(item.get('sha')),
              'COMMIT_PROJECTION_INVALID')
    # Finding an entry, even a "Merge pull request #N" subject, is NOT a
    # cryptographic ancestry proof and cannot replace exact immutable history.
    observed = [x.get('sha') for x in items]
    issues = list(MISSING_TRUSTED_EVIDENCE)
    if pr.get('mergedAt') is None:
        issues.append('MERGE_TIMESTAMP_NOT_EXPOSED')
    if count != len(runs):
        issues.append('CHECK_RUN_PAGINATION_NOT_COMPLETE')
    if not runs:
        issues.append('NO_CHECK_RUNS_RETURNED')
    elif any(x['status'] != 'completed' or x['conclusion'] != 'success' for x in runs):
        issues.append('OBSERVED_CHECK_NOT_SUCCESS')
    if selected_main_sha not in observed:
        issues.append('MAIN_NOT_IN_SELECTED_COMMIT_PAGE')
    if page > 1 or len(items) == limit:
        issues.append('COMMIT_PAGINATION_NOT_PROVEN_COMPLETE')
    # Do not put any PR body/secrets or unverifiable authorization claims into
    # resulting projections. This digest fingerprints *supplied* bytes only.
    return {
        'result': 'BLOCKED_EVIDENCE_GAP',
        'evidenceVerified': False,
        'admissionAllowed': False,
        'deploymentAllowed': False,
        'repository': repository,
        'prNumber': pull_request_number,
        'prHeadSha': expected_head_sha,
        'selectedMainSha': selected_main_sha,
        'observedCheckNames': sorted(checks),
        'issues': sorted(issues),
        'projectionDigest': digest({
            'repo': repository, 'prNumber': pull_request_number,
            'expectedHeadSha': expected_head_sha, 'selectedMainSha': selected_main_sha,
            'pr': pull_request, 'branch': branch,
            'checks': check_runs, 'commits': commit_page,
        }),
    }
