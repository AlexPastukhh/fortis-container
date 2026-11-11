# Release Planning — cross-repository source contract v1

**Status (2026-11-11): V1 source/catalog contract and shared exact-head PR CI
accepted in the five enrolled projects; label/queue automation NOT active.**
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

### V1 Release Labels — normative projection contract (next stage)

Label data is derived from the **same** checked Release Impact, target
catalog and exact PR HEAD. Labels do not express permission to release or
evidence of an installed version. The executable pure projection candidate
is in public action PR
[Release Labels projection #2](https://github.com/AlexPastukhh/fortis-release-impact-action/pull/2).
It is **not active** until owner Merge, subsequent security review of the
publisher and actual end-to-end permission/readback checks.

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

### Fortis Release Planning — GitHub Projects queue (not yet created)

The project will be a **planning view** of PRs and Releases, not the
source of truth for accepted code, runtime state or installed SHAs. The
initial set of enrolled sources is the five repositories above. Each merged
PR is eligible for queue consideration; a `release:no-deployment` PR must
not create a false rebuild/deployment requirement.

Suggested fields: Repository, PR, Source SHA, Build Targets, Release Impact,
Release Status, Batch, Dependencies, Environment, Verification/Evidence.
Use views for new merged changes, awaiting release, blocked/review-required,
batch planning and verified deployments. The operational unit for runtime
tracking remains `Repository + PR + Build Target + Environment` because
one PR may affect multiple independently deployed targets.

GitHub Projects' built-in **Auto-add** can filter `is:pr is:merged`
per repository, but has GitHub-plan-dependent rule limits (e.g. five for
GitHub Pro, one for Free); it does **not** backfill preexisting PRs.
Do not assume the owner account's entitlements or declare historical items
imported without readback. If rules are insufficient, design a minimal
typed Gateway Projects adapter under UC-GW-003, not an AI direct GraphQL
write or a second release database. No such typed operation is currently
accepted and verified through the Fortis Gateway. The owner must approve
Project setup and access separately.

Automated GitHub label/Project metadata does not mean `Deployed`. Only
specific runtime protected release records and independent live verification
can confirm installed versions; GitHub Deployment follows those receipts.

**Next security/owner gates:** review/merge the read-only public Label
Projection PR; independently review/implement a trusted publisher;
pilot label assignment + stale-HEAD and permissions-negative tests on one
repository; verify all five; configure the owner's GitHub Project and auto-add
within verified plan limits; only then build Release Batch and Deployment
interfaces. None of these steps authorizes Production.
