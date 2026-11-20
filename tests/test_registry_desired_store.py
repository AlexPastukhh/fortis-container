"""P5 offline SQLite desired-record candidate journal: no authority or network."""
import copy
import json
import sqlite3
import sys
import tempfile
import threading
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.registry.store import digest
from tools.registry.desired_store import DesiredCandidateStore, DesiredStoreError

REPO = 'AlexPastukhh/fortis-approvals'
OLD = '1'*40
NEW = '2'*40
CAT = '3'*40
CAT_DIGEST = '4'*64


def candidate(source=OLD, targets=('gateway', 'worker'), catalog=CAT,
              catalog_digest=CAT_DIGEST):
    lineage = [{'number': 23, 'headSha': '5'*40, 'mergeSha': '6'*40,
                'mergedAt': '2026-11-20T09:00:00Z', 'impactDigest': '7'*64,
                'ciDigest': '8'*64, 'changedPathsDigest': '9'*64}]
    records = []
    for target in targets:
        ident = {'repository': REPO, 'targetId': target, 'environment': 'production',
                 'desiredSourceSha': source, 'catalogSha': catalog,
                 'catalogDigest': catalog_digest}
        records.append({'recordId': digest(ident), 'identity': ident,
                        'componentMappingStatus': 'UNVERIFIED', 'buildUnitId': 'gw-image',
                        'artifact': {'state': 'NOT_BUILT', 'digest': None},
                        'deploymentProcedure': 'docs/use-cases/releases.md',
                        'requiredActions': ['image-rebuild'], 'mergedPullRequests': lineage,
                        'lineageDigest': digest(lineage), 'dependencies': [],
                        'planningState': 'PLANNED_UNVERIFIED', 'actual': None,
                        'evidenceVerified': False})
    return {'result': 'CANDIDATE_PREVIEW_ONLY', 'sourceReadRef': 'offline-fixture',
            'snapshotDigest': digest({'source':source, 'targets':targets,
                                       'catalog': catalog, 'catalogDigest':catalog_digest}),
            'evidenceVerified': False, 'recordCount': len(records), 'records': records,
            'noDeploymentOnly': not bool(records),
            'warning': 'NO_TRUSTED_COLLECTOR_OR_WRITE_API_INSTALLED'}


def links(preview, predecessor=None, ancestry='offline-reference-not-verified'):
    return [{'newRecordId': row['recordId'],
             'supersedesRecordId': predecessor[row['identity']['targetId']] if predecessor else None,
             'ancestryRef': ancestry if predecessor else None} for row in preview['records']]


class DesiredCandidateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.path = self.root/'candidate.sqlite'
        self.db = DesiredCandidateStore(self.path)
        self.db.initialize()
        self.actor = 'offline-fixture'
        self.counter = 0

    def uuid(self):
        self.counter += 1
        return str(uuid.UUID(int=self.counter))

    def append(self, item=None, *, supersedes=None, **kw):
        item = candidate() if item is None else item
        opts = {'operation_id': self.uuid(), 'actor': self.actor,
                'expected_revision': self.db.verify()['revision'],
                'preview': item, 'links': links(item, supersedes)}
        opts.update(kw)
        return self.db.append(**opts)

    def test_requires_explicit_initialization(self):
        other = DesiredCandidateStore(self.root/'missing.sqlite')
        self.assertFalse(other.path.exists())
        with self.assertRaises(Exception): other.verify()
        with self.assertRaisesRegex(DesiredStoreError, 'STORE_ALREADY_EXISTS'):
            self.db.initialize()

    def test_initial_empty_and_zero_authority(self):
        self.assertEqual(self.db.verify()['revision'], 0)
        self.assertFalse(self.db.verify()['evidenceVerified'])
        self.assertEqual(self.db.list_candidates(repository=REPO), [])

    def test_insert_and_read_after_reopen(self):
        result = self.append()
        self.assertEqual(result['status'], 'CANDIDATE_RECORDED')
        self.assertFalse(result['evidenceVerified'])
        self.assertEqual(result['revision'], 1)
        db = DesiredCandidateStore(self.path)
        self.assertEqual(db.verify()['headHash'], result['eventHash'])
        stored = db.list_candidates(repository=REPO)
        self.assertEqual(len(stored), 2)
        self.assertTrue(all(x['record']['actual'] is None for x in stored))
        self.assertTrue(all(not x['evidenceVerified'] for x in stored))

    def test_no_deployment_creates_audit_only(self):
        zero = candidate(targets=())
        result = self.append(zero)
        self.assertEqual(result['recordIds'], [])
        self.assertEqual(self.db.verify()['revision'], 1)
        self.assertEqual(self.db.list_candidates(repository=REPO), [])

    def test_lost_ack_recover_original_operation(self):
        oid = self.uuid()
        receipt = self.append(operation_id=oid, expected_revision=0)
        self.assertEqual(DesiredCandidateStore(self.path).operation(oid, actor=self.actor), receipt)
        self.assertEqual(self.db.verify()['revision'], 1)

    def test_same_operation_exact_replay_is_idempotent(self):
        oid = self.uuid()
        first = self.append(operation_id=oid, expected_revision=0)
        second = self.append(operation_id=oid, expected_revision=0)
        self.assertEqual(first, second)
        self.assertEqual(self.db.verify()['revision'], 1)

    def test_operation_conflicting_payload_fails(self):
        oid = self.uuid()
        self.append(operation_id=oid, expected_revision=0)
        with self.assertRaisesRegex(DesiredStoreError, 'OPERATION_ID_CONFLICT'):
            self.append(operation_id=oid, expected_revision=1)
        self.assertEqual(self.db.verify()['revision'], 1)

    def test_new_id_same_preview_no_second_batch(self):
        self.append()
        with self.assertRaisesRegex(DesiredStoreError, 'BATCH_ALREADY_STORED'):
            self.append()
        self.assertEqual(self.db.verify()['revision'], 1)

    def test_stale_cas_fails(self):
        self.append()
        new = candidate(source=NEW)
        with self.assertRaisesRegex(DesiredStoreError, 'REVISION_STALE'):
            self.append(new, expected_revision=0)
        self.assertEqual(self.db.verify()['revision'], 1)

    def test_supersession_immutable_old_and_new(self):
        older = candidate()
        first = self.append(older)
        new = candidate(source=NEW)
        previous = {row['identity']['targetId']:row['recordId'] for row in older['records']}
        second = self.append(new, supersedes=previous)
        self.assertEqual(second['revision'], 2)
        stored = self.db.list_candidates(repository=REPO)
        self.assertEqual(len(stored), 4)
        old = {x['record']['recordId']:x for x in stored if x['revision']==1}
        newer = [x for x in stored if x['revision']==2]
        self.assertEqual({x['supersedesRecordId'] for x in newer},set(old))
        self.assertEqual({x['record']['identity']['desiredSourceSha'] for x in newer},{NEW})
        self.assertTrue(all(x['record']['actual'] is None for x in stored))
        self.assertEqual(self.db.verify()['headHash'], second['eventHash'])
        self.assertNotEqual(first['eventHash'], second['eventHash'])

    def test_new_sha_requires_exact_old_identity(self):
        self.append()
        newer = candidate(source=NEW)
        with self.assertRaisesRegex(DesiredStoreError, 'PREDECESSOR_MISMATCH'):
            self.append(newer)
        with self.assertRaisesRegex(DesiredStoreError, 'PREDECESSOR_MISMATCH'):
            self.append(newer, supersedes={'gateway':'a'*64,'worker':'b'*64})

    def test_new_sha_does_not_relabel_catalog_without_proof(self):
        first = candidate()
        self.append(first)
        newer = candidate(source=NEW, catalog='e'*40)
        predecessors={r['identity']['targetId']:r['recordId'] for r in first['records']}
        with self.assertRaisesRegex(DesiredStoreError,'CATALOG_CONTINUITY_NOT_ESTABLISHED'):
            self.append(newer, supersedes=predecessors)

    def test_same_sha_cannot_create_second_version_by_catalog_change(self):
        old = candidate()
        self.append(old)
        newer = candidate(source=OLD, catalog='e'*40)
        predecessors={r['identity']['targetId']:r['recordId'] for r in old['records']}
        with self.assertRaisesRegex(DesiredStoreError,'SAME_SOURCE_SHA_NOT_NEW_VERSION'):
            self.append(newer,supersedes=predecessors)

    def test_unrelated_target_can_progress_without_whole_repo_lock(self):
        self.append(candidate(targets=('gateway',)))
        second = self.append(candidate(targets=('worker',)))
        self.assertEqual(second['revision'], 2)
        self.assertEqual(len(self.db.list_candidates(repository=REPO)),2)

    def test_reference_does_not_equal_ancestry_proof(self):
        old=candidate();self.append(old)
        new=candidate(source=NEW)
        pred={r['identity']['targetId']:r['recordId'] for r in old['records']}
        receipt=self.append(new,supersedes=pred)
        self.assertFalse(receipt['evidenceVerified'])

    def test_empty_new_ancestry_reference_fails(self):
        old=candidate();self.append(old)
        new=candidate(source=NEW)
        pred={r['identity']['targetId']:r['recordId'] for r in old['records']}
        wrong=links(new,pred,ancestry='')
        with self.assertRaisesRegex(DesiredStoreError,'ANCESTRY_REFERENCE_INVALID'):
            self.append(new, links=wrong)

    def test_unexpected_prior_on_initial_record_fails(self):
        item=candidate()
        false_links=[{'newRecordId':r['recordId'],'supersedesRecordId':'a'*64,
                      'ancestryRef':'not-evidence'} for r in item['records']]
        with self.assertRaisesRegex(DesiredStoreError,'UNEXPECTED_PREDECESSOR'):
            self.append(item,links=false_links)

    def test_reject_forged_deployed_state(self):
        forged=candidate();forged['records'][0]['actual']='DEPLOYED'
        with self.assertRaisesRegex(DesiredStoreError,'FORGED_INSTALLED_STATE'):
            self.append(forged)
        forged=candidate();forged['evidenceVerified']=True
        with self.assertRaisesRegex(DesiredStoreError,'UNVERIFIED_ONLY'):
            self.append(forged)
        self.assertEqual(self.db.verify()['revision'],0)

    def test_reject_tampered_record_id(self):
        item=candidate();item['records'][0]['recordId']='a'*64
        with self.assertRaisesRegex(DesiredStoreError,'RECORD_ID_MISMATCH'):
            self.append(item)

    def test_reject_tampered_lineage_digest(self):
        item=candidate();item['records'][0]['lineageDigest']='f'*64
        with self.assertRaisesRegex(DesiredStoreError,'LINEAGE_INVALID'):
            self.append(item)

    def test_reject_mixed_batch_and_count(self):
        item=candidate();item['recordCount']=1
        with self.assertRaisesRegex(DesiredStoreError,'RECORD_COUNT_INVALID'):
            self.append(item)
        item=candidate();item['records'][0]['identity']['desiredSourceSha']=NEW
        item['records'][0]['recordId']=digest(item['records'][0]['identity'])
        with self.assertRaisesRegex(DesiredStoreError,'BATCH_MIXED_OR_DUPLICATE'):
            self.append(item)

    def test_actor_label_mismatch(self):
        oid=self.uuid();self.append(operation_id=oid)
        with self.assertRaisesRegex(DesiredStoreError,'ACTOR_LABEL_MISMATCH'):
            self.db.operation(oid,actor='other-fixture')
        self.assertIsNone(self.db.operation(self.uuid(),actor=self.actor))

    def test_event_corruption_is_detected(self):
        self.append()
        with sqlite3.connect(self.path) as conn:
            conn.execute('UPDATE events SET event_json=? WHERE revision=1',('{}',))
        with self.assertRaisesRegex(DesiredStoreError,'EVENT_PAYLOAD_CHANGED'):
            self.db.verify()

    def test_record_corruption_is_detected(self):
        self.append()
        with sqlite3.connect(self.path) as conn:
            conn.execute('UPDATE records SET record_json=? WHERE target_id=?',('{}','gateway'))
        with self.assertRaisesRegex(DesiredStoreError,'RECORD_HISTORY_CHANGED'):
            self.db.verify()

    def test_missing_history_is_detected(self):
        self.append()
        with sqlite3.connect(self.path) as conn:
            conn.execute('DELETE FROM events')
        with self.assertRaisesRegex(DesiredStoreError,'EVENT_CHAIN_BROKEN'):
            self.db.verify()

    def test_backup_consistent_and_no_overwrite(self):
        receipt=self.append()
        path=self.root/'backup.sqlite'
        backup=self.db.backup_to(path)
        self.assertEqual(backup['headHash'],receipt['eventHash'])
        self.assertEqual(DesiredCandidateStore(path).verify(),self.db.verify())
        with self.assertRaisesRegex(DesiredStoreError,'BACKUP_TARGET_EXISTS'):
            self.db.backup_to(path)

    def test_symlink_and_hardlink_denied(self):
        link=self.root/'symlink.sqlite';link.symlink_to(self.path)
        with self.assertRaises(ValueError):DesiredCandidateStore(link)
        other=self.root/'hardlink.sqlite';other.hardlink_to(self.path)
        with self.assertRaises(ValueError):DesiredCandidateStore(other)

    def test_concurrent_cas_one_winner(self):
        barrier=threading.Barrier(2)
        params=[]
        for target in ('gateway','worker'):
            item=candidate(targets=(target,))
            params.append({'operation_id':self.uuid(),'actor':self.actor,
                           'expected_revision':0,'preview':item,'links':links(item)})
        results=[]
        def worker(params):
            barrier.wait(timeout=4)
            try:results.append(self.db.append(**params)['revision'])
            except DesiredStoreError as error:results.append(str(error))
        jobs=[threading.Thread(target=worker,args=(arg,)) for arg in params]
        for thread in jobs:thread.start()
        for thread in jobs:thread.join(timeout=7)
        self.assertFalse(any(thread.is_alive() for thread in jobs))
        self.assertEqual(sorted(map(str,results)),['1','REVISION_STALE'])
        self.assertEqual(self.db.verify()['revision'],1)

    def test_append_real_offline_preview_output(self):
        from unittest.mock import patch
        import test_registry_desired_preview as fixture_module
        from tools.registry.desired_preview import preview
        with patch('tools.registry.desired_preview.validate_schema'):
            actual_preview = preview(fixture_module.example())
        result = self.append(actual_preview)
        self.assertEqual(len(result['recordIds']), 2)
        self.assertFalse(result['evidenceVerified'])
        self.assertEqual(self.db.verify()['revision'], 1)

    def test_operation_fingerprint_tamper_detected(self):
        self.append()
        with sqlite3.connect(self.path) as conn:
            conn.execute('UPDATE batches SET fingerprint=? WHERE revision=1',('f'*64,))
        with self.assertRaisesRegex(DesiredStoreError,'OPERATION_FINGERPRINT_CHANGED'):
            self.db.verify()

    def test_missing_schema_dependency_in_preview_fails_closed(self):
        from unittest.mock import patch
        import test_registry_desired_preview as fixture_module
        from tools.registry.desired_preview import preview,PreviewError
        from tools.release.validate import ValidationError
        with patch('tools.registry.desired_preview.validate_schema',
                   side_effect=ValidationError('jsonschema missing')):
            with self.assertRaisesRegex(PreviewError,'CATALOG_SCHEMA_INVALID'):
                preview(fixture_module.example())
        self.assertEqual(self.db.verify()['revision'],0)

    def test_invalid_uuid_does_not_write(self):
        with self.assertRaisesRegex(DesiredStoreError,'OPERATION_ID_INVALID'):
            self.append(operation_id='no-uuid')
        self.assertEqual(self.db.verify()['revision'],0)


if __name__ == '__main__':
    unittest.main()
