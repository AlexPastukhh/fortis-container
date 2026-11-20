# P5 — post-merge evidence readiness and trusted collector boundary

**Source-only / NOT LIVE / owner review required.** This complements the
[P5 Registry design](RELEASE-REGISTRY-P5-DESIGN.md),
[desired candidate preview](RELEASE-REGISTRY-P5-DESIRED-PREVIEW.md) and
[durable desired candidate journal](RELEASE-REGISTRY-P5-DESIRED-STORE.md).
The existing P5 SQLite stores persist **unverified candidates only**; they
must not be exposed as an authorized release queue.

## Current live READs and what they actually establish

The supported typed Repo Gateway can project `get_pull_request`, `get_branch`,
`list_check_runs` and bounded `list_commits` for authorized repositories. A
post-merge readback for `fortis-container` PR #39 (2026-11-20) showed
`state=closed`, `merged=true`, an exact former task-branch HEAD, the current
`main` SHA, and `release-schema` passing for that HEAD. These are useful
**point-in-time projections**, not a signed complete merge package.

Current projections do **not** establish the immutable PR body at review
cutoff, exact merge ancestry for all included PRs, complete changed paths,
pinned catalog bytes + revision, CI required-check policy and exact attempts,
or dependency closure. GitHub commit subjects and `merged=true` alone do not
prove these. `get_pull_request.mergedAt` was `null` in the readback; it must
not be made up from a commit timestamp or other fields.

### Why the attempted READ for PR #39 returned `FORTIS_HTTP_403`

The current `get_pr_release_impact_evidence` adapter requires an **open,
non-draft, not-yet-merged same-repository `task/*` PR** with exact HEAD,
base `main` and bounded body. PR #39 is already **merged**. Independently,
the repository's publisher actor/profile has restricted repository scope;
the `default_client()`/requested repository must not be assumed to inherit
that profile. `FORTIS_HTTP_403` is a transport-level signal and **does not
identify which gate rejected this request**. The merged-PR precondition is
sufficient reason not to retry this identical operation; an actor grant is
not a fix for the post-merge contract gap. No direct GitHub route or
alternate credential should be used.

The operation's open-PR body read can be useful **before** merge for a
separately authorized collector to record a reviewed source snapshot, but
that pre-merge result itself is not immutable proof of a subsequent merge.
Its scope must not be expanded by assuming existing generic capabilities
imply authority or that a mutable post-merge PR body preserves the review
cutoff exactly.

## Implemented offline fail-closed readiness assessor

`tools/registry/evidence_readiness.py::assess()` consumes only the bounded
projections named above. It compares PR number/exact head/task branch/base,
verified *reported* merged status, exact current `main` SHA and check-run
HEADs; detects duplicate check names, missing/truncated checks, observed
failures, missing merge time and incomplete commit pages. Every successful
assessment returns **`BLOCKED_EVIDENCE_GAP`**, `evidenceVerified=false`,
`admissionAllowed=false`, `deploymentAllowed=false` and explicit missing
proof classes. Malformed/stale inputs raise `EvidenceReadinessError`.

The assessor is **pure and network-free**. It is not an authenticated
collector, source-of-truth signature verifier, Gateway policy, Registry
writer or manual report API. Its `projectionDigest` fingerprints *supplied
bytes* only; untrusted callers can fabricate matching data. Adding guessed
`body`, `ancestorProof`, `requiredChecks` or `authorized=true` fields to a
fixture cannot change an assessment into `ADMISSIBLE`.

## Future scoped typed READ proposal (not authorized or implemented)

Under [UC-GW-003](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-003), the Gateway owner must independently review a **new**
post-merge evidence contract and actor grants. The following is an API
proposal only, not a callable endpoint or a replacement GitHub client.

| Required proof class | Proposed immutable/scope-bound evidence |
| --- | --- |
| Repository and actor | Exact allowlisted repository, authenticated collector principal, bound request/evidence ID, source read completeness and capture time. No Repo AI GitHub token. |
| Reviewed impact | Retained exact PR body/Release Impact bytes at an accepted review cutoff and body digest, tied to HEAD and an owner-merged outcome; detect edits since that cutoff. |
| Merge lineage | Every included PR number, head SHA, *real* merge SHA/time, selected `main` SHA with verified ancestry; complete pagination and no unknown merge outcomes. |
| Changed paths | Full per-PR path inventory at exact reviewed HEAD, rename semantics and completeness attestation for release-impact validation. |
| Catalog | Exact bytes/digest at a pinned Git revision, repository identity, enrolled `release/targets.yaml` and component/resource bindings; no synthetic catalog. |
| CI | Required workflow/check policy snapshot, exact attempt/job IDs, success/failure for selected head, checks complete with no ambiguous reruns. |
| Dependencies | PR and cross-repo/target dependency closure, pinned source IDs and verified cycle/unknown handling. |
| Snapshot integrity | Attestable provenance and completeness under reviewed owner/Gateway trust boundary, stable request ID, bounded payload/retention and independent recovery record. |

The collector should expose a source-only **preview** distinct from any
future WRITE. A future `registry.ingest_merged` requires its own scoped actor,
exact evidence digest, idempotent operation ID, CAS, durable receipt and
separate owner-reviewed implementation. A `403`, missing field, stale source
SHA, pagination/race, source drift, unknown target or unavailable collector
means **STOP / EVIDENCE_INCOMPLETE**, not an empty release queue or an allow.

## Parallel-work and Gateway release boundary

The Registry's component restrictions remain **exception-only**, scoped to
component, shared resource and affected operation. The absence of a
restriction is `NO_REGISTRY_RESTRICTION`, never `ALLOWED`. The future collector
must not treat an unavailable Gateway during its own Check/Apply/backup as
proof that workers are quiescent or restrictions have cleared. Original
protected controller records and owner Use Cases retain this authority;
independent source-only work is not automatically frozen.

## Source verification and remaining steps

Run `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests
-p 'test_*.py' -q` for offline negative tests. New assessor fixtures check
merged/green-but-insufficient evidence, open/draft/unmerged rejection, exact
head/main drift, failed or ambiguous checks, incomplete pagination, malformed
projections, forged additional claims and no authorization side effects.
A live production collector, cryptographic proof, owner consent, installed
state readback and P6 `REPORTED_COMPLETE` are **not** covered by these tests.

The subsequent source work belongs to the **appropriate owner repository**
for typed Gateway API/actor policies and protected evidence storage. No new
external read endpoint, Gateway release, Linux/Windows deployment, GitHub
Deployments WRITE or automatic CD is part of this PR. P4 Deployments READ is
already complete and must not be re-released as a prerequisite.
