# Naming decisions and Docker resource rename plan

**Status:** naming direction approved by the owner on 2026-11-03. This document records the target vocabulary and a proposed mapping; it does not authorize or perform a runtime change.

## Agreed naming principles

- Human-readable product/service name: **Fortis Approvals Gateway**.
- Source repository: `fortis-approvals`.
- Docker Compose project: `fortis-approvals`.
- Compose service: `gateway`.
- Generated container name: `fortis-approvals-gateway-1`.
- Image repository/name: `fortis-approvals-gateway`.
- Approval-owned volumes use the `fortis-approvals-` prefix and a role-based suffix.
- Do not introduce a new release-numbering scheme or SemVer labels now.
- Keep R7, P1 and P2 only where needed to understand historical source, build, deployment and evidence records. Do not use them in new everyday resource names.
- Keep exact old image IDs/digests, old Compose filenames and old resource names in historical evidence when they are needed for provenance.

## Proposed resource mapping

| Current identifier | Proposed identifier | Evidence / confidence |
|---|---|---|
| Compose project (not established) | `fortis-approvals` | Target decision; current project label needs Docker inspect |
| Compose service `fortis` | `gateway` | Directly present in the P2 Compose reference |
| Reported container `fortis-r7-p1-fortis-1` | `fortis-approvals-gateway-1` | Old name is owner-reported in deployment docs; not verified by current Docker inspect |
| Image `fortis-r7-unified-read-ask-candidate:review-p2-20261103-a3e87c0c` | `fortis-approvals-gateway` | Old tag is present in the Compose reference; proposed new name is not built or tagged |
| `fortis-r7-state` | `fortis-approvals-state` | External volume name in Compose reference |
| `fortis-r7-identity` | `fortis-approvals-tls-identity` | External volume name in Compose reference |
| `fortis-r7-grant` | `fortis-approvals-machine-grant` | External volume name in Compose reference |
| `fortis-r7-sonar-token` | `fortis-approvals-sonar-credential` | External volume name in Compose reference |
| `fortis-r7-client` | `fortis-approvals-client-auth` | Owner-reported Repo-side read-only client volume; verify by Docker inspect |

## Names deliberately left unchanged

- Fortis Repo workspace volume `fortis-repo-workspace`: shared workspace for the Repo container, not owned by Approvals.
- Repo-side workspace paths and the fixed ingress/owner-portal ports `19104` and `19103`: no renaming is proposed.
- Existing in-container application paths `/run/r7-identity`, `/run/r7-grant` and `/run/r7-sonar-token` remain unchanged in this Docker-resource naming pass because the current Gateway implementation consumes them. Renaming these paths would be a separate application/configuration change, not a volume rename.
- R7 API routes, typed request names, database/table names and source package names: they are implementation contracts, not Docker product labels.
- Historical files such as `compose-r7-p2-20261103.yaml` and historical P1/P2 evidence: retain as provenance; do not rename or rewrite merely to remove version words.

## Fortis Repo container name

The name `fortis-repo-test` is recorded in current-state evidence as the Repo/Desktop Commander container. A more descriptive target such as `fortis-repo-mcp` may be considered separately, but the live container name, Compose project and all dependent launchers must first be verified. It is not part of the Approvals Gateway resource migration.

## Required pre-change checks

1. Obtain host-side Docker inspect for the running Approvals container, image, Compose labels, networks, ports and all attached volumes.
2. Obtain Docker inspect for the Repo container and verify the exact `fortis-r7-client` attachment and its consumers.
3. Search all Compose files, scripts, environment files, Windows launchers, health checks, monitoring and documentation for old resource identifiers.
4. Confirm the current image identity and whether the proposed friendly image name can be applied as a tag without rebuilding.
5. Prepare a new Compose rendering with the proposed project/service/volume names; compare every effective field with the current runtime reference.
6. Prepare a data-preserving volume migration and rollback plan. Docker volumes cannot be renamed in place; new volumes and a verified copy would be required.
7. Present the final old→new map, data-copy plan, downtime implications and rollback steps for owner approval.

## Target-name Compose candidate review — 2026-11-03

A draft target-name Compose candidate now exists at `fortis_approvals/deploy/compose-fortis-approvals-dryrun.yaml`, based on the owner-approved naming direction. Compared with the preserved deployment reference, it:
- adds Compose project name `fortis-approvals`;
- renames service `fortis` to `gateway`;
- changes the image reference to the target name `fortis-approvals-gateway`;
- changes the four Gateway-owned external volume identifiers to their approved `fortis-approvals-*` names.

The service's runtime settings are unchanged from the supplied reference: environment, loopback ports, `pull_policy`, restart/init settings, read-only root, UID/GID, dropped capabilities, no-new-privileges, PID limit, mount destinations/read-only flags, tmpfs and healthcheck. The generated service container name is expected to become `fortis-approvals-gateway-1`. The target image has not been tagged and the target external volumes have not been created or verified.

The file is explicitly **render-only**; do not run `up`, `create`, `start` or `down`.

The Docker-host inventory and rendered Compose dry run have **not** been performed. The current Fortis Repo container has no Docker CLI, and this session has no direct Windows-host Docker CLI channel. The candidate's external volume names and image name do not exist as verified live resources. The existing `fortis-r7-client` volume is attached to the separate Fortis Repo container; its proposed target `fortis-approvals-client-auth` is intentionally not in the Gateway Compose candidate and requires a separate Repo-container mount migration plan.

This is a one-time operational check, not a request to build an automated Docker test suite. **The Compose candidate has not yet been rendered by Docker Compose.** On the Windows Docker host, first identify the current Repo container with `docker ps`, copy the candidate file from that container to a temporary host path with `docker cp`, then run only `docker compose -f <temp-file> config`. Compare the rendered output with a fresh `docker inspect` of the deployed Gateway and Repo containers. No volume copy or runtime operation is part of this check.

## Execution boundary

No Docker container, image, project, volume, network, port, mount, credential or active service has been renamed or modified by this plan. Do not create replacement volumes or start a second Gateway during the documentation stage. After the dry run, present the final old→new map, data-copy plan, downtime implications and rollback steps for a separate explicit owner decision.
