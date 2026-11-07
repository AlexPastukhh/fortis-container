# Repo1/Repo2 container baseline and Shared Guard contract

**Review date:** 2026-11-04

**Scope:** the shared `fortis-repo-test` Docker container used by ChatGPT Repo1, Repo2 and the Qwen proxy path.

> This is the pre-cutover source/evidence record for the former base image and container. The subsequent path-guidance image deployment and current live metadata acceptance are recorded in [the patch deployment record](../../patches/desktop-commander-0.2.52/README.md) and [historical status snapshot](../CURRENT-STATE-ARCHIVE-2026-11-04.md). This audit is not a Docker deployment recipe and does not authorize further image replacement, container recreation, volume changes or tunnel restarts.

## Scope and ownership

- `fortis-container` owns the cross-project Docker/runtime baseline and image provenance record.
- `tunnel/runtime/windows-repo/current` owns the canonical Repo1/Repo2 Windows worker and Guard source.
- The nine PowerShell files in that Tunnel directory are pinned by `source-manifest.json`; its inventory revision is `AEF7D17084F951AEAB6F98CF91E7A39E1D6043A0DAC6BC123DBF99463887B0F9` and the manifest file SHA-256 is `8036348F69BB37F94F5E6FDE529BF44A292F4EB91977CE91A491E9860AADBFCA`.
- `script-control-center` owns the Windows release/update workflow and its owner-run verification entrypoints.

## Evidence status

The Docker identity, image and initial runtime properties below are based on owner-provided Windows Docker inspection/build evidence retained in [Container build provenance](../CONTAINER-BUILD-PROVENANCE.md). On 2026-11-04 the owner also copied the GO3 verifier directly from the active container with `docker cp` and ran it on Windows. Its output confirmed the exact running container/image identity, resource values, networks, tmpfs settings, zero published ports, and both Guard Previews. This is **OWNER-REPORTED / OUTPUT REVIEWED** host-side evidence; the Linux MCP session itself still has no Docker CLI and did not independently inspect Docker Engine.

The first GO3 run's mount subsection used the wrong Docker inspect property names (`Source`/`Target`/`ReadOnly`) and is not valid mount evidence. The corrected diagnostic reads `Name`/`Destination`/`RW`/`Mode`/`Driver`/`Propagation` and deliberately omits host-side source paths. The owner completed a second Windows run on 2026-11-04; that output validated all four mount entries. The second-run evidence is recorded below and supersedes the first run's malformed mount rows.

## Recorded Repo container snapshot

| Field | Recorded value | Notes |
|---|---|---|
| Container | `fortis-repo-test` | Exact name |
| Container ID | `04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030` | Full ID from owner inspection |
| Image reference | `fortis-repo-mode:dc-0.2.52` | Current/base image, not the patch candidate |
| Image ID | `sha256:2c84fabebb34265e53b020f21a11683a4c68cbb41a08f5f11f9b01c7de5ed8c9` | Matches the retained BuildKit manifest-list digest |
| Container user | `1000:1000` | Linux `node` identity |
| Container working directory | `/workspace/repos` | Container override |
| Command | `sleep infinity` | Long-lived MCP host process |
| Root filesystem | Read-only | `ReadonlyRootfs=true` |
| Privileged | `false` | No privileged container |
| Capabilities | `CapDrop=ALL` | Shared Guard also rejects additions |
| Security option | `no-new-privileges` | Effective Linux probe checks `NoNewPrivs=1` |
| Network mode | `fortis-repo-egress` | Host/shared network namespaces are rejected |
| Restart policy | `unless-stopped` | Observed; not enforced by current Shared Guard |
| Memory | `4 GiB` | GO3 Windows inspect output; Guard ceiling is 8 GiB |
| MemorySwap | `5 GiB` (`5368709120` bytes) | Docker total memory+swap limit; not checked by Shared Guard |
| CPU | `2` (`NanoCpus=2000000000`) | GO3 Windows inspect output; Guard ceiling is 2 CPUs |
| PIDs | `512` | GO3 Windows inspect output; Guard ceiling is 1024 |
| ShmSize | `64 MiB` (`67108864` bytes) | GO3 Windows inspect output; not checked by Shared Guard |

## Storage, tmpfs and network contract

The retained mount inspection records these volume attachments:

| Volume | Destination | Mode / subpath |
|---|---|---|
| `fortis-repo-workspace` | `/workspace/repo` | Volume root, RW |
| `fortis-repo-workspace` | `/workspace/repos` | Subpath `Repos`, RW |
| `fortis-repo-workspace` | `/workspace/files` | Subpath `Workfiles`, RW |
| `fortis-r7-client` | `/run/fortis-client` | Separate volume, RO; optional in Shared Guard |

The earlier effective-mount inspection recorded `fortis-r7-client` at `/run/fortis-client` with `RW=false`, and the three `fortis-repo-workspace` destinations above with `RW=true`. The requested-mount report recorded `/workspace/repos` with subpath `Repos`, `/workspace/files` with subpath `Workfiles`, and the client volume read-only. The second Windows GO3 run now independently confirms the four volume names, destinations and read/write flags; it also reports `Mode=z`, `Driver=local` and empty propagation for each. The first GO3 run's malformed mount rows remain discarded.

`/tmp` and `/home/node` are tmpfs mounts (128 MiB each), with `nosuid,nodev,noexec`; `/tmp` uses mode 1777 and `/home/node` uses UID/GID 1000, mode 0700. The GO3 Windows output reconfirmed the exact options. The current Guard requires both tmpfs paths and restricts extra tmpfs destinations to approved `/tmp/` scratch paths, but it does not pin tmpfs size or mount flags.

The GO3 Windows output reconfirmed the exact attached network names `fortis-repo-egress` and `rdg-personal_agents`, and zero published port bindings. The Guard requires `fortis-repo-egress`; the only optional second network is `rdg-personal_agents`, and that network must be an internal bridge. The Guard rejects Docker bind mounts, unreviewed extra mounts, host/shared network namespaces and published container ports.

## Shared Guard contract

The canonical policy is `tunnel/runtime/windows-repo/current/launchers/shared/FortisContainerPolicy.ps1`. Repo1 and Repo2 both load this module; do not maintain separate copies of common trust decisions.

### Container-level checks

- Exact container name `fortis-repo-test` and a full 64-character container ID; Repo2 carries the inspected ID through its launcher and Docker exec path.
- Linux container user `1000:1000`; `Privileged=false`; `ReadonlyRootfs=true`.
- PID, IPC, UTS, user and cgroup namespaces must be private (or use Docker's empty/default private representation).
- No devices, device requests, inherited volumes or supplementary groups.
- `CapDrop` must contain `ALL`; no capability additions are accepted.
- `no-new-privileges` is required; unconfined seccomp/AppArmor options are rejected.
- Effective Linux probe requires UID/GID 1000, zero effective/bounding capabilities, `NoNewPrivs=1`, `Seccomp=2` and a read-only `/` mount.

### Resource ceilings and runtime configuration

The current Shared Guard treats these as ceilings, not exact tuning pins:

| Docker field | Guard rule | Recorded runtime value |
|---|---:|---:|
| `HostConfig.Memory` | Greater than 0 and at most 8 GiB | 4 GiB |
| `HostConfig.NanoCpus` | Greater than 0 and at most 2,000,000,000 | 2,000,000,000 |
| `HostConfig.PidsLimit` | Greater than 0 and at most 1024 | 512 |

The recorded 4 GiB / 2 CPU / 512 PID configuration is within the shared ceilings. A lower, stricter allocation is also accepted; the Guard does not require these three exact observed values.

The policy also checks the effective volume identity/access modes, approved network membership, no published ports, no injected container `NODE_OPTIONS`, and safe Linux home/Desktop Commander configuration metadata. It does not hash-pin the Desktop Commander package entry file. The Windows Tunnel Runtime executable and the shared policy source itself do have SHA-256 integrity checks.

### Explicitly not enforced by the current Shared Guard

- **Image identity/provenance:** the Preview displays `ImageId`, but `Assert-FortisContainerPolicy` does not compare it to an approved image digest or tag.
- **Restart policy:** `unless-stopped` is recorded above but is not a Guard condition.
- **MemorySwap and ShmSize:** not checked by Shared Guard. Their owner-reported live values are now known: 5 GiB total memory+swap and 64 MiB shared memory.
- **Tmpfs size and mount flags:** paths are checked, but the 128 MiB sizes and `nosuid,nodev,noexec` options are not pinned by this policy.

These are policy-design questions, not evidence that the current Guard has failed. Do not add exact-value pins without a separate decision about which fields are security requirements versus operational tuning.

## Image provenance and candidate distinction

The active baseline image is `fortis-repo-mode:dc-0.2.52` (`sha256:2c84fabebb34265e53b020f21a11683a4c68cbb41a08f5f11f9b01c7de5ed8c9`). Its ID matches the owner-provided BuildKit manifest-list digest. The original Dockerfile SHA-256 is `1717E364B2F5CD92F4C6CABB039D4272598FE573B5E6CD9CFE7357A0ABD4FA0B`; the recorded base digest is `sha256:c3de60bf2f9dd0ac6370e6117950ff62d6e339527e7472301c9c78a017978392`.

The path-guidance derivative `fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104` (`sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750`) is a **built candidate, not deployed**. It must not be treated as the active image or accepted by the current release pin until separately approved and deployed.

## Release verification decision

The existing `script-control-center/tools/Update-Windows-ControlCenter.ps1` already validates the paired Git clones, the nine-file Tunnel manifest, PowerShell syntax and both read-only Guard Previews during `-Apply`. It is the source-update workflow; it does not pin the Docker image identity.

The GO3-specific `script-control-center/_go3-revision07/Invoke-GO3-Guard-Previews.ps1` already checked the canonical Tunnel source manifest, full container ID and both Guard Preview results. This review extended that same entrypoint with an image identity gate; no parallel Preview system was created. The script now:

1. Inspects the exact container ID and requires name `fortis-repo-test`, running state and the approved image tag/ID.
2. Inspects the image by immutable ID; requires the expected tag and reviewed image defaults (runtime user, workdir, command and required environment).
3. Runs Repo1 Preview and Repo2 Direct Guard Preview against that same full container ID.
4. Requires both Preview JSON results to report the same approved image ID and `Preflight=PASS`.
5. Emits `GO3_RELEASE_VERIFICATION_PASS` only after the image gate, source-manifest check and both Guard Previews pass.

The current pin intentionally accepts only `fortis-repo-mode:dc-0.2.52`; the built path-guidance candidate remains rejected until separately approved and deployed. This is an immutable local image-ID/tag/config check against owner-provided build evidence, not signed provenance or an attestation verification. The original build context and `.dockerignore` remain unresolved.

Static contract tests pass **5/5** and the GO3 PowerShell file parses successfully with the bundled PowerShell runtime. The owner then executed the verifier on Windows by copying it from the active Docker container into `%TEMP%` with `docker cp`. The supplied run passed `GO3_TUNNEL_SOURCE_MANIFEST_PASS`, `GO3_IMAGE_IDENTITY_PASS`, both Guard Preview markers, `GO3_BOTH_GUARD_PREVIEWS_PASS` and `GO3_RELEASE_VERIFICATION_PASS`. It also emitted the live Memory/MemorySwap/CPU/PIDs/ShmSize, restart policy, tmpfs options, attached network names and zero published ports. No container/tunnel lifecycle, Windows profile edit, runtime repair or Sonar request occurred.

The first Windows run exposed a bug in the auxiliary mount formatter: it used non-existent/wrong Docker inspect keys, so `Target` was blank and the printed `Source` was a Docker-internal volume path. That first mount subsection is explicitly invalid and must not be used. The script was corrected in the Docker working tree to read `Name`, `Destination`, `RW`, `Mode`, `Driver` and `Propagation`, and to omit host source paths. The corrected script passed **5/5** static tests and PowerShell parsing, then was recopied from the active container and rerun on Windows. The second run validated all four mount entries; see the owner-side output record below.

The script and test remain uncommitted working-tree files in Docker's Script Center checkout. They are not yet present in the Windows Git clone. For an owner-side dry run, use the Docker-source copy workflow (normal, non-elevated PowerShell):

```powershell
$containerId = '04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030'
$dockerPath = '/workspace/repos/script-control-center/_go3-revision07/Invoke-GO3-Guard-Previews.ps1'
$tempScript = Join-Path $env:TEMP 'Invoke-GO3-Guard-Previews.ps1'
docker cp "${containerId}:$dockerPath" $tempScript
if ($LASTEXITCODE -ne 0) { throw 'Docker copy failed' }
& $tempScript
```

This is a read-only release verification. It must not start/stop a tunnel, start/stop/recreate a container, repair runtime config, edit Windows profiles, or issue Sonar requests. The Windows owner must run it in a normal, non-elevated PowerShell session; this Linux MCP session cannot perform the Docker/Windows runtime check.

## Remaining decisions and next checks

- **Completed 2026-11-04:** the owner copied the corrected GO3 verifier from the active container and reran it on Windows. The corrected four-entry mount diagnostic is now validated. The remaining Repo1/Repo2 runtime gate is the explicit `REPO_RECONNECT_PENDING` state; actual tunnel start/reconnect and functional acceptance remain separate, owner-controlled steps.
- Decide separately whether MemorySwap, ShmSize, RestartPolicy and tmpfs options should become Guard-enforced policy. Current agreement does not change the Shared Guard contract or its nine-file source manifest.
- Repo1 and Repo2 **Guard Preview** is complete against the active base image. Actual Repo1/Repo2 tunnel start and a separate reconnect/functional acceptance are still pending; Preview must not be reported as a successful live tunnel session.
- **At the time of this pre-cutover audit:** the path-guidance image candidate was built but not deployed. That gate was subsequently completed; see the [deployment record](../../patches/desktop-commander-0.2.52/README.md). The old container remains available as a stopped rollback artifact. Qwen reconnect is tracked separately.
- The untracked `script-control-center/_go3-revision06` cutover/resume/rollback scripts pin the former container ID `0c0f8cb2...`, while the currently verified container is `04fed7b7...`. Do not execute those revision-06 scripts against the current host; they require a fresh review/replacement plan if another cutover is needed.
- The GO3 verifier and test are still uncommitted in the Docker Script Center checkout. The Windows run used `docker cp` into `%TEMP%`; it did not require a Windows Git clone or a commit/push.

No Docker lifecycle action, volume operation, image build/pull, Windows profile change, tunnel start/stop, credential read, Git stage, commit or push was performed as part of the source/documentation work. The owner-side `docker cp` only copied the verifier out of the running container and did not alter it.


## Second owner-run Windows verification — 2026-11-04

**Evidence status: OWNER-PROVIDED / OUTPUT REVIEWED.** The owner copied the corrected `_go3-revision07/Invoke-GO3-Guard-Previews.ps1` from container `04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030` to `%TEMP%` with `docker cp` (11.1 kB reported) and executed it in Windows PowerShell. This second run validates the corrected mount formatter; it does not change the earlier evidence classification or imply that the Linux MCP session independently inspected Docker Engine.

Confirmed markers:

- `GO3_TUNNEL_SOURCE_MANIFEST_PASS`
- `GO3_IMAGE_IDENTITY_PASS`
- `GO3_REPO1_GUARD_PREVIEW_PASS`
- `GO3_REPO2_GUARD_PREVIEW_PASS`
- `GO3_BOTH_GUARD_PREVIEWS_PASS`
- `GO3_RELEASE_VERIFICATION_PASS`

Repo1 inventory counters: `REPO1_EXISTING_TUNNEL_COUNT=0`; `REPO1_EXISTING_PROFILE_COUNT=1`. These are read-only inventory values, not a tunnel-start or profile-mutation test.

The corrected mount diagnostic returned exactly four Docker `volume` attachments (driver `local`, mode `z`, empty propagation):

| Volume | Destination | Read/write |
|---|---|---|
| `fortis-r7-client` | `/run/fortis-client` | RO (`ReadWrite=false`) |
| `fortis-repo-workspace` | `/workspace/files` | RW (`ReadWrite=true`) |
| `fortis-repo-workspace` | `/workspace/repo` | RW (`ReadWrite=true`) |
| `fortis-repo-workspace` | `/workspace/repos` | RW (`ReadWrite=true`) |

The same output reconfirmed auxiliary container settings: Memory `4294967296` bytes (4 GiB); MemorySwap `5368709120` bytes (5 GiB); NanoCpus `2000000000` (2 CPUs); PidsLimit `512`; ShmSize `67108864` bytes (64 MiB); restart policy `unless-stopped`; networks `fortis-repo-egress` and `rdg-personal_agents`; published port binding count `0`. Tmpfs entries were `/home/node` (128 MiB, `rw,nosuid,nodev,noexec,uid=1000,gid=1000,mode=700`) and `/tmp` (128 MiB, `rw,nosuid,nodev,noexec,mode=1777`). These are recorded observations; they are not all enforced pins in the Shared Guard.

The script ended with `NO_TUNNEL_START_OR_STOP`, `NO_WINDOWS_PROFILE_EDITS`, `NO_RUNTIME_CONFIG_REPAIR`, `NO_SONAR_REQUEST` and `REPO_RECONNECT_PENDING`. Therefore the corrected diagnostic and GO3 read-only release verification are **PASS**, while the separate reconnect/functional gate remains **PENDING**. No actual tunnel start/stop, Windows profile edit, runtime repair, Sonar request, container replacement, volume operation, commit or push was performed. The `docker cp` copied the verifier from the container to the Windows temp directory; it did not modify the container-side source.
