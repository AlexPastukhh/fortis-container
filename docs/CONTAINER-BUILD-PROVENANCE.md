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

The `fortis-container` repository is currently the central documentation project. It has its first local documentation-baseline commit (`2119ccb`) on `main`, but no remote. No Dockerfile or complete, canonical build context has yet been added to it. The future location for reviewed, version-controlled container build sources should be decided here before files are moved or copied.

## 5. Owner-provided live container inspection

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

## 6. Current MCP tool-description issue

The current Fortis MCP tool metadata returned in this session still includes the generic Windows/Linux-to-`/home/...` host-path translation and Docker Installer `/home/[folder-name]` claim in the `start_process` description. The `read_file` description instead lists the actual mounted container paths.

The source investigation recorded in [AI integrations](AI-INTEGRATIONS.md) identifies the installed Desktop Commander 0.2.52 package as the source of the incorrect `OS_GUIDANCE` block. The intended correction is narrow: remove generic host-path translation assumptions while retaining runtime-derived mount guidance.

The installed package file is root-owned and the connected MCP process runs as UID 1000 without write permission. The approved correction has **not** been deployed. No active package file was changed and no MCP process was killed or restarted.

## 7. Remaining unknowns and safe next steps

Still unknown:
- exact original `docker build` command and absolute build-context path;
- original `.dockerignore` contents and why it is absent from the supplied current directory listing;
- whether any backup contains a later or alternative Dockerfile that was actually used;
- whether the diagnostic/configuration artifacts contain sensitive data (their contents have not been reviewed here).

Before making the container reproducible:
1. Preserve this record as the research baseline.
2. Review the original directory and backups without copying diagnostic logs or secrets into Git.
3. Recover the original build command/context and `.dockerignore`, if available.
4. Agree which reviewed files become canonical under `fortis-container`.
5. Only then prepare a reproducible build definition and perform an explicitly approved build/deployment.

No Docker build, pull, restart, recreation, volume change, source relocation, Git commit or push was performed for this documentation update. For manual-versus-automated verification boundaries, see [Validation policy](VALIDATION-POLICY.md).

## Appendix: Additional details from the original directory and host inspection

PowerShell reported these UTC file timestamps:
- `Dockerfile`: created/modified 2026-10-10 05:57:07Z;
- `build.log`: created 2026-10-10 05:57:07Z, modified 2026-10-10 06:47:19Z;
- `WORKSPACE.md`: created 2026-10-10 11:30:00Z, modified 2026-10-10 12:26:05Z.

The listed backup directories are:
`access-20261010T111644398Z`, `access-20261010T111717413Z`, `access-20261010T111828502Z`, `access-20261010T112024336Z`, `access-20261010T112331268Z`, `docs-centralization-20261010`, `retired-initializer-20261011`, and `startup-saved-key-20261010T115550Z`. Their contents have not been inspected.

The supplied `WORKSPACE.md` output appears garbled under the PowerShell display encoding. Its visible links point to Tunnel's `docs/CURRENT_STATE.md`, `README.md` and `history/repo-mode/WORKSPACE.md`; it says documentation should be updated in the Tunnel Windows clone and that the previous text was preserved while applications/scripts were not moved. Treat it as a historical pointer. The actual file encoding/content should be checked as UTF-8 before any edit; the pasted display alone does not prove that the file bytes are corrupt.

The owner-provided inspect also reported tmpfs mounts:
- `/home/node`: RW, `nosuid,nodev,noexec`, UID/GID 1000, mode 0700, size 128 MiB;
- `/tmp`: RW, `nosuid,nodev,noexec`, mode 1777, size 128 MiB.

These are part of the supplied runtime snapshot, not a rebuild instruction.


## 9. Backup audit access boundary — 2026-11-04

The original Windows directory `C:\Users\alexa\chatgpt-repo-mode` and its `backups/` subtree are not present at the corresponding checked paths under `/workspace/repo`, `/workspace/repos` or `/workspace/files` in the current MCP container. The eight backup directory names supplied by the owner (`access-*`, `docs-centralization-20261010`, `retired-initializer-20261011`, `startup-saved-key-20261010T115550Z`) were also not found in those mounted trees during a bounded directory-name search.

This is consistent with the owner-provided Docker inspection: the container receives named-volume mounts for the Fortis workspace, not a bind mount of `C:\Users\alexa\chatgpt-repo-mode`. The presence of other unrelated backup directories under mounted workspaces does not make them copies of this original source backup set; their contents were not inspected.

**Result:** no backup file contents have been read and no backup files have been changed. A read-only inventory must be run on the Windows host against the original directory. First collect filenames, sizes, timestamps and hashes for candidate Docker/build files; only then decide which specific files are safe and useful to read. Do not copy the full backup tree into Git.


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
- Only the archived Dockerfile was hashed. The bridge, launchers, probe scripts, schema/configuration files and historical documentation have not yet been content-compared.
- The backup contents were not modified, copied into a repository, or deleted.
- Do not import the whole backup tree into Git. First review the small set of candidate source/documentation files, compare them with the current Tunnel and Fortis Container copies, and screen configuration/access artifacts before deciding what belongs in version control.


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
