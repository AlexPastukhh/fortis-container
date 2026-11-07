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

Gateway state, TLS identity, machine authentication and provider credentials
are separate from the Repo workspace. Source map, active release identity,
exact mounts and backup/admission belong to the
[Gateway operating guide](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/guides/FORTIS-APPROVALS-SECURE-DEVELOPMENT.md)
and [Primary controller](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/PRIMARY-GATEWAY-OPERATIONS.md).
The active route is Primary 19203/19204; older 19103/19104 inventory describes
retained Legacy. Do not infer current volume attachment from old Compose labels.
Repo's read-only client-auth mount is described above; it does not contain
provider credentials or Gateway state. Read-only access does not isolate
processes sharing the grant's UID; see [authorization](AUTHORIZATION-AND-APPROVALS.md).

## Persistence and recovery distinctions

- `fortis-repo-workspace` contains source checkouts, Workfiles, the `.fortis-auth` directory and Qwen candidate files.
- `/home/node` is documented as tmpfs in the Repo runtime. Git global config and other HOME state may not survive container recreation.
- The Git credential files in `.fortis-auth` are in the persistent workspace volume.
- Gateway state, TLS identity, machine grant and Sonar token are separate Approval volumes; they are not part of the Repo workspace.
- A Docker image is not a backup of persistent volumes.
- A source checkout is not a backup of deployed secrets or runtime databases.

Never delete, recreate, repair or reattach these volumes as part of a documentation task. Recovery procedures require a separate owner-approved maintenance action.

## Compose and deployment references

`fortis_approvals/deploy/compose-r7-p2-20261103.yaml` is a historical deployment reference, not the current Primary release procedure. The supported Gateway release entry is [UC-GW-005](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005). The paired image-only build script pins `fortis_approvals/deploy/Dockerfile-R7-Unified-Read-Ask-Candidate`; the top-level `deploy/Dockerfile` is an older, separate server recipe and must not be substituted. Its filename retains historical implementation labels; it is not a routine command to rerun or a proposed naming convention. Older Compose files and provisioning/cutover scripts are historical unless a later owner-approved deployment explicitly selects them.

## Human-readable names versus Docker identifiers

The product is **Fortis Approvals Gateway**. Active Primary lifecycle is owned by
[Primary operations](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/PRIMARY-GATEWAY-OPERATIONS.md)
and its protected release records. The owner promoted to `fortis-gateway` and
stopped/retained the older `fortis-approvals-gateway` as Legacy on 2026-11-07;
this does not make older Compose project/service labels current deployment inputs.
Before a later release, read exact live identity and the controller records.

The minimal rename of 2026-11-05 is a
[historical completion](FUTURE-IMPROVEMENTS-ARCHIVE-2026-11-05.md#fortis-approvals-gateway-naming-cleanup-completed--2026-11-05).
Do not recreate its old Compose service, rename today's Primary back, or run
superseded Compose candidates from that record. Runtime names and Compose
labels are separate; any new lifecycle change follows
[UC-CONT-021](use-cases/docker.md#uc-cont-021).
