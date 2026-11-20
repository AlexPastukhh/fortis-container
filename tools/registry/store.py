"""OFFLINE P5 reference: durable, CAS-protected component restriction snapshots.

NO API, grants, production path, trusted evidence verification, or deployment.
Records persist unverified candidate input. A future trusted broker must check
actor, source integrity/freshness, authorization and owner clearance evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path
from contextlib import contextmanager, closing
from typing import Any

from .constraints import _check_snapshot, ConstraintError


class StoreError(ValueError):
    """Fail-closed source-only store error with stable code."""


_UUID = re.compile(r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_ACTOR = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}\Z")
_ZERO = "0" * 64
_SCHEMA = 1


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def fail(code: str):
    raise StoreError(code)


def _ident(value: str, pattern, code: str):
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        fail(code)
    return value


def _safe_path(path: Path, *, allow_absent=False):
    if not path.is_absolute() or path.name in ("", ".", ".."):
        fail("STORE_PATH_INVALID")
    if not path.parent.is_dir() or path.parent.is_symlink():
        fail("STORE_PARENT_NOT_APPROVED")
    if path.is_symlink():
        fail("STORE_SYMLINK_DENIED")
    if not allow_absent and not path.is_file():
        fail("STORE_NOT_INITIALIZED")
    if path.exists():
        info = os.stat(path)
        if not path.is_file() or info.st_nlink != 1:
            fail("STORE_FILE_INVALID")
        if info.st_mode & 0o077:
            fail("STORE_PERMISSIONS_WEAK")


class CandidateStore:
    """Explicit-path reference store; neither actor policy nor owner authority.

    No automatic bootstrap or active production configuration is provided.
    Source-only methods accept fixtures, NOT upstream proof. All outputs have
    evidenceVerified=False, so consumers must not interpret them as permits.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        _safe_path(self.path, allow_absent=True)

    def initialize(self):
        _safe_path(self.path, allow_absent=True)
        if self.path.exists():
            fail("STORE_ALREADY_EXISTS")
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        except FileExistsError:
            fail("STORE_ALREADY_EXISTS")
        else:
            os.close(fd)
        with closing(sqlite3.connect(str(self.path), timeout=3.0)) as db:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE snapshots (
                    revision INTEGER PRIMARY KEY CHECK(revision > 0),
                    snapshot_json TEXT NOT NULL,
                    snapshot_digest TEXT NOT NULL,
                    evidence_ref TEXT NOT NULL,
                    evidence_digest TEXT NOT NULL
                );
                CREATE TABLE operations (
                    operation_id TEXT PRIMARY KEY,
                    actor TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    result_json TEXT NOT NULL
                );
                CREATE TABLE events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT NOT NULL UNIQUE REFERENCES operations(operation_id),
                    revision INTEGER NOT NULL REFERENCES snapshots(revision),
                    event_json TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL
                );
            """)
            db.execute("INSERT INTO meta VALUES ('schemaVersion', ?)", (str(_SCHEMA),))
            db.execute("INSERT INTO meta VALUES ('currentRevision', '0')")
            db.commit()

    @contextmanager
    def _conn(self):
        db = self._connection()
        try:
            yield db
        finally:
            db.close()

    def _connection(self):
        _safe_path(self.path)
        db = sqlite3.connect(str(self.path), timeout=3.0, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=3000")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        version = db.execute("SELECT value FROM meta WHERE key='schemaVersion'").fetchone()
        if version is None or version[0] != str(_SCHEMA):
            db.close()
            fail("SCHEMA_VERSION_UNSUPPORTED")
        return db

    def _current(self, db):
        row = db.execute("SELECT value FROM meta WHERE key='currentRevision'").fetchone()
        if row is None or not str(row[0]).isdigit():
            fail("STORE_METADATA_CORRUPT")
        return int(row[0])

    def _integrity(self, db):
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            fail("STORE_INTEGRITY_FAILED")
        revision = self._current(db)
        previous = _ZERO
        latest_revision = 0
        prior_rules = {}
        rows = db.execute("""SELECT e.seq,e.operation_id,e.revision,e.event_json,e.prev_hash,e.event_hash,
                                  s.snapshot_json,s.snapshot_digest,s.evidence_ref,s.evidence_digest,
                                  o.actor,o.fingerprint,o.result_json
                           FROM events e JOIN snapshots s ON e.revision=s.revision
                           JOIN operations o ON e.operation_id=o.operation_id ORDER BY e.seq""")
        for row in rows:
            if row["prev_hash"] != previous or row["revision"] != latest_revision + 1:
                fail("EVENT_CHAIN_BROKEN")
            try:
                event = json.loads(row["event_json"])
                snapshot = json.loads(row["snapshot_json"])
                receipt = json.loads(row["result_json"])
            except (ValueError, TypeError):
                fail("EVENT_DATA_CORRUPT")
            if canonical(event) != row["event_json"] or canonical(snapshot) != row["snapshot_json"]:
                fail("EVENT_NONCANONICAL")
            if digest(snapshot) != row["snapshot_digest"]:
                fail("SNAPSHOT_DIGEST_MISMATCH")
            # Audit must preserve all proposed clearance references. Their
            # existence is not external verification of owner authority.
            try:
                current_rules = {r["id"]:r for r in snapshot["restrictions"]}
            except (TypeError, KeyError):
                fail("SNAPSHOT_STRUCTURE_CORRUPT")
            clearances = event.get("clearanceRefs")
            if not isinstance(clearances, dict) or set(clearances) != set(prior_rules) - set(current_rules):
                fail("EVENT_CLEARANCE_CORRUPT")
            if any(prior_rules[k] != current_rules[k] for k in prior_rules.keys() & current_rules.keys()):
                fail("RESTRICTION_HISTORY_CHANGED")
            expected = {"revision":row["revision"], "operationId":row["operation_id"],
                        "actor":row["actor"], "snapshotDigest":row["snapshot_digest"],
                        "evidenceDigest":row["evidence_digest"], "evidenceRef":row["evidence_ref"],
                        "previousHash":previous, "clearanceRefs":clearances,
                        "kind":"CANDIDATE_SNAPSHOT"}
            if event != expected:
                fail("EVENT_DATA_MISMATCH")
            previous = digest(event)
            if row["event_hash"] != previous:
                fail("EVENT_CHAIN_BROKEN")
            if receipt.get("revision") != row["revision"] or receipt.get("snapshotDigest") != row["snapshot_digest"]:
                fail("RECEIPT_MISMATCH")
            latest_revision = row["revision"]
            prior_rules = current_rules
        if latest_revision != revision:
            fail("STORE_REVISION_CORRUPT")
        if db.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0] != revision:
            fail("SNAPSHOT_HISTORY_CORRUPT")
        if db.execute("SELECT COUNT(*) FROM operations").fetchone()[0] != revision:
            fail("OPERATION_HISTORY_CORRUPT")
        if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
            fail("FOREIGN_KEY_HISTORY_CORRUPT")
        return {"revision":revision, "headHash":previous, "evidenceVerified":False}

    def verify(self):
        with self._conn() as db:
            return self._integrity(db)

    def current(self):
        with self._conn() as db:
            status = self._integrity(db)
            if status["revision"] == 0:
                return {**status, "snapshot":None}
            row = db.execute("SELECT snapshot_json FROM snapshots WHERE revision=?",
                             (status["revision"],)).fetchone()
            return {**status, "snapshot":json.loads(row[0])}

    def operation(self, operation_id, *, actor):
        _ident(operation_id, _UUID, "OPERATION_ID_INVALID")
        _ident(actor, _ACTOR, "ACTOR_INVALID")
        with self._conn() as db:
            self._integrity(db)
            row = db.execute("SELECT actor,result_json FROM operations WHERE operation_id=?",
                             (operation_id,)).fetchone()
            if row is None:
                return None
            if row["actor"] != actor:
                fail("ACTOR_SCOPE_DENIED")
            return json.loads(row["result_json"])

    def propose(self, *, operation_id, actor, expected_revision, snapshot,
                evidence_ref, evidence_digest, clearance_refs=None):
        """Store an unverified candidate; not an authorization or clearance."""
        _ident(operation_id, _UUID, "OPERATION_ID_INVALID")
        _ident(actor, _ACTOR, "ACTOR_INVALID")
        if type(expected_revision) is not int or expected_revision < 0:
            fail("REVISION_INVALID")
        _ident(evidence_digest, _HEX64, "EVIDENCE_DIGEST_INVALID")
        if not isinstance(evidence_ref, str) or not evidence_ref.strip() or len(evidence_ref) > 512:
            fail("EVIDENCE_REF_INVALID")
        try:
            _check_snapshot(snapshot)
            snap_text = canonical(snapshot)
        except (ConstraintError, ValueError, TypeError, OverflowError) as exc:
            fail("SNAPSHOT_INVALID")
        if len(snap_text.encode()) > 1_000_000:
            fail("SNAPSHOT_TOO_LARGE")
        if clearance_refs is None:
            clearance_refs = {}
        if not isinstance(clearance_refs, dict) or len(clearance_refs) > 1024:
            fail("CLEARANCE_INVALID")
        for name, ref in clearance_refs.items():
            if not isinstance(name, str) or not name or not isinstance(ref, dict) or set(ref) != {"sourceRef", "digest"}:
                fail("CLEARANCE_INVALID")
            if not isinstance(ref["sourceRef"], str) or not ref["sourceRef"].strip() or len(ref["sourceRef"]) > 512:
                fail("CLEARANCE_INVALID")
            _ident(ref["digest"], _HEX64, "CLEARANCE_INVALID")
        fingerprint = digest({"actor":actor, "expectedRevision":expected_revision,
                              "snapshot":snapshot, "evidenceRef":evidence_ref,
                              "evidenceDigest":evidence_digest, "clearanceRefs":clearance_refs})
        with self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                self._integrity(db)
                earlier = db.execute("SELECT fingerprint,result_json FROM operations WHERE operation_id=?",
                                     (operation_id,)).fetchone()
                if earlier is not None:
                    if earlier["fingerprint"] != fingerprint:
                        fail("OPERATION_ID_CONFLICT")
                    db.execute("COMMIT")
                    return json.loads(earlier["result_json"])
                current = self._current(db)
                if expected_revision != current:
                    fail("REVISION_STALE")
                old = db.execute("SELECT snapshot_json FROM snapshots WHERE revision=?", (current,)).fetchone() if current else None
                if old is not None and old[0] == snap_text:
                    fail("SNAPSHOT_UNCHANGED")
                old_rules = {r["id"]:r for r in json.loads(old[0])["restrictions"]} if old else {}
                new_rules = {r["id"]:r for r in snapshot["restrictions"]}
                removed = set(old_rules) - set(new_rules)
                if set(clearance_refs) != removed:
                    fail("CLEARANCE_SCOPE_MISMATCH")
                # Rules with the same identity cannot silently weaken: a
                # changed definition requires removal + re-add with a new ID.
                for ident in old_rules.keys() & new_rules.keys():
                    if old_rules[ident] != new_rules[ident]:
                        fail("RESTRICTION_ID_IMMUTABLE")
                revision = current + 1
                previous = db.execute("SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
                prev_hash = previous[0] if previous else _ZERO
                snap_digest = digest(snapshot)
                event = {"revision":revision,"operationId":operation_id, "actor":actor,
                         "snapshotDigest":snap_digest,"evidenceDigest":evidence_digest,
                         "evidenceRef":evidence_ref,"previousHash":prev_hash,
                         "clearanceRefs":clearance_refs, "kind":"CANDIDATE_SNAPSHOT"}
                event_hash = digest(event)
                result = {"operationId":operation_id, "revision":revision,
                          "snapshotDigest":snap_digest, "eventHash":event_hash,
                          "evidenceVerified":False, "status":"CANDIDATE_RECORDED"}
                db.execute("INSERT INTO snapshots VALUES (?,?,?,?,?)",
                           (revision,snap_text,snap_digest,evidence_ref,evidence_digest))
                db.execute("INSERT INTO operations VALUES (?,?,?,?)",
                           (operation_id,actor,fingerprint,canonical(result)))
                db.execute("INSERT INTO events(operation_id,revision,event_json,prev_hash,event_hash) VALUES (?,?,?,?,?)",
                           (operation_id,revision,canonical(event),prev_hash,event_hash))
                db.execute("UPDATE meta SET value=? WHERE key='currentRevision'", (str(revision),))
                db.execute("COMMIT")
                return result
            except Exception:
                db.execute("ROLLBACK")
                raise

    def backup_to(self, target: Path):
        """One inactive SQLite-consistent snapshot; NEVER installs/restores it."""
        target = Path(target)
        _safe_path(target, allow_absent=True)
        if target.exists():
            fail("BACKUP_TARGET_EXISTS")
        with self._conn() as src:
            status = self._integrity(src)
            try:
                fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
                os.close(fd)
                with sqlite3.connect(str(target)) as dst:
                    src.backup(dst)
                with sqlite3.connect(str(target)) as dst:
                    if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        fail("BACKUP_CORRUPT")
            except Exception:
                if target.is_file() and not target.is_symlink():
                    target.unlink()
                raise
            return {"backupPath":str(target), "revision":status["revision"],
                    "headHash":status["headHash"], "evidenceVerified":False}
