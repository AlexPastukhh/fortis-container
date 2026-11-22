"""Offline V1 manual-release queue projection. NOT a trusted Registry API.

Consumes candidate desired-store rows and source-only owner-report *claims*.
This is a product-state test seam, not a second authoritative SQLite store,
owner authorization, installed-state verifier or release executor.
"""
from __future__ import annotations

from .desired_store import _NAME, _REPO, _SHA, fields as _desired_fields, DesiredStoreError
from .store import _UUID, digest


class ReleaseStateProjectionError(ValueError):
    """Invalid source-only projection input: never a deployment outcome."""


def _need(ok, reason):
    if not ok:
        raise ReleaseStateProjectionError(reason)


def fields(value, names, reason):
    try:
        return _desired_fields(value, names, reason)
    except DesiredStoreError as exc:
        raise ReleaseStateProjectionError(str(exc)) from None


def project_manual_queue(*, desired_rows, report_events):
    """Project latest desired and last owner-reported release per target/env.

    The source inputs are NOT authenticated. In particular, event existence
    cannot populate verified actual, assert DEPLOYED, authorize a controller,
    or establish the current installed version. Future trusted ingestion must
    validate the original owner event and controller receipt independently.
    """
    _need(type(desired_rows) is list and len(desired_rows) <= 500
          and type(report_events) is list and len(report_events) <= 1000,
          'PROJECTION_INPUT_LIMIT')
    by_record = {}
    by_scope = {}
    ordered = []
    for item in desired_rows:
        fields(item, ('record', 'supersedesRecordId', 'revision',
                      'evidenceVerified'), 'DESIRED_ROW_INVALID')
        record = item['record']
        _need(type(record) is dict and set(record) == {
            'recordId','identity','componentMappingStatus','buildUnitId',
            'artifact','deploymentProcedure','requiredActions',
            'mergedPullRequests','lineageDigest','dependencies',
            'planningState','actual','evidenceVerified'}, 'DESIRED_ROW_INVALID')
        identity = fields(record['identity'], ('repository','targetId',
            'environment','desiredSourceSha','catalogSha','catalogDigest'),
            'IDENTITY_INVALID')
        _need(type(identity['repository']) is str
              and _REPO.fullmatch(identity['repository']) is not None
              and all(type(identity[k]) is str and
                      _NAME.fullmatch(identity[k]) is not None
                      for k in ('targetId','environment'))
              and all(type(identity[k]) is str and
                      _SHA.fullmatch(identity[k]) is not None
                      for k in ('desiredSourceSha','catalogSha'))
              and record['recordId'] == digest(identity)
              and type(item['revision']) is int and item['revision'] > 0
              and item['evidenceVerified'] is False
              and record['evidenceVerified'] is False
              and record['planningState'] == 'PLANNED_UNVERIFIED'
              and record['actual'] is None
              and record['componentMappingStatus'] == 'UNVERIFIED'
              and record['artifact'] == {'state':'NOT_BUILT','digest':None},
              'UNVERIFIED_DESIRED_ONLY')
        rid = record['recordId']
        _need(rid not in by_record, 'DUPLICATE_DESIRED_RECORD')
        scope = (identity['repository'], identity['targetId'],
                 identity['environment'])
        previous = by_scope.get(scope)
        _need(item['supersedesRecordId'] ==
              (previous['record']['recordId'] if previous else None),
              'DESIRED_SUPERSESSION_GAP')
        _need(previous is None or
              (item['revision'] > previous['revision'] and
               identity['desiredSourceSha'] !=
               previous['record']['identity']['desiredSourceSha']),
              'DESIRED_ORDER_INVALID')
        by_record[rid] = item
        by_scope[scope] = item
        ordered.append((item['revision'],rid))
    _need(ordered == sorted(ordered), 'DESIRED_ORDER_INVALID')

    last_report = {}
    reported_records = set()
    event_ids = set()
    for position, event in enumerate(report_events, 1):
        fields(event, ('sequence','eventId','kind','recordId',
                       'repository','targetId','environment',
                       'sourceSha','ownerReportRef'),
               'REPORT_EVENT_INVALID')
        _need(type(event['sequence']) is int
              and event['sequence'] == position
              and type(event['eventId']) is str
              and _UUID.fullmatch(event['eventId']) is not None
              and event['eventId'] not in event_ids
              and event['kind'] == 'OWNER_REPORTED_COMPLETE'
              and type(event['ownerReportRef']) is str
              and 1 <= len(event['ownerReportRef']) <= 512
              and event['ownerReportRef'].strip() ==
                  event['ownerReportRef'],
              'REPORT_EVENT_INVALID')
        rid = event['recordId']
        _need(type(rid) is str and rid in by_record
              and rid not in reported_records,
              'REPORT_RECORD_UNKNOWN_OR_DUPLICATE')
        identity = by_record[rid]['record']['identity']
        _need(all(event[k] == identity[name] for k,name in (
            ('repository','repository'), ('targetId','targetId'),
            ('environment','environment'),('sourceSha','desiredSourceSha'))),
            'REPORT_IDENTITY_MISMATCH')
        event_ids.add(event['eventId'])
        reported_records.add(rid)
        scope = (identity['repository'],identity['targetId'],
                 identity['environment'])
        last_report[scope] = event

    result = []
    for scope,item in sorted(by_scope.items()):
        record = item['record']
        event = last_report.get(scope)
        current_report = (event is not None and
                          event['recordId'] == record['recordId'])
        result.append({
            'repository': scope[0], 'targetId': scope[1],
            'environment': scope[2],
            'desiredRecordId': record['recordId'],
            'desiredSourceSha': record['identity']['desiredSourceSha'],
            'lastOwnerReportedSourceSha': (
                event['sourceSha'] if event is not None else None),
            'lastOwnerReportEventId': (
                event['eventId'] if event is not None else None),
            'displayState': ('REPORTED_COMPLETE' if current_report
                             else 'PLANNED_UNVERIFIED'),
            'verifiedInstalled': None,
            'installedVerification': 'UNKNOWN',
            'deploymentVerified': False,
            'evidenceVerified': False,
            'admissionAllowed': False,
            'writeAllowed': False,
        })
    return {'result':'SOURCE_ONLY_RELEASE_QUEUE_CANDIDATE',
            'sourceOnly':True,'eventCount':len(report_events),
            'targetCount':len(result),'targets':result,
            'deploymentVerified':False,'runtimeActivationAllowed':False}
