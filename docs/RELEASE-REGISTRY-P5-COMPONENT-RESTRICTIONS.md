# P5 — Component-scoped release constraints (source-only candidate)

**Status: SOURCE-ONLY REFERENCE / NOT LIVE / NO AUTHORIZATION EFFECT.**
This complements [P5 Registry design](RELEASE-REGISTRY-P5-DESIGN.md), the
[Release Planning Contract](RELEASE-PLANNING-CONTRACT.md) and the
[single roadmap](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue).
It does **not** activate a Registry service, Gateway policy, runtime lock,
SQLite store, automatic controller or CD.

## Purpose: enable parallel work by recording exceptions

Do **not** enumerate everything that is permitted. Record only *effective
restrictions* on a named component or resource for specific operation types.
A component is the deployment/release unit, **not a whole Git repository**.
Several components can live in one repository; several repositories may depend
on a shared component or state resource. One Gateway image contains multiple
capabilities, but release restrictions must still target the affected unit.

The answer to a query is one of:

| Result | Meaning |
| --- | --- |
| `BLOCKED` | An applicable active restriction prohibits this operation in the observed snapshot. |
| `REVIEW_REQUIRED` | An applicable review restriction, unclassified operation, unknown component, or incomplete/stale coverage requires an independent decision for effectful work. |
| `NO_REGISTRY_RESTRICTION` | None was found in an adequately scoped snapshot (or the operation is source-only); **NOT** `ALLOWED`, `OWNER_APPROVED`, `SAFE_TO_DEPLOY`, or `DEPLOYED`. |

**Permission remains with existing Use Cases, machine/actor policy,
controller gates and owner approvals.** There is no grant API and no rule
that says "everything not blocked is authorized". Missing coverage or a
stopped Registry cannot make an effectful operation safe.

## Stable component graph and constrained operations

A catalog version binds `componentId`, its *entire* relevant shared-resource
set and its `requires` dependencies. The evaluator resolves resource and
dependency closure from this catalog, **not** a caller-supplied subset.
A change to this graph needs a separately reviewed pinned catalog revision.
A stale/missing component or resource snapshot is not an implicit permit.

A restriction records: immutable `id`; component/resource selectors;
explicit affected operations; `BLOCK` or `REVIEW_REQUIRED`; observed phase;
source Use Case/protected record; reason; and a *required clearance proof*.
Restrictions remain active across phase/time changes until a trusted new
snapshot attests their clearance. No guessed TTL and no auto-clear on
`Apply completed`, a GitHub check, owner chat or a UI tab change.
A protected controller receipt or owner action may be a prerequisite, but
Registry cannot manufacture that evidence. Restriction state changes and
source snapshots will need durable immutable audit in the owning Registry.

Examples (illustrative only, **not live rules**):

| Component / shared resource | Condition | Restricted operation | Clearance evidence |
| --- | --- | --- | --- |
| `fortis-approvals/primary/gateway`, protected Gateway state | Verified owner release quiescence window | New Gateway WRITE/dispatch on conflicting state | Protected release scope + independent quiescence/readback, per UC-GW-005 |
| Same runtime and controller pointers | Original Apply outcome uncertain | Second Apply/Backup/Promote against that attempt | UC-GW-006 original attempt resolution and owner review |
| Shared state volume used by two components | Owner migration lock | Parallel state migration or replacement | Owner-confirmed migration/restore receipt |

These rows are **design fixtures**, not an assertion that such restrictions
are currently active. Exact Gateway release admission and whether it must
stop are owned by [UC-GW-005](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005)
and [UC-GW-006](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/recovery.md#uc-gw-006).
A Gateway release may require preserving `APPROVED`, `UNCERTAIN` and `CLAIMED`
records, validating worker quiescence and maintaining previous images.
A general "release in progress" label cannot replace those exact checks.

## Runtime failure boundary

During certain Gateway Check/Apply or recovery intervals the machine
Gateway may be unavailable. **Never make that same Gateway/Registry the
sole authority for authorizing its own stop/restart.** A separately owner-
controlled Windows controller and protected original records retain the
operational truth; Registry can later reconcile/annotate what they proved.
A Registry READ error means `UNOBSERVED`/review for effectful work, not an
empty set of restrictions. If the release state is uncertain, the affected
component and shared resources remain gated by their original owner UCs.
Other independent source-only work is not automatically frozen.

## Offline reference implementation

`../tools/registry/constraints.py` is a **pure, network-free evaluator**.
It accepts a typed source snapshot (`schemaVersion`, pinned `components`,
currently active `restrictions`, `coverage`) and a request containing only
`component` and `operation`. The evaluator resolves dependencies and shared
resources, checks active restrictions first, then verifies scope completeness
and freshness for effectful operations. Unknown/new effectful operation types
are not silently admitted. Malformed data raises `ConstraintError` and must
be handled as `REVIEW_REQUIRED` by a future broker (never as an allow).

Coverage is a **claim**, not proof: a future trusted broker must verify
snapshot source, scope, integrity, catalog revision and freshness before
exposing the output in a Release Board or enforcement path. In the present
prototype, fixtures assert coverage without a real protected provider.
Test with `python3 -B -m unittest discover -s tests -p
"test_registry_constraints.py"`. No SQLite, Windows, Docker, HTTP or GitHub
mutation is performed. The previous P5 D1–D7 proposals
remain source-only; durable storage/API/enforcement require their own gates.

## V1 board behavior and extension boundary

Show only **active restrictions**, whose component/resource they cover,
operation class, owner/UC source, phase, evidence freshness and clearance
condition. Display unknown/review as such, not as green permission. A
release window is an information source for coordinating chats, not an AI
claim to stop Gateway, freeze unrelated repos or approve physical release.

Next source phases: complete catalog/resource identity and authoritative
snapshot coverage; add durable append-only constraint events, CAS and
recovery in the separately selected Registry owner; then separately review
Gateway policy/actor scopes and any enforcement. P6 manual
`REPORTED_COMPLETE` is a different event and is **not** a restriction
clearance or verified installation proof. P4 Deployments READ stays complete;
no P4 re-release or GitHub Deployments POST is involved.
