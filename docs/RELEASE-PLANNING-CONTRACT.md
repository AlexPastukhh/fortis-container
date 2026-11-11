# Release Planning — cross-repository source contract v1

**Status: DESIGN / source candidate.** These schemas define the first shared format; no CI validator,
automatic labels, GitHub Project, Release Batch planner or Deployment publisher is deployed by this
document. Acceptance requires the normal task PR/CI/owner merge and separate onboarding tests.

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

- `fortis-container`: one cross-repo schema and validator, release coordination use case,
  onboarding route through [UC-CONT-018](use-cases/delivery.md#uc-cont-018).
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

**Validator source candidate:** `tools/release/validate.py` enforces schema plus
local catalog/impact invariants, with tests in `tests/test_release_validator*.py` and
`tools/release/requirements.txt`. It is not yet enrolled into PR checks of the five projects.
The optional new `release-schema-ci.yml` is a source candidate until its workflow
change is owner-approved, merged and observed at exact PR HEAD.

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

**Next implementation gate:** verify one shared YAML + JSON Schema validator with
positive/negative tests, wire it to a pilot PR without privileged untrusted-code
execution, then review and onboard the five catalogs one at a time. Future scope
belongs in the repository's single `docs/BACKLOG-IMPROVEMENTS.md`; avoid separate
roadmap copies and never call an unimplemented step active.
