# Release Planning — cross-repository source contract v1

**Historical source acceptance (2026-11-11):** V1 catalog and exact-head
PR CI accepted in five enrolled projects. As of 2026-11-19 a separate,
owner-invoked P3.4 Label Publisher passed one live ASK/WebAuthn/receipt pilot;
the CI action itself remains read-only. The current milestone and CD Queue
roadmap are owned by [Fortis Release Planning / CD Queue](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue).
No unattended label publisher, deployment queue or release service is implied.
The shared validator was separated into the public,
version-pinned [fortis-release-impact-action](https://github.com/AlexPastukhh/fortis-release-impact-action)
(`8c9abefdfbe4699aae97b9363a2a66c596680e62`). Owner-merged
CI wrappers in `tunnel`, `docke-windows-mirror`, `fortis-approvals`,
`feed_and_search_and_bank_and_brain` and `rd-graphs` each passed both
the exact-head shared Release Impact and profile CI checks. This **does not**
prove GitHub branch-rule enforcement or that automated Labels, a GitHub
Project, Release Batch planning, GitHub Deployments or runtime releases
are installed. Those remain separate owner-reviewed gates.

**Scope:** multi-repository release planning. The generic Fortis workflow remains owned by
[UC-CONT-002/003](use-cases/delivery.md); Gateway operation policy and releases are owned by
[Fortis Approvals](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/README.md).
No GitHub write, deployment or privileged action is authorized by this design file.

## Why two levels: build units and deployment targets

- **Build unit:** one reproducible artifact recipe. For example, Feedbrain's current Compose
  configuration builds **one** `feedbrain-app:local` image used by `api`, `worker`,
  `action-worker` and `migrate`. A single image build is not four builds.
- **Target:** something independently accounted for during installation and live verification;
  multiple targets may share the same build unit. An update can affect some or all targets,
  and deployed status must be tracked separately per target and environment.
- A repository can have several build units, Windows source-only targets, configuration
  targets or no runtime targets. Avoid treating every historical Dockerfile as active.
- The shared catalog describes **build/deployment topology**, not the running version.
  Protected deployment records plus target-specific live verification own installed state.

## Canonical source formats

- Per enrolled project: `release/targets.yaml`, one current catalog at repository `main`.
  [Machine schema](schemas/build-target-catalog-v1.schema.json); inspect
  [Feedbrain topology example](schemas/feedbrain-catalog-example-v1.yaml).
- Per PR: **exactly one** bounded `releaseImpact` YAML mapping, enclosed by
  `<!-- fortis-release-impact:start -->` and `<!-- fortis-release-impact:end -->`
  in the PR body, and in a fenced `yaml` code block. This is **not** inferred from the
  PR template; typed Gateway PR creation must provide the actual body.
  [Machine schema](schemas/release-impact-v1.schema.json);
  [Feedbrain PR example](schemas/feedbrain-release-impact-example-v1.yaml).
- `schemaVersion: 1` is pinned. Changes to either schema require reviewed migration
  and validator tests; don't interpret unknown versions as `no-deployment`.
- The schemas validate **structure**. A shared validator must also verify repository/target
  references, unique IDs, `buildUnit` existence, safe relative POSIX globs/paths,
  dependency graph, changed files and exact PR HEAD. JSON Schema alone is not proof
  that declared impact is complete or safe.

## Required semantics beyond the JSON schemas

1. Catalog `repository` must equal the canonical GitHub repo slug. `buildUnits[].id`
   and `targets[].id` are each unique; each target's `buildUnit` must exist. For
   source-only targets, use `inputs` without `buildUnit`. A target needs an actual
   build unit or explicitly bounded direct inputs; empty/no-op targets are invalid.
2. Paths are relative to repository root, use `/`, prohibit `..`, symlink escape and
   absolute paths; build recipes and deployment procedures must be reviewed and exist.
   Do not interpret any unmatched changed path as `no-deployment`: use `unknown`.
3. Cross-repository references use **`{repository, target}`**; intra-repository references
   use the same shape. Resolve them against the selected repository's pinned catalog
   revision. Missing, cyclic or unverified dependencies block batch admission.
4. `noDeploymentPaths` is a reviewed **explicit allowlist** of repository file globs
   that do not affect build or runtime targets. CI must fail closed on unmatched files;
   a source-input match takes precedence over a no-deployment match. Never infer
   documentation-only impact from filename alone without catalog coverage.
5. PR `classification: deployment` requires at least one target; `no-deployment`
   requires an empty target list and a specific reason; `unknown` requires review.
   `unknown` must never be silently downgraded to `no-deployment`.
6. PR `targets[].id` references the current catalog of that PR's repository.
   Each target has its **own** required `actions`. Shared build units must be built
   once per source/artifact identity, even if several targets use them.
7. Action values describe impact, not permission to deploy. `migration-required`
   may coexist with `image-rebuild`. Reasons, verification and dependency entries
   are mandatory (empty dependency arrays are valid).
8. CI must evaluate the **exact PR HEAD**, changed file set and catalog from the
   proposed revision. New build/deploy units require an accompanying catalog change.
   Privileged label/project updates must not execute untrusted PR code.
9. One merged `main` SHA includes all of its merged changes. Release Batch selection
   cannot omit code from that SHA. A requested subset requires a separately approved
   source-selection strategy.
10. Project fields and labels are projections. A release manifest describes a proposed
   batch; only target-specific protected evidence and independent runtime readback
   support `Deployed`. `UNCERTAIN` is a STOP, not automatic retry.

## First five adoption repositories (read-only reconnaissance)

| Repository | Existing inputs / current source observation | Next catalog design decision |
| --- | --- | --- |
| `fortis-approvals` | `source-ci.yml`; active Primary controller uses modularized Gateway Dockerfile | Separate active Gateway recipe from historical pilot Dockerfiles; link UC-GW-005 |
| `rd-graphs` | `rdg-ci.yml`; `deploy/rdg-server/Dockerfile` and Compose | Model RDG runtime; archived/extracted Gateway source is not the Primary Gateway |
| `tunnel` | `source-ci.yml`; `runtime/repo-mode/Dockerfile` plus Windows/host parts | Verify source vs installed components; no assumption all have Docker targets |
| `docke-windows-mirror` | `mirror-source-ci.yml`; Windows PowerShell and browser source | Distinguish source CI from Windows installation and owner verification |
| `feed_and_search_and_bank_and_brain` | `ci/workflow-template.yml` only (not active Actions); one Compose app image | Model shared image and four Compose service roles; migration is not an isolated image |

Those observations are **source-only**. Gateway READ access to all five was verified on
2026-11-11; WRITE scope, required GitHub checks, runtime deployments and Windows
acceptance were not established by the inventory.

## Ownership and adoption

- `fortis-container`: normative cross-repo release contract, schema authority,
  release-coordination Use Cases and onboarding through
  [UC-CONT-018](use-cases/delivery.md#uc-cont-018). The separately reviewed
  public `fortis-release-impact-action` publishes the **single executable**
  validator and versioned v1 schema snapshot for both public and private callers.
  Do not independently maintain two divergent validator implementations.
- Each project: one catalog, existing CI augmented rather than overwritten,
  real build/deployment rules and test instructions owned in its repository.
- `fortis-approvals`: typed GitHub and new Project/Deployment operations only after
  UC-GW-003, explicit policy, owner acceptance and live capability readback.
- `docke-windows-mirror`: Windows source sync and its already accepted safety gates.
- `UC-CONT-027` remains new-repo Git bootstrap; `UC-CONT-018` is the subsequent
  same readiness path for new **and** existing repos.
- At this stage, `GATEWAY_ACCESS_READY` means authenticated read/selected grants;
  `RELEASE_WORKFLOW_READY` is reserved for tested catalog, PR, CI, rules and queue.
  Neither is inferred from this design document.

**Accepted source:** source schemas and `tools/release/validate.py` were
initially accepted in `fortis-container` (`6bde4c84b9625719bc7f87b1397758636d6c85c2`).
The public, reviewed composite action now owns the one reusable executable
implementation. The legacy private composite action remains a pinned
historical compatibility artifact, **not** the current caller reference.
Future schema changes must be reviewed at the normative owner first and
released as an immutable new public-action version with compatibility tests.

### Validator invocation (source candidate)

The validator is **read-only**. After installing `tools/release/requirements.txt`,
run `python3 tools/release/validate.py catalog --repo-root . --repository <repo>`
in a trusted checkout with an enrolled `release/targets.yaml`.

For impact checks use `impact` and the same repo flags, plus
`--pr-body <body.txt> --changed-files-json <changed.json>
--expected-head-sha <full-40-character-PR-head-SHA>`.
The JSON file must be the **complete** changed-path list from trusted PR metadata,
not an unverified user-edited subset. The validator compares the checkout's
actual Git HEAD with the expected SHA. CI must supply exact-head checkout and
a trusted changed-file inventory; source validation does not discover those
GitHub facts by itself. `unknown` and unmatched changed paths fail closed.

### Accepted read-only exact-head CI integration

All five enrolled repositories use the same reviewed immutable action:

`AlexPastukhh/fortis-release-impact-action@8c9abefdfbe4699aae97b9363a2a66c596680e62`

Their `.github/workflows/release-impact.yml` wrappers check out exact
same-repository PR HEAD with full Git history and `persist-credentials: false`,
run the shared validator under `permissions: contents: read` and **preserve**
project-specific CI. The action verifies a non-draft PR to `main`, the
event/checkout SHA agreement and full local Git merge-base diff, parses the
catalog and bounded PR metadata and fails closed for unknown source paths.
The action itself performs no write. Source CI passing is **not** proof that
GitHub branch protection made the check required at the time of merge.

The initial public implementation passed 30/30 GitHub CI tests and ran as
part of green RDG #7, proving public-to-public action access. Later the
private callers were migrated through owner-merged PRs: Tunnel #6,
Mirror #17, Approvals #69 and FeedBrain #14; all shared and profile PR checks
passed. No installation or Windows source update was authorized by those
CI-only PRs.

### V1 Release Labels — normative projection contract

Label data is derived from the **same** checked Release Impact, target
catalog and exact PR HEAD. Labels do not express permission to release or
evidence of an installed version. The executable pure projection is implemented in the independently pinned
[fortis-release-impact-action](https://github.com/AlexPastukhh/fortis-release-impact-action).
The original source proposal in [PR #2](https://github.com/AlexPastukhh/fortis-release-impact-action/pull/2)
is historical. A separate trusted one-shot Gateway Publisher passed a
bounded live ASK/WebAuthn/add-label/receipt pilot on 2026-11-19; it did
not activate unattended publication or deployment. Runtime acceptance
belongs to the Gateway current-state evidence, not this normative contract.

| Metadata | Projected GitHub PR labels |
| --- | --- |
| `classification: no-deployment`, zero targets | `release:no-deployment` |
| `classification: deployment`, declared target `id` | `build:<target-id>` for each declared target |
| Target action `image-rebuild` | `release:image-rebuild` |
| Target action `config-deploy` | `release:config-deploy` |
| Target action `windows-update` | `release:windows-update` |
| Target action `package-build` | `release:package-build` |
| Target action `migration-required` | `release:migration-required` |
| Target action `unknown` | `release:review-required` (never an approval) |
| Entire PR `classification: unknown` | Release Impact gate **fails**; no implicit `no-deployment` |

Use stable, sorted, unique, bounded label names (including GitHub's
50-character name limit). Catalog structure and affected targets must be
checked first; extra deliberately declared targets remain in the label
projection conservatively. New sources and catalogs must fail closed on
unclassified paths. The **managed** namespaces are `build:` and `release:`;
preserve all unrelated human labels. A future updater must handle stale
managed labels idempotently without silently discarding manual safety review.

**Privileged publication boundary:** PR-controlled workflows/artifacts or
green statuses alone must never authorize GitHub writes; an attacker could
change a workflow in their PR. A separate default-branch trusted publisher
must independently verify current PR SHA, body, catalog, complete diff and
validator result before issuing limited label mutations. It must not execute
untrusted PR code or hand privileged credentials to untrusted inputs.
Prefer a separately reviewed `workflow_run`-based privilege boundary, with
explicit GitHub permissions and independent revalidation, rather than
turning the unprivileged PR validator into a write-capable job. For public
repos, GitHub's new `pull_request_target` policy must also be considered.
Any failed provenance, race, missing label capability or uncertain write
means **STOP**, not a synthetic `PASS` or permission bypass.

### Post-merge CD Queue and Fortis Release Board

**V1 product decision (owner, 2026-11-20):** the canonical release queue and
manual-result events belong to an independent, persistent **Fortis Registry**.
GitHub Deployments/statuses are **optional external projections/READ inputs**, not
the queue database, installation executor or mandatory dependency for Board.
The accepted UI direction remains a **Fortis Release Board**, not GitHub Projects.
The installation path is manual: owner follows the appropriate existing Use Case
and reusable scripts. AI may mark a specific Registry record `REPORTED_COMPLETE`
only through an independently reviewed, authorized typed API after the owner's
report; this is not technical proof of deployment. Source/readback collector,
CD runner, GitHub deployment WRITE and Registry write API are NOT deployed.
Sequence and open work remain solely in the
[single current roadmap](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue).
[Current handoff / open gates](RELEASE-REGISTRY-V1-HANDOFF-2026-11-21.md).

The desired deployment identity is `repository + deployment target +
environment + desired source/artifact identity`. A repository is an
aggregate view, not a unit of physical installation. Multiple merged PRs
may be covered by one exact `main` SHA and one verified deployment,
subject to the source-selection rule above. Shared build units are built
once for a given artifact identity; deployed state is tracked separately
for every target and environment.

PR merge, Release Impact, labels and GitHub Deployment status are inputs
or published projections, **not proof of installation**. Only target-specific
protected controller receipts with independent live readback can establish
`DEPLOYED` / `VERIFIED`. A manually entered `REPORTED_COMPLETE` event records
an operator's statement and available references, **not** an independently
verified installed source/artifact. Missing or conflicting technical evidence
is `UNKNOWN` for verified actual state, never an implicit deployment success,
absence of installation or authorization to retry.
Planning/publication cannot trigger Production without separately reviewed
owner authority. GitHub Projects is excluded from the current roadmap.


### P4 — GitHub Deployments READ live; optional projection/WRITE design only

**Owner-reported P4 RELEASE COMPLETE on 2026-11-20:** the four typed
Deployments GET operations are enabled in the Primary Gateway for repository
`fortis-approvals`, and `writeEnabled=false`. Owner reports Check/Apply,
Backup/Promote and live typed READ acceptance. The accepted emergency Promote
source fix was merged as [#159](https://github.com/AlexPastukhh/fortis-approvals/pull/159)
(commit `585211b0240fd543b475d2196edc0bd4efb83951`). The missing historical
image makes `DISASTER_RECOVERY_VERIFIED=NO`; do not infer verified rollback or
rerun P4. This paragraph reports owner evidence; this docs change has not
independently inspected the Windows Primary.

This subsection retains the **GitHub wire/API contract for optional projection**.
It does not register any Deployments WRITE operation, create the Fortis Registry
or authorize a GitHub POST. Delivery
milestones and unaccepted work remain solely in the [roadmap](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue).
GitHub's [Deployments REST API](https://docs.github.com/en/rest/deployments/deployments)
and [status API](https://docs.github.com/en/rest/deployments/statuses) define the
provider wire semantics; Fortis owns the stricter interpretation below.

#### Identities and catalog binding

- **Queue subject:** canonical GitHub \`owner/repository\`, exact catalog target
  \`id\`, and one environment admitted by that target's *pinned*
  \`release/targets.yaml\` revision. Build units are not deployment subjects.
- **Desired version:** immutable \`desiredSourceSha\` (40-hex merged/accepted
  repository \`main\`), catalog SHA, required target actions and artifact
  identity: \`buildUnit\` + content-addressed image/package digest when available.
  Before a build, \`artifactDigest=null\` means **not verified/built**, never
  a wildcard matching the installed artifact. A source-only target binds an
  owner-verifiable source/installation manifest identity instead of an image.
- **Actual version:** per-target/per-environment source SHA **and** installed
  artifact/manifest identity, observed timestamp, controller identity, protected
  immutable original receipt ID/hash, and independent target-specific readback.
  \`actual=null\` means unknown, not absent. A GitHub deployment/status/CI or
  Docker image existing in a registry alone cannot fill this field.
- **Logical version key:** \`{repository,target,environment,desiredSourceSha,
  catalogSha,artifactIdentity}\`; the stable \`projectionId\` is a digest of the
  canonical key. Build pending versus materialized digest are different known
  identity stages; never rewrite an old GitHub deployment's immutable payload
  to change the target version. \`operationId\` identifies the individual
  publisher attempt/receipt, *not* the physical deployment or the identity key.
- **Shared build unit:** the same source/digest may serve several targets, but
  each target/environment gets its own actual state, dependencies and receipt.
  Cross-repository dependencies remain \`{repository,target}\` resolved against
  explicitly pinned catalog revisions; missing, cyclic or drifted graph blocks
  admission, not silently dropped edges. A future batch can group by the shared
  build identity without converting one build receipt to multiple deploy receipts.

#### Merged PR lineage and supersession

A lineage row binds repository, PR number, original PR HEAD, verified Release
Impact/body and catalog revision, actual GitHub merge commit and merge time,
and proof that the selected merged \`main\` contains the change. Prefer trusted
merged-PR/commit association plus compare/ancestry readback over current editable
PR labels or bodies. Existing Gateway \`get_pull_request\` projects \`merged\`
but not the merge commit/time: it is **insufficient by itself**. Incomplete
pagination, incomplete changed paths, missing historical validation or ambiguous
squash/rebase ancestry is \`UNKNOWN\`, not an invented PR association.

A newer desired \`main\` SHA **supersedes** an older queued desired version only
when ancestry, catalog scope and target coverage are proven. Supersession
preserves the older immutable entry and receipts; it does not retroactively
mark the newer version DEPLOYED or erase a FAILED/UNKNOWN attempt. A single
deployment can cover multiple merged PRs but necessarily contains the complete
chosen source SHA, not a selectively omitted subset. The current installed
version may legitimately be older than the newest desired version.

#### Fortis status calculation (per identity, not the latest GitHub status)

| Fortis state | Sufficient evidence / effect |
| --- | --- |
| \`QUEUED\` | Desired target/version and complete lineage/dependencies are verified; independent fresh actual/readback proves a different installed version, no unconfirmed in-flight attempt. Planning only. |
| \`BLOCKED\` | Known unmet dependency, required prerequisite, policy or owner gate, with no ambiguous effect; preserve the specific blocking reason. |
| \`IN_PROGRESS\` | Protected controller record proves an actual authorized attempt started for **this exact identity**; a GitHub \`in_progress\` status alone is insufficient. |
| \`DEPLOYED\` | Immutable original controller receipt **and** independent fresh live readback match this target, environment, source and artifact identity. |
| \`FAILED\` | A protected receipt proves an error of the identified attempt; it does not prove that an older installed version is gone. Retry requires a separate authorized attempt. |
| \`UNKNOWN\` | Missing/stale/conflicting receipt or readback, ambiguous lineage/ancestry, unconfirmed ACK, \`UNCERTAIN\`/active claim or identity mismatch. Never silently map to \`QUEUED\`, \`FAILED\` or \`DEPLOYED\`. |
| \`REPORTED_COMPLETE\` (proposed V1 registry event) | Owner states that a specific manual UC release finished; AI registers original target/desired SHA, owner assertion and optional evidence references via scoped typed API. No independent installed proof is implied. |
| \`PLANNED_UNVERIFIED\` (proposed V1 display) | Confirmed target/desired source from merge, but current installed state is not independently known. It is a planning item, not a verified mismatch or known-queued deployment. |

\`NO_DEPLOYMENT\` is an exact-head, validated impact classification and creates
**no** deployment identity. \`SUPERSEDED\` is a relation between immutable
desired versions, not proof of a deployment result. A target can expose both
its *latest desired* and *last confirmed actual*, with an explicit evidence
freshness/completeness flag. Unknown effect takes precedence over a nominally
queued or blocked action for that same identity.

#### Canonical Fortis Registry V1 (owner product decision; offline source schema v2 accepted, not live)

- **Authoritative queue:** durable Fortis-owned records, not Deployment objects;
  proposed logical key `{repository,target,environment,desiredSourceSha,catalogSha,
  artifactIdentity}` with explicit `unknown/notBuilt` artifact semantics. An
  immutable record can cover several owner-merged PRs after full validated
  Release Impact, catalog revision and lineage readback. A changed desired SHA
  links an immutable superseding record; no deletion/rewrite of earlier manual
  outcomes. Do not treat `no-deployment` as a queued target.
- **Forward-only V1 enrollment:** accounting starts at the first
  owner-accepted Registry release/enrollment boundary for the enrolled
  repository. The exact source/catalog baseline and cutover proof are
  immutable; no pre-baseline PR history backfill or synthetic installation
  records. Actual state stays unknown without independent target evidence.
  All post-baseline merges must be continuously covered; no rebaseline to
  hide gaps. The [P5 baseline contract](RELEASE-REGISTRY-P5-DESIGN.md#forward-only-enrollment-baseline-owner-decision-2026-11-21)
  owns bootstrap details.
- **Review/CI evidence:** full historical provider proof or a separately
  owner-accepted protected Registry-specific policy and immutable review
  cutoff may establish planning admission. See the
  [P5 alternative proposal](RELEASE-REGISTRY-P5-DESIGN.md#registry-specific-review-cutoff-and-ci-policy-proposed-alternative-2026-11-21).
  The alternative must not claim historical GitHub policy verification,
  weaken GitHub merge protection, or authorize deployment.
- **Manual installation:** record the relevant existing Use Case and approved
  command family; e.g., Gateway [UC-GW-005](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005)
  is `SelfTest → Check → Apply → live readback → Backup → Promote → host inspect`.
  Owner executes this separately on Windows; other products have their own UC.
  Nothing in a Registry or Release Board launches the script in V1.
- **Manual result event:** typed actor-scoped write with exact record ID/revision,
  target/environment/desired SHA, time, owner statement, original release/attempt
  reference where known, evidence links and immutable audit. A manual note
  cannot forge controller receipts, retroactively create `actual`, rewrite
  historical events or set `VERIFIED/DEPLOYED`. Existing technical evidence,
  when available, is labeled by its own verified evidence class.
- **Security/unknowns:** define authoritative data owner, storage, ACL/backup,
  CAS/idempotency, concurrent merges/annotations, actor policy, append-only audit,
  stale SHA checks and negative/recovery tests **before live Registry activation**.\n  Offline source candidates through Approvals PR #210 are not a protected runtime.
  If the entry cannot be bound to the intended source/target, STOP/UNKNOWN.
  No installed write API exists today. CD automation and automatic receipt
  collection are future separately owner-approved milestones.

#### GitHub projection mapping and event safety

- A future reviewed publisher uses \`POST /repos/{owner}/{repo}/deployments\`
  with \`ref=desiredSourceSha\`, explicit \`auto_merge=false\`, explicit
  \`task=fortis-cd-projection\`, \`transient_environment=false\` and a bounded
  \`payload\`. **Never omit \`auto_merge\`**: GitHub defaults it to \`true\` and
  may create a merge commit instead of a deployment. Do not use
  \`required_contexts=[]\` to bypass release admission. GitHub 202 (auto-merge)
  is not a created-deployment receipt; require HTTP 201 plus independent GET.
- Use an owner-reviewed, collision-free *target-scoped* GitHub environment
  mapping, proposed \`fortis-cd/<target>/<environment>\` for catalog-safe slugs
  with a bounded total length. Payload repeats the actual environment and
  target. Never conflate \`production\` across several targets, or silently
  reuse a human/Actions-managed environment. Source tests and an isolated
  owner-reviewed GitHub pilot must confirm naming/visibility before WRITE.
- Proposed bounded \`payload\` v1: \`schemaVersion=1\`,
  \`kind=fortis-cd-projection\`, \`repository\`, \`target\`, \`environment\`,
  \`desiredSourceSha\`, \`catalogSha\`, \`buildUnit\` (nullable),
  \`artifactDigest\` (nullable), \`actions\`, \`linkedPRs\`,
  \`projectionId\`, \`operationId\`. If complete lineage exceeds the accepted
  bound, STOP; never silently truncate or execute payload instructions.
  Validate exact GitHub response SHA, environment, task and payload binding.
- A planned \`QUEUED\` may project GitHub \`queued\`; verified start projects
  \`in_progress\`, protected failed attempt \`failure\`, verified installed
  state \`success\`. \`BLOCKED\` and \`UNKNOWN\` are Fortis overlay states,
  **not** false GitHub \`failure\` or \`success\`. \`inactive\` is not
  supersession. On success set \`auto_inactive=false\` to prevent GitHub
  auto-inactivation of earlier same-environment deployments. Statuses append
  to history; never rewrite source of truth to follow GitHub display state.
- **STOP on event risk:** GitHub emits \`deployment\` and
  \`deployment_status\` events on creation; Actions workflows/webhooks/apps
  can react and execute CD. A custom task name, environment namespace,
  \`queued\` state, ASK or \`auto_merge=false\` does **not** suppress events.
  Until owner-reviewed inventory/deny-by-default checks cover all consumers
  and repo/environment scopes, allow read-only preview **only**, no GitHub
  Deployment/status POST even as a harmless test. P4 does not activate P5/P6.
- GitHub retains previous deployment statuses only **90 days** (most recent
  current state remains). Historical original protected receipts, not GitHub
  status-list retention, own the audit trail. GitHub status publication can
  lag controller truth; lost ACK cannot trigger a repeated deployment.

#### Proposed typed Gateway READ and separately gated WRITE

**READ first**, using the existing authenticated \`github\` typed broker and
strict route catalogue: \`list_deployments(repo, page, perPage, filters)\`,
\`get_deployment(repo, deploymentId)\`,
\`list_deployment_statuses(repo, deploymentId, page, perPage)\`, and
\`get_deployment_status(repo, deploymentId, statusId)\`. The adapter must expose
only bounded typed projections (IDs, 40-hex SHA, task/environment, safe
versioned payload fields, timestamps, state, origin/readback links), never raw
provider objects/URLs/token. A separate bounded merged-PR evidence READ is
needed for merge SHA/time and full validated lineage. Unknown namespace,
foreign repo, malformed identity/payload, missing status or unexpected
provider response fails closed or surfaces \`UNKNOWN\`, never absence of work.

Follow GitHub \`page/per_page\` (maximum 100; prefer bounded 30), explicit
\`hasNextPage\` and a page/row budget, with no claim of an atomic snapshot.
Recheck head/catalog/merge SHA and selected deployment IDs after pagination;
an incomplete/changed enumeration is \`UNKNOWN\`. Group by repo, target,
environment, actions and desired identity **only after** validating the full
filtered inventory. The P4 Primary has these four typed GET capabilities only in the owner's
accepted `fortis-approvals` scope; no generic multi-repo READ and no
Deployments WRITE should be inferred from source presence.

**WRITE is a different owner-reviewed operation and release**, via
[UC-GW-003](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-003)
and [UC-GW-005](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005).
Propose distinct \`github.create_cd_projection\` and
\`github.append_cd_status\` with exact repo/target/environment/desired
fingerprint, immutable requestId, frozen preview, explicit \`ASK\`/WebAuthn,
scoped GitHub Deployments WRITE credential and trusted Publisher actor;
no default ALLOW, no arbitrary POST method/URL/status/task, no deploy command.
For \`success\`, Gateway additionally requires protected original controller
receipt and fresh independent installed readback, not a client assertion.
Preserve original UUID and worker evidence; on lost ACK/timeout/UNCERTAIN
read original result and independently enumerate matching projectionId/status
before contemplating another authorized publication. Never replay the
**physical install** as a consequence of publication uncertainty.

**Acceptance split:** the four P4 READ operations passed separate owner
runtime activation as reported on 2026-11-20. This does **not** activate
GitHub Deployments WRITE, a Fortis Registry, post-merge queue publication,
Release Board or automatic CD. Any GitHub POST still requires new API contract,
negative event/policy/receipt/race tests, exact-head CI, trusted Publisher,
owner-reviewed consumers/webhooks and explicit runtime release. A design-only
PR remains **SOURCE-CANDIDATE**, not a privileged write acceptance.
