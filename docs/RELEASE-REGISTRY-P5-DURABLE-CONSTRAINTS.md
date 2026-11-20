# P5 — Durable component restrictions, offline reference (2026-11-20)

**SOURCE-ONLY CANDIDATE / NOT INSTALLED / DOES NOT GRANT AUTHORITY.**
This adds a proposed SQLite persistence layer to the previously merged
[component restriction model](RELEASE-REGISTRY-P5-COMPONENT-RESTRICTIONS.md)
and the [P5 design](RELEASE-REGISTRY-P5-DESIGN.md). It does **not** implement
the production desired-release queue, merge lineage collector, Gateway broker,
Live Registry API, owner grants, deployment executor or release window lock.

## Separation of concerns

`tools/registry/constraints.py` is the side-effect-free evaluator.
`tools/registry/store.py` is an explicitly bootstrapped **offline candidate
store** for complete component/resource/restriction snapshots. The store is
not automatically configured with any default DB path or production volume,
and creates no data unless a caller explicitly initializes a chosen path.
No project is allowed to treat an unverified stored snapshot as permission,
a release stop signal, a verified clearance or owner approval. The source
alone cannot establish freshness, complete catalog coverage or actor policy.

The accepted restriction philosophy is deliberately sparse: record only
**what is restricted**, not every action permitted. Each restriction refers
to a scoped component/resource, operation types, observed phase, source UC,
reason and exact clearance condition. In the evaluator,
`NO_REGISTRY_RESTRICTION` does **not** mean `ALLOWED`.
External Gateway policy, existing UCs and owner-controlled controllers keep
their own gates, especially while Gateway is unavailable during release.

## Reference schema and write transaction

Persistent SQLite schema v1 is separate from Gateway Core and worker DBs:
`meta`, immutable `snapshots`, `operations` (original request fingerprints and
receipts), and ordered `events` with previous/current SHA-256 hashes.

The proposed offline `CandidateStore.propose` is a **candidate append**, not
a live authorization endpoint. Inputs: canonical snapshot, explicit
`operation_id` UUID, actor string (currently *caller-supplied, untrusted*),
`expected_revision`, source evidence reference and digest, and optionally
clearance evidence references for removed restriction IDs. The store:

1. Rejects malformed snapshots/operations and unsupported schema versions;
   validates component cycles/resource scopes using the pure evaluator.
2. Begins `BEGIN IMMEDIATE`; verifies prior event chain, snapshot digests,
   exact revision, foreign keys and operation history in the same transaction.
3. Returns the original persisted receipt for **the same UUID + exact
   fingerprint**, even if the record has advanced; conflicting reuse is STOP.
4. Refuses stale revision and duplicate unchanged snapshots. One concurrent
   CAS writer wins; the loser gets `REVISION_STALE` without another event.
5. Refuses silent weakening of an existing restriction ID. Removing a rule
   requires exact explicit clearance references for **every removed ID**;
   these references are retained in the immutable event JSON.
6. Inserts snapshot + original operation receipt + hash-linked event and
   updates current revision atomically, then returns a candidate receipt
   with `evidenceVerified=false`. No runtime effect is performed.

### Non-trust and replay boundaries

A caller-provided actor label does not prove machine identity; a referenced
clearance digest does not prove its protected receipt or owner origin. **A
trusted, separately reviewed broker must verify identity, immutable evidence,
coverage, original controller receipts and authorization before a future
live Registry may rely on any candidate.** No grant path exists here.

If an ACK is lost, read the **original** operation ID and its persisted
receipt; do not assume failure or submit a second release mutation. The
local store does not implement cross-actor network access or any future
`report_manual_complete` P6 API. Actual installed state remains UNKNOWN.

## Backup, integrity, failure behavior

The reference opens SQLite with `foreign_keys=ON`, WAL and bounded busy
handling; it never uses memory-only fallback. `verify` recomputes event and
snapshot hashes, revision counts, and foreign-key structure. The hash chain
is **only local corruption evidence**; without a separately protected
checkpoint, anyone with DB write access can rewrite history and recompute
hashes. Therefore it does not prove independent tamper resistance.

`backup_to(new_path)` uses the SQLite consistent backup protocol to create
one **inactive** separate copy, and records the expected revision/head hash.
It never overwrites existing backup targets and never performs a restore
into a running instance. An owner-reviewed restore process still needs
checkpoint attestation, verified backups, permissions, retention and isolated
recovery tests. Owner location/volume/UID/encryption remain unresolved D1/D6.

This reference deliberately does not bind a production path, background
service, container, credential, HTTP endpoint, GitHub Deployment or Windows
controller. Store schema v1 is **not** an accepted production migration.
Do not run it against existing Gateway SQLite files.

## Exact source-only test scope

Run offline without GitHub/Windows/Production:

`PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_*.py' -q`

Durability fixtures cover restart/readback, original-operation retrieval,
UUID conflicts, stale/concurrent CAS, unchanged snapshots, scoped actor read,
explicit clearance, tampering and orphan operations, missing revisions,
SQLite backup round-trip, invalid inputs, and symlink/hardlink rejection.
These fixtures are **not** a live actor-policy, sealed storage or protected
controller test. Before activating P5 in any environment, separately define
owner placement/actor scope, trusted merge+catalog lineage, release queue
records, backup/restore/checkpoint protection and full failure/negative tests.
P4 GitHub Deployments READ remains complete; do not re-release it.
