# Source map and ownership

## Current project boundaries

| Component | Working source | Responsibility | State |
|---|---|---|---|
| Tunnel | `/workspace/repos/tunnel` | Repo1/Repo2 workers, shared Guard, Windows runtime source and legacy Repo bridge guidance | Existing Git repo; main with 11 modified tracked and 2 untracked task files; no commit/push |
| Script Control Center | `/workspace/repos/script-control-center` | Windows Script Catalog UI, adapters, resolver and updater | Existing Git repo; dirty main plus second worktree |
| RDG | `/workspace/repos/rd-graphs` | RDG application, graph, plan, decision and viewer | Existing Git repo; heavily dirty |
| Fortis Approvals original | `/workspace/repos/rd-graphs/fortis_approvals` | Original Fortis Approvals Gateway source, typed client, Core, policy, owner portal, tests and deployment references | Embedded in dirty rd-graphs working tree; 0 tracked files; original preserved |
| Fortis Approvals | `/workspace/repos/fortis-approvals/fortis_approvals` | Canonical development source for the Fortis Approvals Gateway; current-copy manifest and offline test report alongside it | 196 package files; owner-approved standalone Git repo on `main`; no commit or remote yet |
| Qwen integration artifacts | `/workspace/files/Qwen-Fortis-MCP` | Qwen-specific transport README plus retained legacy gateway artifacts | Workfiles; not a Git checkout; the active Windows `uvx` / `mcp-proxy` route to Desktop Commander 0.2.52 and 26-tool Qwen use are OWNER-REPORTED / transcript-backed |
| Mirror | `/workspace/repos/docke-windows-mirror` | Standalone Windows Mirror UI/exporter and the canonical ordinary-project `Repos` / `Worktrees` convention, GitHub Actions handoff and Docker → GitHub → Windows workflow; future read-only AI inventory API | Existing Git repository; documentation owns the agreed workflow. Worktree discovery and AI API are not implemented in the current GUI. See [canonical workflow](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md). |
| Fortis Container | `/workspace/repos/fortis-container` | Cross-project documentation hub, navigation, technical references, the Future Improvements backlog, dated evidence records and container-build provenance | Owner-approved standalone documentation repository; original Windows build files are documented but not adopted as a canonical Git-managed build context. Check live Git state before any repository operation; no continuously maintained working-tree snapshot is published here. |
| Original Fortis Repo build directory | `C:\Users\alexa\chatgpt-repo-mode` | Windows Dockerfile, build log, legacy bridge/probe files, PowerShell scripts, backups and runtime diagnostics | Owner-provided directory listing; no Git metadata; exact build context not proven |

Repository-state values in this table are the last recorded audit snapshot, except `fortis-container`, which was rechecked read-only in this continuation. Do not interpret the other repository status cells as fresh live checks.

The owner approved the extracted `fortis-approvals` tree as the canonical development source and approved a separate repository. Local Git is initialized on `main`; no commit or remote exists. The original RDG subtree remains untouched as the preserved original copy. `fortis-container` is also an owner-approved standalone documentation repository. Qwen remains in `/workspace/files/Qwen-Fortis-MCP`; no separate Qwen repository or move is planned for now.

## Tunnel ownership

- Canonical Repo1/Repo2 worker and shared Guard source: `tunnel/main`, `runtime/windows-repo/current`.
- The [Tunnel Windows source-mirror runbook](https://github.com/AlexPastukhh/tunnel/blob/main/runtime/windows-repo/README.md) describes the canonical Repo1/Repo2 worker source and its nine-file manifest.
- The [Tunnel Guard-change checklist](https://github.com/AlexPastukhh/tunnel/blob/main/docs/FORTIS_GIT_WINDOWS_LAUNCHER_WORKFLOW.md) defines the review/Preview sequence.
- The [Script Center Windows source-of-truth runbook](https://github.com/AlexPastukhh/script-control-center/blob/main/docs/GIT-WINDOWS-SOURCE-OF-TRUTH.md) owns the paired Windows clone update procedure.
- `script-control-center` owns the UI and thin adapters; it does not own the shared Guard implementation.
- `runtime/repo-mode/Dockerfile` is byte-identical to the owner-provided Windows Dockerfile (SHA-256 `1717e364b2f5cd92f4c6cabb039d4272598fe573b5e6cd9cfe7357a0abd4fa0b`), but the surrounding `runtime/repo-mode` directory is explicitly labelled a legacy Repo Mode reference, not current topology. See [container build provenance](CONTAINER-BUILD-PROVENANCE.md).
- The original Windows build directory has no Git metadata. Its backups and `runtime-diag-*.jsonl` files have not been reviewed for secrets or classified for archival; do not bulk-copy them into Git.
- `runtime/repo-mode/workspace-config.example.json` and older architecture/access docs contain a pre-volume description and must be treated as historical until reconciled.
- `runtime/repo-mode/fortis-mcp-bridge.mjs` is a legacy Repo initialize/tool-list wrapper. The following source investigation is a pre-deployment historical record; current deployment status is in the [path-guidance patch record](../patches/desktop-commander-0.2.52/README.md). The current ChatGPT tool descriptions are visible per tool in the Fortis Repo app UI: the supplied screenshot shows the `Read` description with the correct mounted-path list. Current connected metadata shows that `read_file` receives `PATH_GUIDANCE`, while `start_process` receives a different `OS_GUIDANCE` block containing generic Windows/Linux-to-`/home/...` translation that is wrong for the Fortis shared-volume topology. The source is the installed Desktop Commander package: `server.js:8-10` builds both guidance strings; `server.js:791-798` injects `OS_GUIDANCE` into `start_process`; `system-info.js:585-593` hard-codes the obsolete `/home` mapping; `system-info.js:699-711` builds the correct dynamic mount-path guidance. The historical exact `C:\Users\alexa` replacement remains in the installed legacy wrapper but is absent from the current connected tool schema. Current Repo1/Repo2 workers use the direct Desktop Commander entry point; the bridge is not in their observed process path. The owner approved the narrow correction on 2026-11-04. A hash-pinned build-time patch candidate, test script, patch-only Dockerfile and Windows build runner now exist under `fortis-container/patches/desktop-commander-0.2.52/`. Tests passed against a disposable copy; at that point the candidate had not yet been deployed. The installed package remains root-owned on the read-only root filesystem and the connected process runs as UID 1000. The host-side image build, controlled replacement and Repo2 reconnect were subsequently completed; Repo1's corrected description was owner-confirmed. No active package file was changed and no process was killed or restarted. See `docs/AI-INTEGRATIONS.md` for details.

## Script Control Center ownership

The main worktree is at `/workspace/repos/script-control-center`. A second worktree exists at `/workspace/repo/Repos/script-control-center-filequarantine-launch`, branch `feature/filequarantine-script-center-launch-20261103`. Both currently point to commit `8fc2731`. Main has 2 modified (unstaged) files and 44 untracked files. Preserve all of them.

## RDG and Fortis Approvals boundary

The original Approval package remains inside the dirty `rd-graphs` checkout. It contains 293 files across package root, deploy, tests, static assets and archive. Git tracks zero files in this subtree; 196 non-generated files are untracked and 97 files are generated Python cache/bytecode. The owner-approved repository at `/workspace/repos/fortis-approvals/` contains the 196 non-generated source files, initially verified against an original SHA-256 manifest. It is the canonical development source; local Git is initialized on `main`, with no commit or remote. The original RDG subtree remains untouched as the preserved original copy. The broader RDG checkout also has many unrelated modified and untracked files.

The standalone repository preserves the Python import root `fortis_approvals`, tests, existing deployment references, evidence and historical archive. It contains 196 non-generated package files; the original source manifest matched at extraction. A separate current-copy manifest records four changed original package files: two historical-pointer test corrections and two README naming/documentation updates. A new render-only Compose candidate was added separately and is not part of the 196-entry extraction manifest. Selected offline/static regression coverage is 198/198 across 26 suites; WebAuthn-dependent suites remain blocked by missing pinned packages. The original subtree remains untouched. The local repository boundary is approved and initialized; remote visibility and credential scope remain pending.

The current source contains some stale module docstrings inherited from earlier candidate stages. In particular, comments in `repo_action_contract.py` and `sonar.py` do not fully describe their later Gateway composition. Treat the current-state README, Gateway composition and live evidence as the higher-level description; correct source comments during the reviewed extraction, not by guessing at the deployed image.

## Deployed copies versus source

- The deployed Gateway image contains a package under `/opt/fortis/fortis_approvals`, according to owner deployment evidence. The standalone repository also contains a render-only target Compose candidate, `fortis_approvals/deploy/compose-fortis-approvals-dryrun.yaml`; it is not the active deployment file and must not be started. The image-only build script `Build-R7-Windows-ImageOnly-p2-20261103.ps1` pins `Dockerfile-R7-Unified-Read-Ask-Candidate` by SHA-256; the top-level `deploy/Dockerfile` is a different older `fortis_approvals.server` / port-18990 recipe and is not the Dockerfile named by that build script. See the [deployment artifact index](https://github.com/AlexPastukhh/fortis-approvals/blob/main/fortis_approvals/deploy/README.md).
- Editing `rd-graphs/fortis_approvals` does not update the running Gateway image.
- The dated Compose file with R7/P2 in its filename is a preserved artifact reference, not an instruction to rerun it or a proposed new naming convention.
- Windows installed workers and profiles are separate from Docker source checkouts. Use the Tunnel and Script Center manifests/runbooks to reason about them.

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
