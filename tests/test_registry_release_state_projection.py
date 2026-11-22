"""Offline P5/P6/P7 event-accounting projection — not a live Registry."""
import copy
import sys
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.registry.store import digest
from tools.registry.release_state_projection import (
    project_manual_queue, ReleaseStateProjectionError,
)

REPO = 'AlexPastukhh/fortis-approvals'
CAT = '3'*40
HEX = '4'*64
OLD = 'a'*40
NEW = 'b'*40


def row(*, source=OLD, target='gateway', revision=1, previous=None):
    identity = {'repository':REPO,'targetId':target,'environment':'production',
                'desiredSourceSha':source,'catalogSha':CAT,'catalogDigest':HEX}
    record = {'recordId':digest(identity),'identity':identity,
              'componentMappingStatus':'UNVERIFIED','buildUnitId':None,
              'artifact':{'state':'NOT_BUILT','digest':None},
              'deploymentProcedure':'docs/use-cases/releases.md',
              'requiredActions':['config-deploy'],'mergedPullRequests':[],
              'lineageDigest':HEX,'dependencies':[],
              'planningState':'PLANNED_UNVERIFIED','actual':None,
              'evidenceVerified':False}
    return {'record':record,'revision':revision,
            'supersedesRecordId':previous,'evidenceVerified':False}


def event(item, sequence=1):
    ident=item['record']['identity']
    return {'sequence':sequence,'eventId':str(uuid.UUID(int=sequence)),
            'kind':'OWNER_REPORTED_COMPLETE',
            'recordId':item['record']['recordId'],
            'repository':ident['repository'],'targetId':ident['targetId'],
            'environment':ident['environment'],
            'sourceSha':ident['desiredSourceSha'],
            'ownerReportRef':f'owner-report-{sequence}'}


class OfflineReleaseStateTests(unittest.TestCase):

    def project(self,rows=None,events=None):
        return project_manual_queue(
            desired_rows=rows if rows is not None else [row()],
            report_events=events if events is not None else [])

    def test_desired_record_is_visible_without_runtime_readback(self):
        projection=self.project()
        self.assertEqual(projection['result'],'SOURCE_ONLY_RELEASE_QUEUE_CANDIDATE')
        self.assertEqual(projection['targetCount'],1)
        item=projection['targets'][0]
        self.assertEqual(item['desiredSourceSha'],OLD)
        self.assertEqual(item['displayState'],'PLANNED_UNVERIFIED')
        self.assertIsNone(item['verifiedInstalled'])
        self.assertEqual(item['installedVerification'],'UNKNOWN')
        self.assertFalse(item['deploymentVerified'])
        self.assertFalse(item['admissionAllowed'])

    def test_manual_report_changes_display_state_not_verified_actual(self):
        first=row()
        projection=self.project([first],[event(first)])
        item=projection['targets'][0]
        self.assertEqual(item['displayState'],'REPORTED_COMPLETE')
        self.assertEqual(item['lastOwnerReportedSourceSha'],OLD)
        self.assertIsNone(item['verifiedInstalled'])
        self.assertFalse(item['deploymentVerified'])
        self.assertFalse(projection['runtimeActivationAllowed'])

    def test_new_merge_after_manual_release_retains_last_report(self):
        first=row()
        second=row(source=NEW,revision=2,
                   previous=first['record']['recordId'])
        projection=self.project([first,second],[event(first)])
        item=projection['targets'][0]
        self.assertEqual(item['desiredSourceSha'],NEW)
        self.assertEqual(item['lastOwnerReportedSourceSha'],OLD)
        self.assertEqual(item['displayState'],'PLANNED_UNVERIFIED')
        self.assertIsNone(item['verifiedInstalled'])

    def test_report_new_desired_does_not_claim_deployed(self):
        first=row()
        second=row(source=NEW,revision=2,
                   previous=first['record']['recordId'])
        projection=self.project([first,second],[event(first),event(second,2)])
        item=projection['targets'][0]
        self.assertEqual(item['displayState'],'REPORTED_COMPLETE')
        self.assertEqual(item['lastOwnerReportedSourceSha'],NEW)
        self.assertIsNone(item['verifiedInstalled'])

    def test_late_report_for_older_release_does_not_close_latest(self):
        first=row()
        second=row(source=NEW,revision=2,
                   previous=first['record']['recordId'])
        projection=self.project([first,second],[event(second),event(first,2)])
        self.assertEqual(projection['targets'][0]['displayState'],'PLANNED_UNVERIFIED')
        self.assertEqual(projection['targets'][0]['lastOwnerReportedSourceSha'],OLD)

    def test_target_environment_are_independent(self):
        gateway=row()
        worker=row(target='worker')
        rows=sorted([gateway,worker],key=lambda r:(r['revision'],r['record']['recordId']))
        projection=self.project(rows,[event(gateway)])
        self.assertEqual(projection['targetCount'],2)
        by_id={x['targetId']:x for x in projection['targets']}
        self.assertEqual(by_id['gateway']['displayState'],'REPORTED_COMPLETE')
        self.assertEqual(by_id['worker']['displayState'],'PLANNED_UNVERIFIED')
        self.assertEqual(by_id['worker']['lastOwnerReportedSourceSha'],None)

    def test_no_desired_no_fake_queue(self):
        self.assertEqual(self.project([],[])['targets'],[])
        with self.assertRaisesRegex(ReleaseStateProjectionError,
                                    'REPORT_RECORD_UNKNOWN_OR_DUPLICATE'):
            self.project([], [event(row())])

    def test_forged_success_or_authority_fields_rejected(self):
        desired=row()
        for injected in ({'kind':'DEPLOYED'},
                         {'kind':'CONTROLLER_VERIFIED_INSTALL'},
                         {'deployed':True},
                         {'admissionAllowed':True},
                         {'evidenceVerified':True},
                         {'reportedBy':'owner'},
                         {'sourceSha':NEW},
                         {'recordId':'0'*64},
                         {'repository':'Evil/repo'}):
            with self.subTest(injected=injected):
                altered={**event(desired),**injected}
                with self.assertRaises(ReleaseStateProjectionError):
                    self.project([desired],[altered])

    def test_replay_and_gapped_event_sequence_fail(self):
        desired=row()
        bad=[event(desired),event(desired,2)]
        with self.assertRaisesRegex(ReleaseStateProjectionError,
                                    'REPORT_RECORD_UNKNOWN_OR_DUPLICATE'):
            self.project([desired],bad)
        with self.assertRaisesRegex(ReleaseStateProjectionError,
                                    'REPORT_EVENT_INVALID'):
            self.project([desired],[event(desired,2)])

    def test_dangling_supersession_and_wrong_order_denied(self):
        first=row()
        second=row(source=NEW,revision=2)
        with self.assertRaisesRegex(ReleaseStateProjectionError,
                                    'DESIRED_SUPERSESSION_GAP'):
            self.project([first,second],[])
        second['supersedesRecordId']=first['record']['recordId']
        with self.assertRaisesRegex(ReleaseStateProjectionError,
                                    'DESIRED_SUPERSESSION_GAP'):
            self.project([second,first],[])

    def test_fake_installed_state_and_verified_record_denied(self):
        desired=row()
        for changed in ({'actual':{'sourceSha':OLD}},
                        {'planningState':'DEPLOYED'},
                        {'evidenceVerified':True},
                        {'componentMappingStatus':'VERIFIED'},
                        {'recordId':'a'*64}):
            with self.subTest(changed=changed):
                altered=copy.deepcopy(desired)
                altered['record'].update(changed)
                with self.assertRaises(ReleaseStateProjectionError):
                    self.project([altered],[])

    def test_refuse_unknown_event_shape_and_overlarge_lists(self):
        desired=row()
        invalid={**event(desired),'sequence':True}
        with self.assertRaises(ReleaseStateProjectionError):
            self.project([desired],[invalid])
        with self.assertRaises(ReleaseStateProjectionError):
            self.project([desired]*501,[])
        with self.assertRaises(ReleaseStateProjectionError):
            self.project([desired],[event(desired)]*1001)


if __name__=='__main__':
    unittest.main()
