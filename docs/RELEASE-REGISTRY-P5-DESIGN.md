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
The [offline durable restrictions candidate](RELEASE-REGISTRY-P5-DURABLE-CONSTRAINTS.md) persists only the component-coordination model for negative tests; it does **not** complete the canonical desired-release queue or install a Registry API.
The [offline desired release preview](RELEASE-REGISTRY-P5-DESIRED-PREVIEW.md) separately derives unverified per-target candidate identities from claimed merge and catalog inputs; it never writes to the authoritative queue and needs a trusted collector.
The [separate offline durable desired journal](RELEASE-REGISTRY-P5-DESIRED-STORE.md) persists only unverified candidate records and original-operation/supersession history, with no live or trusted API.
The [post-merge evidence readiness contract](RELEASE-REGISTRY-P5-POST-MERGE-EVIDENCE.md) records why current typed READs are insufficient, without granting an additional actor or installing an endpoint.

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
### 2.1 Concrete first-pilot decision proposal (2026-11-21)

**Owner review requested; source architecture only.** The owner agreed to
proceed with a `fortis-approvals`-only pilot, leaving unresolved dependencies
blocked. The following concrete decisions replace the alternatives for the
purposes of the next source review; they are NOT existing runtime facts,
active grants, or a live-launch GO. Owner merge of the decision PR accepts
the source design, not provisioning, keys, permissions or evidence trust.

| ID | Proposed pilot decision | Before live acceptance |
| --- | --- | --- |
| D1 | Dedicated Registry process/container, separate from Gateway and worker processes; source owned in `fortis-approvals` under a separate module and independently built runtime. One SQLite writer, separate persistent volume; no direct Repo/AI access. | Owner verifies host placement, encryption, service UID/GID and volume permissions; provisions and tests backup/restore. |
| D2 | Gateway-authenticated collector, separate Registry planner and read principals. Exact single repository scope, deny by default, typed operations only. | Closed operation schemas, ingress/broker/worker contracts where applicable, credential isolation, exact grants and negative live checks. |
| D3 | Immutable desired subject = canonical repository, target, environment, selected full main SHA and exact catalog commit/raw digest. Artifact identity is a separate immutable event/version; supersession preserves history. | Confirm exact catalog/component/environment continuity and target-specific UC; no artifact/installed-state inference. |
| D4 | Only independently obtained, owner-bound evidence from the collector may reach admission; full proof and protected provenance required. | Accept historical policy and review cutoff, complete selected-source lineage, component mapping, dependency closure, authenticated collector and evidence retention. |
| D5 | Separate operation UUID plus canonical actor/scope/arguments/evidence digest fingerprint and revision CAS; original receipt is authoritative. | Concurrency, conflict, lost ACK, restart, unknown outcome tests; no replayed mutation without original receipt reconciliation. |
| D6 | Immutable records and append-only operation/event histories; independent owner-protected checkpoint and inactive consistent backup. | Validate external anchor authority, crash reconciliation, retention and restore with independent owner readback. |
| D7 | Initial enrollment exactly `AlexPastukhh/fortis-approvals`. Preview/queue only; manual UC execution stays outside Registry. No installed-state verifier, manual result marking or deploy in P5. | Separate owner acceptance of protected source, image/runtime, live scopes and end-to-end pilot. |

#### D1/D6 — isolation, persistence and recovery

Proposed deployment is a separate service, not a new table in Core or a
shared volume in the Repo container. Candidate in-container state mount
`/var/lib/fortis-registry` contains `registry.sqlite`; it is a new mount,
not a claim that this path or a volume exists. Run as a dedicated non-root
service identity (candidate UID/GID 10001:10001, confirm collision-free
ownership with the host operator before provisioning). State directory
0700, DB and private sidecars 0600, no shared mount into AI/Repo, no host
Docker socket, no credentials copied from Publisher/Gateway. SQLite
foreign keys, WAL, FULL synchronous, bounded busy timeout and explicit
schema version. No auto-create on a missing configured DB; an explicit
one-time owner provisioning step and an independently verified schema
are required. Owner must select encrypted-at-rest host storage and
separate encrypted backup destination; do not invent an existing host
path or encryption configuration.

The independent integrity anchor is owned outside the Registry writer's
security boundary. Anchor records contain Registry instance/schema ID,
revision and event digest. Source contract: an ingestion transaction
atomically appends state, operation fingerprint and original local
receipt; external anchor advancement uses compare-and-set on the exact
previous and next checkpoint. Do not report an authoritative committed
receipt or expose new desired records until the exact advanced anchor
is observed. Interruptions between DB commit and anchor confirmation
return UNKNOWN_OUTCOME/blocked reads, not a fresh attempt or empty
queue. On restart compare original operation and both checkpoint
identities; anchor mismatch, unexpected revision or unverifiable
pending commit is STOP for owner recovery. The anchor cannot be
silently initialized from the current DB or rolled back by the writer.
The exact implementation of this inter-system recovery protocol and
its fault-injection tests precede admission, rather than treating
a local hash chain as a protected external anchor.

Candidate backup policy: daily consistent SQLite snapshots plus a
pre-change snapshot before every migration/runtime switchover; retain
30 daily backup copies and all pre-change snapshots until explicit
owner-approved retirement. Immutable records/events and original
evidence are not purged by snapshot rotation. Storage/retention bounds
must fail closed rather than silently delete evidence. Each backup
records exact schema, revision, event digest, row counts and independent
anchor; verify in an inactive separate instance before any restore
switchover. No restore into active state, no resetting to blank DB, no
automatic reconstruction from current GitHub metadata. Host/backup
placement, at-rest protection and actual recovery operator are still
owner verification gates, not assumed current configuration.

#### D2 — proposed closed principal and operation contract

These names are candidate identities, not created credentials or active
policy. Collector `release-registry-collector-v1` remains internal to
the owner-composed Gateway; retain and attest source snapshots only.
Registry writer `release-registry-planner-v1` may ingest a verified
collector evidence identity only for the pilot repository. Scoped
reader `release-registry-reader-v1` has read-only capabilities,
preview, list/get records and operation readback limited by exact
repository and receipt visibility. Planner can read its own original
operations; reader cannot spoof planner identity or supply an actor
field as authority. No new rights for the current Repo actor or for
the P3 publisher. All routes and actors outside approved scope DENY.
The proposed typed broker boundary must authenticate and bind the
principal, validate exact params, and reject caller-supplied proof
claims, credential/URL/path selectors, arbitrary SQL or generic
GitHub requests. The new Registry process receives no GitHub token.

Candidate public contract is the method table in section 6, with
ingest accepting only `operationId`, canonical pilot repository,
`evidenceId`, exact `evidenceDigest` and `expectedRevision`.
No caller-selected environment, desired SHA, action list, completeness
booleans or arbitrary preview DTO on WRITE. The owner-reviewed
environment/component binding and source proof determine the plan.
The evidence identity is a reference to an original immutable
collector snapshot; authenticated internal retrieval must bind issuer,
scope, schema version, source identity, bytes/digest and receipt to
the expected source. A signature or digest alone is not proof that
missing source evidence has been supplied. Authentication and transport
design, exact credential lifecycle and collector receipt format need
their own implementation review under UC-GW-003. Read-only preview
must distinguish incomplete evidence from no-deployment. No callable
endpoint is created by this proposal.

#### D3/D5 — canonical state and write boundaries

Use the existing offline desired journal as a reference for transaction
and invariant tests, not as an authoritative data source. No duplicate
parallel production schema; separately review the owning Registry
module and exact versioned migrations. All record IDs and fingerprints
use canonical JSON SHA-256; a stable subject and an immutable artifact
version are distinct. Bind the selected source and catalog commit plus
raw bytes SHA-256 (do not conflate raw catalog and parsed JSON hashes).
Environment selection comes from an independently reviewed closed
target/environment/component/resource binding, not all possible
environments in the catalog nor a parameter supplied by AI. Preserve
deployment procedure and target actions; artifacts begin NOT_BUILT
and actual=null. Valid, fully admitted no-deployment is an audit-only
decision with zero desired items. Incomplete evidence produces a
blocked intake result and reason codes, not a release record or a
no-deployment classification. For a future admitted plan with unknown
actual use PLANNED_UNVERIFIED; do not call it QUEUED.

An exact operation replay returns the anchored original receipt;
conflicting UUID/fingerprint reuse is refused. Revision CAS covers the
whole ingestion transaction, evidence association and supersession;
same desired identity cannot duplicate records. A new source SHA
supersedes only with complete verified lineage and catalog/target
continuity, preserving earlier records and all original attempts.
No rewriting installed state, no treatment of a mutable ref or
ancestryRef string as proof. If an incoming snapshot has a later
unverified merge, baseline gap, unresolved dependency or changed
target mapping, block rather than select a subset of the source.

#### D4/D7 — pilot evidence boundary and delivery order

The merged Approvals source through [PR #193](https://github.com/AlexPastukhh/fortis-approvals/pull/193)
(`407f9c7be730af73a8df84fda4ed2ebedafbc994`) composes retained v2
bundle, Core ASK, exact-head CI observations, pinned real Impact
validator, raw Git commit checks and local dependency graph at one
exact selected tip merge. All four exact-head CI jobs passed; this
is source acceptance only. It explicitly returns false for historical
policy/cutoff, dependency closure, component binding and admission.
See the [owning Gateway evidence contract](https://github.com/AlexPastukhh/fortis-approvals/blob/407f9c7be730af73a8df84fda4ed2ebedafbc994/docs/RELEASE-REGISTRY-P5-POST-MERGE-GATEWAY-CONTRACT.md).
No old merged PR body is reconstructed from current editable text.

Initial pilot must use new reviewed captures, not backfill history
from CI green or old merge descriptions. Require an owner-reviewed
baseline source/coverage decision, including any unapplied earlier
PRs; do not silently assume existing production is at current main.
Only the exact tip merge with no unresolved dependency can be a
candidate under the existing source implementation; complete lineage
from baseline and policy/cutoff still need independent proof. A
later main, multi-PR gap, catalog remapping or PR dependency not fully
proved against enrolled source blocks intake. An external target or
PR dependency is BLOCKED on this single-repository scope, even if a
local checkout happens to exist. Cross-repository enrollment needs
separate owner-selected canonical repo and immutable source policy
with recursive graph/cycle checks. No automatic grant expansion.

Next implementation increments, each with exact-head CI and owner
review:

1. Define and implement closed Registry preview/receipt boundary,
   explicitly fail closed on all current evidence gaps. Reuse
   candidate-store invariant tests; never promote a fixture DTO.
2. Establish owner-reviewed merge cutoff and historical policy
   provenance (or a separately accepted trusted alternative), full
   source coverage and component/environment bindings. Integrate
   live pre-merge evidence only after protected capture authority,
   actual storage/anchor and provider scope have been accepted.
3. Implement canonical durable writer with independent trusted
   evidence retrieval, CAS and anchored operation recovery; verify
   backup/restore and negative/concurrency tests. No false evidence
   flags or placeholder admission path to demonstrate a queue.
4. Separately approve runtime placement, exact credentials and
   scopes, release, and new one-repository end-to-end acceptance
   including blocked intake, no-deployment and a verified
   PLANNED_UNVERIFIED desired record. Owner manually runs any
   deployment UC outside this pilot. P6/P7/P8 remain separate.

**STOP** until D1-D7 source choices are reviewed; runtime acceptance
requires all listed operational gates, not merely a merged design.
P4 and P3 scopes, installed images and permissions are unchanged.

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
