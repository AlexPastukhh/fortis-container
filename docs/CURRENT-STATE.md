# Fortis current state

**Baseline date:** 2026-11-03; follow-up evidence added through 2026-11-04
**Scope:** current Fortis Repo MCP process, accessible workspace, repository working trees, source documentation, Qwen candidate test and owner-provided container build/inspect evidence.

## Evidence summary

| Area | Status | Finding |
|---|---|---|
| Current MCP process | LIVE VERIFIED | Linux Docker environment, UID/GID 1000, Desktop Commander 0.2.52, Node 22.23.3; current `start_process` tool metadata still contains the generic `/home/...` host-path guidance |
| Workspace mounts | LIVE VERIFIED | Three paths resolve to subpaths of one ext4 volume and are mounted read-write |
| Docker Engine inspection | OWNER-REPORTED | Windows-host `docker inspect` output was supplied for `fortis-repo-test`; image, rootfs, security settings and volume subpaths are recorded in [container build provenance](CONTAINER-BUILD-PROVENANCE.md) and [containers and volumes](CONTAINERS-AND-VOLUMES.md) |
| Image/build provenance | OWNER-PROVIDED + HASH VERIFIED | Original Windows Dockerfile/build log located; SHA-256 matches Tunnel's legacy copy; build-log image digest matches the inspected image ID; exact build context/command remain unknown |
| Tunnel checkout | LIVE VERIFIED | `main`, HEAD `8172026`, 11 modified tracked files and 2 untracked task files; no commit/push |
| Script Control Center | LIVE VERIFIED | `main`, HEAD `8fc2731`, 2 modified (unstaged) files and 44 untracked files; second worktree exists |
| RDG checkout | LIVE VERIFIED | `main`, HEAD `176ce44`, 58 modified/staged entries, 325 untracked files and 1 deletion |
| Fortis Approvals source | LIVE VERIFIED / OWNER APPROVED | Extracted package is canonical development source in a separate local Git repo on `main`; original RDG subtree remains untouched |
| Fortis Approvals Gateway | OWNER-REPORTED | Current-state and live E2E evidence describe one deployed Gateway and one Sonar project; R7/P1/P2 are retained only in historical artifact identifiers |
| Repo client-auth volume | LIVE VERIFIED | `/run/fortis-client` is `fortis-r7-client`, mounted RO; grant metadata UID 1000/mode 0600; contents not read |
| Qwen proxy transport | OWNER-REPORTED | Windows `mcp-proxy` log shows loopback SSE and `docker exec` into the existing Repo container |
| Qwen gateway source | LIVE VERIFIED | Pinned hash matches supplied proxy log; source exposes six read-only tools; local acceptance test passed |
| Qwen tool surface in chat | OWNER-REPORTED / TRANSCRIPT-BACKED | The supplied Qwen chat transcript records 26 tools and successful read/write/edit/move/process calls; the exact source path is not reconciled with the separately pinned six-tool gateway |

## Current Fortis Repo process

The connected Desktop Commander configuration reports:
- Linux Docker environment, user `node`, UID/GID 1000.
- Desktop Commander version 0.2.52.
- Node.js 22.23.3 at `/usr/local/bin/node`.
- Allowed directories: `/workspace/repos`, `/workspace/files`, `/workspace/repo`.
- Runtime/container name prefix reported as `04fed7b726a8`.

The current process has no `docker` executable and cannot inspect Docker Engine from inside the container. The owner subsequently supplied separate Windows-host `docker inspect` output for the exact container; those host-side findings are OWNER-REPORTED, not independently executed by this MCP session. See [Container build provenance](CONTAINER-BUILD-PROVENANCE.md) for the image ID, security settings, mounts and the remaining build-provenance gaps. Do not treat the tool's container name prefix alone as a complete Docker inspection.

## Workspace mounts

Read-only inspection of `/proc/self/mountinfo` and `findmnt` showed:
- `/workspace/repo` → ext4 volume root `/data/docker/volumes/fortis-repo-workspace/_data`, RW.
- `/workspace/repos` → subpath `.../_data/Repos`, RW.
- `/workspace/files` → subpath `.../_data/Workfiles`, RW.

The path aliases `/workspace/repo/Repos` and `/workspace/repos` have the same device/inode. The aliases `/workspace/repo/Workfiles` and `/workspace/files` also have the same device/inode. These are not Windows bind mounts in the current process; they are subpaths of the same ext4 workspace volume.

A separate read-only mount at `/run/fortis-client` was also confirmed by `findmnt` as the `fortis-r7-client` ext4 volume. Metadata-only inspection found `grant` and `server.crt`; the grant is UID 1000/mode 0600 and the public certificate UID 1000/mode 0644. The grant contents were not read. The `get_config` mountPoints summary listed the three workspace paths but omitted this client mount, so it is not a complete mount inventory.

## Git working trees

- `tunnel`: one worktree, branch `main`, HEAD `81720265017787a587a338c8e9c0fd6e203fba89`; currently 11 modified tracked files and 2 untracked files from this documentation/MCP-guidance task; no commit or push.
- `script-control-center`: main worktree plus `script-control-center-filequarantine-launch` worktree on `feature/filequarantine-script-center-launch-20261103`; both at HEAD `8fc2731`. Main has 2 modified (unstaged) files and 44 untracked files.
- `rd-graphs`: one worktree, branch `main`, HEAD `176ce44c820757ecfb827ea881c0cac6613c8831`; 58 modified/staged entries, 325 untracked files and one deletion.
- `fortis-container` was created as the cross-project documentation repository and now has local Git metadata on `main`; no commit or remote exists.
- `fortis-approvals` was extracted from the RDG subtree, accepted by the owner as the canonical development source, and initialized as a local Git repository on `main`; no commit or remote exists. The original RDG subtree remains untouched.

Do not clean, reset, stash, overwrite, commit or push these existing working trees as part of documentation work.

## Fortis Approvals

The original source and documentation inside `rd-graphs/fortis_approvals/` describe Fortis Approvals Gateway, the typed Repo client, machine ingress, Owner Portal/WebAuthn and Sonar adapters.

The original subtree contains 293 files in total across package root, deploy, tests, static assets and archive. Git tracks zero files in this subtree; 196 files appear as untracked and 97 are generated Python cache/bytecode. The broader RDG tree is also dirty. The owner-approved canonical development source exists at `/workspace/repos/fortis-approvals/fortis_approvals`: 196 non-generated package files, initially matched against the original SHA-256 manifest. The original RDG source remains untouched. Four package files in the extracted copy have since changed only for historical-doc pointer/test alignment and README naming/documentation; `docs/SOURCE-MANIFEST.sha256` preserves the original extraction hashes and `docs/CURRENT-SOURCE-MANIFEST.sha256` records the current copy.

The extracted source is owner-approved as the canonical development source and now has local Git metadata on `main`; it has no commit or remote. Its selected offline/static regression report records 198 passing tests across 26 suites. Five additional suites cannot import because `cryptography` is missing; `test_sonar.py` has 21/22 passing with one WebAuthn test blocked by missing `fido2`. The running Repo Python environment has no pip module, and no dependencies were installed.

The preserved Approval Gateway Compose reference and live E2E documents are owner-provided evidence. Docker CLI is unavailable here, so this session did not independently verify the running Fortis Approvals Gateway container or its volumes.

## Qwen

The container-side STDIO gateway passed its local six-tool read-only acceptance test. Its current SHA-256 (`a6f32603304f4163b55364744e5da1f08d4530fefd6d96e45360a3217a71b1c2`) matches the pin in the owner-provided Windows proxy log. The source allowlist exposes only six read/search tools and rejects other tool calls.

Owner-provided Windows output shows an `mcp-proxy` process, a loopback SSE listener at `127.0.0.1:18765`, established local connections, and a `docker exec` command launching this gateway as UID/GID 1000 in the existing Repo container. This is transport evidence; it is not a fresh Windows inspection.

The owner-provided Qwen chat transcript records 26 tools and successful directory listing, read, create, write, edit, move, process execution, process-output and cleanup calls. This is practical evidence of write/process capability in the tested Qwen chat. The exact pinned six-tool read-only gateway source cannot have served those calls in that exact form, so its relationship to the active Qwen tool path remains a source-provenance question. This does not block the first documentation stage and does not require repeating the functional test. The old PowerShell launcher scripts still target the HTTP design and are not the proxy path shown in the supplied logs.

## Known gaps

1. The target-name Compose candidate exists, but the Docker-host inventory and rendered dry run remain pending. Exact live Approval container/project labels and volume attachments require a Windows-host read-only inspect; no runtime resource has been renamed.
2. Qwen source provenance remains not fully reconciled: the active chat's 26-tool/read/write/process transcript and the separate six-tool gateway source do not describe the same tool surface. This is non-blocking for the first documentation stage; the legacy PowerShell scripts still target the HTTP design.
3. The GitHub credential store has both a current shared helper file and a legacy credential file still referenced by some local Git configs. Credential isolation is a later-stage item; no credential changes are part of this stage.
4. Key Tunnel architecture/access/isolation and dated G2/G3 mount snapshots now carry explicit historical warnings. Remaining dated evidence/plan files are retained as historical records; do not use their old mount statements as current topology.
5. **Per-tool ChatGPT MCP descriptions are visible in the Fortis Repo app UI; `start_process` still contains an inaccurate generic path mapping.** The supplied screenshot shows `Read` with the current mounted directories `/workspace/files`, `/workspace/repo`, and `/workspace/repos`. Current metadata confirms `read_file` receives correct dynamic `PATH_GUIDANCE`; `start_process` receives `OS_GUIDANCE` with generic Windows/Linux-to-`/home/...` translation and a `/home/[folder-name]` installer claim. Source is verified: `server.js:791-798` attaches `OS_GUIDANCE` to `start_process`; installed `system-info.js:585-593` generates the incorrect mapping; `system-info.js:699-711` generates the correct mounted-path guidance used by `read_file`. The owner approved a narrow correction on 2026-11-04, but it is not deployed: the package file is root-owned (`0644`), this MCP process runs as UID 1000 without capabilities, `sudo` is absent and `su` requires the root password. The active package was not changed. The current process topology has no identified in-container supervisor, so the MCP process was not killed. Root-level package deployment followed by reconnecting only the ChatGPT Fortis Repo MCP and checking both descriptions remains outstanding.
