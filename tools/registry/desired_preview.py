"""P5 offline candidate desired-release preview. NO TRUSTED INGESTION / NO API.

This PURE function checks structural consistency against the reviewed Release
Impact v1 rules. All external merge/ancestry/CI/path completeness is a CLAIM
in input fixtures. It cannot authenticate Gateway, GitHub, owner or controller.
Never persist its results as an authoritative queue without an independent
trusted collector and a separately reviewed actor-scoped admission operation.
"""
from __future__ import annotations

import re
from datetime import datetime
from tools.registry.store import digest
from tools.release.validate import validate_impact, validate_schema, ValidationError
from pathlib import Path

SCHEMAS = Path(__file__).resolve().parents[2] / 'docs/schemas'
SHA = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
REPO = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\Z')
NAME = re.compile(r'[a-z][a-z0-9-]{0,99}\Z')
COMPLETE_KEYS = {'mergeLineage', 'changedPaths', 'catalogPinned',
                 'ciChecks', 'ancestorProof', 'dependencyGraph'}


class PreviewError(ValueError):
    pass


def need(condition, code):
    if not condition:
        raise PreviewError(code)


def exact(obj, keys, code):
    need(type(obj) is dict and set(obj) == set(keys), code)
    return obj


def reference(x, code):
    need(type(x) is str and 1 <= len(x) <= 512 and x.strip() == x, code)


def sha(x, code):
    need(type(x) is str and SHA.fullmatch(x) is not None, code)


def _graph(catalog, repository):
    targets = catalog['targets']
    ids = [t['id'] for t in targets]
    need(len(ids) == len(set(ids)), 'CATALOG_DUPLICATE_TARGET')
    units = [u['id'] for u in catalog['buildUnits']]
    need(len(units) == len(set(units)), 'CATALOG_DUPLICATE_UNIT')
    for t in targets:
        need('buildUnit' not in t or t['buildUnit'] in units,
             'CATALOG_BUILD_UNIT_MISSING')
    by_id = {t['id']:t for t in targets}
    visiting, done = set(), set()
    def visit(ident):
        if ident in visiting:
            raise PreviewError('CATALOG_DEPENDENCY_CYCLE')
        if ident in done:
            return
        visiting.add(ident)
        for dep in by_id[ident].get('dependsOn', []):
            if dep['repository'] == repository.split('/')[1]:
                need(dep['target'] in by_id, 'CATALOG_LOCAL_DEPENDENCY_MISSING')
                visit(dep['target'])
        visiting.remove(ident)
        done.add(ident)
    for ident in by_id:
        visit(ident)
    return by_id


def preview(snapshot):
    """Deterministic preliminary records; all results evidenceVerified=False."""
    exact(snapshot, ('schemaVersion','repository','selectedMainSha',
                     'catalogSha','catalogDigest','catalog','mergedPullRequests',
                     'completeness','environmentBindings','dependencyProofs',
                     'sourceReadRef'), 'INPUT_FIELDS_INVALID')
    need(type(snapshot['schemaVersion']) is int and snapshot['schemaVersion']==1,
         'SCHEMA_VERSION_UNSUPPORTED')
    repo=snapshot['repository']
    need(type(repo) is str and REPO.fullmatch(repo) is not None, 'REPOSITORY_INVALID')
    for key in ('selectedMainSha','catalogSha'):
        sha(snapshot[key], 'SOURCE_SHA_INVALID')
    need(type(snapshot['catalogDigest']) is str and
         HEX64.fullmatch(snapshot['catalogDigest']) is not None,
         'CATALOG_DIGEST_INVALID')
    need(type(snapshot['catalog']) is dict and
         digest(snapshot['catalog']) == snapshot['catalogDigest'],
         'CATALOG_DIGEST_MISMATCH')
    reference(snapshot['sourceReadRef'], 'SOURCE_REFERENCE_MISSING')
    complete=exact(snapshot['completeness'], COMPLETE_KEYS, 'COVERAGE_FIELDS_INVALID')
    need(all(type(value) is bool and value for value in complete.values()),
         'EVIDENCE_INCOMPLETE')
    try:
        validate_schema(snapshot['catalog'], SCHEMAS/'build-target-catalog-v1.schema.json')
    except (ValidationError, TypeError, ValueError, KeyError) as e:
        raise PreviewError('CATALOG_SCHEMA_INVALID') from e
    need(snapshot['catalog']['repository'] == repo.split('/')[1],
         'CATALOG_REPOSITORY_MISMATCH')
    targets=_graph(snapshot['catalog'],repo)
    prs=snapshot['mergedPullRequests']
    need(type(prs) is list and 0 < len(prs) <= 100, 'LINEAGE_INCOMPLETE')
    seen, lineage, actions, extras = set(), [], {}, set()
    pr_dependencies={}
    for entry in prs:
        exact(entry, ('number','headSha','mergeSha','mergedAt','mainContainsMerge',
                      'impact','changedPaths','ci','mergeProofRef','pathProofRef'),
              'PR_FIELDS_INVALID')
        num=entry['number']
        need(type(num) is int and 0 < num <= 1000000 and num not in seen,
             'LINEAGE_DUPLICATE_OR_INVALID')
        seen.add(num)
        sha(entry['headSha'],'PR_HEAD_INVALID')
        sha(entry['mergeSha'],'MERGE_SHA_INVALID')
        need(entry['mainContainsMerge'] is True, 'LINEAGE_UNPROVEN')
        for name in ('mergeProofRef','pathProofRef'):
            reference(entry[name],'LINEAGE_REFERENCE_MISSING')
        try:
            dt=datetime.fromisoformat(entry['mergedAt'])
            need(dt.tzinfo is not None, 'MERGED_AT_INVALID')
        except (ValueError, TypeError):
            raise PreviewError('MERGED_AT_INVALID')
        ci=exact(entry['ci'], ('headSha','complete','passedChecks','readbackRef'),
                 'CI_FIELDS_INVALID')
        need(ci['headSha']==entry['headSha'] and ci['complete'] is True and
             type(ci['passedChecks']) is list and 0 < len(ci['passedChecks']) <= 40 and
             all(type(x) is str and 0 < len(x) <= 120 for x in ci['passedChecks']) and
             len(ci['passedChecks'])==len(set(ci['passedChecks'])),
             'CI_NOT_EXACT_HEAD')
        reference(ci['readbackRef'], 'CI_REFERENCE_MISSING')
        try:
            validate_schema(entry['impact'],SCHEMAS/'release-impact-v1.schema.json')
            result=validate_impact(entry['impact'],snapshot['catalog'],entry['changedPaths'])
        except (ValidationError, TypeError, ValueError, KeyError) as e:
            raise PreviewError('IMPACT_NOT_VALIDATED') from e
        impact=entry['impact']['releaseImpact']
        for target in impact['targets']:
            need('unknown' not in target['actions'],'ACTION_UNKNOWN')
            actions.setdefault(target['id'],set()).update(target['actions'])
        deps=set()
        for dependency in impact['dependencies']['pullRequests']:
            need(dependency['repository'] == repo.split('/')[1],
                 'CROSS_REPO_PR_DEPENDENCY_REVIEW')
            deps.add(dependency['number'])
        pr_dependencies[num] = deps
        for dependency in impact['dependencies']['targets']:
            extras.add((dependency['repository'],dependency['target']))
        lineage.append({'number':num,'headSha':entry['headSha'],
                        'mergeSha':entry['mergeSha'],
                        'mergedAt':entry['mergedAt'],
                        'impactDigest':digest(entry['impact']),
                        'ciDigest':digest(ci),
                        'changedPathsDigest':digest(entry['changedPaths'])})
    need(set().union(*pr_dependencies.values()) <= seen,
         'PR_DEPENDENCY_UNVERIFIED')
    visited, active=set(),set()
    def walk(pr_number):
        need(pr_number not in active,'PR_DEPENDENCY_CYCLE')
        if pr_number in visited:
            return
        active.add(pr_number)
        for dependency in pr_dependencies[pr_number]:
            walk(dependency)
        active.remove(pr_number)
        visited.add(pr_number)
    for pr_number in seen:
        walk(pr_number)
    bindings=snapshot['environmentBindings']
    need(type(bindings) is dict and set(bindings)==set(actions),
         'ENVIRONMENT_SCOPE_INCOMPLETE')
    for ident,env in bindings.items():
        need(type(ident) is str and NAME.fullmatch(ident) is not None and
             type(env) is str and env in targets[ident]['deployment']['environments'],
             'ENVIRONMENT_NOT_IN_CATALOG')
    dependencies=set(extras)
    for ident in actions:
        for dep in targets[ident].get('dependsOn',[]):
            dependencies.add((dep['repository'],dep['target']))
    proofs=snapshot['dependencyProofs']
    need(type(proofs) is list and len(proofs) <= 256,'DEPENDENCY_PROOFS_INVALID')
    proof_keys=set()
    for proof in proofs:
        exact(proof,('repository','target','catalogSha','readbackRef'),
              'DEPENDENCY_PROOF_FIELDS_INVALID')
        need(type(proof['repository']) is str and NAME.fullmatch(proof['repository']) and
             type(proof['target']) is str and NAME.fullmatch(proof['target']),
             'DEPENDENCY_PROOF_ID_INVALID')
        sha(proof['catalogSha'],'DEPENDENCY_CATALOG_SHA_INVALID')
        reference(proof['readbackRef'],'DEPENDENCY_PROOF_REFERENCE_MISSING')
        pair=(proof['repository'],proof['target'])
        need(pair not in proof_keys,'DEPENDENCY_PROOF_DUPLICATE')
        proof_keys.add(pair)
        if pair[0] == repo.split('/')[1]:
            need(pair[1] in targets and proof['catalogSha']==snapshot['catalogSha'],
                 'DEPENDENCY_CATALOG_DRIFT')
    need(dependencies == proof_keys,'DEPENDENCY_UNVERIFIED')
    source=snapshot['selectedMainSha']
    lineage=sorted(lineage,key=lambda x:x['number'])
    records=[]
    for ident in sorted(actions):
        t=targets[ident];env=bindings[ident]
        key={'repository':repo,'targetId':ident,'environment':env,
             'desiredSourceSha':source,'catalogSha':snapshot['catalogSha'],
             'catalogDigest':snapshot['catalogDigest']}
        record={'recordId':digest(key), 'identity':key,
                'componentMappingStatus':'UNVERIFIED',
                'buildUnitId':t.get('buildUnit'),
                'artifact':{'state':'NOT_BUILT','digest':None},
                'deploymentProcedure':t['deployment']['procedure'],
                'requiredActions':sorted(actions[ident]),
                'mergedPullRequests':lineage,
                'lineageDigest':digest(lineage),
                'dependencies':sorted([{'repository':a,'target':b}
                                       for a,b in dependencies],key=lambda x:(x['repository'],x['target'])),
                'planningState':'PLANNED_UNVERIFIED', 'actual':None,
                'evidenceVerified':False}
        records.append(record)
    return {'result':'CANDIDATE_PREVIEW_ONLY','sourceReadRef':snapshot['sourceReadRef'],
            'snapshotDigest':digest(snapshot),'evidenceVerified':False,
            'recordCount':len(records),'records':records,
            'noDeploymentOnly':not bool(actions),
            'warning':'NO_TRUSTED_COLLECTOR_OR_WRITE_API_INSTALLED'}
