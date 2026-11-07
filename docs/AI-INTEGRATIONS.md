# AI integrations

## Credentialed requests to external services

When an AI task needs an authenticated request to an external service, Fortis Approvals is the intended central broker: AI sends a typed operation, while the Gateway owns the upstream credential and enforces its ALLOW / ASK / DENY policy. Use the [Fortis Approvals Gateway agent guide](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/GATEWAY-AGENT-GUIDE.md) for the canonical usage and service-extension procedure.

Accepted integrations include scoped SonarCloud READ / ASK and token-scoped
multi-repo GitHub/native workspace operations. This does not imply every provider,
repository or operation is enabled: verify live capabilities and policy.
This document owns AI-to-container client paths; Fortis Approvals owns service
authorization and operation policy.

## Shared execution model

There is one shared Fortis Repo Docker container for these client paths. Each client can have its own MCP server process; a separate process is not a separate container or workspace.

- ChatGPT Repo1 uses the Windows Tunnel / Repo1 worker chain.
- ChatGPT Repo2 uses the Windows Tunnel / Repo2 worker chain.
- Qwen Studio uses the Windows `uvx` / `mcp-proxy` route with a local loopback SSE endpoint.
- The Qwen proxy uses `docker exec` to start the original Desktop Commander 0.2.52 entrypoint in the existing Fortis Repo container. It does not use the Workfiles six-tool gateway as its active server and does not create another container.

The Tunnel runbook describes Repo1 and Repo2 as separate Windows profiles with one shared Guard policy. On 2026-11-04, owner-provided PowerShell output confirmed the active Repo1 process chain through Script Catalog → Script-Runner → Repo1 worker → Tunnel runtime; Repo2 Guard Preview returned `no running tunnel detected`. These are owner-provided Windows observations, not direct process access from this Docker MCP session.

The Desktop Commander processes serving ChatGPT and Qwen run as Linux UID/GID 1000 and use the same workspace tree. They are separate MCP process instances using the same installed Desktop Commander version and container workspace. Separate per-client container volumes or OS identities are not established by the available evidence; other container processes were not exhaustively enumerated.

## ChatGPT / Repo1 / Repo2

The documented route is ChatGPT account → Windows Script Catalog / profile-specific worker → Windows Tunnel Client → existing Fortis Repo container → Desktop Commander MCP.

**Repo1 process-chain evidence (owner-provided Windows process output, 2026-11-04):**

`Start-ScriptCatalog.ps1` → `Script-Runner.ps1` → Script Center `Repo1-Worker.ps1` adapter → canonical Tunnel `current/Repo1-Worker.ps1` → `run-tunnel-quiet-logs.ps1 -Mode Run` → `tunnel-client-runtime.exe --profile repo-mode` → stdio `docker exec -i` → the existing container. The parent PowerShell above `Start-ScriptCatalog.ps1` was not identified. The observed command line and worker source confirm that the active Repo1 path is the Script Catalog adapter chain, not the old Script Center `launchers/chatgpt-repo-mode/run-tunnel.ps1` tree.

The Script Center adapter resolves the sibling Windows `Repos\\tunnel` clone and fails closed unless both Script Center and Tunnel clones are on clean, synchronized `main` with approved origins and the nine-file Tunnel source manifest/hash inventory matches. It has no local worker fallback.

The Script Catalog hidden-runner mode creates a run specification and stop-token file. `Script-Runner.ps1` monitors that token and, on an explicit Catalog Stop action, terminates the owned worker child process tree with `taskkill /T /F`. This is the observed Repo1 lifecycle-control path; do not substitute the legacy HTTP control script for the active stdio tunnel. In particular, its `Get-RepoTunnel` counts only a loopback listener whose `/metrics` contains the Repo tunnel ID. The current stdio `--mcp.command` process has no such listener, so the Preview result `ExistingTunnelCount=0` together with `ExistingProfileCount=1` is expected, not evidence of a stopped Repo1 connection.

**Repo2 source path:** Script Center adapter → canonical Tunnel `current/Repo2-Worker.ps1` → `Start-Fortis.ps1` / shared policy → Repo2 Direct Guard → Repo2 quiet launcher → pinned runtime and direct Docker exec. `Start-Fortis.ps1` may start only the already-existing container if it is stopped; the worker captures the inspected full Container ID and passes that exact ID through the Repo2 Guard and exec path. Repo2 keeps its independent profile/key/ACL and tunnel checks.

Source ownership:
- `tunnel`: Repo1/Repo2 workers, Windows launcher chain, shared Guard policy and runtime source map.
- `script-control-center`: Script Catalog/Control Center UI, thin worker adapters, resolver and paired updater.
- Fortis Repo container: separate runtime; it is not built from the Tunnel repository.

## ChatGPT MCP tool-description provenance

The Fortis Repo app UI exposes descriptions for individual tools. The app-level listing may still say "Нет описания"; that is separate from the descriptions attached to individual tools.

### Current deployment — 2026-11-04

The hash-pinned Desktop Commander 0.2.52 path-guidance patch is deployed in
`fortis-repo-test` (container
`3c4b50df90381ffd23809e0c7ba5e3bf8762ac33829ce2fb3a6d44a29da2d07c`,
image
`fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104`). The active
`system-info.js` hash is
`128c7f8c29dab1dd95e277d7929bc6dc05ade62a00d0df8b345bf04d7929c2f1`.

After reconnect, the Repo2 MCP tool catalog in this ChatGPT account was
directly inspected. Its live `start_process` description now lists the
runtime-mounted `/workspace/files`, `/workspace/repo` and
`/workspace/repos` paths and explicitly prohibits guessed host-to-container
translations. The obsolete Windows/Linux-to-`/home` examples and
Docker Installer `/home/[folder-name]` claim are absent. The installed file
hash matches the reviewed patch. The owner separately confirmed Repo1 exposes
the corrected description as well.

Both Repo1 and Repo2 Guard Previews passed during the owner-run cutover. The
old container is retained stopped as
`fortis-repo-test-pre-path-guidance-20261104`; see the
[patch deployment record](../patches/desktop-commander-0.2.52/README.md) for
the exact IDs and post-cutover checks.

### Pre-deployment investigation (historical; superseded by the live status above)

The pre-deployment screenshots and tool metadata showed the original mismatch.
The supplied screenshots showed the `Read` tool description, including the
mounted-path guidance. This did not establish that `start_process` was
corrected.

Pre-deployment connected tool metadata confirmed two different guidance paths. The `start_process` definition returned by the active Fortis MCP tool catalog in the 2026-11-04 session still contains the generic Windows/Linux-to-`/home/...` examples and Docker Installer `/home/[folder-name]` claim; this is direct confirmation that the inaccurate description remains exposed:

- `read_file` includes `PATH_GUIDANCE`: absolute-path advice and the mounted directories `/workspace/files`, `/workspace/repo`, and `/workspace/repos`. This is generated by `getPathGuidance(SYSTEM_INFO)` and matches the current `get_config.allowedDirectories`.
- `start_process` includes `OS_GUIDANCE`: it lists the same mounted directories but then appends generic Docker path-translation examples mapping Windows `C:\\projects\\data\\file.txt` and Linux `/Users/john/...` into `/home/...`, plus a claim that Desktop Commander Docker Installer mounts folders at `/home/[folder-name]`. That mapping is not valid for the observed Fortis workspace topology.

The source is now established:

- `server.js:8-10` builds `OS_GUIDANCE` and `PATH_GUIDANCE` once at process startup.
- `server.js:791-798` injects `OS_GUIDANCE` into `start_process`; `server.js:330-331` injects `PATH_GUIDANCE` into `read_file`.
- `utils/system-info.js:525-594` constructs OS guidance and hard-codes generic `/home` translation at lines 585-593.
- `utils/system-info.js:699-711` constructs path guidance and inserts the actual mountpoint list at line 708.
- The supplied screenshot's `Read` description is consistent with `read_file` and does not establish that `start_process` is corrected. The current tool schema confirms that `start_process` still has the generic `/home` block.
- `runtime/repo-mode/linux-tools.json` is generated by `probe.mjs`, not the source of live descriptions. The installed legacy wrapper still contains the historical `C:\\Users\\alexa` replacement text, but that exact claim is absent from the current connected schema. Current Repo1/Repo2 workers use the direct Desktop Commander entry point; the bridge is not in their observed process path.

The code-level source is established. On 2026-11-04, the owner approved a narrow correction. The installed target remains unmodified at `/opt/dc/node_modules/@wonderwhy-er/desktop-commander/dist/utils/system-info.js` in Desktop Commander `0.2.52`. A hash-pinned build-time patch candidate is now prepared under `fortis-container/patches/desktop-commander-0.2.52/`; its source-level tests pass against a disposable copy of the installed package. It is not deployed.

The source is established, but an in-place patch is blocked by both file permissions and the read-only container root filesystem:

- The target file and its parent directories are owned by `root:root`; the file mode is `0644`.
- The connected Desktop Commander process runs as `uid=1000(node)` with no effective Linux capabilities. The file is not writable by this process.
- `sudo` is not installed; `su` requires the root password. No privilege escalation was attempted.
- Direct `/proc/self/mountinfo` inspection shows the root overlay mounted `ro`; `findmnt -T` resolves the package file to `/` with read-only options. The owner-provided Docker inspect also reports `ReadonlyRootfs=true`. The package path is not a writable volume mount, so even `docker exec -u 0` cannot modify it in place.
- No active package file was changed.

The approved patch scope is deliberately narrow:

1. In the mounted-directories branch, preserve the runtime-generated mountpoint list and the advice to prefer those container paths. Remove the generic Windows/Linux-to-`/home/...` translation and replace it with a rule not to infer host-to-container mappings; verify the actual runtime mount configuration before translating a host path.
2. In the no-mounted-directories branch, remove the generic Docker Installer `/home/[folder-name]` claim and the generic remount advice. Do not assume a host path is mounted; require verification of the actual mount configuration.
3. Leave `getPathGuidance()` and the correct `read_file` description unchanged.

Restart is separately blocked by the current process topology. The connected configuration reports Desktop Commander PID `91`; procfs shows direct Desktop Commander Node processes at PIDs `91` and `105`, with stdio pipes and no visible parent process. Container PID 1 is `sleep infinity`; no in-container supervisor/restart command was identified. Killing either process could terminate an MCP connection without a demonstrated automatic restart path, so neither process was killed.

The patch candidate pins Desktop Commander `0.2.52` and the original `system-info.js` SHA-256, replaces only the two generic Docker path-guidance branches, verifies `getPathGuidance()` byte-for-byte unchanged, and tests both mounted-directory and no-mount behavior. The patched file SHA-256 is `128c7f8c29dab1dd95e277d7929bc6dc05ade62a00d0df8b345bf04d7929c2f1`.

A patch-only Dockerfile and `build-candidate.ps1` were prepared and run successfully by the owner on the Windows Docker Host. Candidate image: `fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104`; image ID: `sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750`. The runner's current-container/base-image preflight passed, the patch and source tests completed during the build, the base image ID remained unchanged, and the candidate's default user/command/entrypoint/workdir matched the base. The runner did not start, stop, restart or replace a container.

The running Repo container is shared by ChatGPT Repo1, Repo2 and the Qwen proxy path. A replacement will interrupt all client processes/connections, not only ChatGPT. Before cutover, capture a fresh secret-safe inspect of the full runtime config, confirm volume/network/security/port settings, and prepare rollback plus reconnect checks for all clients. At that pre-deployment point the candidate was built but not deployed; this status was superseded by the live deployment record above.
### Desktop Commander MCP UI visibility — deployed and live-verified (2026-11-04)

The UI shown as **View config · Desktop Commander** is the config-editor
MCP UI resource (`CONFIG_EDITOR_RESOURCE_URI`), not the old path-guidance text.
`server.js` attaches its UI metadata to `get_config` with
`buildUiToolMeta(CONFIG_EDITOR_RESOURCE_URI, true, showMcpUiPreviews)`; the
visibility decision is in `utils/mcp-ui-ab-test.js` under the
`McpUiPreviews` experiment. This is tool-catalog/resource presentation, not a
side effect of reading or editing repository files. The appearance after the
container cutover/reconnect is consistent with the client refreshing and
rendering the MCP tool metadata, but the available evidence does not establish
that file operations caused it.

**Current deployment: PASS.** The owner-run Windows cutover deployed
`fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104` as
`fortis-repo-test` (container ID
`1f67b67cacf3d4435982df9c0606dcb1a89d99f3f8ac73d365f3e6bb3d2f658b`). Both
Repo1 and Repo2 Guard Previews passed during cutover. After reconnect, this
ChatGPT Repo2 session confirmed `DESKTOP_COMMANDER_DISABLE_MCP_UI=1`, a false
`shouldShowMcpUiPreviews()` result, an empty UI resource list, and blocked
reads of both UI resource URIs. Repo1 post-cutover reconnect is owner-confirmed.
Qwen reconnect is not required for acceptance by owner decision. See the
[deployment record](../patches/desktop-commander-0.2.52-mcp-ui-headless/README.md)
and [dated audit](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md).

The repository contains a previously tested suppression method for the
separate Windows G2 runtime:
- `tunnel/runtime/host-g2/g2-stdio-gate.py` forces
  `DESKTOP_COMMANDER_DISABLE_MCP_UI=1` into the child environment.
- `tunnel/runtime/host-g2/README.md` records a G2 test with 0 UI metadata and
  0 UI resources on its Windows Desktop Commander 0.2.52 route.

The G2 switch is **proven on its tested Windows route**. The mounted
source contains the G2 stdio wrapper that forces
`DESKTOP_COMMANDER_DISABLE_MCP_UI=1`, and G2 acceptance records 26 tools,
zero UI metadata and zero UI resources. The G2-installed `server.js` /
`headless-mode.js` bytes are not archived in the mounted source repositories,
so the Docker implementation below preserves the proven environment contract
and behavior; it is not claimed to be a byte-for-byte port.

The active Docker package uses Desktop Commander 0.2.52 and the same
`index.js` SHA-256 as G2
(`a4145198dc75cd34e7c7452c2054b4cc0d29e199ae1459961a17e4da25a13500`).
The Docker `server.js` independently exposes UI metadata through
`shouldShowMcpUiPreviews()` and UI resources through an unconditional
`listUiResources()` handler. Setting an environment variable alone would
not have changed the unpatched Docker package.

### Docker behavior-compatible patch — implementation details (deployed)

The deployed patch source, Dockerfile and verification record are maintained under
[`patches/desktop-commander-0.2.52-mcp-ui-headless/`](../patches/desktop-commander-0.2.52-mcp-ui-headless/README.md).

- `utils/mcp-ui-ab-test.js`: when the exact environment value is `'1'`,
  `shouldShowMcpUiPreviews()` returns false before the remote A/B decision.
- `ui/resources.js`: the same switch makes `listUiResources()` return an
  empty list and `readUiResource()` refuse the two UI resource URIs.
- The deployed Docker image sets `ENV DESKTOP_COMMANDER_DISABLE_MCP_UI=1`.
  This image-level default is inherited by Repo1, Repo2 and other
  container-side Desktop Commander children, avoiding changes to either
  Windows launcher or the shared Guard.
- The existing `NODE_OPTIONS` quiet-log preload and the deployed
  `system-info.js` path-guidance patch remain unchanged.

At candidate stage, the patch was applied to a disposable package copy. Tests passed for metadata suppression, empty resource listing, blocked resource reads, normal behavior when the variable is unset or `0`, unchanged A/B show/hide logic, and preservation of the deployed path-guidance hash. The reviewed changes were then incorporated into the candidate image and deployed through the owner-approved cutover recorded below.

**Candidate build and pre-cutover runtime verification — owner-run Windows Docker Host, 2026-11-04 (historical):**

- Base image: `fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104`,
  ID `sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750`.
- Candidate: `fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104`,
  ID `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`.
- The owner-run builder reported: `PASS: MCP UI patch candidate built; only the reviewed environment default was added.`
- A disposable, network-isolated, read-only runtime test confirmed
  `DESKTOP_COMMANDER_DISABLE_MCP_UI=1`, `shouldShowMcpUiPreviews() === false`,
  an empty `listUiResources()` result, and null reads for both the config-editor
  and file-preview resource URIs. The test container used `--rm` and was
  automatically removed.
- The normalized Windows-host pre-cutover inspection passed all identity,
  environment, mount, network, security, resource, restart-policy and tmpfs
  assertions. The active container and existing rollback container were not
  modified. Initial false negatives in the first preflight were PowerShell
  comparison/null semantics and a `$home`/`$HOME` name collision; corrected
  checks passed. Full evidence is in the [dated verification audit](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md).

No Repo1/Repo2 launcher or Guard source edit is indicated. The canonical
`Invoke-FortisRepo.ps1` dispatcher and shared `FortisContainerPolicy.ps1`
resolve `fortis-repo-test` by name and pass its current inspected full ID
through the execution path; the shared policy validates effective mounts and
isolation rather than pinning the image digest. At the pre-cutover stage both
Guard Previews were still pending; the successful cutover subsequently passed
both canonical Guard Previews against the new container.

**Historical pre-cutover note — superseded:** before deployment, the active container was `fortis-repo-test` ID `3c4b50df90381ffd23809e0c7ba5e3bf8762ac33829ce2fb3a6d44a29da2d07c` on the path-guidance image. The owner-approved cutover has since promoted the MCP-UI-headless candidate and preserved the former path-guidance container under `fortis-repo-test-pre-mcp-ui-headless-20261104`. Current deployment and acceptance status is recorded above and in the [dated verification audit](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md).

**Cutover runner execution — PASS (2026-11-04):**
`tools/Invoke-FortisMcpUiHeadlessCutover.ps1` was copied to the Windows Docker
Host, passed its read-only Preview, then ran with the exact typed confirmation.
It preserved the prior path-guidance container as
`fortis-repo-test-pre-mcp-ui-headless-20261104`, promoted the candidate, ran
the guarded Repo2 tmpfs config bootstrap (no tunnel start), and passed the
live package check plus both canonical Guard Previews. The runner emitted
`DOCKER_CUTOVER_PASS`. See the [deployment record](../patches/desktop-commander-0.2.52-mcp-ui-headless/README.md)
and [dated verification audit](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md).

## Desktop Commander and Qwen

### Active Qwen route

The current Qwen route uses the original Desktop Commander 0.2.52 entrypoint in the existing Fortis Repo container:

`Qwen Studio → Windows uvx → mcp-proxy → loopback SSE → docker exec → Desktop Commander 0.2.52`

Owner-provided Windows process/log evidence identifies the `uvx` / `mcp-proxy` chain, a local SSE endpoint and a `docker exec` command that starts the original Desktop Commander entrypoint under UID/GID 1000. The route starts a separate Desktop Commander MCP process in the existing container; it does not create another container or use the Workfiles gateway as its active server.

**Evidence class: OWNER-REPORTED.** The transport and direct-entrypoint route were supplied by the owner; this documentation session did not independently inspect the Windows process tree. The detailed Qwen launch configuration remains Windows-side.

### Shared tool catalog — 26 tools

The current Fortis Repo Desktop Commander catalog exposes these 26 named tools. The owner-provided Qwen transcript also reports 26 tools and successful read, write, edit, move and process operations.

| Category | Tools | Count |
|---|---|---:|
| Files and directories | `read_file`, `read_multiple_files`, `write_file`, `write_pdf`, `create_directory`, `list_directory`, `move_file`, `get_file_info`, `edit_block` | 9 |
| Search | `start_search`, `get_more_search_results`, `stop_search`, `list_searches` | 4 |
| Processes | `start_process`, `read_process_output`, `interact_with_process`, `force_terminate`, `list_sessions`, `list_processes`, `kill_process` | 7 |
| Configuration, diagnostics and onboarding | `get_config`, `set_config_value`, `get_usage_stats`, `get_recent_tool_calls`, `give_feedback_to_desktop_commander`, `get_prompts` | 6 |
| **Total** | | **26** |

The tool names and count are confirmed from the current Fortis Repo MCP catalog. The Qwen transcript independently reports the same count and practical read/write/process use. A full archived JSON comparison of every Qwen and ChatGPT tool description and input schema is not available, so exact schema-by-schema identity is not claimed.

### Shared capability boundaries

- File operations use the Desktop Commander server's configured allowed directories. The current Fortis Repo workspace paths are documented in [Containers and volumes](CONTAINERS-AND-VOLUMES.md).
- File-tool directory restrictions are not a separate operating-system boundary and do not automatically constrain process execution.
- Process tools execute in the Linux Fortis Repo container, not on the Windows HOST.
- `read_file` supports URL reads when explicitly invoked with `isUrl=true`; availability also depends on the container's network path.
- `write_file`, `edit_block`, `move_file`, `create_directory` and `write_pdf` can modify workspace content. Process tools can start, interact with and terminate processes; `set_config_value` changes Desktop Commander configuration.
- Docker identity, mounts, filesystem mode, networks and resource limits are owned by [Containers and volumes](CONTAINERS-AND-VOLUMES.md), not duplicated here.

### Qwen Workfiles artifacts

`/workspace/files/Qwen-Fortis-MCP` is a retained Workfiles folder, not a separate Git repository. Its gateway files belong to earlier implementations:

- `gateway-stdio.mjs` — earlier six-tool read-only STDIO gateway; not the active Qwen entrypoint.
- `gateway.mjs` — predecessor HTTP gateway.
- `test-gateway.cjs` — local acceptance test for the earlier six-tool gateway, not a test of the current direct Desktop Commander route.
- The PowerShell Start/Stop scripts target the earlier gateway design; they are not the active Qwen proxy lifecycle controls.
- `package.json` records dependencies for the earlier gateway implementation, not the Windows `uvx` proxy environment.

Keep these artifacts in place for provenance. Do not use the legacy scripts to start or stop the current Qwen connection. The Qwen-specific README is maintained at `/workspace/files/Qwen-Fortis-MCP/README.md`; this document remains the cross-client source of truth for the tool catalog and capability boundaries.

## Shared files and concurrent work

ChatGPT Repo1, Repo2 and Qwen are separate client paths into the same Fortis Repo container and workspace. Their MCP server processes use the same Desktop Commander package/version and Linux UID/GID 1000, but they are not one shared MCP process. Actual access is determined by the process identity, Desktop Commander configuration and container-level controls; a file-tool allowlist is not a substitute for OS/container enforcement.

No automatic file-level synchronization exists between Docker checkouts and the separate Windows Git clones. The documented Tunnel / Script Center delivery path is Git commits followed by the Windows Preview/Apply workflow.
