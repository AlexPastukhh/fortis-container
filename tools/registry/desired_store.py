"""Offline durable P5 desired-release *candidate* journal, never live ingestion.

All actors, provenance and ancestry references are untrusted fixtures. No
network, Gateway API, background service, release runner or production path.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

from .store import _ACTOR, _HEX64, _UUID, _safe_path, canonical, digest


class DesiredStoreError(ValueError):
    """Fail-closed candidate store error, never a release outcome."""


_SHA = re.compile(r"[0-9a-f]{40}\Z")
_REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\Z")
_NAME = re.compile(r"[a-z][a-z0-9-]{0,99}\Z")
_ZERO = "0" * 64
_ACTIONS = {"image-rebuild", "config-deploy", "windows-update", "package-build", "migration-required"}


def check(condition, reason):
    if not condition:
        raise DesiredStoreError(reason)


def fields(value, names, reason):
    check(type(value) is dict and set(value) == set(names), reason)
    return value


def shape(preview):
    """Confirm only DTO consistency. Does NOT validate a merge or CI evidence."""
    fields(preview, ("result", "sourceReadRef", "snapshotDigest", "evidenceVerified",
                     "recordCount", "records", "noDeploymentOnly", "warning"), "PREVIEW_FIELDS_INVALID")
    check(preview["result"] == "CANDIDATE_PREVIEW_ONLY" and
          preview["evidenceVerified"] is False and
          preview["warning"] == "NO_TRUSTED_COLLECTOR_OR_WRITE_API_INSTALLED",
          "UNVERIFIED_ONLY")
    check(type(preview["sourceReadRef"]) is str and 0 < len(preview["sourceReadRef"]) <= 512,
          "SOURCE_REF_INVALID")
    check(type(preview["snapshotDigest"]) is str and _HEX64.fullmatch(preview["snapshotDigest"]),
          "SNAPSHOT_DIGEST_INVALID")
    records = preview["records"]
    check(type(records) is list and len(records) <= 200 and
          type(preview["recordCount"]) is int and preview["recordCount"] == len(records) and
          type(preview["noDeploymentOnly"]) is bool and
          preview["noDeploymentOnly"] == (len(records) == 0), "RECORD_COUNT_INVALID")
    ids = []
    scopes = []
    sources = set()
    for row in records:
        fields(row, ("recordId", "identity", "componentMappingStatus", "buildUnitId",
                     "artifact", "deploymentProcedure", "requiredActions", "mergedPullRequests",
                     "lineageDigest", "dependencies", "planningState", "actual", "evidenceVerified"),
               "RECORD_FIELDS_INVALID")
        identity = fields(row["identity"], ("repository", "targetId", "environment",
                                            "desiredSourceSha", "catalogSha", "catalogDigest"),
                          "IDENTITY_INVALID")
        check(type(identity["repository"]) is str and _REPO.fullmatch(identity["repository"])
              and all(type(identity[x]) is str and _NAME.fullmatch(identity[x])
                      for x in ("targetId", "environment"))
              and all(type(identity[x]) is str and _SHA.fullmatch(identity[x])
                      for x in ("desiredSourceSha", "catalogSha"))
              and type(identity["catalogDigest"]) is str and _HEX64.fullmatch(identity["catalogDigest"]),
              "IDENTITY_INVALID")
        check(row["recordId"] == digest(identity), "RECORD_ID_MISMATCH")
        check(row["actual"] is None and row["evidenceVerified"] is False and
              row["planningState"] == "PLANNED_UNVERIFIED" and
              row["componentMappingStatus"] == "UNVERIFIED", "FORGED_INSTALLED_STATE")
        check(row["artifact"] == {"state": "NOT_BUILT", "digest": None}, "ARTIFACT_INVALID")
        check(row["buildUnitId"] is None or
              (type(row["buildUnitId"]) is str and _NAME.fullmatch(row["buildUnitId"])),
              "BUILD_UNIT_INVALID")
        check(type(row["deploymentProcedure"]) is str and
              0 < len(row["deploymentProcedure"]) <= 240, "PROCEDURE_INVALID")
        actions = row["requiredActions"]
        check(type(actions) is list and bool(actions) and actions == sorted(set(actions)) and
              set(actions) <= _ACTIONS, "ACTIONS_INVALID")
        lineage = row["mergedPullRequests"]
        check(type(lineage) is list and bool(lineage) and len(lineage) <= 100 and
              row["lineageDigest"] == digest(lineage), "LINEAGE_INVALID")
        nums = []
        for item in lineage:
            fields(item, ("number", "headSha", "mergeSha", "mergedAt", "impactDigest",
                          "ciDigest", "changedPathsDigest"), "LINEAGE_FIELDS_INVALID")
            check(type(item["number"]) is int and item["number"] > 0 and
                  type(item["mergedAt"]) is str and bool(item["mergedAt"]) and
                  all(type(item[x]) is str and _SHA.fullmatch(item[x]) for x in ("headSha", "mergeSha")) and
                  all(type(item[x]) is str and _HEX64.fullmatch(item[x])
                      for x in ("impactDigest", "ciDigest", "changedPathsDigest")),
                  "LINEAGE_INVALID")
            nums.append(item["number"])
        check(nums == sorted(set(nums)), "LINEAGE_ORDER_INVALID")
        dependencies = row["dependencies"]
        check(type(dependencies) is list and len(dependencies) <= 256, "DEPENDENCIES_INVALID")
        pairs = []
        for dep in dependencies:
            fields(dep, ("repository", "target"), "DEPENDENCY_FIELDS_INVALID")
            check(all(type(dep[x]) is str and _NAME.fullmatch(dep[x]) for x in ("repository", "target")),
                  "DEPENDENCY_INVALID")
            pairs.append((dep["repository"], dep["target"]))
        check(pairs == sorted(set(pairs)), "DEPENDENCY_ORDER_INVALID")
        ids.append(row["recordId"])
        scopes.append((identity["repository"], identity["targetId"], identity["environment"]))
        sources.add((identity["repository"], identity["desiredSourceSha"],
                     identity["catalogSha"], identity["catalogDigest"], row["lineageDigest"]))
    check(len(set(ids)) == len(ids) and len(set(scopes)) == len(scopes) and
          len(sources) <= 1, "BATCH_MIXED_OR_DUPLICATE")
    return digest(preview)


class DesiredCandidateStore:
    """Explicit-path SQLite store for unverified candidate records only."""

    def __init__(self, path):
        self.path = Path(path)
        _safe_path(self.path, allow_absent=True)

    def initialize(self):
        _safe_path(self.path, allow_absent=True)
        check(not self.path.exists(), "STORE_ALREADY_EXISTS")
        try:
            handle = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except FileExistsError as exc:
            raise DesiredStoreError("STORE_ALREADY_EXISTS") from exc
        os.close(handle)
        with closing(sqlite3.connect(str(self.path), timeout=3)) as db:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE batches (
                    revision INTEGER PRIMARY KEY CHECK(revision > 0),
                    operation_id TEXT UNIQUE NOT NULL, actor TEXT NOT NULL,
                    fingerprint TEXT NOT NULL, preview_json TEXT NOT NULL,
                    preview_digest TEXT UNIQUE NOT NULL, links_json TEXT NOT NULL,
                    result_json TEXT NOT NULL
                );
                CREATE TABLE records (
                    record_id TEXT PRIMARY KEY,
                    revision INTEGER NOT NULL REFERENCES batches(revision),
                    repository TEXT NOT NULL, target_id TEXT NOT NULL,
                    environment TEXT NOT NULL, desired_sha TEXT NOT NULL,
                    catalog_sha TEXT NOT NULL, catalog_digest TEXT NOT NULL,
                    supersedes_id TEXT UNIQUE REFERENCES records(record_id),
                    record_json TEXT NOT NULL, record_digest TEXT NOT NULL
                );
                CREATE TABLE events (
                    revision INTEGER PRIMARY KEY REFERENCES batches(revision),
                    event_json TEXT NOT NULL, prev_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL
                );
            """)
            db.execute("INSERT INTO meta VALUES('schemaVersion', '1')")
            db.execute("INSERT INTO meta VALUES('revision', '0')")
            db.commit()

    @contextmanager
    def _connection(self):
        _safe_path(self.path)
        db = sqlite3.connect(str(self.path), timeout=3, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA busy_timeout=3000")
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            schema = db.execute("SELECT value FROM meta WHERE key='schemaVersion'").fetchone()
            check(schema is not None and schema[0] == '1', "SCHEMA_UNSUPPORTED")
            yield db
        finally:
            db.close()

    @staticmethod
    def _revision(db):
        row = db.execute("SELECT value FROM meta WHERE key='revision'").fetchone()
        check(row is not None and str(row[0]).isdigit(), "REVISION_CORRUPT")
        return int(row[0])

    def _verify(self, db):
        check(db.execute("PRAGMA integrity_check").fetchone()[0] == 'ok', "STORE_INTEGRITY_FAILED")
        check(db.execute("PRAGMA foreign_key_check").fetchone() is None, "FOREIGN_KEYS_CORRUPT")
        revision = self._revision(db)
        previous_hash = _ZERO
        previous_revision = 0
        seen_records = set()
        active = {}
        for batch in db.execute("SELECT * FROM batches ORDER BY revision"):
            n = batch['revision']
            check(n == previous_revision + 1, "BATCH_HISTORY_GAP")
            event_row = db.execute("SELECT * FROM events WHERE revision=?", (n,)).fetchone()
            check(event_row is not None and event_row['prev_hash'] == previous_hash,
                  "EVENT_CHAIN_BROKEN")
            try:
                preview = json.loads(batch['preview_json'])
                links = json.loads(batch['links_json'])
                event = json.loads(event_row['event_json'])
                receipt = json.loads(batch['result_json'])
                check(batch['preview_json'] == canonical(preview) and
                      batch['links_json'] == canonical(links) and
                      event_row['event_json'] == canonical(event) and
                      batch['result_json'] == canonical(receipt), "HISTORY_NONCANONICAL")
                shape(preview)
            except (TypeError, ValueError, OverflowError) as exc:
                raise DesiredStoreError("HISTORY_DATA_INVALID") from exc
            check(batch['preview_digest'] == digest(preview), "PREVIEW_DIGEST_CHANGED")
            check(batch['fingerprint'] == digest({
                "actor": batch['actor'], "expectedRevision": n - 1,
                "preview": preview, "links": links}), "OPERATION_FINGERPRINT_CHANGED")
            expected = {"revision": n, "operationId": batch['operation_id'],
                        "actor": batch['actor'], "previewDigest": batch['preview_digest'],
                        "recordIds": [r['recordId'] for r in preview['records']],
                        "links": links, "previousHash": previous_hash,
                        "kind": "UNVERIFIED_DESIRED_BATCH"}
            check(expected == event, "EVENT_PAYLOAD_CHANGED")
            previous_hash = digest(event)
            check(event_row['event_hash'] == previous_hash, "EVENT_CHAIN_BROKEN")
            expected_receipt = {"operationId": batch['operation_id'], "revision": n,
                                "previewDigest": batch['preview_digest'],
                                "recordIds": expected['recordIds'],
                                "eventHash": previous_hash, "status": "CANDIDATE_RECORDED",
                                "evidenceVerified": False}
            check(receipt == expected_receipt, "RECEIPT_CHANGED")
            check(type(links) is list and len(links) == len(preview['records']),
                  "SUPERSESSION_LINKS_INVALID")
            for record, link in zip(preview['records'], links):
                identity = record['identity']
                rid = record['recordId']
                check(type(link) is dict and set(link) == {'newRecordId', 'supersedesRecordId',
                                                            'ancestryRef'} and link['newRecordId'] == rid,
                      "SUPERSESSION_LINKS_INVALID")
                row = db.execute("SELECT * FROM records WHERE record_id=?", (rid,)).fetchone()
                check(row is not None and row['revision'] == n and
                      row['record_json'] == canonical(record) and
                      row['record_digest'] == digest(record) and
                      row['repository'] == identity['repository'] and
                      row['target_id'] == identity['targetId'] and
                      row['environment'] == identity['environment'] and
                      row['desired_sha'] == identity['desiredSourceSha'] and
                      row['catalog_sha'] == identity['catalogSha'] and
                      row['catalog_digest'] == identity['catalogDigest'], "RECORD_HISTORY_CHANGED")
                scope = (identity['repository'], identity['targetId'], identity['environment'])
                old = active.get(scope)
                check(row['supersedes_id'] == old and link['supersedesRecordId'] == old,
                      "SUPERSESSION_HISTORY_CHANGED")
                if old is not None:
                    previous = db.execute("SELECT * FROM records WHERE record_id=?", (old,)).fetchone()
                    check(previous is not None and previous['desired_sha'] != identity['desiredSourceSha']
                          and previous['catalog_sha'] == identity['catalogSha']
                          and previous['catalog_digest'] == identity['catalogDigest']
                          and type(link['ancestryRef']) is str and bool(link['ancestryRef']),
                          "SUPERSESSION_HISTORY_CHANGED")
                else:
                    check(link['ancestryRef'] is None, "SUPERSESSION_HISTORY_CHANGED")
                active[scope] = rid
                seen_records.add(rid)
            previous_revision = n
        check(previous_revision == revision and
              db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == revision and
              db.execute("SELECT COUNT(*) FROM records").fetchone()[0] == len(seen_records),
              "HISTORY_COUNT_MISMATCH")
        return {"revision": revision, "headHash": previous_hash, "evidenceVerified": False}

    def verify(self):
        with self._connection() as db:
            return self._verify(db)

    def operation(self, operation_id, *, actor):
        check(type(operation_id) is str and _UUID.fullmatch(operation_id), "OPERATION_ID_INVALID")
        check(type(actor) is str and _ACTOR.fullmatch(actor), "ACTOR_INVALID")
        with self._connection() as db:
            self._verify(db)
            result = db.execute("SELECT actor,result_json FROM batches WHERE operation_id=?",
                                (operation_id,)).fetchone()
            if result is None:
                return None
            check(result['actor'] == actor, "ACTOR_LABEL_MISMATCH")
            return json.loads(result['result_json'])

    def list_candidates(self, *, repository):
        check(type(repository) is str and _REPO.fullmatch(repository), "REPOSITORY_INVALID")
        with self._connection() as db:
            self._verify(db)
            rows = db.execute("SELECT * FROM records WHERE repository=? ORDER BY revision,record_id",
                              (repository,))
            return [{"record": json.loads(row['record_json']),
                     "supersedesRecordId": row['supersedes_id'], "revision": row['revision'],
                     "evidenceVerified": False} for row in rows]

    def append(self, *, operation_id, actor, expected_revision, preview, links):
        check(type(operation_id) is str and _UUID.fullmatch(operation_id), "OPERATION_ID_INVALID")
        check(type(actor) is str and _ACTOR.fullmatch(actor), "ACTOR_INVALID")
        check(type(expected_revision) is int and expected_revision >= 0, "REVISION_INVALID")
        shape(preview)
        preview_json = canonical(preview)
        check(len(preview_json.encode('utf-8')) <= 1_000_000, "PREVIEW_TOO_LARGE")
        check(type(links) is list and len(links) == len(preview['records']), "LINK_SCOPE_INVALID")
        ordered = []
        for record, link in zip(preview['records'], links):
            fields(link, ("newRecordId", "supersedesRecordId", "ancestryRef"),
                   "LINK_FIELDS_INVALID")
            check(link['newRecordId'] == record['recordId'], "LINK_ORDER_INVALID")
            previous = link['supersedesRecordId']
            reference = link['ancestryRef']
            check((previous is None and reference is None) or
                  (type(previous) is str and _HEX64.fullmatch(previous) and
                   type(reference) is str and 0 < len(reference) <= 512),
                  "ANCESTRY_REFERENCE_INVALID")
            ordered.append(link)
        fingerprint = digest({"actor": actor, "expectedRevision": expected_revision,
                              "preview": preview, "links": ordered})
        preview_digest = digest(preview)
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                state = self._verify(db)
                original = db.execute("SELECT fingerprint,result_json FROM batches WHERE operation_id=?",
                                      (operation_id,)).fetchone()
                if original is not None:
                    check(original['fingerprint'] == fingerprint, "OPERATION_ID_CONFLICT")
                    db.execute("COMMIT")
                    return json.loads(original['result_json'])
                check(state['revision'] == expected_revision, "REVISION_STALE")
                check(db.execute("SELECT 1 FROM batches WHERE preview_digest=?",
                                 (preview_digest,)).fetchone() is None,
                      "BATCH_ALREADY_STORED")
                for record, link in zip(preview['records'], ordered):
                    identity = record['identity']
                    check(db.execute("SELECT 1 FROM records WHERE record_id=?",
                                     (record['recordId'],)).fetchone() is None,
                          "RECORD_ALREADY_STORED")
                    old = db.execute("""SELECT r.* FROM records r
                           WHERE r.repository=? AND r.target_id=? AND r.environment=?
                           AND NOT EXISTS(SELECT 1 FROM records next WHERE next.supersedes_id=r.record_id)""",
                        (identity['repository'], identity['targetId'], identity['environment'])).fetchall()
                    check(len(old) <= 1, "AMBIGUOUS_PREDECESSOR")
                    if not old:
                        check(link['supersedesRecordId'] is None, "UNEXPECTED_PREDECESSOR")
                    else:
                        prev = old[0]
                        check(link['supersedesRecordId'] == prev['record_id'], "PREDECESSOR_MISMATCH")
                        check(prev['desired_sha'] != identity['desiredSourceSha'],
                              "SAME_SOURCE_SHA_NOT_NEW_VERSION")
                        check(prev['catalog_sha'] == identity['catalogSha'] and
                              prev['catalog_digest'] == identity['catalogDigest'],
                              "CATALOG_CONTINUITY_NOT_ESTABLISHED")
                        # This is a stored CLAIM, not verified GitHub ancestry evidence.
                        check(link['ancestryRef'] is not None, "ANCESTRY_REFERENCE_MISSING")
                revision = expected_revision + 1
                event = {"revision": revision, "operationId": operation_id,
                         "actor": actor, "previewDigest": preview_digest,
                         "recordIds": [r['recordId'] for r in preview['records']],
                         "links": ordered, "previousHash": state['headHash'],
                         "kind": "UNVERIFIED_DESIRED_BATCH"}
                event_hash = digest(event)
                receipt = {"operationId": operation_id, "revision": revision,
                           "previewDigest": preview_digest, "recordIds": event['recordIds'],
                           "eventHash": event_hash, "status": "CANDIDATE_RECORDED",
                           "evidenceVerified": False}
                db.execute("INSERT INTO batches VALUES(?,?,?,?,?,?,?,?)",
                           (revision, operation_id, actor, fingerprint, preview_json,
                            preview_digest, canonical(ordered), canonical(receipt)))
                for record, link in zip(preview['records'], ordered):
                    identity = record['identity']
                    db.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                               (record['recordId'], revision, identity['repository'],
                                identity['targetId'], identity['environment'],
                                identity['desiredSourceSha'], identity['catalogSha'],
                                identity['catalogDigest'], link['supersedesRecordId'],
                                canonical(record), digest(record)))
                db.execute("INSERT INTO events VALUES(?,?,?,?)",
                           (revision, canonical(event), state['headHash'], event_hash))
                db.execute("UPDATE meta SET value=? WHERE key='revision'", (str(revision),))
                db.execute("COMMIT")
                return receipt
            except Exception:
                db.execute("ROLLBACK")
                raise

    def backup_to(self, target):
        target = Path(target)
        _safe_path(target, allow_absent=True)
        check(not target.exists(), "BACKUP_TARGET_EXISTS")
        with self._connection() as source:
            state = self._verify(source)
            try:
                fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                os.close(fd)
                with closing(sqlite3.connect(str(target))) as dest:
                    source.backup(dest)
                check(DesiredCandidateStore(target).verify() == state,
                      "BACKUP_VERIFICATION_FAILED")
            except Exception:
                if target.is_file() and not target.is_symlink():
                    target.unlink()
                raise
            return {"backupPath": str(target), **state}
