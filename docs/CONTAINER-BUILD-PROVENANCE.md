# Fortis Repo container build provenance

> **Status:** source and build evidence consolidated on 2026-11-04. This is a forensic record, not a deployment recipe. It does not authorize rebuilding, replacing, restarting or renaming any live Docker resource.

## Purpose

Record where the Fortis Repo image came from, what its Dockerfile installs, which source copies exist, what the supplied build log proves, and what remains unknown. Read this before repeating the original build/source investigation.

Evidence labels:
- **OWNER-PROVIDED** — output pasted from the Windows Docker host by the owner.
- **SOURCE VERIFIED** — read from a file through the Fortis Repo MCP connection.
- **HASH VERIFIED** — SHA-256 calculated in the current Fortis Repo environment and matched to the owner-provided value.
- **INFERENCE** — a conclusion supported by multiple records but not directly printed by one command.
- **UNKNOWN** — not established by the evidence currently retained.

## 1. Original Windows source directory

Owner-provided directory: `C:\Users\alexa\chatgpt-repo-mode`.

The supplied listing contains:
- `Dockerfile`, `build.log`, `WORKSPACE.md`;
- `linux-tools.json`, `fortis-mcp-bridge.mjs`, `probe.mjs`, verification/configuration JSON files;
- PowerShell control and Tunnel launcher scripts;
- a `backups/` directory with dated access, documentation-centralization, initializer and startup snapshots;
- many `runtime-diag-*.jsonl` diagnostic logs.

The directory has **no Git metadata**. It is not currently a version-controlled canonical source repository.

The listing made with `Get-ChildItem -Force` did not show a `.dockerignore`, while the supplied BuildKit log says it loaded a `.dockerignore` of 2 bytes. This discrepancy is unresolved; do not assume the currently listed directory is byte-for-byte the original build context.

Do not bulk-copy the directory into Git. Diagnostic logs, backups, access/configuration records and runtime artifacts need separate classification and possible secret review first.

## 2. Dockerfile contents and image recipe

The owner-provided Windows Dockerfile has SHA-256:

`1717E364B2F5CD92F4C6CABB039D4272598FE573B5E6CD9CFE7357A0ABD4FA0B`

Its instructions establish this recipe:

1. Base: `node:22-bookworm-slim`.
2. Environment: `MCP_CLIENT_DOCKER=true`, `HOME=/home/node`, `NODE_ENV=production`.
3. Install OS packages: `bash`, `git`, `python3`, `ca-certificates`, `ripgrep`.
4. Create `/opt/dc` and `/workspace/repo`; make the workspace root owned by `node`.
5. Set working directory to `/opt/dc`.
6. Install `@wonderwhy-er/desktop-commander@0.2.52` with production/no-audit/no-fund/ignore-scripts options, then rebuild `@vscode/ripgrep`.
7. Run as UID/GID `1000:1000`.
8. Set working directory to `/workspace/repo`.
9. Default command: `sleep infinity`.

The build log resolves the base image to digest `sha256:c3de60bf2f9dd0ac6370e6117950ff62d6e339527e7472301c9c78a017978392`. The Dockerfile itself uses the mutable tag `node:22-bookworm-slim`, not a digest-pinned `FROM`; the digest is recorded by that historical build log. A later rebuild must not assume the tag still resolves to the same base image.

The Dockerfile contains no `COPY` or `ADD` instruction. The recorded image history likewise shows the base image, OS packages, directory/ownership setup, npm installation and workdir/command layers; it does not show project source copied into the image. Desktop Commander is installed from npm during image build, rather than built from the local Tunnel or Fortis Container checkout.

## 3. Build log and image identity

The owner-provided `build.log` records BuildKit using the `desktop-linux` builder with the Docker driver. It records loading `Dockerfile`, loading a 2-byte `.dockerignore`, resolving the base image, installing dependencies, and exporting the image.

Recorded output:
- image tag: `fortis-repo-mode:dc-0.2.52`;
- exported image manifest digest: `sha256:2a9c226bf54ad6a28000edd431795cc5baadc2d7f4f1e1453473369d8691727a`;
- exported image config digest: `sha256:26bacee23190a82822ebbb07abbb34c15ffbfb6ea8a8f78da8f64106bd49b6f6`;
- attestation manifest digest: `sha256:eae27e1b44b43f2867eaffc1642f9b69a94002af00b73444823a2b65903944fe`;
- exported manifest-list digest: `sha256:2c84fabebb34265e53b020f21a11683a4c68cbb41a08f5f11f9b01c7de5ed8c9`;
- npm reported 619 packages added; `@vscode/ripgrep` rebuild completed successfully;
- build completed successfully, despite deprecation warnings emitted by npm.

The install command uses `--no-audit`, so the successful build does not establish that an npm vulnerability audit was run. The deprecation warnings are recorded build output; they are not, by themselves, a vulnerability assessment.

The owner-provided Docker image inspection returned image ID `sha256:2c84fabebb34265e53b020f21a11683a4c68cbb41a08f5f11f9b01c7de5ed8c9` and creation time `2026-10-10T06:46:21.953363197Z`. **The image ID exactly matches the manifest-list digest printed by the supplied build log.** This ties the retained build log to the inspected image identity.

The build log does not record the exact original `docker build` invocation, absolute build-context path or the contents of `.dockerignore`; it does record the resulting image tag. The path `C:\Users\alexa\chatgpt-repo-mode` is a strong candidate source directory because it contains the matching Dockerfile and build log, but the build-context path is not proven by the log.

Do not infer that a current rebuild from that directory will be identical: the base tag may resolve differently now, npm dependency resolution may differ, and the original context/.dockerignore are not fully preserved in the evidence shown here.

## 4. Relationship to Tunnel and Fortis Container

The Dockerfile in the existing Tunnel checkout at `/workspace/repos/tunnel/runtime/repo-mode/Dockerfile` was hashed through Fortis Repo MCP. Its SHA-256 is exactly the same as the Windows Dockerfile hash above (**HASH VERIFIED**).

The adjacent Tunnel `runtime/repo-mode/README.md` explicitly labels that directory **Legacy Repo Mode reference / historical, not current topology**. It also states that:
- `linux-tools.json` is generated probe output, not the source of live MCP tool descriptions;
- `fortis-mcp-bridge.mjs` is a legacy wrapper, not the active Repo1/Repo2 worker path;
- the old example workspace configuration must not be treated as current runtime configuration.

Therefore, the matching Tunnel Dockerfile is a preserved identical copy, but the surrounding directory is not evidence that the current container is built from the Tunnel checkout.

The `fortis-container` repository is the central documentation project and has its first documentation-baseline commit (`2119ccb`) on `main`; an `origin` remote is now configured. No Dockerfile or complete, canonical build context has yet been added to it. This document does not maintain a live branch/upstream/working-tree dashboard; inspect Git directly before any repository operation. The future location for reviewed, version-controlled container build sources should be decided here before files are moved or copied.

## 5. Owner-provided pre-cutover container inspection (historical)

The following is based on Docker output pasted by the owner, not a new Docker Engine inspection from inside this MCP session.

Container:
- name: `fortis-repo-test`;
- ID: `04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030`;
- image: `fortis-repo-mode:dc-0.2.52`;
- image ID: the digest recorded in section 3;
- user: `1000:1000`;
- working directory: `/workspace/repos`;
- command: `sleep infinity`;
- read-only root filesystem: `true`;
- privileged: `false`;
- dropped capabilities: `ALL`;
- security option: `no-new-privileges`;
- network mode: `fortis-repo-egress`;
- restart policy: `unless-stopped`.

Owner-provided mount inspection:
| Volume | Container destination | Mode / subpath |
|---|---|---|
| `fortis-repo-workspace` | `/workspace/repo` | volume root, RW |
| `fortis-repo-workspace` | `/workspace/repos` | subpath `Repos`, RW |
| `fortis-repo-workspace` | `/workspace/files` | subpath `Workfiles`, RW |
| `fortis-r7-client` | `/run/fortis-client` | RO |

The three workspace paths are one persistent volume with aliases/subpaths, not separate Windows bind mounts. The client-auth volume is separate and read-only. Earlier metadata-only inspection found `grant` and `server.crt` there; the grant contents were not read.

**Later owner-side validation (2026-11-04):** two GO3 release-verifier runs against this exact container confirmed the base image identity and both Repo1/Repo2 Guard Previews. The second run also validated the corrected four-entry mount diagnostic, and reconfirmed Memory 4 GiB, MemorySwap 5 GiB, 2 CPUs, 512 PIDs, ShmSize 64 MiB, restart policy, tmpfs options, two network attachments and zero published ports. The first version of the auxiliary mount formatter was wrong; do not use that initial output for mount destinations. The corrected output and evidence classification are in [Repo container / Shared Guard baseline](audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md).

## 6. MCP tool-description correction and deployment

### Current deployed state — 2026-11-04

The Desktop Commander 0.2.52 path-guidance patch is deployed in container
`fortis-repo-test` (full ID
`3c4b50df90381ffd23809e0c7ba5e3bf8762ac33829ce2fb3a6d44a29da2d07c`) using
image `fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104` (ID
`sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750`).
The live patched `system-info.js` hash is
`128c7f8c29dab1dd95e277d7929bc6dc05ade62a00d0df8b345bf04d7929c2f1`.

After reconnect, the Repo2 MCP catalog in this ChatGPT account directly
confirmed that `start_process` now uses the actual mounted paths and no
longer contains the generic `/home` translation or Docker Installer claim.
The live package hash was also verified. The owner confirmed Repo1 shows the
corrected description. Both Guard Previews passed during cutover, and the
owner's post-cutover read-only Docker check returned
`FINAL_DOCKER_VERIFICATION_PASS` (12/12 assertions). The former container
`04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030` remains
stopped under rollback name
`fortis-repo-test-pre-path-guidance-20261104`.

The detailed implementation and verification record is
[here](../patches/desktop-commander-0.2.52/README.md). The original full
Dockerfile build-context and `.dockerignore` provenance questions below
remain open; the narrow derivative deployment does not resolve them.

### Pre-deployment investigation (historical; superseded above)

The pre-deployment Fortis MCP tool metadata still included the generic
Windows/Linux-to-`/home/...` host-path translation and Docker Installer
`/home/[folder-name]` claim in the `start_process` description. The
`read_file` description instead listed the actual mounted container paths.

The source investigation recorded in [AI integrations](AI-INTEGRATIONS.md) identifies the installed Desktop Commander 0.2.52 package as the source of the incorrect `OS_GUIDANCE` block. The intended correction is narrow: remove generic host-path translation assumptions while retaining runtime-derived mount guidance.

The installed package file is root-owned and the connected MCP process runs as UID 1000 without write permission. Direct `/proc/self/mountinfo` / `findmnt` inspection also shows that the package resides on the read-only root overlay; the owner-provided Docker inspect reports `ReadonlyRootfs=true`. Even a root `docker exec` cannot edit the package in place. A hash-pinned patch candidate is prepared at `patches/desktop-commander-0.2.52/`. It targets only the two generic Docker path-guidance branches, pins Desktop Commander 0.2.52 and the reviewed original file SHA-256, and verifies `getPathGuidance()` remains byte-for-byte unchanged. Source tests pass for mounted-directory and no-mount branches. The owner successfully built the patch-only derivative image on the Windows Docker Host: `fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104`, ID `sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750`. The base container/image preflight and post-build base-image identity checks passed; the patch tests ran during build; default runtime user/command/entrypoint/workdir matched the base. No container was started, stopped, restarted or replaced. The active package and live tool metadata remain unchanged.

The current container is shared by ChatGPT Repo1, Repo2 and Qwen. A replacement interrupts all client processes/connections, not only ChatGPT. The GO3 owner-run snapshot is the current baseline; immediately before any candidate cutover, refresh the secret-safe inspect, confirm no drift, and prepare rollback/reconnect checks for all clients.

## 7. Remaining unknowns and safe next steps

Still unknown:
- exact original `docker build` command and absolute build-context path;
- original `.dockerignore` contents and why it is absent from the supplied current directory listing;
- whether any backup contains a later or alternative Dockerfile that was actually used;
- whether the diagnostic/configuration artifacts contain sensitive data (their contents have not been reviewed here).

Before making the full container build reproducible:
1. Preserve this record as the research baseline.
2. Review the original directory and backups without copying diagnostic logs or secrets into Git.
3. Recover the original build command/context and `.dockerignore`, if available.
4. Agree which reviewed files become canonical under `fortis-container`.
5. Only then prepare a reproducible full build definition.

For the narrow `OS_GUIDANCE` correction, the patch-only derivative described in
`patches/desktop-commander-0.2.52/` has now been built, deployed and live
verified. Its deployment does not resolve the original full build-context /
`.dockerignore` provenance gaps; those remain separate research items.

No Docker build, pull, restart, recreation, volume change, source relocation, Git commit or push was performed for this documentation update. For manual-versus-automated verification boundaries, see [Validation policy](VALIDATION-POLICY.md).

## Appendix: Additional details from the original directory and host inspection

PowerShell reported these UTC file timestamps:
- `Dockerfile`: created/modified 2026-10-10 05:57:07Z;
- `build.log`: created 2026-10-10 05:57:07Z, modified 2026-10-10 06:47:19Z;
- `WORKSPACE.md`: created 2026-10-10 11:30:00Z, modified 2026-10-10 12:26:05Z.

The listed backup directories are:
`access-20261010T111644398Z`, `access-20261010T111717413Z`, `access-20261010T111828502Z`, `access-20261010T112024336Z`, `access-20261010T112331268Z`, `docs-centralization-20261010`, `retired-initializer-20261011`, and `startup-saved-key-20261010T115550Z`. Their file-count inventory and selected source-file hash/content review are recorded in sections 10–14. This was a selective review, not a complete review of every backup file; verification/access/mount JSON and runtime diagnostic logs remain unreviewed.

The supplied `WORKSPACE.md` output appears garbled under the PowerShell display encoding. Its visible links point to Tunnel's `docs/CURRENT_STATE.md`, `README.md` and `history/repo-mode/WORKSPACE.md`; it says documentation should be updated in the Tunnel Windows clone and that the previous text was preserved while applications/scripts were not moved. Treat it as a historical pointer. The actual file encoding/content should be checked as UTF-8 before any edit; the pasted display alone does not prove that the file bytes are corrupt.

The owner-provided inspect also reported tmpfs mounts:
- `/home/node`: RW, `nosuid,nodev,noexec`, UID/GID 1000, mode 0700, size 128 MiB;
- `/tmp`: RW, `nosuid,nodev,noexec`, mode 1777, size 128 MiB.

These are part of the supplied runtime snapshot, not a rebuild instruction.


## 9. Backup audit access boundary — 2026-11-04

The original Windows directory `C:\Users\alexa\chatgpt-repo-mode` and its `backups/` subtree are not present at the corresponding checked paths under `/workspace/repo`, `/workspace/repos` or `/workspace/files` in the current MCP container. The eight backup directory names supplied by the owner (`access-*`, `docs-centralization-20261010`, `retired-initializer-20261011`, `startup-saved-key-20261010T115550Z`) were also not found in those mounted trees during a bounded directory-name search.

This is consistent with the owner-provided Docker inspection: the container receives named-volume mounts for the Fortis workspace, not a bind mount of `C:\Users\alexa\chatgpt-repo-mode`. The presence of other unrelated backup directories under mounted workspaces does not make them copies of this original source backup set; their contents were not inspected.

**Result at the time of this initial access check:** no backup file contents had been read and no backup files had been changed. The owner subsequently completed the Windows inventory and supplied selected source content for review; the later results are recorded in sections 10–14. That review was selective, not a complete audit of every backup or diagnostic file. Do not copy the full backup tree into Git.


## 10. Windows backup inventory — partial result, 2026-11-04

The owner ran a read-only PowerShell inventory against `C:\Users\alexa\chatgpt-repo-mode\backups`. The top-level directory enumeration succeeded and confirmed these eight snapshots:

| Snapshot | Created UTC | Last written UTC |
|---|---|---|
| `access-20261010T111644398Z` | 2026-10-10 11:16:44 | 2026-10-10 11:16:44 |
| `access-20261010T111717413Z` | 2026-10-10 11:17:17 | 2026-10-10 11:17:26 |
| `access-20261010T111828502Z` | 2026-10-10 11:18:28 | 2026-10-10 11:18:55 |
| `access-20261010T112024336Z` | 2026-10-10 11:20:24 | 2026-10-10 11:20:52 |
| `access-20261010T112331268Z` | 2026-10-10 11:23:31 | 2026-10-10 11:30:00 |
| `docs-centralization-20261010` | 2026-10-10 12:23:07 | 2026-10-10 12:30:43 |
| `retired-initializer-20261011` | 2026-10-11 03:12:25 | 2026-10-11 03:12:25 |
| `startup-saved-key-20261010T115550Z` | 2026-10-10 11:55:50 | 2026-10-10 11:55:50 |

Two PowerShell `foreach { ... } | Format-Table` statements then failed to parse with `EmptyPipeElement`. Consequently, the per-snapshot file counts/byte totals, recursive candidate file list and backup-file SHA-256 values were **not** produced. The subsequent current-source checks did execute:

- Current Windows `Dockerfile`: SHA-256 `1717E364B2F5CD92F4C6CABB039D4272598FE573B5E6CD9CFE7357A0ABD4FA0B`. This exactly matches the hash already recorded for the owner-provided Dockerfile and the Tunnel historical copy.
- Current Windows `build.log`: SHA-256 `D73DECE36147A2DA79E4C5B6FA0D8622D8F903B2E84BA9A8E52997CB24EEBBA1` (newly recorded; no backup copy has yet been hashed for comparison).
- Current root `.dockerignore`: not found. The historical BuildKit log says it loaded a 2-byte `.dockerignore`; this discrepancy remains unresolved and the original build context is still not proven.

No backup file contents were read or changed. No files were copied, moved, deleted or edited on the Windows host. A corrected read-only inventory is still required to establish snapshot contents and compare historical Dockerfile/build-log copies.


## 11. Complete Windows backup inventory — 2026-11-04

The corrected read-only PowerShell inventory completed successfully. It enumerated 85 files across the eight snapshot directories (the first access snapshot is empty). Snapshot counts and rounded sizes:

| Snapshot | Files | Total |
|---|---:|---:|
| `access-20261010T111644398Z` | 0 | 0 MB |
| `access-20261010T111717413Z` | 9 | 0.03 MB |
| `access-20261010T111828502Z` | 9 | 0.03 MB |
| `access-20261010T112024336Z` | 9 | 0.03 MB |
| `access-20261010T112331268Z` | 9 | 0.03 MB |
| `docs-centralization-20261010` | 46 | 0.31 MB |
| `retired-initializer-20261011` | 1 | 0 MB |
| `startup-saved-key-20261010T115550Z` | 2 | 0 MB |

### Build-related files and hashes

- The only file matching the backup inventory's Dockerfile pattern is `docs-centralization-20261010/originals/runtime/repo-mode/Dockerfile`.
- Its SHA-256 is `1717E364B2F5CD92F4C6CABB039D4272598FE573B5E6CD9CFE7357A0ABD4FA0B`, exactly matching the current Windows Dockerfile and the Tunnel historical copy.
- No `build.log`, `.dockerignore`, Compose YAML or other Dockerfile candidate was found in the eight backup snapshots under the inventory patterns.
- This establishes that the scanned backup set contains one matching archived Dockerfile, not which directory was used as the original Docker build context. The original 2-byte `.dockerignore` discrepancy remains unresolved.

### Source and documentation candidates found

The four non-empty `access-*` snapshots contain repeated copies of these launcher/bridge/probe files: `check-controls.ps1`, `check-presentation.mjs`, `configure-tunnel.ps1`, `control.ps1`, `fortis-mcp-bridge.mjs`, `probe.mjs`, and `run-tunnel.ps1`. The final access snapshot additionally contains `bridge-before-worktree-guidance.mjs`. The displayed sizes and modification timestamps match across repeated copies, but hashes were not computed for these files; byte identity is therefore not established.

The `docs-centralization-20261010` snapshot contains archived documentation under `originals/history/`, host launcher files under `originals/runtime/host/`, and a preserved Repo Mode source/documentation set under `originals/runtime/repo-mode/`. That Repo Mode set includes the single Dockerfile above, `fortis-mcp-bridge.mjs`, `probe.mjs`, PowerShell launch/control scripts, schema files and `workspace-config.example.json`. These are archived originals under a backup directory, not a current active build context.

The remaining snapshots contain one `configure-tunnel.ps1` in `retired-initializer-20261011` and one `run-tunnel.ps1` in `startup-saved-key-20261010T115550Z`; the other file in the latter snapshot was outside the candidate-name filter.

### What this does and does not establish

- The backup inventory is complete at the directory/file-count level for the eight snapshots, and the relevant candidate filenames/sizes/timestamps were listed.
- At the time of this inventory, only the archived Dockerfile had been hashed. Selected bridge, launcher, probe and historical helper files were later hash/content-reviewed in sections 12–14; the omitted verification/access/mount JSON and runtime diagnostic logs remain unreviewed.
- The backup contents were not modified, copied into a repository, or deleted.
- Do not import the whole backup tree into Git. The selected source/documentation files were subsequently reviewed, but any future import still requires separate owner approval and secret screening of the relevant configuration/access artifacts.


## 12. Current Tunnel Repo Mode hash baseline — 2026-11-04

Read-only SHA-256 values from the current checkout at `/workspace/repos/tunnel/runtime/repo-mode`. These are comparison anchors for the Windows backup files; they do not prove that the backup copies are identical until their own hashes are collected.

| File | SHA-256 |
|---|---|
| `Dockerfile` | `1717e364b2f5cd92f4c6cabb039d4272598fe573b5e6cd9cfe7357a0abd4fa0b` |
| `Fortis-Repo-Control.cmd` | `bb1d002bde31aae23e9f882e2ac343122ada0dd36c0cba3743867b5453c95389` |
| `check-controls.ps1` | `20eae01d8ed89d5352203b93e67ab012a158d5104ed7419a7510bbd53edcf869` |
| `check-presentation.mjs` | `a1f2176170863bb01cc67d1eae5eeef266fcbd9fe4d2c80703b5db8ce31ace9f` |
| `check-schemas.mjs` | `5d6a589bb749b6c498657aff445b2c77f9af10fa6815edbd0e3002dddd7ebcc2` |
| `control.ps1` | `e80e209b4758b194d2bcc7dcafdfb83d296289e29a543f192e6726538641ae34` |
| `expected-schemas.json` | `db4dc0e7d0811a93994a1f8e208daac6dfdb6a4d32cf115f31ed7077ad3249ef` |
| `fortis-mcp-bridge.mjs` | `863fd54cf49995adc94d9b5d41b00f36d8872d89d32d1864c0ce4fe405caefca` |
| `probe.mjs` | `f300ef82966ac0b12a981143d3f8ae4062f129699ab6c6e3234a790c2b747105` |
| `run-tunnel.ps1` | `3877266c3c97becc82045be16d994981eb4f8973353b285236df9caac158a5a3` |
| `workspace-config.example.json` | `6e153483baf9021a74353cca3443d33ad0d38a949e3ec8488eeb9a85fa2515fc` |

`configure-tunnel.ps1` and `bridge-before-worktree-guidance.mjs` were not present in the current `runtime/repo-mode` directory. Their backup copies remain historical candidates pending content/hash review. No source file was changed by this hash collection.


## 13. Windows backup-to-current-source hash comparison — 2026-11-04

The owner supplied SHA-256 results for selected files in all eight Windows backup snapshots and selected files in the current Windows source directory. These are compared with the current Tunnel baseline in section 12. Hash equality establishes byte identity; inequality establishes only that file bytes differ, not which version is correct.

### 13.1 Repeated access snapshots

The four non-empty access snapshots contain the same seven files with identical hashes in every snapshot:

| File | SHA-256 |
|---|---|
| `check-controls.ps1` | `3e970da1cac2e9981ebc637e2d01d342f7bc175c8fc0ecd34679f2aa84e589a9` |
| `check-presentation.mjs` | `b3282d678ec13f2ec5046417e4e949fc399bb075f669de6a5f03fd5570299ce7` |
| `configure-tunnel.ps1` | `6b52e1c5429c0a19331b2665d6aa92587f4a11e37b4bc5107cf5669742b5060f` |
| `control.ps1` | `4dbac49491071881c83a24efcf759b9166f42c9325011193f966320a4f16ff38` |
| `fortis-mcp-bridge.mjs` | `1036c8b124fa6c41433f490cabae917e2e692ceaa792784a0148e5d827f9898` |
| `probe.mjs` | `5b64f1b6bf91822ef199211597318591561e52fb19b44b4eccfbaa2e987d4370` |
| `run-tunnel.ps1` | `8faa6d40b526ecead66f804119e318f1906d8aa80883044dfa14270c04de0104` |

The last access snapshot also contains `bridge-before-worktree-guidance.mjs` (SHA-256 `f8c24c544f35665fcb8a9375d5581e4f5c451fa2622f3e469022b7e8176f31fb`). It was not found in the current Windows source root or current Tunnel `runtime/repo-mode` listing. At the time of this hash-only inventory its contents had not been reviewed; the subsequent content-level comparison in section 14.5 established it is a historical pre-worktree-guidance snapshot of the legacy bridge.


### 13.2 `docs-centralization` Repo Mode files versus current Windows and Tunnel

| File | Current Windows root | Archived Repo Mode copy | Current Tunnel |
|---|---|---|---|
| `Dockerfile` | `1717e364...` | `1717e364...` | `1717e364...` |
| `fortis-mcp-bridge.mjs` | `83894366...` | `83894366...` | `863fd54c...` |
| `probe.mjs` | `8af052b1...` | `f300ef82...` | `f300ef82...` |
| `check-controls.ps1` | `20eae01d...` | `20eae01d...` | `20eae01d...` |
| `check-presentation.mjs` | `a1f21761...` | `a1f21761...` | `a1f21761...` |
| `check-schemas.mjs` | `5d6a589b...` | `5d6a589b...` | `5d6a589b...` |
| `control.ps1` | `605f9d54...` | `e80e209b...` | `e80e209b...` |
| `run-tunnel.ps1` | `f84c37b0...` | `3877266c...` | `3877266c...` |
| `Fortis-Repo-Control.cmd` | `bb1d002b...` | `bb1d002b...` | `bb1d002b...` |
| `expected-schemas.json` | `db4dc0e7...` | `db4dc0e7...` | `db4dc0e7...` |
| `workspace-config.json` | `6e153483...` | `workspace-config.example.json`: `6e153483...` | `workspace-config.example.json`: `6e153483...` |

Hashes in this compact table are abbreviated for readability; the complete SHA-256 values supplied by the owner and collected from Tunnel are recorded in the preceding inventory and section 12. Important scope: the `Current Tunnel` column here refers specifically to `runtime/repo-mode`, the historical Repo Mode directory, not to the canonical Windows worker source under `runtime/windows-repo/current`; see section 13.5. `workspace-config.json` in the current Windows root is byte-identical to the archived/Tunnel `workspace-config.example.json`, despite the filename difference.

Interpretation: the archived `docs-centralization` Repo Mode set is byte-identical to current Tunnel for Dockerfile, check-controls, check-presentation, check-schemas, control, bridge control CMD, expected schemas, probe and run-tunnel, except that the current Windows root has four divergent files: `fortis-mcp-bridge.mjs` matches the older archived bridge rather than the edited Tunnel candidate; `probe.mjs`, `control.ps1` and `run-tunnel.ps1` also differ. The Windows `fortis-mcp-bridge`, `probe`, `control` and `run-tunnel` content has not been compared textually here; do not assume either copy is authoritative or obsolete based only on hashes.


### 13.3 Complete current Windows root hash results

The owner-provided current Windows root hashes are:

| File | SHA-256 / status |
|---|---|
| `Dockerfile` | `1717e364b2f5cd92f4c6cabb039d4272598fe573b5e6cd9cfe7357a0abd4fa0b` |
| `fortis-mcp-bridge.mjs` | `8389436658e22f213d9865a78872159e027ca33094999db64ca96b5a7c79fc21` |
| `probe.mjs` | `8af052b1b836527c7ff4136dcd6a9a03ce8bfe27e5ac228df5c5de5b2008b312` |
| `check-controls.ps1` | `20eae01d8ed89d5352203b93e67ab012a158d5104ed7419a7510bbd53edcf869` |
| `check-presentation.mjs` | `a1f2176170863bb01cc67d1eae5eeef266fcbd9fe4d2c80703b5db8ce31ace9f` |
| `check-schemas.mjs` | `5d6a589bb749b6c498657aff445b2c77f9af10fa6815edbd0e3002dddd7ebcc2` |
| `control.ps1` | `605f9d54a0a35ff3011dc44356a733f975a8993f1225ff53378a6b7880a193c5` |
| `run-tunnel.ps1` | `f84c37b0c20e7af803d1794f13f824f69700629b4fb4a380ad2c6501c35708f1` |
| `Fortis-Repo-Control.cmd` | `bb1d002bde31aae23e9f882e2ac343122ada0dd36c0cba3743867b5453c95389` |
| `expected-schemas.json` | `db4dc0e7d0811a93994a1f8e208daac6dfdb6a4d32cf115f31ed7077ad3249ef` |
| `workspace-config.json` | `6e153483baf9021a74353cca3443d33ad0d38a949e3ec8488eeb9a85fa2515fc` |
| `WORKSPACE.md` | `2ea937a3dbf22dde30fb06792e2b435bf44ec39603dfa2c465f285c5b20aab54` |

Not found in the current Windows root: `bridge-before-worktree-guidance.mjs`, `configure-tunnel.ps1`, `workspace-config.example.json`, `desktop-commander-trusted.cmd`, `Start-Desktop-Commander-Secure-Tunnel.ps1` and `README.md`.

### 13.4 Other notable comparisons

- Archived host launchers `desktop-commander-trusted.cmd` and `Start-Desktop-Commander-Secure-Tunnel.ps1` match byte-for-byte with current Tunnel files under `runtime/host/`. Their hashes are respectively `c9140f20071153c44393f474f79f8144658fdb45dd103672abeaafd521b5b4a3` and `0f644d4239e60886354eb83b6438cc888d8bdf3202b944b0304508e7c1336dfe`.
- `configure-tunnel.ps1` exists in two distinct historical variants: access snapshots use `6b52e1c5...`; `docs-centralization` and `retired-initializer` use `b1af30ca221635c78a4dd91c1f248a725d64508baee59054a0c54743ce8fbc2`. It is absent from both current Windows root and current Tunnel `runtime/repo-mode`. At the time of this hash-only comparison the contents had not yet been compared; section 14.6 records the later content-level review and classifies both as historical profile-registration helpers, not current setup instructions.
- Current Windows `WORKSPACE.md` (`2ea937a3...`) differs from the archived historical Repo Mode pointer (`6ced8b19...`). The previous PowerShell output displayed garbled characters, so encoding/content must be read explicitly before interpreting this difference.
- The archived history README files are historical documents. Their presence is not evidence that they are current root-level runtime documentation.


### 13.5 Important reclassification: legacy runtime-root files are not the canonical current worker source

The first hash comparison treated the current Windows `C:\Users\alexa\chatgpt-repo-mode` root files as if they were peers of the current canonical Tunnel Windows worker source. The source documentation shows that this is not a safe assumption and the labels must be kept separate:

- `runtime/repo-mode/README.md` explicitly labels `runtime/repo-mode` **HISTORICAL / NOT CURRENT TOPOLOGY**. It describes the earlier Docker Repo-mode packaging/probe and states that current Repo1/Repo2 Windows worker source is under `runtime/windows-repo/current`.
- `runtime/windows-repo/current/README.md` explicitly identifies that directory as the canonical Windows worker source for both profiles. It states that nine executable PowerShell files are pinned by `source-manifest.json` and that the manifest inventory hash is pinned by the Windows dispatcher and Script Center resolver.
- The current source manifest declares `status` `TUNNEL_CANONICAL_SHARED_GUARD_POLICY_GO3C`, source `tunnel:main`, inventory SHA-256 `AEF7D17084F951AEAB6F98CF91E7A39E1D6043A0DAC6BC123DBF99463887B0F9`. It pins `launchers/chatgpt-repo-mode/control.ps1` to `62a93bfa5f4c957c5a89267ac3416ce09bb28fab71ebd87db976f20e21092d58` and `launchers/chatgpt-repo-mode/run-tunnel-quiet-logs.ps1` to `213c44b75ea9d0eeaed6efc98ece96abd64aa2b1bf2dd686dccb34de67fdc2aa`. Independently computed hashes of those two checked-out files match the manifest.
- The owner-provided hashes for the files at the root of `C:\Users\alexa\chatgpt-repo-mode` are different: `control.ps1` is `605f9d54...` and `run-tunnel.ps1` is `f84c37b0...`. They are not the two manifest-pinned canonical launcher files. The names are similar, but the paths and hashes differ.
- `probe.mjs` and `fortis-mcp-bridge.mjs` are not entries in the nine-file canonical Windows worker manifest. The legacy Repo Mode README says current Repo1/Repo2 workers use the direct Desktop Commander entry point and do not invoke the legacy bridge. The current quiet-log launcher also explicitly says it does not use old `probe.mjs` or bridge exec.

Therefore, the four files in the Windows `chatgpt-repo-mode` root should currently be classified as **Windows runtime-root copies / legacy or local candidates — not verified canonical Repo1/Repo2 worker source**. The hash-only evidence does not establish whether the local copies are stale, intentionally retained, or used by another manual workflow. Do not execute, overwrite, delete or import them based on this comparison. In particular, do not use the historical `runtime/repo-mode/run-tunnel.ps1` as a substitute for the manifest-pinned `runtime/windows-repo/current/launchers/chatgpt-repo-mode/run-tunnel-quiet-logs.ps1`.

At the time of this hash-only comparison, the contents and purpose of the four Windows root files, the unique `bridge-before-worktree-guidance.mjs`, and the two historical `configure-tunnel.ps1` variants were unresolved. The subsequent owner-provided content export and review in section 14 established their source-level classifications. It did not establish whether the local `control.ps1` is actively used or independently verify installation of the PR-A-15 `run-tunnel.ps1` candidate.


## 14. Content-level review of selected Windows Repo Mode sources — 2026-11-04

The owner supplied chatgpt-repo-mode-source-review-20261104-083246.txt, a 1,131-line read-only export containing selected Windows-root and backup source files, their SHA-256 values, sizes and contents. The conclusions below are SOURCE REVIEW of an OWNER-PROVIDED export; they do not prove that a file is installed, selected by a profile or currently executing.

The export is intentionally selective. It does not include workspace-config.json, expected-schemas.json, verification.json, access-verification.json, host-mount-verification.json, the three check scripts, or the runtime diagnostic logs. Do not infer their contents or treat this export as a complete secret/configuration audit.

### 14.1 Windows-root fortis-mcp-bridge.mjs

- SHA-256: 8389436658e22f213d9865a78872159e027ca33094999db64ca96b5a7c79fc21 (5,344 bytes).
- This is byte-identical to the installed legacy bridge hash recorded earlier for /workspace/repo/.fortis/mcp-bridge.mjs.
- Its REPO_GUIDANCE says that C:\Users\alexa\Repos and C:\Users\alexa\Workfiles are Windows bind mounts at /workspace/repos and /workspace/files, and that changes directly change host files. That statement is false for the current topology: the three workspace paths are subpaths of the shared ext4 fortis-repo-workspace volume, not Windows bind mounts.
- The bridge changes initialize instructions and tools/list descriptions, strips selected legacy UI metadata and disables legacy resources. Its comment and implementation preserve operation results, errors and structured content unchanged.
- Current Repo1/Repo2 worker source uses the direct Desktop Commander entry point; this legacy bridge is not in that worker path. Its guidance affects a connection only if a profile explicitly launches it.
- Classification: LEGACY / INSTALLED LEGACY WRAPPER MATCH. Do not deploy it as a correction or use its path claims as current mount evidence.

### 14.2 Windows-root probe.mjs

- SHA-256: 8af052b1b836527c7ff4136dcd6a9a03ce8bfe27e5ac228df5c5de5b2008b312 (7,594 bytes).
- The probe reads workspace-config.json, pins a container ID and checks security/resource settings. Its configured-folder loop explicitly requires each configured folder mount to have Docker type bind; the current Repo topology instead uses fortis-repo-workspace volume mounts with Repos and Workfiles subpaths.
- The script is not read-only: it writes Desktop Commander settings (allowedDirectories, defaultShell, telemetryEnabled), changes global Git safe.directory / core.autocrlf, writes linux-tools.json and verification.json, and can start the container when --start-if-stopped is supplied.
- It launches MCP through /workspace/repo/.fortis/mcp-bridge.mjs, not the direct Desktop Commander entry point used by the current Repo1/Repo2 worker chain.
- The referenced workspace-config.json was not included in the export, so its contents were not directly reviewed here. Its owner-provided hash matches the archived Tunnel example; see section 14.9 for the qualified inference.
- Classification: LEGACY / MUTATING PROBE FOR AN OLDER BIND-MOUNT MODEL. Do not run it as a current read-only diagnostic or use it as the current topology gate.

### 14.3 Windows-root control.ps1

- SHA-256: 605f9d54a0a35ff3011dc44356a733f975a8993f1225ff53378a6b7880a193c5 (3,982 bytes).
- It discovers both tunnel-client.exe and tunnel-client-runtime.exe, records process creation time, and rechecks PID plus creation time immediately before stopping a discovered Repo process.
- Start launches the sibling run-tunnel.ps1. StopContainer compares the inspected container ID with the containerId in sibling workspace-config.json, stops Repo access and then stops that container.
- The Windows workspace-config.json was omitted from the export; its owner-provided hash matches an archived Tunnel example whose containerId is the exited before-isolation container (section 14.9). The StopContainer pin is therefore a hash-supported inference, not a direct Windows-file read. The script is a local control helper, not one of the manifest-pinned canonical Repo1/Repo2 worker files.
- Classification: LOCAL CONTROL / LEGACY OR MANUAL-WORKFLOW CANDIDATE; active use is UNKNOWN. Do not run its start/stop actions as part of this documentation work.

### 14.4 Windows-root run-tunnel.ps1 — PR-A-15 candidate

- SHA-256: f84c37b0c20e7af803d1794f13f824f69700629b4fb4a380ad2c6501c35708f1 (16,355 bytes).
- Its header self-labels it PR-A-15 CANDIDATE, Source only; NOT installed. Installation status was not independently checked in this review. It defaults to Mode='Run', checks the owner Windows identity, pins the control/runtime file hashes and performs fail-closed Docker/Linux preflight.
- Unlike the older launcher, it selects the direct Desktop Commander executable; it explicitly avoids the old probe, bridge execution, registration, profile writes and container start/stop. In the recognized missing/factory-reset case, however, its guarded bootstrap can write Desktop Commander config and Git global config. It is therefore not a read-only script.
- Critical stale pin: the candidate expects container ID 0c0f8cb2d608679b4c3de51c527cbe2aca687cbf1360e6bf116444b2a0928cc2. The owner-provided docker ps -a output identifies that exact ID as the old rollback container, exited with code 137; the current running container is 04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030.
- Consequently, this candidate cannot pass its container-identity gate against the currently reported running container. Do not execute it, refresh its pin or treat it as installed without a new owner-side read-only Docker inspection and a separate review/approval.
- Classification: CANDIDATE / SELF-LABELLED NOT INSTALLED / BLOCKED BY STALE CONTAINER ID.

### 14.5 Unique bridge-before-worktree-guidance backup

- backups/access-20261010T112331268Z/bridge-before-worktree-guidance.mjs has SHA-256 F8C24C544F35665FCB8A9375D5581E4F5C451FA2622F3E469022B7E8176F31FB (5,107 bytes).
- A content diff against the Windows-root fortis-mcp-bridge.mjs shows one change only: the current file adds two sentences to REPO_GUIDANCE warning that host-created linked worktrees can contain Windows absolute paths, should not be pruned/repaired from Linux solely because those paths are unresolved, and should be managed with host Git.
- Classification: HISTORICAL PRE-WORKTREE-GUIDANCE SNAPSHOT. Its provenance is now explained; it is not a separate current implementation.

### 14.6 Earlier access and documentation-centralization variants

- The four non-empty access-* snapshots have identical hashes for their seven repeated launcher/bridge/probe files. The final access snapshot adds the unique pre-worktree-guidance bridge described above.
- The access-snapshot bridge (1036c8b124fa6c41433f490cabae917e2e692ceaa792784a0148e5d827f9898) is an older offline/single-volume variant. The docs-centralization bridge (8389436658e22f213d9865a78872159e027ca33094999db64ca96b5a7c79fc21) matches the current Windows-root bridge and installed legacy wrapper.
- Two historical configure-tunnel.ps1 variants differ only in their MCP command: the access snapshot (6b52e1c5...) selects the direct Desktop Commander executable; the docs-centralization / retired-initializer copy (b1af30ca...) selects the legacy bridge. Both are historical profile-registration helpers, not current setup instructions.
- Two historical run-tunnel.ps1 variants also differ in credential and launch handling: the access snapshot (8faa6d40...) prompts for a runtime key as a SecureString, passes it through a temporary environment variable and removes that variable in finally; the docs-centralization copy (3877266c...) relies on the already saved runtime-key file. Both launch the legacy bridge.
- The access control.ps1 (4dbac494...) hard-codes an older container ID; the docs-centralization copy (e80e209b...) reads the ID from workspace-config.json; the current Windows-root copy (605f9d54...) adds runtime-process discovery, creation-time revalidation and a read-only health URL.
- These comparisons explain the historical variants; none of these files is promoted to canonical worker source by this review.

### 14.7 Classification result

| Windows-root / backup item | Classification | Decision |
|---|---|---|
| fortis-mcp-bridge.mjs | Legacy wrapper copy | Not the current Repo1/Repo2 worker path; contains obsolete Windows bind-mount guidance |
| probe.mjs | Legacy mutating probe | Encodes the old bind-mount model and changes runtime config; do not run as read-only |
| control.ps1 | Local control helper | Hash-matched config points to exited before-isolation ID; active use unknown |
| run-tunnel.ps1 | PR-A-15 candidate | Self-labelled not installed; stale pin matches an exited rollback container |
| bridge-before-worktree-guidance.mjs | Historical predecessor | Exact content delta is the later worktree warning |
| configure-tunnel.ps1 variants | Historical registration helpers | Direct-DC and legacy-bridge variants; neither is current setup guidance |

The canonical Repo1/Repo2 Windows worker source remains tunnel/runtime/windows-repo/current, pinned by its source manifest. Similar filenames in the Windows chatgpt-repo-mode root do not override that source authority.

### 14.8 Export limits and safe continuation

The source export did not include workspace-config.json, expected-schemas.json, verification/access/mount JSON, the check scripts or diagnostic logs. The expected-schemas file and three check scripts were reviewed through hash-matched Tunnel historical copies (section 14.10). The workspace-config.json bytes were not directly read; a hash-matched Tunnel example is analyzed in section 14.9 as a qualified inference. Verification/access/mount JSON and diagnostic logs remain unreviewed.

Do not copy the entire Windows source directory or backup tree into Git. Diagnostic JSONL, access/configuration records and generated snapshots require separate classification and secret screening. This review changed no Windows file, Docker resource, installed package, MCP bridge or process; no Git file was staged, committed or pushed.


### 14.9 Hash-supported reconstruction of the omitted workspace-config.json

The Windows source export did not contain the bytes of workspace-config.json, but its owner-provided SHA-256 in section 13.3 is 6e153483baf9021a74353cca3443d33ad0d38a949e3ec8488eeb9a85fa2515fc. Section 13.2 records the same hash for Tunnel's historical runtime/repo-mode/workspace-config.example.json. The exact-hash Tunnel example was read during this review; this is a HASH-SUPPORTED INFERENCE about the omitted Windows file, not a direct read of that Windows file.

The matching example declares:
- containerId c6d7be9fe6eb4138a9dc47db3f82c32c377007c2d461c1f03ad37fe9bb3d074a;
- two Windows folder mappings: C:\Users\alexa\Repos to /workspace/repos and C:\Users\alexa\Workfiles to /workspace/files;
- network fortis-repo-egress, internetEnabled true, and internalVolume fortis-repo-workspace.

The owner's earlier docker ps -a output identifies c6d7be9... as fortis-repo-test-before-isolation, exited with code 143 about seven days before the inspection. The same output identifies 04fed7b... as the current running container. The sample's container ID and Windows bind-mount mappings therefore describe the pre-isolation topology, not the current runtime.

Consequences if the Windows workspace-config.json is byte-identical as its reported hash indicates:
- probe.mjs fails its initial container-identity assertion against the current 04fed7b... container; it does not reach its later configuration/Git writes.
- Its folder assertions also encode the obsolete bind-mount topology and do not describe the current volume-backed Repos/Workfiles subpaths.
- control.ps1 StopContainer compares the live ID with this old c6d7be9... value and should fail closed rather than stop the current container.
- The PR-A-15 run-tunnel.ps1 candidate uses a third, separate stale pin: 0c0f8cb2..., the exited GO3 rollback container.

This resolves the old config's likely contents and explains why the Windows-root probe/control pair and the PR-A-15 candidate do not target the current running container. Keep the evidence label explicit: the Windows file itself was not exported; the conclusion depends on the owner's hash and the byte-identical archived example. No config file was changed.


### 14.10 Hash-matched validation scripts and schema snapshot

The Windows export omitted the three check scripts and expected-schemas.json. Their owner-provided Windows-root hashes match the corresponding files in Tunnel's historical runtime/repo-mode directory, so those exact-hash copies were read there. This is content equivalence based on the supplied hashes; it does not make the historical directory current or canonical.

- check-controls.ps1 (SHA-256 20eae01d...) is a mocked PowerShell unit harness for the adjacent historical control.ps1. It replaces process enumeration, TCP lookup, HTTP, Stop-Process, Start-Process and docker with in-memory mocks. It verifies Repo-only stopping, the old c6d7be9... container identity, changed-target rejection, duplicate-start protection, panel selection and runner launch. It explicitly says process/network actions are mocked and live services are unchanged. It is not a live runtime check and does not test the divergent Windows-root control.ps1.
- check-presentation.mjs (SHA-256 a1f21761...) launches both direct Desktop Commander and the legacy bridge through docker exec. It checks initialize/tool-list presentation, schemas/annotations, file access, terminal execution and denial of /etc/passwd. It writes /workspace/repo/.fortis/presentation-check.txt and presentation-verification.json; the source has no cleanup for the workspace test file. Its report explicitly sets chatPresentationVerified=false and tunnelRestartRequired=true. It is a mutating integration test, not a read-only check and not proof of the ChatGPT app UI.
- check-schemas.mjs (SHA-256 5d6a589b...) reads expected-schemas.json and linux-tools.json and compares inputSchema objects by tool name. The check itself is read-only, but linux-tools.json is generated probe output, not live MCP metadata; the comparison cannot establish current descriptions or active tool presentation.
- expected-schemas.json (SHA-256 db4dc0e7...) is a static expected-input-schema snapshot containing 19 definitions. It is not the source of live MCP tool descriptions.

Classification: check-controls is a legacy mocked unit test; check-presentation is a legacy mutating integration test that should not be run casually; check-schemas is a read-only comparison against a generated historical snapshot. None of these files is part of the nine-file canonical Repo1/Repo2 worker manifest. No test script was executed during this review.
