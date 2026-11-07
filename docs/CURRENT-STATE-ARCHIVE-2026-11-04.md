# Historical current-state snapshot — 2026-11-04

> Archived reference only. This is not a live status dashboard or the active plan. Planned work is maintained in [Future improvements](FUTURE-IMPROVEMENTS.md); inspect the exact live runtime or Git target before acting.

**Baseline date:** 2026-11-03; follow-up evidence added through 2026-11-04
**Scope:** current Fortis Repo MCP process, accessible workspace, repository working trees, source documentation, Qwen candidate test, owner-provided container build/inspect evidence, the Windows Docker Host inventory / Compose render, Repo1/Repo2 GO3 Guard verification, and the 2026-11-04 MCP-UI-headless cutover plus live Repo2 runtime acceptance.

## Evidence summary

| Area | Status | Finding |
|---|---|---|
| Current MCP process | LIVE VERIFIED | Linux Docker environment, UID/GID 1000, Desktop Commander 0.2.52, Node 22.23.3; deployed `system-info.js` patch hash matches, and live `start_process` guidance now uses actual mounted paths without generic `/home` translation |
| Workspace mounts | LIVE VERIFIED | Three paths resolve to subpaths of one ext4 volume and are mounted read-write |
| Docker Engine inspection | OWNER-REPORTED / OUTPUT REVIEWED | Windows-host read-only inventory supplied 2026-11-04: 9 Fortis-named containers (3 running, 6 exited), 14 volumes, 7 networks and 14 images; container labels, image IDs, ports and mounts reviewed. Both Compose renders exited 0. Docker `running` is not application-health evidence. Details: [containers and volumes](CONTAINERS-AND-VOLUMES.md) and [follow-up audit](audits/FOLLOW-UP-2026-11-03.md). |
| Repo1/Repo2 Guards and path-guidance release | OWNER-REPORTED + LIVE MCP VERIFIED | The path-guidance image remains the base of the active MCP-UI-headless image. Both Guard Previews passed during the latest cutover; Repo2 is reconnected and its corrected `start_process` guidance remains live. Repo1's corrected description and post-headless-cutover reconnect are owner-confirmed. Details: [path-guidance patch record](../patches/desktop-commander-0.2.52/README.md). |
| Desktop Commander MCP UI suppression | OWNER-REPORTED CUTOVER + LIVE REPO2 RUNTIME VERIFIED + REPO1 OWNER-CONFIRMED | MCP-UI-headless image deployed to `fortis-repo-test`; cutover and both Guard Previews passed. Repo2 live runtime confirms `DESKTOP_COMMANDER_DISABLE_MCP_UI=1`, false preview decision, empty UI resource list and blocked reads. Repo1 post-cutover reconnect is owner-confirmed. Qwen reconnect is not required for acceptance by owner decision. Details: [deployment record](../patches/desktop-commander-0.2.52-mcp-ui-headless/README.md) and [dated audit](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md). |
| Image/build provenance | OWNER-PROVIDED + HASH VERIFIED | Original Windows Dockerfile/build log located; SHA-256 matches Tunnel's legacy copy; build-log image digest matches the inspected image ID; exact build context/command remain unknown |
| Tunnel checkout | LIVE VERIFIED | `main`, HEAD `8172026`, 11 modified tracked files and 2 untracked task files; no commit/push |
| Script Control Center | LIVE VERIFIED | `main`, HEAD `8fc2731`, 2 modified (unstaged) files and 44 untracked files; second worktree exists |
| RDG checkout | LIVE VERIFIED | `main`, HEAD `176ce44`, 58 modified/staged entries, 325 untracked files and 1 deletion |
| Fortis Approvals source | LIVE VERIFIED / OWNER APPROVED | Extracted package is canonical development source in a separate local Git repo on `main`; original RDG subtree remains untouched |
| Fortis Approvals runtime | OWNER-REPORTED / OUTPUT REVIEWED | Windows inspect shows G2 and G4 owner containers `running` in separate Compose projects on loopback ports 18990 and 18991; the R7 P1-named container is `exited` despite its P2 image tag and P2 Compose-config label. Application health, owner intent and which deployment is authoritative remain UNKNOWN; current source docs classify G2/G4 as historical, so documentation conflicts with host state. |
| Repo client-auth volume | LIVE VERIFIED | `/run/fortis-client` is `fortis-r7-client`, mounted RO; grant metadata UID 1000/mode 0600; contents not read |
| AI isolation audit | READ-ONLY AUDIT COMPLETE | Four credential files are readable by UID 1000; workspace mounts are shared RW; Docker socket/CLI absent in this container; host gateway and default route exist. Full findings and limits: [AI isolation audit](audits/AI-CONTAINER-ISOLATION-2026-11-04.md). |
| Qwen proxy transport | OWNER-REPORTED | Windows `mcp-proxy` log shows loopback SSE and `docker exec` into the existing Repo container |
| Qwen gateway source | LIVE VERIFIED | Pinned hash matches supplied proxy log; source exposes six read-only tools; local acceptance test passed |
| Qwen tool surface in chat | OWNER-REPORTED / TRANSCRIPT-BACKED | The supplied Qwen chat transcript records 26 tools and successful read/write/edit/move/process calls; the exact source path is not reconciled with the separately pinned six-tool gateway |

## Current Fortis Repo process

The connected Desktop Commander configuration reports:
- Linux Docker environment, user `node`, UID/GID 1000.
- Desktop Commander version 0.2.52.
- Node.js 22.23.3 at `/usr/local/bin/node`.
- Allowed directories: `/workspace/repos`, `/workspace/files`, `/workspace/repo`.
- Runtime/container name prefix reported as `1f67b67cacf3` (post-MCP-UI-headless cutover).

The current process has no `docker` executable and cannot inspect Docker Engine from inside the container. The owner subsequently supplied Windows-host `docker inspect` and GO3 verifier output for the exact container; those host-side findings are OWNER-REPORTED, not independently executed by this MCP session. See [Container build provenance](CONTAINER-BUILD-PROVENANCE.md) and [Containers and volumes](CONTAINERS-AND-VOLUMES.md) for image identity, security settings, resource values and mount evidence. Do not treat the tool's container name prefix alone as a complete Docker inspection.

## Desktop Commander path-guidance deployment — 2026-11-04 (historical base image; superseded as active container by MCP-UI-headless)

**Status: COMPLETE for the path-guidance correction and Repo1/Repo2 tool
description acceptance.** This does not close the broader A1 tool-isolation
backlog. Qwen reconnect is not required for acceptance by owner decision;
the separate Qwen source-provenance question remains documented as a
non-blocking observation.

- Pre-UI active container: `fortis-repo-test`, full ID
  `3c4b50df90381ffd23809e0c7ba5e3bf8762ac33829ce2fb3a6d44a29da2d07c`.
- Base image for the current MCP-UI-headless deployment:
  `fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104`,
  ID `sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750`.
- Installed `system-info.js` SHA-256:
  `128c7f8c29dab1dd95e277d7929bc6dc05ade62a00d0df8b345bf04d7929c2f1`.
- Rollback container:
  `fortis-repo-test-pre-path-guidance-20261104`, old ID
  `04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030`;
  it remains stopped and preserved.

The owner-run replacement reported Docker configuration, installed package
version/hash and both Repo1/Repo2 Guard Preview PASS. A separate owner-run
read-only verification emitted `FINAL_DOCKER_VERIFICATION_PASS`; all 12
assertions were true, covering running state, exact candidate image, preserved
stopped rollback container, read-only rootfs, non-privileged mode,
`CapDrop=ALL`, `no-new-privileges`, no host binds, no `VolumesFrom`, both
expected networks and reviewed resource limits.

After reconnect, this ChatGPT Repo2 session directly confirmed the new
container hostname prefix, Desktop Commander 0.2.52, UID/GID 1000, the three
allowed workspace paths and the deployed patch hash. The live `start_process`
description now lists the real mounted paths and forbids guessed host-path
translation; generic `/home` translation and Docker Installer claims are
absent. The owner separately confirmed that Repo1 also exposes the corrected
description. The path-guidance deployment item is closed.

The shared Guard source and canonical nine-file Tunnel manifest were not
changed. No volumes were deleted. Repo1 post-cutover reconnect is owner-confirmed;
Qwen reconnect is not required for acceptance by owner decision. The separate
Qwen source-provenance observation remains non-blocking. See the
[patch deployment record](../patches/desktop-commander-0.2.52/README.md).

## Desktop Commander MCP UI suppression — deployed and live-verified — 2026-11-04

**Status: DEPLOYED; cutover PASS; live Repo2 runtime acceptance PASS.** This is separate from the completed path-guidance correction above. The owner supplied the successful Windows-host cutover output, then reconnected Fortis Repo in this ChatGPT account; the current session independently read the new MCP configuration and exercised the live runtime.

- Active container: `fortis-repo-test`, full ID `1f67b67cacf3d4435982df9c0606dcb1a89d99f3f8ac73d365f3e6bb3d2f658b`.
- Active image: `fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104`, ID `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`.
- Rollback container: `fortis-repo-test-pre-mcp-ui-headless-20261104` (preserves the prior path-guidance container). The older `fortis-repo-test-pre-path-guidance-20261104` rollback remains a separate historical image/container.
- Owner-run cutover output: `GUARDED_RUNTIME_CONFIG_REPAIR_PASS`, `REPO1_GUARD_PREVIEW_PASS`, `REPO2_GUARD_PREVIEW_PASS`, `DOCKER_CUTOVER_PASS`. The runner reported that no named volume was deleted and no Windows profile or tunnel lifecycle action was requested.
- Live `get_config` after reconnect reports Desktop Commander `0.2.52`, MCP client `openai-mcp 1.0.0`, Linux Docker, Node.js `22.23.3`, UID/GID `1000`, and allowed workspace paths `/workspace/repo`, `/workspace/repos`, `/workspace/files`. The reported container hostname prefix is `1f67b67cacf3`.
- Live `start_process` confirmed `DESKTOP_COMMANDER_DISABLE_MCP_UI=1`. A direct runtime probe passed: `shouldShowMcpUiPreviews()` is `false`; `listUiResources()` returns `[]`; reads of both `CONFIG_EDITOR_RESOURCE_URI` and `FILE_PREVIEW_RESOURCE_URI` return `null`.
- The MCP experiment metadata still reports the `showMCPUi` A/B variant at 100% in `get_config`; this is not the effective UI decision. The explicit environment opt-out takes precedence, and the live runtime returns `false` with no UI resources.
- Repo1 and Repo2 Guard Previews passed during cutover. This ChatGPT Repo2 connection subsequently reconnected and passed the live runtime checks above. Repo1 post-cutover reconnect is owner-confirmed. Qwen reconnect is not an acceptance gate by owner decision; no Qwen reconnect confirmation is required to close this deployment item.

The [deployment record](../patches/desktop-commander-0.2.52-mcp-ui-headless/README.md) contains the implementation and cutover procedure. The [dated audit](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md) preserves candidate/preflight evidence, the cutover result and post-cutover runtime checks.

### Pre-cutover candidate verification (historical; superseded by the deployment above)

The following candidate identity, build, disposable-runtime and normalized preflight details describe the state before the successful cutover. They are retained as historical evidence; they are not the current deployment status.

- Active production container remains `fortis-repo-test`, ID
  `3c4b50df90381ffd23809e0c7ba5e3bf8762ac33829ce2fb3a6d44a29da2d07c`, on
  path-guidance image ID `sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750`.
- Candidate image:
  `fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104`, ID
  `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`.
  Its base is the deployed path-guidance image above.
- The previous pre-path-guidance rollback remains stopped and preserved as
  `fortis-repo-test-pre-path-guidance-20261104`, ID
  `04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030`.
  It is not a rollback of the current path-guidance deployment. A future UI
  cutover must separately preserve the current active path-guidance container
  under a new rollback name before replacing the service name.

The owner-run candidate build reported that only the reviewed image-level
`DESKTOP_COMMANDER_DISABLE_MCP_UI=1` default was added. A disposable
`docker run --rm --network none --read-only --user 1000:1000` runtime test
passed: the environment value was present, `shouldShowMcpUiPreviews()` returned
false, `listUiResources()` returned an empty list, and reads of both the config
editor and file-preview UI resource URIs returned null. The disposable test
container was automatically removed.

The owner then ran a normalized, read-only Windows-host pre-cutover check.
All assertions passed: active/base/candidate/rollback identities; active
container running and rollback stopped; no missing or extra base environment
entries; candidate UI default and runtime defaults; read-only rootfs,
non-privileged mode, `CapDrop=ALL`, `no-new-privileges`; no host binds,
`VolumesFrom` or published ports; all four named-volume mounts and both
networks; network mode; memory/swap/CPU/PID/shared-memory limits; restart
policy; and both tmpfs definitions. Earlier false negatives were caused by
PowerShell array/null handling and the case-insensitive `$home`/`$HOME`
variable collision; corrected normalized checks passed. No production
container, image or volume was changed by the preflight.

The canonical `Invoke-FortisRepo.ps1` dispatcher and shared
`FortisContainerPolicy.ps1` resolve the container by the stable name
`fortis-repo-test` and pass the inspected full ID to the Repo execution path;
the active policy validates effective mounts and isolation rather than pinning
an exact image digest. No Repo1/Repo2 Guard source edit was indicated for this image-only environment default. At the pre-cutover stage, both Guard Previews and client reconnect checks were still outstanding. The subsequent cutover passed both Guard Previews, and Repo2 later reconnected and passed live MCP UI runtime verification; see the deployed-status section above. Repo1 post-cutover reconnect and Qwen reconnect remain separate checks.

At the pre-cutover stage, the typed-confirmation Windows runner at `tools/Invoke-FortisMcpUiHeadlessCutover.ps1` had a read-only Preview action and a Cutover action that staged the candidate from inspected Config/HostConfig, preserved the path-guidance container as rollback, checked the live package and both canonical Guard Previews, and attempted automatic rollback on failure. It also invoked the hash-verified Repo2 Direct Guard's narrowly scoped runtime-config bootstrap for the fresh `/home/node` tmpfs (no tunnel start). The owner subsequently executed this runner successfully on the Windows Docker Host; the cutover and live Repo2 acceptance are recorded above and in the [MCP UI deployment audit](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md) and [deployment record](../patches/desktop-commander-0.2.52-mcp-ui-headless/README.md).

## Pre-deployment Repo1/Repo2 Windows Guard baseline — 2026-11-04

> Historical pre-cutover evidence against the former base image and container.
> The deployment status above is authoritative for the current runtime.

The owner copied `script-control-center/_go3-revision07/Invoke-GO3-Guard-Previews.ps1` from the active container with `docker cp` and ran it on Windows. The supplied console output confirms:

- `fortis-repo-test` is running with full ID `04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030` and image `fortis-repo-mode:dc-0.2.52` / ID `sha256:2c84fabebb34265e53b020f21a11683a4c68cbb41a08f5f11f9b01c7de5ed8c9`.
- The canonical Tunnel nine-file source manifest passed its fingerprint and per-file checks.
- The image identity/configuration gate passed.
- Repo1 Guard Preview and Repo2 Direct Guard Preview both returned `Preflight=PASS` against the same full container and image IDs. Both reported Linux UID 1000 and the expected Linux security probe/direct entry checks.
- Repo1 reported zero existing tunnels and one existing profile. This is an inventory result, not a start test.
- The script emitted `NO_TUNNEL_START_OR_STOP`, `NO_WINDOWS_PROFILE_EDITS`, `NO_RUNTIME_CONFIG_REPAIR`, and `NO_SONAR_REQUEST`; no runtime lifecycle action occurred.

The first run's auxiliary mount formatter was incorrect (wrong inspect property names), so its printed mount rows remain discarded. The owner completed a second read-only Windows run on 2026-11-04; the corrected formatter now reports all four mounts by volume name, destination, read/write flag, mode, driver and propagation, without exposing host source paths. The second run emitted `GO3_RELEASE_VERIFICATION_PASS`. It ends with `REPO_RECONNECT_PENDING`; no tunnel start/stop, Windows profile edit, runtime repair or Sonar request occurred. Full output and mount values are recorded in the [GO3 baseline audit](audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md).

**GO3 status:** current-base-image identity and both launch Guards' Preview gates are **PASS**. Actual Repo1/Repo2 tunnel start and a separate reconnect/functional acceptance are **PENDING**. The path-guidance candidate image is separate: it is built but not deployed. This Guard verification does not test that candidate or validate the corrected ChatGPT tool description.

The older untracked `script-control-center/_go3-revision06` cutover/resume/rollback scripts pin former container ID `0c0f8cb2...`, not the currently verified `04fed7b7...`; do not run them against the current host without a new review. Full evidence and the next steps are in [Repo container / Shared Guard baseline](audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md).

## Pre-deployment Fortis Repo MCP read-only smoke — 2026-11-04

The currently exposed `Fortis_Repo` MCP tool endpoint was exercised from this ChatGPT session without changing files or runtime state. `get_config` reported Desktop Commander `0.2.52`, client `openai-mcp` `1.0.0`, Linux container hint `04fed7b726a8`, and UID/GID 1000 (`node`). A read-only `start_process` check completed with exit code 0 and emitted `READ_ONLY_SMOKE_PASS`.

- `/workspace/repos/tunnel/runtime/windows-repo/current/source-manifest.json` and its alias `/workspace/repo/Repos/tunnel/runtime/windows-repo/current/source-manifest.json` both returned SHA-256 `8036348f69bb37f94f5e6fde529bf44a292f4eb91977ce91a491e9860aadbfca`.
- `/workspace/files/Qwen-Fortis-MCP/README.md` and its alias `/workspace/repo/Workfiles/Qwen-Fortis-MCP/README.md` both returned SHA-256 `bf24172fb750966e382980e2c060fb3d87b91aa20618052952e1f81c1cf15c4d`.
- Direct MCP file reads succeeded through both canonical workspace paths and aliases; the shell check confirmed `uid=1000(node) gid=1000(node)`, working directory `/workspace/repos`, and container hostname prefix `04fed7b726a8`.

**Scope limit:** this proves that the currently exposed Fortis Repo MCP endpoint and these workspace aliases respond. The tool metadata does not identify this endpoint as the Windows Repo1 or Repo2 tunnel profile, so this smoke test is **not** a Repo1/Repo2 reconnect acceptance. The GO3 Windows result remains `REPO_RECONNECT_PENDING`; Repo1's latest Preview inventory still reports zero recognized tunnel listeners and one process matching the `repo-mode` profile pattern. Identify that process on Windows before any Start/Stop action. The `get_config` `mountPoints` summary is not Docker Engine mount evidence and was not used for this test.

## Workspace mounts

Read-only inspection of `/proc/self/mountinfo` and `findmnt` showed:
- `/workspace/repo` → ext4 volume root `/data/docker/volumes/fortis-repo-workspace/_data`, RW.
- `/workspace/repos` → subpath `.../_data/Repos`, RW.
- `/workspace/files` → subpath `.../_data/Workfiles`, RW.

The path aliases `/workspace/repo/Repos` and `/workspace/repos` have the same device/inode. The aliases `/workspace/repo/Workfiles` and `/workspace/files` also have the same device/inode. These are not Windows bind mounts in the current process; they are subpaths of the same ext4 workspace volume.

The current Desktop Commander `get_config` system summary labels the three workspace paths as `type=bind` and reports `/dev/sdd` as `hostPath`. This is not Docker Engine mount metadata: direct `/proc/self/mountinfo` identifies ext4 mounts rooted under `/data/docker/volumes/fortis-repo-workspace`, and the owner-provided Windows `docker inspect` output identifies the Engine mounts as `Type=volume`. Do not use the `get_config` summary to determine Docker Engine mount type or as a complete mount inventory.

A separate read-only mount at `/run/fortis-client` was also confirmed by `findmnt` as the `fortis-r7-client` ext4 volume. Metadata-only inspection found `grant` and `server.crt`; the grant is UID 1000/mode 0600 and the public certificate UID 1000/mode 0644. The grant contents were not read. The second owner-run GO3 diagnostic independently reported the four Docker volume attachments: `fortis-r7-client` RO at `/run/fortis-client`, and `fortis-repo-workspace` RW at `/workspace/files`, `/workspace/repo` and `/workspace/repos`. The `get_config` mountPoints summary listed only the three workspace paths and remains incomplete.

## Pre-deployment Repo1 Windows follow-up — 2026-11-04 (owner-provided output)

The owner ran the canonical `Invoke-FortisRepo.ps1 -Repo Repo1 -Action Preview` and `control.ps1 -Action Status` on Windows. Guard Preview returned `Preflight=PASS`, `ConfigState=Pinned`, Linux UID 1000, Linux security verified, direct entry available, and quiet preload probe PASS. Docker Status confirmed `fortis-repo-test` running with the currently verified full container ID `04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030`, root read-only, no host bind mounts, no published ports, and the expected four volume attachments (client volume RO; shared workspace volume RW at its three paths).

The same Windows read-only inventory found exactly one `repo-mode` profile process: PID `22556`, `tunnel-client-runtime.exe`, parent PID `25644`, owner `FORTIS_M\alexa`, created `2026-11-04 06:44:14`, executable `C:\Tools\tunnel-client\runtime\v0.0.15\tunnel-client-runtime.exe`. It has no listening TCP sockets. `control.ps1 -Action Status` found no recognized Repo tunnel listener. The parent chain had already been established by the earlier owner-provided read-only inventory: PID `22556` → PowerShell PID `25644` (`Repo1-Worker.ps1`) → PID `25036` (`Script-Runner.ps1`) → PID `29268` (`Start-ScriptCatalog.ps1`) → PID `27232` (`explorer.exe`). Therefore repeating ancestry discovery is unnecessary.

The canonical Repo1 launcher calls `Assert-FortisTunnelRuntime` before Preview; that function verifies both the expected runtime executable path and its SHA-256 against the shared policy pin. Since Repo1 Preview passed, a separate Authenticode/signature check is not required for this diagnosis. `control.ps1` recognizes a healthy Repo1 tunnel only through a loopback listening socket whose `/metrics` contains the pinned Repo ID. Thus `LISTENERS=NONE` explains the empty `tunnel` array, but does not by itself establish whether the runtime has an outbound TCP connection.

**Why Start/Restart are currently blocked:** `run-tunnel-quiet-logs.ps1 -Mode Run` refuses to launch if any `repo-mode` profile process already exists. Its `-RestartRepo1` path requires exactly one recognized tunnel and exactly one profile process before it will stop anything. Current counts are `ExistingTunnelCount=0`, `ExistingProfileCount=1`, so neither a duplicate start nor the guarded restart path can proceed. This is an intentional fail-closed guard, not evidence that the Guard needs editing.

**Interpretation / safety:** container identity and Repo1 Guard Preview pass, but Repo1 is not proven connected. The known process ancestry rules out the need to rediscover its parent; the remaining uncertainty is why the supervised runtime process has no recognized loopback health listener. All TCP connection states and the runtime diagnostic log have not yet been inspected. No Windows runtime lifecycle action was performed in this follow-up.

## Git working trees

The Tunnel and RDG status entries below remain the last recorded snapshot from the earlier audit. Script Center and `fortis-container` were rechecked read-only on 2026-11-04 after the GO3 verifier/documentation edits.

- `tunnel`: branch `main`, HEAD `81720265017787a587a338c8e9c0fd6e203fba89`; the earlier audit recorded 11 modified tracked files and 2 untracked task files. This continuation did not edit Tunnel source or its nine-file Guard manifest.
- `script-control-center`: branch `main`, HEAD `8fc2731b02c82d4332a87957c27a1bac5dab9304`, tracking `origin/main`. Two tracked files are modified (`README.md`, `docs/GIT-WINDOWS-SOURCE-OF-TRUTH.md`); `_go3-revision06/`, `_go3-revision07/`, `test_go3_release_verification.py` and `windows-installed-sources/` are untracked. No commit or push.
- `rd-graphs`: last recorded snapshot: branch `main`, HEAD `176ce44c820757ecfb827ea881c0cac6613c8831`; 58 modified/staged entries, 325 untracked files and one deletion. Not re-inspected in this continuation.
- `fortis-container`: branch `main`, HEAD `47e1761188e1267da64a6764bbf29a6de9ad50e6`; `origin` remote is configured, but `main` has no upstream tracking branch. Eleven tracked documentation files are modified; the GO3 audit and `patches/` are untracked. No staged changes, commit or push.
- `fortis-approvals`: earlier owner-approved extraction from the RDG subtree remains the canonical development source, initialized as a local Git repository on `main`; no commit or remote exists. Not re-inspected in this continuation; the original RDG subtree remains untouched.

Do not clean, reset, stash, overwrite, commit or push these existing working trees as part of documentation work.

### Worktree layout rollout audit — 2026-11-04

Read-only inventory of the top-level Docker project directories was repeated for the new `Repos` / `Worktrees` convention. The `/workspace/repo/Repos` and `/workspace/repos` paths are aliases, so the inventory was deduplicated by repository identity.

- `/workspace/repo/Worktrees/` now exists as an empty reserved directory in the persistent workspace volume. No new task Worktree was created and no existing linked Worktree was moved.
- The `FileQuarantine` primary checkout is on `main`. Its three existing linked Worktrees remain at the legacy paths `Repos/FileQuarantine-download-filename`, `Repos/FileQuarantine-host-monitoring-h1` and `Repos/FileQuarantine-lab-dev`; their feature branches and working changes were not altered.
- The `script-control-center` primary checkout is on `main`. Its existing linked Worktree `Repos/script-control-center-filequarantine-launch` remains in place; it was not moved.
- `visual-workspace` is a standalone primary checkout on `work/initial-visual-workspace-20261101`, clean and tracking the corresponding origin branch. `origin/main` exists, but no local `main` branch is checked out. This checkout is the repository's documented Fortis Repo / Blender development environment. It was deliberately not switched during this documentation-only stage; it is a known exception to the new primary-on-`main` convention until a separate, reviewed migration preserves its active development context.
- All other inspected top-level primary clones were on `main` at the time of this read-only inventory. Existing linked Worktrees are not primary clones and should not be treated as branch-policy violations merely because their branches are feature branches.
- The current Mirror GUI's `АКТУАЛЕН · НЕ MAIN` label is conditional: it appears only when the active Docker and Windows branches match and Docker, GitHub and Windows SHAs are equal with a clean Windows tree. It is not an unconditional warning for every non-main primary checkout. A persistent primary-default-branch warning is documented as future Mirror work; the application code was not changed.

No branch, index, working tree, Git ref or Worktree registration was changed during this audit.

## Fortis Approvals

The original source and documentation inside `rd-graphs/fortis_approvals/` describe Fortis Approvals Gateway, the typed Repo client, machine ingress, Owner Portal/WebAuthn and Sonar adapters.

The original subtree contains 293 files in total across package root, deploy, tests, static assets and archive. Git tracks zero files in this subtree; 196 files appear as untracked and 97 are generated Python cache/bytecode. The broader RDG tree is also dirty. The owner-approved canonical development source exists at `/workspace/repos/fortis-approvals/fortis_approvals`: 196 non-generated package files, initially matched against the original SHA-256 manifest. The original RDG source remains untouched. Four package files in the extracted copy have since changed only for historical-doc pointer/test alignment and README naming/documentation; `docs/SOURCE-MANIFEST.sha256` preserves the original extraction hashes and `docs/CURRENT-SOURCE-MANIFEST.sha256` records the current copy.

The extracted source is owner-approved as the canonical development source and now has local Git metadata on `main`; it has no commit or remote. Its selected offline/static regression report records 198 passing tests across 26 suites. Five additional suites cannot import because `cryptography` is missing; `test_sonar.py` has 21/22 passing with one WebAuthn test blocked by missing `fido2`. The running Repo Python environment has no pip module, and no dependencies were installed.

The preserved Approval Gateway Compose reference and the 2026-11-04 live E2E evidence now establish that the Repo typed client can reach the Gateway service path and complete Sonar READ/ASK/Reject/Approve. Docker CLI is unavailable here, so this session still cannot independently identify the exact post-start Windows Gateway container, Compose labels, image or attached server volumes. A fresh host-side read-only inspect is the remaining identity check.

## Windows Docker Host inventory — 2026-11-04

**Evidence status: OWNER-REPORTED / OUTPUT REVIEWED.** The owner ran the read-only PowerShell inventory on Windows Docker Host and supplied its console output. Docker Engine and Compose versions were 29.8.0 and 5.5.1. The filter returned 9 Fortis-named containers: 3 `running` and 6 `exited`; the inventory also listed 14 Fortis-related volumes, 7 networks and 14 images.

- Running: `fortis-repo-test`, `fortis-approvals-g2-owner-1` (project `fortis-approvals-g2`, service `owner`, loopback port 18990), and `fortis-approvals-g4-owner-1` (project `fortis-approvals-g4`, service `owner`, loopback port 18991).
- Exited: `fortis-r7-p1-fortis-1`, `fortis-a3-synthetic-fortis-1`, `fortis-observatory-api`, and three historical Repo rollback / pre-migration containers.
- The R7-named container has project label `fortis-r7-p1` and service `fortis`, but its image tag is the P2 candidate and its Compose config-file label points to `compose-r7-p2-20261103.yaml`. Its state is `exited`; no published ports appear in inspect output.
- G2 and G4 are separate running Compose projects. Their runtime status conflicts with the source deployment index, which labels them historical-only. `docker inspect` status does not establish application health, intended owner role, or production authority.
- The target Compose candidate rendered successfully, but its target image and target external volumes are absent from the listed host resources. No target `fortis-approvals` project/container was found. Render-only success is not deployment evidence.

See [Containers and volumes](CONTAINERS-AND-VOLUMES.md), [Archived naming decision record](NAMING-AND-RENAME-PLAN-ARCHIVE-2026-11-04.md), and the [follow-up audit](audits/FOLLOW-UP-2026-11-03.md). No Docker resource was changed.

## Fortis Approvals live functional revalidation — 2026-11-04

After the earlier inventory, the owner started a Gateway container. The existing Repo typed client then completed fresh live E2E against the pinned SonarCloud project: 1 project visible; 275 Issues total (100 returned on page 1, `hasMore=true`); Quality Gate `OK` on `CURRENT_DEFAULT_BRANCH`; PR/SHA binding remains `NOT_VERIFIED_D2`.

- Reject request `2b3580dc-6a88-4f44-a1e6-9a7097c84b0c` for Issue `AaGC4d9TJxEkuf26a_ZX`: status readback `REJECTED`; independent Sonar GET remained `OPEN`.
- Approve request `2db54607-f0c3-4f43-9597-f73f54ea46af` for Issue `AaGC4d9TJxEkuf26a_ZY`: owner WebAuthn confirmation; status readback `EXECUTED`; independent Sonar GET returned `ACCEPTED`.

This closes Stage 4's **functional** Approval acceptance gate for the single-actor Sonar pilot. Stage 3 (the approved `start_process` MCP-description correction) remains the next priority and is not deployed. Stage 5 (Approval Gateway Docker naming/rename) remains PLANNED; do not start it until a fresh post-start Windows `docker inspect` reconciles the active Gateway container/project/image/volume identity. These Stage 3/4/5 labels belong to the separate Approval Gateway roadmap; they are not the Repo container GO3 Guard-verification stages above. This E2E does not prove multi-agent isolation, new scan dispatch, PR/SHA binding, backup/restore or full production hardening. Full evidence: `/workspace/repos/fortis-approvals/fortis_approvals/evidence/FORTIS-SONAR-LIVE-E2E-20261104.md`.

## Qwen

The container-side STDIO gateway passed its local six-tool read-only acceptance test. Its current SHA-256 (`a6f32603304f4163b55364744e5da1f08d4530fefd6d96e45360a3217a71b1c2`) matches the pin in the owner-provided Windows proxy log. The source allowlist exposes only six read/search tools and rejects other tool calls.

Owner-provided Windows output shows an `mcp-proxy` process, a loopback SSE listener at `127.0.0.1:18765`, established local connections, and a `docker exec` command launching this gateway as UID/GID 1000 in the existing Repo container. This is transport evidence; it is not a fresh Windows inspection.

The owner-provided Qwen chat transcript records 26 tools and successful directory listing, read, create, write, edit, move, process execution, process-output and cleanup calls. This is practical evidence of write/process capability in the tested Qwen chat. The exact pinned six-tool read-only gateway source cannot have served those calls in that exact form, so its relationship to the active Qwen tool path remains a source-provenance question. This does not block the first documentation stage and does not require repeating the functional test. The old PowerShell launcher scripts still target the HTTP design and are not the proxy path shown in the supplied logs.

## Known gaps

1. The Windows Docker-host inventory and both `docker compose config` renders completed on 2026-11-04. After the pre-start inventory, the owner started a Gateway container and fresh live E2E passed through the fixed endpoint (READ, ASK, Reject and WebAuthn Approve). The pre-start inventory's R7-exited / G2-G4-running picture is now stale for runtime status; a post-start `docker inspect` is still required to identify the exact active container/project/image/volumes. The target image and target external volumes were absent from the earlier inventory, so render success still does not establish rename-candidate deployability. No runtime resource has been renamed.
2. Qwen source provenance remains not fully reconciled: the active chat's 26-tool/read/write/process transcript and the separate six-tool gateway source do not describe the same tool surface. This is a non-blocking provenance observation; Qwen reconnect is not required for acceptance by owner decision. Repo1 post-cutover reconnect is owner-confirmed. The legacy PowerShell scripts still target the HTTP design.
3. The GitHub credential store has both a current shared helper file and a legacy credential file still referenced by some local Git configs. Credential isolation is a later-stage item; no credential changes are part of this stage.
4. Key Tunnel architecture/access/isolation and dated G2/G3 mount snapshots now carry explicit historical warnings. Remaining dated evidence/plan files are retained as historical records; do not use their old mount statements as current topology.



## Windows Repo Mode source review — 2026-11-04

A selected owner-provided Windows source export was reviewed at content level; details are in [Container build provenance](CONTAINER-BUILD-PROVENANCE.md), section 14.

- The Windows-root bridge matches the installed legacy wrapper but still claims the current workspace paths are Windows bind mounts. It is not in the canonical Repo1/Repo2 worker path.
- The Windows-root probe.mjs encodes the old bind-mount model and mutates Desktop Commander settings, Git global config and verification files; it is not a read-only diagnostic.
- The Windows-root run-tunnel.ps1 self-labels as an uninstalled PR-A-15 candidate pinned to 0c0f8cb2..., an exited rollback container; installation was not independently checked. It cannot pass the identity gate against the owner-reported running container 04fed7b7...; it was not executed. The omitted workspace-config.json hash matches an archived example pinned to the exited before-isolation container c6d7be9f... and old Windows bind-mount mappings (provenance section 14.9); if byte identity holds, probe.mjs fails its initial ID assertion and control.ps1 StopContainer fails closed.
- The unique bridge-before-worktree-guidance.mjs is the exact predecessor of the current Windows-root bridge before two worktree-safety sentences were added.
- Hash-matched validation scripts are historical, not current runbooks: check-controls.ps1 is a mocked legacy unit test; check-presentation.mjs is a mutating integration test and does not verify ChatGPT UI; check-schemas.mjs compares a generated historical snapshot, not live MCP metadata. None was run.
- The source export omitted the Windows workspace-config.json bytes and verification/access/mount JSON plus diagnostic logs. Its hash matches a Tunnel example pinned to an exited pre-isolation container; this is a qualified inference, not a direct Windows-file read. The three check scripts and expected-schemas.json were reviewed through hash-matched Tunnel copies; the remaining verification/access/mount JSON and logs remain unreviewed. Do not execute or import the Windows-root scripts on this evidence.
- Read-only Fortis Repo reconnect succeeded during this review (openai-mcp, Desktop Commander 0.2.52, allowed directories /workspace/repos, /workspace/files, /workspace/repo). No runtime configuration was changed.


## MCP UI headless cutover runner — pre-cutover Preview diagnostics (historical; deployment subsequently passed)

The owner ran the Windows-host runner in read-only Preview mode. Its first
attempt exposed a PowerShell 5.1 false negative for Docker `CapAdd=null`; the
runner was corrected to ignore null entries while continuing to reject every
non-null capability addition. The second Preview passed that check and exposed
a separate false negative: an empty JSON `PortBindings: {}` object was counted
as a scalar. The runner now inspects object keys explicitly, accepting only
null/empty port-binding representations and rejecting actual port keys or
unexpected types. Local parser, null/empty/non-empty behavior tests and
`git diff --check` passed. At the time of these Preview diagnostics, the corrected runner had not yet been recopied to Windows and production cutover had not yet run; these were read-only attempts and did not modify a live container, rollback, network or volume. The owner subsequently completed the cutover successfully; see the [MCP UI deployment audit](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md).
