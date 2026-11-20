# Fortis Registry P5 — offline desired-release preview (2026-11-20)

**STATUS: SOURCE-ONLY CANDIDATE; NOT LIVE; NOT AN AUTHORITATIVE QUEUE.**
This extends the [accepted P5 architecture proposal](RELEASE-REGISTRY-P5-DESIGN.md)
and the [component restriction model](RELEASE-REGISTRY-P5-COMPONENT-RESTRICTIONS.md).
It does not add a Gateway operation, deploy a service or create any production
Registry record, credential, image, state volume or GitHub Deployment.

## Why this stage exists

The release registry needs two separate models:
1. **Desired release candidates**, keyed per deployment target and environment
   for one exact accepted merged `main` SHA and pinned catalog identity.
2. **Component/resource restrictions**, defined by explicit exceptions only:
   they coordinate release windows without blocking unrelated repository work.

Do not equate a target with an entire Git repository or a buildUnit with an
installed component. A single image may serve several deployment targets,
each with its own target/environment desired and actual states.

## Pure offline API

`tools/registry/desired_preview.py::preview(snapshot)` consumes a complete
*caller-supplied* fixture and returns `CANDIDATE_PREVIEW_ONLY` or raises a
`PreviewError`. It never contacts GitHub or Gateway, writes SQLite, executes
owner scripts or issues policy decisions. Output always contains
`evidenceVerified=false`, and each candidate has `actual=null`,
`planningState=PLANNED_UNVERIFIED`, `artifact.state=NOT_BUILT` and
`componentMappingStatus=UNVERIFIED`.

An input `snapshot` currently includes:

| Field | Offline meaning; **not independently trusted** |
| --- | --- |
| `repository`, `selectedMainSha`, `sourceReadRef` | Claimed canonical repo, selected full merge source SHA and readback reference |
| `catalogSha`, `catalogDigest`, `catalog` | Pinned catalog commit and **canonical JSON** digest, not proof of a real Git blob/checkout |
| `mergedPullRequests` | PR numbers, exact PR-head and merge SHA/time, main-contains-merge *claim*, impact and changed paths, CI check readback claims |
| `completeness` | Claimed complete lineage, paths, catalog, exact CI, ancestry, dependencies; **booleans do not prove completeness** |
| `environmentBindings` | Exact environment chosen for every affected target, not wildcard expansion |
| `dependencyProofs` | Exact catalog/repository/target reference claims; no implication that dependencies are installed |

The [post-merge evidence readiness assessment](RELEASE-REGISTRY-P5-POST-MERGE-EVIDENCE.md) explicitly blocks trusted ingestion from current Gateway projections.

The pure candidate validates the pinned catalog structure using the accepted
`tools/release/validate.py` JSON Schema implementation, the existing
`validate_impact` semantic validator and extra graph/identity checks.
Unknown source paths, missing/duplicate PR, missing claimed coverage, wrong
CI head, unproven ancestry claim, missing dependencies, catalog digest drift,
invalid environment or `unknown` action fails closed. An exact validated
`no-deployment` impact creates **zero** desired records. A mixed batch with
several PRs against one chosen SHA creates one candidate per affected target
and environment with the full covered PR lineage (including docs-only PRs).

This preview is **NOT** an equivalent of the independently trusted merged-PR
collector specified in the [release planning contract](RELEASE-PLANNING-CONTRACT.md).
A malicious caller can forge `mainContainsMerge=true`, changed path lists,
CI status, input reference or completeness flags; matching input hashes show
only equality of those supplied bytes. In particular, the currently deployed
typed `get_pull_request` does not expose all required immutable historical
merge evidence. **Therefore preview output cannot be admitted to a canonical
Registry queue or used as deployment authority without a new reviewed
trusted collector, actor policy and durable admission transaction.**

## Component mapping and parallel-work safety

The desired target record carries a repository/target/environment identity.
Mapping it onto the accepted component graph, with shared state resources,
requires a separate pinned catalog binding and trusted snapshot. It is not
silently inferred from repo name. Each component still follows the explicit
restriction evaluator: an empty restriction set is not a grant. A Gateway
release quiescence window may block conflicting gateway operations but not
independent source editing or release work for unrelated components.
Release windows, `UNCERTAIN`/`CLAIMED` preservation and stopped-Gateway
scenarios stay under original owner Use Cases and protected controller
records, not under the candidate preview module.

## Verification, dependencies, open work

Run `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests
-p 'test_*.py' -q` to test fixtures and offline semantics. The new preview
unit tests **stub only the `jsonschema` schema gate** to isolate dependency-
free planning behavior; they also confirm its missing-dependency path fails
closed. The accepted schema validator requires pinned
`tools/release/requirements.txt` (PyYAML and jsonschema) in a separately
prepared test environment for real schema integration. The current Fortis
Repo Python lacks `jsonschema`; **full end-to-end schema integration is not
claimed verified by the local fixture tests.** A follow-up source CI job
should install pinned dependencies and run unmocked integration fixtures.

Next milestones before P5 is live:
- Add independently authenticated typed merged PR/CI/catalog/ancestry
  evidence without relying on editable PR labels or supplied booleans.
- Bind release target/environment onto component/resource graph with
  reviewed target identifiers and exact catalog versions; verify dependency
  closure and installed technical evidence independently.
- The [offline desired journal](RELEASE-REGISTRY-P5-DESIRED-STORE.md) now exercises candidate-only durable records, CAS and supersession; trusted ingestion and actual state remain unimplemented.
- Owner review and explicit runtime placement/grants/backup/restore before
  installation; manual `REPORTED_COMPLETE` belongs to P6, not this stage.

**P4 GitHub Deployments READ is already complete** and no P4 re-release,
Deployments POST, auto-CD, Windows/Production action is authorized here.
