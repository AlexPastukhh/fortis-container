# Source map and ownership

## Current project boundaries

| Component | Working source | Responsibility | State |
|---|---|---|---|
| Tunnel | `/workspace/repos/tunnel` | Repo1/Repo2 workers, shared Guard, Windows runtime source and legacy Repo bridge guidance | Existing Git repo; main with 11 modified tracked and 2 untracked task files; no commit/push |
| Script Control Center | `/workspace/repos/script-control-center` | Windows Script Catalog UI, adapters, resolver and updater | Existing Git repo; dirty main plus second worktree |
| RDG | `/workspace/repos/rd-graphs` | RDG application, graph, plan, decision and viewer | Existing Git repo; heavily dirty |
| Fortis Approvals original | `/workspace/repos/rd-graphs/fortis_approvals` | Original Fortis Approvals Gateway source, typed client, Core, policy, owner portal, tests and deployment references | Embedded in dirty rd-graphs working tree; 0 tracked files; original preserved |
| Fortis Approvals | `/workspace/repos/fortis-approvals/fortis_approvals` | Canonical development source for the Fortis Approvals Gateway; current-copy manifest and offline test report alongside it | 196 package files; owner-approved standalone Git repo on `main`; no commit or remote yet |
| Qwen integration artifacts | `/workspace/files/Qwen-Fortis-MCP` | HTTP predecessor, pinned six-tool STDIO gateway and local acceptance test | Workfiles; not a Git checkout; Windows proxy transport is OWNER-REPORTED, while the Qwen chat's claimed 26-tool surface conflicts with the pinned source |
| Fortis Container | `/workspace/repos/fortis-container` | Cross-project system documentation, architecture, source map, recovery guidance and container-build provenance record | Owner-approved local Git repo on `main`; first documentation-baseline commit `2119ccb`; no remote; original Windows build files located but not yet adopted as canonical Git-managed source |
| Original Fortis Repo build directory | `C:\Users\alexa\chatgpt-repo-mode` | Windows Dockerfile, build log, legacy bridge/probe files, PowerShell scripts, backups and runtime diagnostics | Owner-provided directory listing; no Git metadata; exact build context not proven |

The owner approved the extracted `fortis-approvals` tree as the canonical development source and approved a separate repository. Local Git is initialized on `main`; no commit or remote exists. The original RDG subtree remains untouched as the preserved original copy. `fortis-container` is also an owner-approved standalone documentation repository. Qwen remains in `/workspace/files/Qwen-Fortis-MCP`; no separate Qwen repository or move is planned for now.

## Tunnel ownership

- Canonical Repo1/Repo2 worker and shared Guard source: `tunnel/main`, `runtime/windows-repo/current`.
- The [Tunnel Windows source-mirror runbook](../../tunnel/runtime/windows-repo/README.md) describes the canonical Repo1/Repo2 worker source and its nine-file manifest.
- The [Tunnel Guard-change checklist](../../tunnel/docs/FORTIS_GIT_WINDOWS_LAUNCHER_WORKFLOW.md) defines the review/Preview sequence.
- The [Script Center Windows source-of-truth runbook](../../script-control-center/docs/GIT-WINDOWS-SOURCE-OF-TRUTH.md) owns the paired Windows clone update procedure.
- `script-control-center` owns the UI and thin adapters; it does not own the shared Guard implementation.
- `runtime/repo-mode/Dockerfile` is byte-identical to the owner-provided Windows Dockerfile (SHA-256 `1717e364b2f5cd92f4c6cabb039d4272598fe573b5e6cd9cfe7357a0abd4fa0b`), but the surrounding `runtime/repo-mode` directory is explicitly labelled a legacy Repo Mode reference, not current topology. See [container build provenance](CONTAINER-BUILD-PROVENANCE.md).
- The original Windows build directory has no Git metadata. Its backups and `runtime-diag-*.jsonl` files have not been reviewed for secrets or classified for archival; do not bulk-copy them into Git.
- `runtime/repo-mode/workspace-config.example.json` and older architecture/access docs contain a pre-volume description and must be treated as historical until reconciled.
- `runtime/repo-mode/fortis-mcp-bridge.mjs` is a legacy Repo initialize/tool-list wrapper. The corrected Tunnel source candidate passes 4/4 source tests, but is not deployed. The current ChatGPT tool descriptions are visible per tool in the Fortis Repo app UI: the supplied screenshot shows the `Read` description with the correct mounted-path list. Current connected metadata shows that `read_file` receives `PATH_GUIDANCE`, while `start_process` receives a different `OS_GUIDANCE` block containing generic Windows/Linux-to-`/home/...` translation that is wrong for the Fortis shared-volume topology. The source is the installed Desktop Commander package: `server.js:8-10` builds both guidance strings; `server.js:791-798` injects `OS_GUIDANCE` into `start_process`; `system-info.js:585-593` hard-codes the obsolete `/home` mapping; `system-info.js:699-711` builds the correct dynamic mount-path guidance. The historical exact `C:\Users\alexa` replacement remains in the installed legacy wrapper but is absent from the current connected tool schema. Current Repo1/Repo2 workers use the direct Desktop Commander entry point; the bridge is not in their observed process path. The owner approved the narrow correction on 2026-11-04, but it is not deployed: the installed package is root-owned and the connected MCP process runs as UID 1000 without write permission. No active package file was changed; no process was killed because no safe in-container restart path was identified. Root-level deployment and a ChatGPT-only MCP reconnect remain outstanding. See `docs/AI-INTEGRATIONS.md` for details.

## Script Control Center ownership

The main worktree is at `/workspace/repos/script-control-center`. A second worktree exists at `/workspace/repo/Repos/script-control-center-filequarantine-launch`, branch `feature/filequarantine-script-center-launch-20261103`. Both currently point to commit `8fc2731`. Main has 2 modified (unstaged) files and 44 untracked files. Preserve all of them.

## RDG and Fortis Approvals boundary

The original Approval package remains inside the dirty `rd-graphs` checkout. It contains 293 files across package root, deploy, tests, static assets and archive. Git tracks zero files in this subtree; 196 non-generated files are untracked and 97 files are generated Python cache/bytecode. The owner-approved repository at `/workspace/repos/fortis-approvals/` contains the 196 non-generated source files, initially verified against an original SHA-256 manifest. It is the canonical development source; local Git is initialized on `main`, with no commit or remote. The original RDG subtree remains untouched as the preserved original copy. The broader RDG checkout also has many unrelated modified and untracked files.

The standalone repository preserves the Python import root `fortis_approvals`, tests, existing deployment references, evidence and historical archive. It contains 196 non-generated package files; the original source manifest matched at extraction. A separate current-copy manifest records four changed original package files: two historical-pointer test corrections and two README naming/documentation updates. A new render-only Compose candidate was added separately and is not part of the 196-entry extraction manifest. Selected offline/static regression coverage is 198/198 across 26 suites; WebAuthn-dependent suites remain blocked by missing pinned packages. The original subtree remains untouched. The local repository boundary is approved and initialized; remote visibility and credential scope remain pending.

The current source contains some stale module docstrings inherited from earlier candidate stages. In particular, comments in `repo_action_contract.py` and `sonar.py` do not fully describe their later Gateway composition. Treat the current-state README, Gateway composition and live evidence as the higher-level description; correct source comments during the reviewed extraction, not by guessing at the deployed image.

## Deployed copies versus source

- The deployed Gateway image contains a package under `/opt/fortis/fortis_approvals`, according to owner deployment evidence. The standalone repository also contains a render-only target Compose candidate, `fortis_approvals/deploy/compose-fortis-approvals-dryrun.yaml`; it is not the active deployment file and must not be started. The image-only build script `Build-R7-Windows-ImageOnly-p2-20261103.ps1` pins `Dockerfile-R7-Unified-Read-Ask-Candidate` by SHA-256; the top-level `deploy/Dockerfile` is a different older `fortis_approvals.server` / port-18990 recipe and is not the Dockerfile named by that build script. See the [deployment artifact index](../../fortis-approvals/fortis_approvals/deploy/README.md).
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
