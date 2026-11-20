# Fortis Release Registry V1 — P5 source-only design candidate (2026-11-20)

**Status: DESIGN CANDIDATE / OWNER REVIEW REQUIRED / NOT LIVE.**
This document proposes implementation decisions for P5. The accepted product
decision is a **Fortis-owned canonical release queue**, with **manual owner
release execution** in V1; GitHub Deployments are optional READ/projections.
No new Registry service, API, credential, persistent volume, deployment job,
Gateway permission or runtime image is installed by this document.

**Authority:** [Release Planning Contract](RELEASE-PLANNING-CONTRACT.md#post-merge-cd-queue-and-fortis-release-board),
[one roadmap](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue),
[handoff](RELEASE-REGISTRY-V1-HANDOFF-2026-11-20.md).
All changes described below remain subject to source review and separate owner
approval of the trust boundary. GitHub PR merge alone is not deployment.

## 1. Scope and ownership

P5: inspect trusted evidence for an owner-merged PR, generate a deterministic
plan for each catalog-pinned target/environment, persist immutable desired
records and audit under controlled ingestion; expose **READ-only** planning
views. Missing evidence -> blocked ingestion, not invented queued records.
P6 adds a narrowly authorized `REPORTED_COMPLETE` owner statement event;
P7 displays these records; P8 groups manual release batches.
Automatic CD and a universal installed-state collector are post-V1.

**Component-aware parallel-work coordination (P5 extension):** model only
[active release constraints](RELEASE-REGISTRY-P5-COMPONENT-RESTRICTIONS.md)
by component, shared resource and affected operation. Do not maintain an
allowlist of normal work: no applicable restriction is **not permission**.
Unknown effectful-work coverage needs review. Existing Gateway/owner gates
remain independent, including during Gateway downtime.

**Proposed source split:** `fortis-container` owns product constraints and
shared Release Impact/catalog schemas; an independently reviewed Fortis
Registry component owns state and audit, with typed brokered API integration
in the Gateway-owned `fortis-approvals` source if selected by the owner.
No AI/Repo process gets raw SQL access or a direct GitHub token. Whether the
Registry component lives in an isolated runtime or a separately isolated
module remains an **owner decision**, not something inferred from this file.

## 2. Decisions required before implementation

| ID | Proposed direction | Still needs explicit owner acceptance |
| --- | --- | --- |
| D1 | Dedicated SQLite V1 store, independently persistent from Gateway Core and worker stores; transactional single writer | Runtime owner, location, volume, UID/GID, encryption, backup lifecycle |
| D2 | Trusted planner principal for post-merge ingestion; independent scoped readers; all writes default DENY | Exact machine actor and repository allowlist, policy path and rollout |
| D3 | Stable desired queue subject separate from immutable artifact-version events | Final desired/artefact identity semantics against Release Planning Contract |
| D4 | Exact merged-PR lineage, catalog and CI evidence, with explicit completeness proof | Required typed upstream projections / signed evidence admission |
| D5 | One operationId = one immutable input fingerprint, transaction-bound CAS and receipt | Conflict/retry protocol and original-attempt recovery admission |
| D6 | Append-only per-record events and integrity checkpoint; immutable histories | Protected integrity anchor, backup/restore attestation and retention |
| D7 | V1 starts without runtime execution, result marking or installed-state verifier | Initial enrolled repositories, product acceptance and live launch GO |

**STOP:** these open decisions are not silently approved by merging a
design-only PR. Implementations may be prepared offline only after trust
placement and API authority have been reviewed.
## 3. Trusted evidence and admission

A post-merge intake must bind **one immutable evidence snapshot**:
1. Canonical `owner/repository`, full selected GitHub `main` SHA and proven
   ancestry that contains each attributed merge; no selective cherry-picking
   from that SHA without a separately accepted source-selection contract.
2. For every included PR: number, exact PR head, actual merge commit/time,
   proof that the merge belongs to this `main`, immutable reviewed PR-body
   `releaseImpact`, exact-head validation and required CI attempt/job results.
3. A pinned `release/targets.yaml` catalog revision and content digest,
   target ID, allowed environment, buildUnit/input mapping, deployment
   procedure, required actions and dependency closure (cross-repo included).
4. Complete changed-path and PR pagination, explicit `noDeploymentPaths`
   coverage and exact schemaVersion. A missing/malformed catalog, target
   remapping, unknown action/path, CI gap or cyclic dependency is fatal.
5. Source identity, evidence class, capture timestamps and completeness
   attestations by a **trusted** reader. Mutable PR labels, CI green alone,
   GitHub Deployment `success` and model text are not provenance.

Current typed `get_pull_request` projects `merged` but not guaranteed exact
merge SHA/time, complete changed-path lineage or the prior immutable PR body.
Therefore **the existing READs are insufficient for automatic P5 ingestion**.
A separately reviewed typed evidence contract is a prerequisite; do not
infer missing facts from branch/commit lists or invent source authority.

Intake results:
- `INGEST_BLOCKED`: preserve reason/gap and original operation identity;
  **do not** create a desired release record.
- Fully validated `classification: no-deployment`: record an audit decision
  if authorized, but create **zero** deployment queue records.
- `classification: unknown` or unproven lineage: STOP/UNKNOWN.
- Validated target and source with unknown installed actual:
  `PLANNED_UNVERIFIED` and `actual=null`. Use `QUEUED` only with fresh
  independent target evidence of a **different** installed identity and
  absence of unknown in-flight effects.

## 4. Canonical identities and DTO (proposed)

One *desired-release subject* is repository + deployment target +
environment + full merged `main` SHA + pinned catalog identity.
The stable desired record ID may hash this canonical tuple; preserve a
separate immutable artifact/version identity containing build unit and digest.
This prevents an unbuilt -> built event from duplicating the *queue item*
while preserving the Release Planning Contract's full source/artifact
version semantics. This separation is D3; **not yet adopted**.

Minimum `desired_record` (all persisted identities are canonical):
`recordId`, `schemaVersion=1`, `repository`, `targetId`, `environment`,
`desiredSourceSha` (40 hex), `catalogCommitSha` (40 hex),
`catalogBlobSha256` (64 hex), `buildUnitId | null`,
`artifactStatus=NOT_BUILT | KNOWN`, `artifactDigest | null`,
`requiredActions`, `deploymentProcedure`, `mergedPullRequests`
(proven head, merge, impact digest, CI digest), `lineageEvidenceDigest`,
`dependencies`, `planningState`, `actual=null`, `revision`,
`createdAt`, `evidenceClass`, `supersedesRecordId | null`.

An unbuilt `artifactDigest=null` is **not** a matching wildcard and does
not assert that no installation exists. Source SHA is not an installed
version. Artifacts are versioned append-only, not retroactively substituted.
Build units are shared inputs, never queue subjects; the same build artifact
may feed multiple target/environment identities with separate actual state.
## 5. Durable store, transactions, audit and recovery

**Candidate storage:** injected dedicated SQLite DB in a separately
owner-provisioned persistent path. No default production path or automatic
mount. Suggested tables: `desired_records`, `record_lineage`,
`record_dependencies`, `artifact_versions`, `evidence_snapshots`,
`ingestion_operations`, `record_events`, `schema_migrations`.
Enable `foreign_keys=ON`, `WAL`, bounded busy timeouts and explicit schema
version. `BEGIN IMMEDIATE` serializes **both** uniqueness/CAS checks and
event + operation receipt insertion. Unique desired identity across writers.

Each WRITE request needs an immutable `operationId`, authenticated actor /
repo-scope grant, canonical payload fingerprint (including evidence snapshot
digest) and expected record revision. Same ID+fingerprint returns the
original bound receipt; same ID with a different fingerprint is a hard
conflict. A changed revision or stale trusted evidence is a STOP and fresh
READ/preview, not last-writer-wins. No second WRITE after lost ACK without
reading `get_operation(operationId)`; unknown original outcome stays
`UNKNOWN_OUTCOME` until safely resolved.

Append-only events include trusted actor principal, operation ID, exact
record/revision, event type, evidence digest, timestamp, previous event hash
and current hash. A hash chain detects local corruption but is **not**
independent tamper-resistance without a protected external checkpoint. Do
not claim it proves owner intent or installed state. Preserve old records,
failure/unknown outcomes, prior release assertions and audit on supersession.

New merged `main` SHA creates a new desired record only when ancestry,
coverage and catalog/target continuity are proven. It links to the older
record with `supersedesRecordId`; never overwrite the old record or copy
its `DEPLOYED` evidence to the new SHA. Identical merge/readback should
not generate duplicate records or duplicate audit events. Different PRs
covered by one chosen SHA are stored as a complete lineage of that
target/version, not separate physical installations.

Before any owner-authorized store activation: define private ownership,
permissions, at-rest protection, schema migration guards, backup schedule,
retention and verification. Backup must use SQLite's consistent snapshot
protocol (including WAL semantics), capture schema, row/event counts and
audit-chain head; restore to **inactive new instance** and verify
integrity/evidence/unique constraints before owner-approved switchover.
No restore into live DB, blind reset or auto-regeneration from GitHub.
On unavailable database, fail closed with `STORAGE_UNAVAILABLE` (never
memory-only or GitHub Deployment fallback).

## 6. Minimal typed API surface (all proposed; NOT LIVE)

| Method | Future policy | Behavior |
| --- | --- | --- |
| `registry.capabilities` | authenticated READ | Exact version, grants, rollout; no source-only flags advertised live |
| `registry.preview_merged` | per-repo scoped READ | Deterministic plan, gaps, digest; zero effects |
| `registry.get_record` / `registry.list_records` | scoped READ | Bounded projection, cursor, evidence class and explicit actual unknown |
| `registry.ingest_merged` | trusted planner WRITE only | Fixed evidence, operationId, CAS, append-only receipt; no deploy |
| `registry.get_operation` | bound READ | Result of **original** operation after lost ACK |
| `registry.report_manual_complete` | **DENY P5**; P6 separately reviewed | Owner statement + exact record and CAS; never technical proof |
| `registry.verify_actual` / `registry.deploy` / GitHub Deployments POST | **DENY** | No V1 grant or runner from source design |

Explicit error classes: `EVIDENCE_INCOMPLETE`, `LINEAGE_UNPROVEN`,
`CATALOG_NOT_PINNED`, `CI_NOT_EXACT_HEAD`,
`DEPENDENCY_UNVERIFIED`, `ACTOR_DENIED`, `REVISION_STALE`,
`OPERATION_ID_CONFLICT`, `STORAGE_UNAVAILABLE`,
`UNKNOWN_OUTCOME`. Do not expose sensitive error bodies or secrets.
## 7. P6/P7 boundary and required source tests

`REPORTED_COMPLETE` is an immutable P6 **owner assertion event** produced
by an authorized typed operation after an attributable owner report,
bound to record/target/environment/desired SHA, expected revision and
optional protected attempt/evidence references. It is *not* installed
`actual`; `actual` stays UNKNOWN until a protected original controller
receipt **and** independent current target readback match. AI chat text
cannot be treated as a stored Fortis event without a successful future API
receipt. P5 does not implement this operation or auto-run manual UC scripts.

Source/negative fixtures required before executable implementation:
1. Same merged PR replay and concurrent identical ingestion -> one record,
   same original operation result; two PRs in same main SHA -> full lineage.
2. Same SHA repeat -> no new record; newer proven SHA -> append/supersede;
   unrelated SHA, missing ancestry or changed catalog target -> STOP.
3. Missing catalog, partial pages, unverified merge commit/time,
   unknown file, missing exact-head CI, missing/cyclic dependencies,
   forged/changed evidence digest -> no queue admission.
4. Exact validated `no-deployment` -> zero desired releases; classification
   `unknown` -> no silent `no-deployment` mapping.
5. Owner claim/forged report, wrong target/env/SHA, unsupported actor,
   `DEPLOYED` inference from a GitHub `success` status -> DENY/UNKNOWN.
6. Concurrent stale revision, conflicting same operation ID, timeout
   before/after durable commit, lost ACK, uncertain receipt, retry after
   crash -> no duplicate events or unproven success.
7. Simulated SQLite corruption, restart, point-in-time backup + restore,
   unknown schema, cross-actor READ and malformed cursor -> safe STOP,
   intact immutable history and no hidden data leaks.
8. Network-free fixture runners; no GitHub POST, Windows shell, Docker,
   production state, Repo direct GitHub, or real machine credentials.

**Source-only acceptance:** decide D1–D7, add exact trusted evidence
contracts and migrations in the owning implementation repository, test all
negative/concurrency/recovery cases, pass exact-head CI and obtain owner UI
merge. A separate runtime release and owner-approved grants are needed
before any Registry API is live. **P4 Deployments READ is already complete;
never rerun that release for P5.**
