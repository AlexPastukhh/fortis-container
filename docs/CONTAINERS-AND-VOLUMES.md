# Containers and volumes

## Fortis Repo workspace

**LIVE VERIFIED in the current MCP process:** the following paths are mounted read-write from one ext4 volume tree.

| Container path | Mount source in mountinfo | Purpose |
|---|---|---|
| `/workspace/repo` | `/data/docker/volumes/fortis-repo-workspace/_data` | Workspace root and internal project/service files |
| `/workspace/repos` | `.../_data/Repos` | Git checkouts |
| `/workspace/files` | `.../_data/Workfiles` | Workfiles and temporary handoff material |

All three show the same ext4 device and RW mount options. The aliases `/workspace/repo/Repos` ↔ `/workspace/repos` and `/workspace/repo/Workfiles` ↔ `/workspace/files` resolve to the same directories.

This corrects the older description that `/workspace/repos` and `/workspace/files` are Windows bind mounts. Current mount evidence shows they are subpaths of the persistent `fortis-repo-workspace` volume, not independent Windows host directories.

At the 2026-11-04 rollout snapshot, the reserved directory `/workspace/repo/Worktrees` existed inside this same persistent workspace volume; it is not a separate mount and was empty. No new task Worktrees had been created and no existing linked Worktrees had been moved in that stage; some pre-existing linked Worktrees remained under legacy paths inside `Repos`. The folder convention and Docker/Windows Git handoff are owned by the [canonical Mirror workflow](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md); this document remains the source of truth only for actual container mounts and storage topology. See the [archived rollout snapshot](CURRENT-STATE-ARCHIVE-2026-11-04.md#git-working-trees) for historical checkout observations; recheck live state before migration.

## Repo runtime

| Item | Current evidence |
|---|---|
| Container role | Fortis Repo MCP / Desktop Commander runtime |
| Container name | `fortis-repo-test`; current owner-provided full ID `1f67b67cacf3d4435982df9c0606dcb1a89d99f3f8ac73d365f3e6bb3d2f658b` (MCP-UI-headless deployment, 2026-11-04) |
| Linux identity | UID/GID 1000 (`node`) |
| Desktop Commander | 0.2.52 |
| Node | 22.23.3 |
| Workspace volume | `fortis-repo-workspace`, RW at the three paths above |
| Image | `fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104`; owner-provided image ID `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9` (path-guidance image is its base) |
| Gateway client-auth volume | `fortis-r7-client` → `/run/fortis-client`, RO — LIVE VERIFIED in current Repo container |
| Docker socket | Not established by this audit; do not infer from absence of the Docker CLI |

The Docker CLI is not installed in this MCP container, so Docker Engine cannot be inspected from inside it. The original GO3 read-only release verifier and its mount snapshot were run against the pre-cutover container; those historical checks established the shared Guard baseline. The owner then replaced that container with the path-guidance derivative and supplied a post-cutover read-only check. The post-cutover check returned `FINAL_DOCKER_VERIFICATION_PASS` with all 12 assertions true: running state, exact image ID, old container preserved/stopped, read-only rootfs, non-privileged mode, `CapDrop=ALL`, `no-new-privileges`, no host binds, no `VolumesFrom`, both networks and reviewed resource limits. The cutover runner separately asserted all four named-volume mounts, including `Repos` and `Workfiles` subpaths, before reporting replacement configuration PASS. These Windows-host findings remain OWNER-REPORTED / OUTPUT REVIEWED, not Docker Engine inspections performed by the Linux MCP process.

The rollback container is `fortis-repo-test-pre-path-guidance-20261104`, preserving old ID `04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030`; it remains stopped. The current image and full deployment evidence are recorded in the [path-guidance patch record](../patches/desktop-commander-0.2.52/README.md). The recorded Docker resource snapshot is:

| Docker setting | Owner-reported live value | Shared Guard status |
|---|---:|---|
| Memory | 4 GiB | Ceiling: 8 GiB |
| MemorySwap | 5 GiB total memory+swap | Not checked |
| NanoCpus | 2,000,000,000 (2 CPUs) | Ceiling: 2 CPUs |
| PidsLimit | 512 | Ceiling: 1024 |
| ShmSize | 64 MiB | Not checked |
| RestartPolicy | `unless-stopped` | Not checked |
| Tmpfs `/home/node` | 128 MiB, `nosuid,nodev,noexec`, UID/GID 1000, mode 0700 | Path required; size/options not pinned |
| Tmpfs `/tmp` | 128 MiB, `nosuid,nodev,noexec`, mode 1777 | Path required; size/options not pinned |
| Networks | `fortis-repo-egress`, `rdg-personal_agents` | Both accepted by policy; second must be internal |
| Published port bindings | 0 | Must be 0 |

The owner completed a second Windows GO3 run against this exact container on 2026-11-04. Its corrected diagnostic reported `fortis-repo-workspace` RW at `/workspace/files`, `/workspace/repo` and `/workspace/repos`, plus `fortis-r7-client` RO at `/run/fortis-client`; all four are Docker `volume` mounts using driver `local` and mode `z`. The first run's malformed mount rows remain invalid and are superseded by this second output. The corrected formatter reports `Name`, `Destination`, `RW`, `Mode`, `Driver` and `Propagation`, without exposing host source paths. This is owner-provided Windows output, reviewed here; the Linux MCP session did not independently inspect Docker Engine. See [Repo container / Shared Guard baseline](audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md) for the full record and evidence limits.

## Fortis Approvals Gateway runtime

The earlier Windows Docker Host inventory supplied 2026-11-04 was a **pre-start snapshot**: it showed the R7 P1-named container `fortis-r7-p1-fortis-1` exited at that time. The owner subsequently confirmed on 2026-11-05 that **R7-P1 / Compose project `fortis-r7-p1` is the active Gateway**; there is no G2/G4/R7 runtime conflict. Owner-provided live PowerShell output on 2026-11-05 confirmed the active container ID `0852c39c9e5d0889290f94128b93555522d9447f9bebc7d880397bd43b4f5a6b`, image ID `sha256:e751f6ca0cfe6ce290cf580de2f243071ee1f3e681baa8827c6cea41a16fa402`, Compose project/service labels `fortis-r7-p1` / `fortis`, and historical Compose config path `C:\Users\alexa\Downloads\fortis-r7-p2-rollout-go3-20261103\compose-r7-p2-20261103.yaml`. The existing Repo typed client previously completed live Sonar READ, ASK, Reject and WebAuthn Approve through `https://host.docker.internal:19104`, recorded in `fortis-approvals/fortis_approvals/evidence/FORTIS-SONAR-LIVE-E2E-20261104.md`.

| Existing volume identifier | Container path | Purpose | Decision for naming cleanup | Evidence |
|---|---|---|---|---|
| `fortis-r7-state` | `/state` | Approval state, owner state and Sonar receipts | Keep existing name and contents | OWNER-REPORTED; recheck live attachment |
| `fortis-r7-identity` | `/run/r7-identity` | Server certificate and private TLS key | Keep existing name and contents | OWNER-REPORTED; recheck live attachment |
| `fortis-r7-grant` | `/run/r7-grant` | Machine ingress grant | Keep existing name and contents | OWNER-REPORTED; recheck live attachment |
| `fortis-r7-sonar-token` | `/run/r7-sonar-token` | Private SonarCloud token | Keep existing name and contents | OWNER-REPORTED; recheck live attachment |
| `fortis-r7-client` | `/run/fortis-client` in Repo | Client grant copy and public server certificate | Keep existing name and contents; do not touch | LIVE VERIFIED in current Repo container |

The Repo client mount is confirmed read-only in the current container. It contains `grant` and `server.crt`. Metadata: grant owned by UID 1000, mode 0600; public certificate owned by UID 1000, mode 0644. Desktop Commander runs as UID 1000 and can read the grant. Read-only prevents writes, not reads.

The preserved R7 P2 Compose reference documents loopback-only ports 19103 (Owner Portal) and 19104 (machine ingress), read-only root filesystem, UID/GID 10001, dropped capabilities and no-new-privileges. The earlier pre-start inspect showed the R7 volumes listed above, but it is not a post-start snapshot. The current naming cleanup deliberately retains all existing Gateway and Repo volume names and contents; no target volumes are to be created and no data is to be copied. Verify the active container's exact mounts immediately before the in-place rename.

## Planned Gateway GitHub credential volume — not created

The Gateway currently has a separate Sonar token volume but no GitHub credential volume. The planned GitHub integration targets a new external volume named `fortis-github-token`, mounted read-only at `/run/github-token` (PAT file: `/run/github-token/token`). This volume has not been created, populated or attached; do not add it to a historical Compose file or infer that the running Gateway can access GitHub. Provisioning and deployment require a reviewed source/Compose target and a separate owner-approved release. The existing Sonar, state, identity and machine-grant volumes remain unchanged.

## Persistence and recovery distinctions

- `fortis-repo-workspace` contains source checkouts, Workfiles, the `.fortis-auth` directory and Qwen candidate files.
- `/home/node` is documented as tmpfs in the Repo runtime. Git global config and other HOME state may not survive container recreation.
- The Git credential files in `.fortis-auth` are in the persistent workspace volume.
- Gateway state, TLS identity, machine grant and Sonar token are separate Approval volumes; they are not part of the Repo workspace.
- A Docker image is not a backup of persistent volumes.
- A source checkout is not a backup of deployed secrets or runtime databases.

Never delete, recreate, repair or reattach these volumes as part of a documentation task. Recovery procedures require a separate owner-approved maintenance action.

## Compose and deployment references

The current source index identifies `fortis_approvals/deploy/compose-r7-p2-20261103.yaml` as the preserved deployment reference for the currently documented artifact. The paired image-only build script pins `fortis_approvals/deploy/Dockerfile-R7-Unified-Read-Ask-Candidate`; the top-level `deploy/Dockerfile` is an older, separate server recipe and must not be substituted. Its filename retains historical implementation labels; it is not a routine command to rerun or a proposed naming convention. Older Compose files and provisioning/cutover scripts are historical unless a later owner-approved deployment explicitly selects them.

## Human-readable names versus Docker identifiers

Use **Fortis Approvals Gateway** as the human-readable product name. The owner-confirmed active Compose project is `fortis-r7-p1`; the Compose service remains `fortis`. On 2026-11-05 the owner successfully renamed the existing running container in place to `fortis-approvals-gateway` and added image tag `fortis-approvals-gateway:current` to the existing image ID `sha256:e751f6ca0cfe6ce290cf580de2f243071ee1f3e681baa8827c6cea41a16fa402`. The container ID remained `0852c39c9e5d0889290f94128b93555522d9447f9bebc7d880397bd43b4f5a6b`; post-operation `docker ps` reported `Up 44 minutes (healthy)`, and image inspect confirmed the new tag resolves to the same image ID. No volume, port, network, data, credential or application configuration operation was performed.

**Future Compose caveat:** this was a Docker runtime rename only; it did not change the Compose file or its project/service labels. If Compose later recreates service `fortis`, it may generate the old name `fortis-r7-p1-fortis-1` again. At the next planned deployment, identify the maintained Compose source and, if the friendly name should persist, add `container_name: fortis-approvals-gateway` there as part of a reviewed deployment (which may recreate the container). Do not edit or deploy the historical P2 Compose reference just for this naming change.

The exact completion record and evidence limits are maintained in [Future improvements — Fortis Approvals Gateway naming cleanup](FUTURE-IMPROVEMENTS.md#fortis-approvals-gateway-naming-cleanup-completed--2026-11-05). The old full-recreation Compose candidate is superseded; do not use it.
