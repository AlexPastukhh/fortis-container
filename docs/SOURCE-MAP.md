# Source map and ownership

## Current project boundaries

| Component | Canonical source | Responsibility | Boundary |
| --- | --- | --- | --- |
| Tunnel | `/workspace/repo/Repos/tunnel` | Repo1/Repo2 workers, shared Guard and Windows launcher source | `runtime/windows-repo/current` is source, not installed Windows runtime |
| Script Control Center | `/workspace/repo/Repos/script-control-center` | Windows UI, thin adapters, resolver and paired updater | Does not own shared Guard implementation |
| RDG | `/workspace/repo/Repos/rd-graphs` | RDG application, graph, plan, decision and viewer | Independent project; no state scan or edits implied by this map |
| Fortis Approvals | `/workspace/repo/Repos/fortis-approvals` | Gateway, typed client, Core/policy, owner portal, tests and deployment controller | Standalone published repo; Python import root remains `fortis_approvals` |
| Qwen integration artifacts | `/workspace/files/Qwen-Fortis-MCP` | Transport README and retained legacy artifacts | Workfiles, not a Git checkout; active transport evidence is OWNER-REPORTED |
| Mirror | `/workspace/repo/Repos/docke-windows-mirror` | Docker/Windows inventory, UI/API source and Git delivery convention | API-first source candidate is separate from installed Windows acceptance |
| Fortis Container | `/workspace/repo/Repos/fortis-container` | Shared UC registry, docs navigation, container provenance and one improvements backlog | Docs repo; original full build context is not yet canonicalized |
| Original Repo build directory | `C:\Users\alexa\chatgpt-repo-mode` | Historical Windows Dockerfile, build log and runtime diagnostics | Build provenance only; do not bulk-copy unreviewed backups/logs |

`/workspace/repos` and `/workspace/files` alias the persistent Docker workspace
subpaths, not Windows clones. Exact task membership comes from `git worktree list`.
This map owns responsibilities and paths; it does not maintain branch/dirty/SHA
snapshots. Canonical `Repos/<repo>` stays on clean `main`; edits belong in registered
task worktrees. Verify actual state before operations, using the common
[worktree UC](use-cases/worktrees.md#uc-cont-019).

## Tunnel ownership

- Canonical Repo1/Repo2 worker and shared Guard source: `tunnel/main`, `runtime/windows-repo/current`.
- The [Tunnel Windows source-mirror runbook](https://github.com/AlexPastukhh/tunnel/blob/main/runtime/windows-repo/README.md) describes the canonical Repo1/Repo2 worker source and its nine-file manifest.
- The [Tunnel Guard-change checklist](https://github.com/AlexPastukhh/tunnel/blob/main/docs/FORTIS_GIT_WINDOWS_LAUNCHER_WORKFLOW.md) defines the review/Preview sequence.
- The [Script Center Windows source-of-truth runbook](https://github.com/AlexPastukhh/script-control-center/blob/main/docs/GIT-WINDOWS-SOURCE-OF-TRUTH.md) owns the paired Windows clone update procedure.
- `script-control-center` owns the UI and thin adapters; it does not own the shared Guard implementation.
- `runtime/repo-mode/Dockerfile` is byte-identical to the owner-provided Windows Dockerfile (SHA-256 `1717e364b2f5cd92f4c6cabb039d4272598fe573b5e6cd9cfe7357a0abd4fa0b`), but the surrounding `runtime/repo-mode` directory is explicitly labelled a legacy Repo Mode reference, not current topology. See [container build provenance](CONTAINER-BUILD-PROVENANCE.md).
- The original Windows build directory has no Git metadata. Its backups and `runtime-diag-*.jsonl` files have not been reviewed for secrets or classified for archival; do not bulk-copy them into Git.
- `runtime/repo-mode/workspace-config.example.json` and older architecture/access docs contain a pre-volume description and must be treated as historical until reconciled.
- `runtime/repo-mode/fortis-mcp-bridge.mjs` is a legacy wrapper; current
  Repo1/Repo2 workers use direct Desktop Commander. Source investigation,
  reviewed path-guidance patch and deployment evidence are owned by the
  [patch record](../patches/desktop-commander-0.2.52/README.md).
  MCP UI suppression is owned by its
  [separate derivative record](../patches/desktop-commander-0.2.52-mcp-ui-headless/README.md).
  Neither legacy wrapper edits nor Markdown changes update the installed package.

## Script Control Center ownership

Canonical source and Windows update procedure are in the Script Center
[runbook](https://github.com/AlexPastukhh/script-control-center/blob/main/docs/GIT-WINDOWS-SOURCE-OF-TRUTH.md).
Existing task worktrees and local recovery snapshots are separate from primary;
inspect membership and deployment references before cleanup. Do not maintain
a second live worktree inventory in this document.

## RDG and Fortis Approvals boundary

The original `rd-graphs/fortis_approvals` subtree is a preserved historical copy,
not the development target. The standalone `fortis-approvals` repository owns
all new Gateway work. Extraction hashes, original file counts and the initial
offline test limitations belong to the dated
[source extraction audit](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/audits/SOURCE-EXTRACTION-2026-11-03.md),
not a current status table. The original RDG checkout is outside this task.

Gateway package layout, tests, manifests and controller source are linked from
its [package map](https://github.com/AlexPastukhh/fortis-approvals/blob/main/fortis_approvals/README.md).
Do not infer installed behavior from inherited docstrings or an extraction snapshot.

## Deployed copies versus source

- Gateway source, immutable image and live container are separate targets.
  Supported source/image admission and controller operations belong to the
  [Gateway release UC](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005)
  and [deployment source map](https://github.com/AlexPastukhh/fortis-approvals/blob/main/fortis_approvals/deploy/README.md).
- Superseded render-only Compose candidates are historical artifacts; do not
  select or run one merely because its filename contains a release label.
- Editing the old RDG subtree does not update the standalone source or live image.
- Windows workers/profiles are separate from Docker source. Use Tunnel/Script Center
  manifests and owner-run Preview/Apply; a source pull does not restart workers.

## Classification rules

Every source item must be classified as one of:
- canonical source;
- development copy;
- deployed copy;
- runtime state;
- historical snapshot;
- candidate;
- generated artifact.

Do not infer canonical ownership from a folder name or recent timestamp alone.

## Fortis Repo Mode lifecycle — 2026-11-04

Detailed source hashes, qualifications and file-by-file findings are recorded in [container build provenance](CONTAINER-BUILD-PROVENANCE.md), sections 14.1–14.10. This summary connects those findings to the system-wide source map.

| Lifecycle role | Artifact | Status and handling |
|---|---|---|
| CANONICAL | `tunnel/main`, `runtime/windows-repo/current` | Authoritative Repo1/Repo2 Windows worker and shared Guard source, pinned by its source manifest. |
| DEPLOYED RUNTIME | Desktop Commander 0.2.52 in the current Repo container | Active MCP backend; current connection is LIVE VERIFIED. It is not a Git source checkout. |
| LEGACY / INSTALLED COPY | Windows-root `fortis-mcp-bridge.mjs` and matching `/workspace/repo/.fortis/mcp-bridge.mjs` | Hash-identical legacy wrapper. Current Repo1/Repo2 workers use direct Desktop Commander, not this wrapper. Its Windows bind-mount guidance is stale. |
| LEGACY / MUTATING | Windows-root `probe.mjs` | Encodes the old bind-mount model; changes Desktop Commander and Git config and writes generated snapshots. Not a read-only diagnostic. |
| LOCAL CONTROL / UNKNOWN USE | Windows-root `control.ps1` | Manual control helper; active use is not established. Do not run its start/stop actions during documentation work. |
| CANDIDATE | Windows-root `run-tunnel.ps1` (PR-A-15) | Self-labelled not installed; pins an exited rollback container. Not approved as current launcher. |
| ARCHIVE | Backup snapshots, `bridge-before-worktree-guidance.mjs`, historical configure/run scripts | Provenance only; not current setup instructions. |
| ARCHIVE / TEST ARTIFACTS | `check-controls.ps1`, `check-presentation.mjs`, `check-schemas.mjs`, `expected-schemas.json` | Historical mocked, mutating-integration and generated-snapshot checks; none was run in this review. |
| UNKNOWN / NOT REVIEWED | Windows verification/access/mount JSON and runtime diagnostic logs | Not present in the export. Do not bulk-copy to Git before classification and secret screening. |

### Architecture generations

1. **Initial isolation:** one Docker-managed workspace volume at `/workspace/repo`, `network=none`, no Windows folder mounts.
2. **Transitional host mounts:** Windows `Repos` and `Workfiles` bind-mounted at `/workspace/repos` and `/workspace/files`, with egress through `fortis-repo-egress`.
3. **Current volume-subpath model:** one ext4 `fortis-repo-workspace` volume exposed at `/workspace/repo`, with `Repos` and `Workfiles` subpaths exposed at `/workspace/repos` and `/workspace/files`; direct Desktop Commander connection.

Do not combine instructions from these generations. The current MCP process, version, client and allowed directories were re-confirmed LIVE in this session; full Docker identity/security details remain based on owner-provided host inspection.

**Operational boundary:** do not execute the legacy probe, local controller, PR-A-15 candidate or historical registration scripts; do not change Docker, active packages, Tunnel workers or credentials during documentation work. Preserve all existing uncommitted changes. See provenance section 14 for exact hashes, stale container IDs, inference limits and export omissions.
