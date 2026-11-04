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

## Repo runtime

| Item | Current evidence |
|---|---|
| Container role | Fortis Repo MCP / Desktop Commander runtime |
| Container name | `fortis-repo-test`; owner-provided full ID `04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030` |
| Linux identity | UID/GID 1000 (`node`) |
| Desktop Commander | 0.2.52 |
| Node | 22.23.3 |
| Workspace volume | `fortis-repo-workspace`, RW at the three paths above |
| Image | `fortis-repo-mode:dc-0.2.52`; owner-provided image ID `sha256:2c84fabebb34265e53b020f21a11683a4c68cbb41a08f5f11f9b01c7de5ed8c9` |
| Gateway client-auth volume | `fortis-r7-client` → `/run/fortis-client`, RO — LIVE VERIFIED in current Repo container |
| Docker socket | Not established by this audit; do not infer from absence of the Docker CLI |

The Docker CLI is not installed in this MCP container, so Docker Engine cannot be inspected from inside it. The owner subsequently supplied Windows-host `docker inspect` output for this exact Repo container. That output is OWNER-REPORTED evidence: image `fortis-repo-mode:dc-0.2.52`, full ID, read-only rootfs, non-privileged mode, `CapDrop=ALL`, `no-new-privileges`, network `fortis-repo-egress`, restart policy `unless-stopped`, UID/GID 1000 and volume subpaths are recorded in [Container build provenance](CONTAINER-BUILD-PROVENANCE.md). These host-inspected properties must not be described as independently inspected by this MCP session.

## Fortis Approvals Gateway runtime

The current Approval evidence describes one deployed **Fortis Approvals Gateway** service. Docker Engine state was not inspected from this Repo container, so the exact live container/project identifiers remain OWNER-REPORTED until checked on the Windows Docker host.

| Existing volume identifier | Container path | Purpose | Approved target identifier | Evidence |
|---|---|---|---|---|
| `fortis-r7-state` | `/state` | Approval state, owner state and Sonar receipts | `fortis-approvals-state` | OWNER-REPORTED |
| `fortis-r7-identity` | `/run/r7-identity` | Server certificate and private TLS key | `fortis-approvals-tls-identity` | OWNER-REPORTED |
| `fortis-r7-grant` | `/run/r7-grant` | Machine ingress grant | `fortis-approvals-machine-grant` | OWNER-REPORTED |
| `fortis-r7-sonar-token` | `/run/r7-sonar-token` | Private SonarCloud token | `fortis-approvals-sonar-credential` | OWNER-REPORTED |
| `fortis-r7-client` | `/run/fortis-client` in Repo | Client grant copy and public server certificate | `fortis-approvals-client-auth` | LIVE VERIFIED in current Repo container |

The Repo client mount is confirmed read-only in the current container. It contains `grant` and `server.crt`. Metadata: grant owned by UID 1000, mode 0600; public certificate owned by UID 1000, mode 0644. Desktop Commander runs as UID 1000 and can read the grant. Read-only prevents writes, not reads.

The preserved Compose reference documents loopback-only ports 19103 (Owner Portal) and 19104 (machine ingress), read-only root filesystem, UID/GID 10001, dropped capabilities and no-new-privileges. These are OWNER-REPORTED deployment properties, not a fresh Docker inspection from this session. The old volume names above remain the identifiers in the supplied deployment evidence; target names are a separate approved migration plan, not live resources.

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

Use **Fortis Approvals Gateway** as the service name in explanatory documentation. Do not use R7/P1/P2 as current product or release labels. The preserved deployment reference still contains the older Compose service `fortis`, image tag `fortis-r7-unified-read-ask-candidate:review-p2-20261103-a3e87c0c` and historical volume identifiers. Deployment notes report a generated container name `fortis-r7-p1-fortis-1`; it has not been independently checked with Docker inspect in this session. These exact identifiers remain only to identify the existing artifact and prepare its migration.

The owner-approved target names are recorded in [Naming and rename plan](NAMING-AND-RENAME-PLAN.md). No deployed container, Compose project/service, image or volume has been renamed. Do not describe the target names as live. A runtime migration still requires a Windows-host inventory, rendered Compose dry run, data-preserving volume migration plan and rollback review.
