"""Offline P5 candidate preview; no provider or production evidence."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.registry.desired_preview import preview,PreviewError
from tools.registry.store import digest

A,B,C,D=('1'*40,'2'*40,'3'*40,'4'*40)
REPO='fortis-approvals'


def example(deploy=True):
    cat={'schemaVersion':1,'repository':REPO,'buildUnits':[{'id':'app','artifactType':'docker-image',
         'recipe':'Dockerfile','inputs':['src/**']}],
         'targets':[{'id':name,'buildUnit':'app','deployment':{'kind':'owner-controlled',
          'procedure':'docs/release.md','environments':['production']},'verification':['health']}
          for name in ('gateway','worker')],'noDeploymentPaths':['docs/**']}
    impact={'releaseImpact':{'schemaVersion':1,'classification':'deployment' if deploy else 'no-deployment',
      'reason':'Reviewed source change affects image or documentation only.',
      'targets':[{'id':t,'actions':['image-rebuild']} for t in ('gateway','worker')] if deploy else [],
      'dependencies':{'pullRequests':[],'targets':[]},'verification':['source-ci']}}
    pr={'number':23,'headSha':B,'mergeSha':C,'mergedAt':'2026-11-20T09:00:00+00:00',
        'mainContainsMerge':True,'impact':impact,'changedPaths':['src/app.py'] if deploy else ['docs/README.md'],
        'ci':{'headSha':B,'complete':True,'passedChecks':['source-ci'],'readbackRef':'offline/ci'},
        'mergeProofRef':'offline/merge','pathProofRef':'offline/paths'}
    return {'schemaVersion':1,'repository':'AlexPastukhh/'+REPO,'selectedMainSha':A,
            'catalogSha':D,'catalogDigest':digest(cat),'catalog':cat,
            'mergedPullRequests':[pr],
            'completeness':{k:True for k in ('mergeLineage','changedPaths','catalogPinned',
                           'ciChecks','ancestorProof','dependencyGraph')},
            'environmentBindings':{'gateway':'production','worker':'production'} if deploy else {},
            'dependencyProofs':[],'sourceReadRef':'offline/input'}


class PreviewTests(unittest.TestCase):
    def setUp(self):
        # The accepted schema validator is an external pinned dependency;
        # semantic unit fixtures stub ONLY the JSON schema dependency gate.
        # Real schema integration remains separately fail-closed.
        stub=patch('tools.registry.desired_preview.validate_schema')
        stub.start()
        self.addCleanup(stub.stop)

    def rejects(self, data, reason):
        with self.assertRaisesRegex(PreviewError,reason): preview(data)

    def test_missing_required_schema_dependency_fails_closed(self):
        from tools.release.validate import ValidationError
        with patch('tools.registry.desired_preview.validate_schema',
                   side_effect=ValidationError('jsonschema unavailable')):
            self.rejects(example(),'CATALOG_SCHEMA_INVALID')

    def test_target_specific_and_no_proof(self):
        a=preview(example())
        self.assertEqual(a['recordCount'],2)
        self.assertFalse(a['evidenceVerified'])
        self.assertEqual({r['identity']['targetId'] for r in a['records']},{'gateway','worker'})
        self.assertEqual({r['recordId'] for r in a['records']},
                         {r['recordId'] for r in preview(example())['records']})
        self.assertTrue(all(r['actual'] is None and r['artifact']['digest'] is None
                            and r['planningState']=='PLANNED_UNVERIFIED' for r in a['records']))

    def test_no_deployment_no_queue_records(self):
        a=preview(example(False));self.assertEqual(a['records'],[]);self.assertTrue(a['noDeploymentOnly'])

    def test_two_prs_one_desired_version(self):
        data=example();pr=copy.deepcopy(example(False)['mergedPullRequests'][0])
        pr['number']=24;pr['headSha']=C;pr['mergeSha']=D;pr['ci']['headSha']=C
        data['mergedPullRequests'].append(pr)
        a=preview(data); self.assertEqual(a['recordCount'],2)
        self.assertEqual({x['number'] for x in a['records'][0]['mergedPullRequests']},{23,24})
        b=copy.deepcopy(data);b['mergedPullRequests'].reverse()
        self.assertEqual(a['records'],preview(b)['records'])

    def test_missing_completeness(self):
        d=example();d['completeness']['changedPaths']=False;self.rejects(d,'EVIDENCE_INCOMPLETE')

    def test_missing_main_ancestry(self):
        d=example();d['mergedPullRequests'][0]['mainContainsMerge']=False;self.rejects(d,'LINEAGE_UNPROVEN')

    def test_ci_head_mismatch(self):
        d=example();d['mergedPullRequests'][0]['ci']['headSha']=D;self.rejects(d,'CI_NOT_EXACT_HEAD')

    def test_catalog_digest_conflict(self):
        d=example();d['catalogDigest']='f'*64;self.rejects(d,'CATALOG_DIGEST_MISMATCH')

    def test_shared_image_omission(self):
        d=example();d['mergedPullRequests'][0]['impact']['releaseImpact']['targets'].pop()
        self.rejects(d,'IMPACT_NOT_VALIDATED')

    def test_missing_changed_paths(self):
        d=example();d['mergedPullRequests'][0]['changedPaths']=[]
        self.rejects(d,'IMPACT_NOT_VALIDATED')

    def test_environment_missing(self):
        d=example();d['environmentBindings'].pop('worker');self.rejects(d,'ENVIRONMENT_SCOPE_INCOMPLETE')

    def test_unknown_environment(self):
        d=example();d['environmentBindings']['worker']='test';self.rejects(d,'ENVIRONMENT_NOT_IN_CATALOG')

    def test_catalog_cycle(self):
        d=example();d['catalog']['targets'][0]['dependsOn']=[{'repository':REPO,'target':'worker'}]
        d['catalog']['targets'][1]['dependsOn']=[{'repository':REPO,'target':'gateway'}]
        d['catalogDigest']=digest(d['catalog']);self.rejects(d,'CATALOG_DEPENDENCY_CYCLE')

    def test_dependency_proof_missing_and_drift(self):
        d=example();d['catalog']['targets'][0]['dependsOn']=[{'repository':REPO,'target':'worker'}]
        d['catalogDigest']=digest(d['catalog']);self.rejects(d,'DEPENDENCY_UNVERIFIED')
        d['dependencyProofs']=[{'repository':REPO,'target':'worker','catalogSha':C,'readbackRef':'offline'}]
        self.rejects(d,'DEPENDENCY_CATALOG_DRIFT')
        d['dependencyProofs'][0]['catalogSha']=D
        self.assertEqual(preview(d)['recordCount'],2)

    def test_duplicate_pr(self):
        d=example();d['mergedPullRequests'].append(copy.deepcopy(d['mergedPullRequests'][0]))
        self.rejects(d,'LINEAGE_DUPLICATE_OR_INVALID')

    def test_self_cycle_pr(self):
        d=example();d['mergedPullRequests'][0]['impact']['releaseImpact']['dependencies']['pullRequests']=[
            {'repository':REPO,'number':23}]
        self.rejects(d,'PR_DEPENDENCY_CYCLE')

    def test_cross_repo_pr_dependency_requires_review(self):
        d=example();d['mergedPullRequests'][0]['impact']['releaseImpact']['dependencies']['pullRequests']=[
            {'repository':'rd-graphs','number':4}]
        self.rejects(d,'CROSS_REPO_PR_DEPENDENCY_REVIEW')

    def test_unknown_action(self):
        d=example();d['mergedPullRequests'][0]['impact']['releaseImpact']['targets'][0]['actions'].append('unknown')
        self.rejects(d,'ACTION_UNKNOWN')

    def test_empty_lineage(self):
        d=example();d['mergedPullRequests']=[];self.rejects(d,'LINEAGE_INCOMPLETE')

    def test_extra_installed_state_fails(self):
        d=example();d['actual']='DEPLOYED';self.rejects(d,'INPUT_FIELDS_INVALID')


if __name__=='__main__': unittest.main()
