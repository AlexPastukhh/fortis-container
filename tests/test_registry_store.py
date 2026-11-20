"""Offline SQLite P5 candidate persistence: no real releases, tokens or network."""
from __future__ import annotations

import copy
import json
import sqlite3
import sys
import tempfile
import threading
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.registry.store import CandidateStore, StoreError


GW = "fortis-approvals/primary/gateway"
RDG = "rd-graphs/backend/api"


def snapshot():
    return {
        "schemaVersion": 1,
        "components": [
            {"id": GW, "resources": ["gateway-state"], "requires": []},
            {"id": RDG, "resources": ["rdg-state"], "requires": []},
        ],
        "restrictions": [{"id": "gateway-release-window", "components": [GW],
                          "resources": ["gateway-state"],
                          "operations": ["gateway_apply", "gateway_request_write"],
                          "effect": "BLOCK", "phase": "QUIESCENCE",
                          "reason": "owner Check/Apply window requires worker quiescence",
                          "sourceRef": "UC-GW-005", "clearBy": "protected original attempt and fresh readback"}],
        "coverage": {"completeComponents": [GW, RDG],
                     "completeResources": ["gateway-state", "rdg-state"],
                     "fresh":True, "sourceRef":"untrusted-offline-fixture"},
    }


class DurableStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / "p5-candidate.sqlite"
        self.store = CandidateStore(self.path)
        self.store.initialize()
        self.actor = "trusted-planner-fixture"
        self.i = 0

    def uuid(self):
        self.i += 1
        return str(uuid.UUID(int=self.i))

    def submit(self, obj=None, **overrides):
        params = dict(operation_id=self.uuid(), actor=self.actor,
                      expected_revision=self.store.verify()["revision"],
                      snapshot=snapshot() if obj is None else obj,
                      evidence_ref="offline-test-fixture", evidence_digest="a"*64)
        params.update(overrides)
        return self.store.propose(**params)

    def test_explicit_bootstrap_not_implicit(self):
        other = CandidateStore(self.root / "absent.sqlite")
        self.assertFalse(other.path.exists())
        with self.assertRaisesRegex(StoreError, "STORE_NOT_INITIALIZED"):
            other.current()
        with self.assertRaisesRegex(StoreError, "STORE_ALREADY_EXISTS"):
            self.store.initialize()

    def test_current_initial_revision_and_no_trust(self):
        self.assertEqual(self.store.current()["revision"], 0)
        self.assertIsNone(self.store.current()["snapshot"])
        self.assertIs(self.store.current()["evidenceVerified"], False)

    def test_commit_and_fresh_readback(self):
        receipt = self.submit()
        self.assertEqual(receipt["status"], "CANDIDATE_RECORDED")
        self.assertEqual(receipt["revision"], 1)
        self.assertFalse(receipt["evidenceVerified"])
        reopened = CandidateStore(self.path)
        self.assertEqual(reopened.current()["snapshot"], snapshot())
        self.assertEqual(reopened.verify()["headHash"], receipt["eventHash"])

    def test_retry_same_id_returns_original_receipt_without_new_event(self):
        operation_id = self.uuid()
        first = self.submit(operation_id=operation_id, expected_revision=0)
        second = self.submit(operation_id=operation_id, expected_revision=0)
        self.assertEqual(first, second)
        self.assertEqual(self.store.current()["revision"], 1)

    def test_same_id_different_payload_rejected(self):
        operation_id = self.uuid()
        self.submit(operation_id=operation_id, expected_revision=0)
        with self.assertRaisesRegex(StoreError, "OPERATION_ID_CONFLICT"):
            self.submit(operation_id=operation_id, expected_revision=1)
        self.assertEqual(self.store.verify()["revision"], 1)

    def test_stale_cas_rejected_without_mutation(self):
        self.submit()
        before = self.store.verify()
        with self.assertRaisesRegex(StoreError, "REVISION_STALE"):
            self.submit(expected_revision=0)
        self.assertEqual(self.store.verify(), before)

    def test_operation_read_scoped_to_actor(self):
        ident = self.uuid()
        receipt = self.submit(operation_id=ident)
        self.assertEqual(self.store.operation(ident, actor=self.actor), receipt)
        self.assertIsNone(self.store.operation(self.uuid(), actor=self.actor))
        with self.assertRaisesRegex(StoreError, "ACTOR_SCOPE_DENIED"):
            self.store.operation(ident, actor="other-fixture")

    def test_rule_removal_requires_exact_clearance_reference(self):
        self.submit()
        later = snapshot();later["restrictions"] = []
        with self.assertRaisesRegex(StoreError, "CLEARANCE_SCOPE_MISMATCH"):
            self.submit(later)
        with self.assertRaisesRegex(StoreError, "CLEARANCE_SCOPE_MISMATCH"):
            self.submit(later, clearance_refs={"irrelevant":{"sourceRef":"UC","digest":"b"*64}})
        recorded = self.submit(later, clearance_refs={"gateway-release-window":{
            "sourceRef":"protected-receipt-reference-not-verified", "digest":"b"*64}})
        self.assertEqual(recorded["revision"], 2)
        self.assertFalse(recorded["evidenceVerified"])
        self.assertEqual(self.store.current()["snapshot"]["restrictions"], [])

    def test_rule_id_cannot_silently_weaken(self):
        self.submit()
        later = snapshot(); later["restrictions"][0]["effect"] = "REVIEW_REQUIRED"
        with self.assertRaisesRegex(StoreError, "RESTRICTION_ID_IMMUTABLE"):
            self.submit(later)

    def test_schema_validation_and_invalid_snapshot(self):
        bad = snapshot();bad["schemaVersion"] = 2
        with self.assertRaisesRegex(StoreError, "SNAPSHOT_INVALID"):
            self.submit(bad)
        self.assertEqual(self.store.verify()["revision"], 0)

    def test_missing_revision_no_fabrication(self):
        self.submit()
        db = sqlite3.connect(self.path)
        db.execute("DELETE FROM events")
        db.commit();db.close()
        with self.assertRaisesRegex(StoreError, "STORE_REVISION_CORRUPT"):
            self.store.current()

    def test_event_tamper_detected(self):
        self.submit()
        db = sqlite3.connect(self.path)
        db.execute("UPDATE events SET event_json='{}' WHERE seq=1")
        db.commit();db.close()
        with self.assertRaises(StoreError):self.store.verify()

    def test_snapshot_tamper_detected(self):
        self.submit()
        db = sqlite3.connect(self.path)
        db.execute("UPDATE snapshots SET snapshot_json='{}' WHERE revision=1")
        db.commit();db.close()
        with self.assertRaisesRegex(StoreError, "SNAPSHOT_DIGEST_MISMATCH"):
            self.store.verify()

    def test_backup_to_new_inactive_store(self):
        self.submit()
        backup = self.root / "offline-backup.sqlite"
        record = self.store.backup_to(backup)
        self.assertFalse(record["evidenceVerified"])
        reopened = CandidateStore(backup)
        self.assertEqual(reopened.verify()["revision"], 1)
        self.assertEqual(reopened.verify()["headHash"], record["headHash"])
        with self.assertRaisesRegex(StoreError, "BACKUP_TARGET_EXISTS"):
            self.store.backup_to(backup)
        self.assertEqual(self.store.current()["revision"], 1)

    def test_world_readable_sqlite_is_denied(self):
        self.path.chmod(0o644)
        try:
            with self.assertRaisesRegex(StoreError, "STORE_PERMISSIONS_WEAK"):
                self.store.verify()
        finally:
            self.path.chmod(0o600)
        self.assertEqual(self.store.verify()["revision"], 0)

    def test_symlink_storage_denied(self):
        alias = self.root / "symlink.sqlite"
        alias.symlink_to(self.path)
        with self.assertRaisesRegex(StoreError, "STORE_SYMLINK_DENIED"):
            CandidateStore(alias)

    def test_concurrent_competing_cas_one_wins(self):
        params = []
        for i in range(2):
            d = snapshot();d["restrictions"].append({
                "id": f"new-rule-{i}", "components":[RDG], "resources":[],
                "operations":["release_apply"],"effect":"BLOCK", "phase":"CHECK",
                "reason":"fixture", "sourceRef":"fixture", "clearBy":"receipt"})
            params.append(dict(operation_id=self.uuid(), actor=self.actor,
                               expected_revision=0, snapshot=d, evidence_ref="fixture",
                               evidence_digest="c"*64))
        barrier = threading.Barrier(2)
        answers = []
        def worker(arg):
            barrier.wait(timeout=3)
            try:answers.append(self.store.propose(**arg)["revision"])
            except StoreError as exc:answers.append(str(exc))
        threads = [threading.Thread(target=worker, args=(arg,)) for arg in params]
        for t in threads:t.start()
        for t in threads:t.join(timeout=5)
        self.assertFalse(any(t.is_alive() for t in threads))
        self.assertEqual(sorted(map(str, answers)), ["1", "REVISION_STALE"])
        self.assertEqual(self.store.verify()["revision"], 1)

    def test_lost_ack_read_original_operation_then_do_not_retry(self):
        ident=self.uuid()
        receipt=self.submit(operation_id=ident)
        recovered=CandidateStore(self.path).operation(ident,actor=self.actor)
        self.assertEqual(receipt,recovered)
        self.assertEqual(self.store.verify()["revision"], 1)

    def test_invalid_id_does_not_change_db(self):
        with self.assertRaisesRegex(StoreError,"OPERATION_ID_INVALID"):
            self.submit(operation_id="not-a-uuid")
        with self.assertRaisesRegex(StoreError,"EVIDENCE_DIGEST_INVALID"):
            self.submit(evidence_digest="not-a-digest")
        self.assertEqual(self.store.verify()["revision"], 0)


    def test_different_request_identical_snapshot_does_not_create_new_event(self):
        self.submit()
        before = self.store.verify()
        with self.assertRaisesRegex(StoreError, "SNAPSHOT_UNCHANGED"):
            self.submit()
        self.assertEqual(self.store.verify(), before)

    def test_clearance_references_are_preserved_in_immutable_event(self):
        self.submit()
        later = snapshot();later["restrictions"] = []
        proof = {"gateway-release-window": {"sourceRef":"owner-evidence-placeholder",
                                            "digest":"d"*64}}
        self.submit(later, clearance_refs=proof)
        with sqlite3.connect(self.path) as db:
            rows = db.execute("SELECT event_json FROM events ORDER BY seq").fetchall()
        self.assertEqual(json.loads(rows[1][0])["clearanceRefs"], proof)
        self.assertEqual(self.store.verify()["revision"], 2)

    def test_untracked_orphan_operation_is_detected(self):
        self.submit()
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO operations VALUES (?,?,?,?)",
                       (self.uuid(), self.actor, "f"*64, "{}"))
        with self.assertRaisesRegex(StoreError, "OPERATION_HISTORY_CORRUPT"):
            self.store.verify()

    def test_two_revision_backup_integrity(self):
        self.submit()
        newer = snapshot()
        newer["restrictions"].append({
            "id":"rdg-migration", "components":[RDG], "resources":["rdg-state"],
            "operations":["migration_apply"], "effect":"REVIEW_REQUIRED", "phase":"PREPARE",
            "reason":"requires separate owner gate", "sourceRef":"UC-RDG-planned",
            "clearBy":"verified migration receipt"})
        second = self.submit(newer)
        self.assertEqual(second["revision"], 2)
        dest = self.root / "backup-two.sqlite"
        self.store.backup_to(dest)
        self.assertEqual(CandidateStore(dest).verify()["headHash"], second["eventHash"])

    def test_hardlinked_store_is_not_accepted(self):
        other = self.root / "hardlink.sqlite"
        other.hardlink_to(self.path)
        with self.assertRaisesRegex(StoreError, "STORE_FILE_INVALID"):
            CandidateStore(other)


if __name__ == "__main__":
    unittest.main()
