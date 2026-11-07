# AI container isolation audit — 2026-11-04

**Mode:** read-only / dry-run. No runtime, credential, Docker, network, Windows profile or Git state was changed. Secret contents were not read or printed.

## Confirmed live observations

- Desktop Commander 0.2.52 runs in Linux Docker as UID/GID 1000 (node).
- CapEff=0, CapBnd=0, NoNewPrivs=1, Seccomp=2. Container root overlay is read-only.
- /workspace/repo, /workspace/repos and /workspace/files are read-write mountpoints backed by one ext4 fortis-repo-workspace volume tree. They are aliases/subpaths, not independent trust domains.
- /run/fortis-client is a separate read-only volume. Its grant is owned by UID 1000, mode 0600, and is readable by the current process. Read-only prevents writes, not reads.
- Docker CLI and standard Docker/containerd sockets were absent in this container. This does not prove there is no alternate host-control API.
- host.docker.internal resolves to 192.168.65.254. A default route exists. This is not LAN or host-network isolation.

## Secret exposure — metadata and readability only

The current UID 1000 can read the following files. Contents were not accessed:

| Path | Purpose | Mode / owner | Finding |
|---|---|---|---|
| /workspace/repo/.fortis-auth/github-shared/credentials | Current GitHub PAT store | 0600, 1000:1000 | AI-readable |
| /workspace/repo/.fortis-auth/github-credentials | Legacy GitHub credential store | 0600, 1000:1000 | AI-readable |
| /workspace/repo/.fortis-observatory-repo-client/token | Observatory API token | 0600, 1000:1000 | AI-readable |
| /run/fortis-client/grant | Fortis Approvals machine grant | 0600, 1000:1000; RO mount | AI-readable |

File mode 0600, directory mode 0700 and a read-only mount do not isolate secrets from a same-UID process.

## Threat-boundary assessment

| Threat | Assessment |
|---|---|
| Direct Windows filesystem access | No direct Windows host bind is recorded in current owner-provided inspect evidence; current mounts are Docker named-volume subpaths. Fresh host inspection is still required. |
| Shared project data | UID 1000 has read/write access to one persistent workspace. Git only recovers committed/pushed source, not secrets or uncommitted work. |
| Docker control | Standard socket and CLI absent. Do not add them: Docker API/socket access can be equivalent to host administrator access. |
| Secret exfiltration | Four credential files are readable and egress exists; exfiltration is therefore a realistic risk. |
| LAN / host discovery | Not isolated: default route and host gateway resolution exist. Owner-reported networks are fortis-repo-egress and rdg-personal_agents; Guard requires the latter to be internal. |
| Arbitrary shell | start_process runs commands as UID 1000. allowedDirectories constrains Desktop Commander file tools, not arbitrary subprocess access to the container's mounts and network. |
| Anonymity | Not guaranteed. VPN alone does not hide timezone, locale, DNS, host gateway or other system metadata. |

## Documentation consistency findings

1. An earlier configuration summary described three workspace paths as bind mounts with hostPath /dev/sdd. Current mountinfo and owner-provided Docker inspect evidence show subpaths of one Docker named volume, not Windows host bind mounts.
2. Some historical AI integration sections retain pre-deployment claims about path guidance or MCP UI suppression. Current-state and deployment records say these changes deployed on 2026-11-04; treat older passages as historical only where labelled.
3. Qwen source documents six read-only tools, while an owner-provided transcript records 26 tools including writes and process execution. The source-to-session mapping remains unresolved; do not rely on the read-only gateway label as a security boundary.
4. Repo1, Repo2 and Qwen share the container/workspace and UID 1000. Per-agent OS identities, volumes and secret boundaries are not established.
5. The Repo machine grant is read-only mounted but readable by UID 1000.
6. Socket absence in this container does not establish host-side socket/pipe or alternate broker exposure; keep this as a manual verification gate.

## Recommended target design

- Split agents/clients into distinct Linux UIDs and preferably distinct containers/volumes. Keep the workspace the only direct writable data surface.
- Move GitHub PAT, Observatory token and Repo machine grant out of the shared workspace and same-UID runtime. Use per-agent short-lived credentials or narrow typed brokers.
- Never mount Docker socket/named pipe or grant generic Docker API/CLI access. For self-container build/redeploy, use a host-side broker restricted to one named agent-owned target and a fixed build context. Deny host binds, privileged mode, host namespaces, devices, published ports, VolumesFrom and volume deletion. Require owner approval for lifecycle operations; current Repo container is shared by Repo1, Repo2 and Qwen.
- For occasional Windows access, compare a dedicated non-admin identity, NTFS ACLs, PowerShell JEA, Constrained Language Mode and WDAC/AppLocker. Prefer typed operations over arbitrary PowerShell strings.
- Enforce deterministic deny-by-default command policy. AST analysis and a second local/remote model may explain or score risk but must be advisory only; a model must never override a hard deny. Validate aliases, dynamic/encoded invocation, child processes, external executables, canonical paths, reparse points and network effects.
- Use controlled proxy/VPN egress with fail-closed behavior. Block LAN/private, link-local, metadata and host-gateway destinations except explicit API endpoints. Review DNS, timezone, locale and host-identifying metadata.

## Dry-run boundary

Completed read-only checks: process identity/capabilities/seccomp, mount modes and mountinfo, standard Docker socket/CLI presence, host gateway DNS, route table, credential metadata/readability, documentation and Git working-tree status.

Not performed: Windows Docker Engine inspection, Compose render, port scan, credential content read, token validation, ACL mutation, container lifecycle, volume operation, image build, PowerShell execution on Windows, VPN leak test, adversarial escape test or secret rotation. These require separate owner-approved procedures.

**Conclusion:** useful hardening exists (read-only rootfs, no capabilities, no-new-privileges, seccomp, non-root UID, no standard Docker socket), but the requested guarantee is not met. Main blockers: shared UID and writable workspace, four readable credentials, broad shell execution and unproven network egress isolation. No runtime security change was made.
