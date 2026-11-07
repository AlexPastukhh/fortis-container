# Desktop Commander MCP UI suppression — verification audit

**Date:** 2026-11-04
**Evidence class:** owner-provided Windows Docker Host output, reviewed in ChatGPT Repo2 session
**Status:** DEPLOYED; owner-run cutover PASS; live Repo2 runtime acceptance PASS; Repo1 post-cutover reconnect owner-confirmed. Qwen reconnect is not required for acceptance by owner decision.

## Scope and decision

This record covers the Desktop Commander 0.2.52 Docker patch, candidate/pre-cutover verification, successful production cutover, and post-cutover live Repo2 runtime acceptance. The candidate and preflight sections below are historical; the final sections record the deployed state and client acceptance evidence. Repo1 reconnect is owner-confirmed; Qwen reconnect is not required for acceptance.

## Candidate and pre-cutover image identities (historical)

- Active container: `fortis-repo-test`, ID `3c4b50df90381ffd23809e0c7ba5e3bf8762ac33829ce2fb3a6d44a29da2d07c`.
- Active/base image: `fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104`, ID `sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750`.
- Candidate: `fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104`, ID `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`.
- Existing older rollback: `fortis-repo-test-pre-path-guidance-20261104`, ID `04fed7b726a8536d63c4d2533cfc7ee3072956ff0c3f571504d7f709f7909030`, stopped and preserved.

The candidate builder reported: `PASS: MCP UI patch candidate built; only the reviewed environment default was added.` The candidate image configuration check confirmed the expected image ID and `DESKTOP_COMMANDER_DISABLE_MCP_UI=1`.

## Disposable runtime verification

The owner ran the candidate with `docker run --rm --network none --read-only --user 1000:1000`, mounting only a temporary probe file read-only. Output:

- `PASS: image environment inherited`
- `PASS: UI metadata disabled`
- `PASS: UI resources list empty`
- `PASS: UI resource reads blocked`
- `CANDIDATE_RUNTIME_VERIFICATION_PASS`

The probe verified the exact environment value, `shouldShowMcpUiPreviews() === false`, `listUiResources()` returning `[]`, and `readUiResource()` returning `null` for both `CONFIG_EDITOR_RESOURCE_URI` and `FILE_PREVIEW_RESOURCE_URI`. The disposable test container was automatically removed. This is candidate runtime evidence, not live MCP discovery from a connected ChatGPT client.

## Normalized pre-cutover Docker inspection

The owner supplied a read-only Windows PowerShell inspection of the active container, base image, candidate image and existing older rollback. The final normalized checks all passed:

- Active container ID and running state; active/base image ID; candidate image ID.
- Existing older rollback ID and stopped state.
- Active environment had no missing or extra entries relative to its base image; candidate environment had exactly the reviewed UI switch in addition to base defaults.
- Candidate user, working directory, command and entrypoint matched the base image.
- `ReadonlyRootfs=true`, `Privileged=false`, `CapDrop=ALL`, and `no-new-privileges`.
- No Docker host binds, no `VolumesFrom`, and no published ports.
- Exactly four expected named-volume mounts: `fortis-r7-client` RO at `/run/fortis-client`; `fortis-repo-workspace` RW at `/workspace/repo`, `/workspace/repos` (subpath `Repos`) and `/workspace/files` (subpath `Workfiles`).
- Networks `fortis-repo-egress` and `rdg-personal_agents`; network mode `fortis-repo-egress`.
- Memory 4 GiB, memory+swap 5 GiB, 2 CPUs, 512 PIDs, 64 MiB shared memory; restart policy `unless-stopped`.
- `/home/node` and `/tmp` tmpfs options exactly matched the reviewed values.

The first aggregate preflight showed several false negatives from PowerShell expression semantics, not Docker drift. The active/base environment arrays contained the same entries but were compared in order; null `Binds` / `VolumesFrom` values were counted without filtering; and `$home` collided with PowerShell's read-only `$HOME` variable because variable names are case-insensitive. A follow-up diagnostic showed no missing/extra environment entries, and the final normalized checks used filtered null collections and `PSObject.Properties` for tmpfs keys. Final output: `NORMALIZED_PREFLIGHT_PASS` and `NO CONTAINER MODIFIED`.

## Pre-cutover Guard impact analysis (historical)

The canonical Tunnel dispatcher `runtime/windows-repo/Invoke-FortisRepo.ps1` and shared `current/launchers/shared/FortisContainerPolicy.ps1` resolve the stable container name `fortis-repo-test` and pass the inspected full ID through the Repo execution path. The shared policy checks effective mounts and isolation, not a fixed image digest. Therefore this image-level UI default did not require a Repo1/Repo2 launcher or Guard source change. At the time of this pre-cutover analysis, both Guard Previews still needed to be rerun against the new container ID; the successful cutover later passed both. Do not use the stale `_go3-revision07` or historical `repo1/` / `repo2/` static-ID artifacts as the current source of truth.

At the pre-cutover stage, the older rollback container listed above preserved the pre-path-guidance image, not the active path-guidance deployment. The approved cutover therefore preserved the active path-guidance container separately under `fortis-repo-test-pre-mcp-ui-headless-20261104`. The shared-container replacement interrupts Repo1, Repo2 and Qwen because they share this container. The actual cutover and post-cutover Repo2 runtime acceptance are recorded below; Repo1 and Qwen reconnect remain separate client checks.

No production container, persistent volume, Windows profile, Guard source or active MCP process was modified during this verification. No commit or push was performed.
## Owner-approved cutover runner preparation — 2026-11-04 (historical; subsequently executed)

The owner approved proceeding with the shared-container replacement. A Windows PowerShell 5.1 runner is now staged at:

`tools/Invoke-FortisMcpUiHeadlessCutover.ps1`

The runner defaults to `-Action Preview` and performs read-only checks of the active container ID/image, candidate/base image IDs, environment, four named-volume mounts, both networks, tmpfs, security settings, resource limits, restart policy and the existing older rollback. `-Action Cutover` repeats those checks, requires the exact typed confirmation `CUTOVER MCP UI HEADLESS`, and then stages a new container from the inspected Config and HostConfig using the Windows Docker Engine named-pipe API. It does not use `--volumes-from`, host binds, image pulls, compose, volume deletion or profile edits.

The runner stops and renames the current path-guidance container to
`fortis-repo-test-pre-mcp-ui-headless-20261104`, promotes the staged candidate
to `fortis-repo-test`, restores the optional internal network, starts it, and
checks the candidate image ID, environment, mounts, networks, security and
resource policy. It then runs the live package test and both canonical
read-only Repo1/Repo2 Guard Previews. Any failure after the original container
is stopped invokes rollback: the failed candidate is retained under a separate
diagnostic name, the original container is renamed back and restarted, and
its original ID/image are verified. The older
`fortis-repo-test-pre-path-guidance-20261104` remains untouched.

A new container receives fresh `/home/node` and `/tmp` tmpfs contents. The
runner therefore invokes the hash-verified canonical Repo2 Direct Guard in
its narrowly scoped `-Mode Run` bootstrap mode after first validating the
source through the canonical dispatcher. This may recreate the recognized
missing/factory-default Desktop Commander config and create the convenience
Git config only if absent; it does not start either tunnel. If another MCP
process is already active or the config state is unexpected, the Guard fails
closed and the runner rolls back.

**Execution status at this stage: NOT YET RUN (superseded by the production cutover below).** At the time this preparation note was written, the script had only been syntax-checked; this ChatGPT Fortis Repo endpoint ran inside Linux and had no control channel to the Windows Docker Host. The owner subsequently copied and executed the runner on Windows; the successful cutover is recorded in the final sections below.

At this pre-cutover stage, live MCP resource discovery and client reconnects were still future acceptance steps. Guard Previews prove policy/runtime readiness, not successful client reconnects.


## Cutover Preview follow-up — PowerShell 5.1 null CapAdd false negative

The owner's first Windows-host run of the prepared runner stopped at the
capability assertion, before any container lifecycle operation. The cause was
a PowerShell 5.1 null-array semantic mismatch: Docker inspect can serialize an
unset `HostConfig.CapAdd` as JSON null, while `@($null).Count` evaluates to 1.
The original runner incorrectly treated that null as a capability addition.

The runner was corrected to filter null entries before evaluating CapAdd,
while still requiring exactly one `CapDrop=ALL` and rejecting every non-null
CapAdd entry. The full script passes the PowerShell parser. A PowerShell test
covering `CapAdd=$null`, an empty array, and a non-empty `NET_ADMIN` addition
passed: `NULL_CAPADD_PASS`, `EMPTY_CAPADD_PASS`, and
`CAPADD_REJECTION_PASS`. This was a runner validation bug, not evidence of Docker capability drift. At this point in the sequence, the corrected script had not yet been copied to the Windows host or rerun; the subsequent successful cutover is recorded below.


## Second Cutover Preview follow-up — empty PortBindings object

The owner recopied the corrected runner and reran `-Action Preview`. The
CapAdd check now passed; Preview stopped at `PortBindings` before any
container lifecycle operation. The runner had grouped PortBindings with
array-valued Docker fields and counted a non-null empty JSON object as one
scalar. Docker inspect may represent no published port bindings as either
null or an empty object (`{}`); the latter is not a published port.

The check now handles PortBindings separately: null, an empty JSON object, or
an empty dictionary are accepted; any actual port/protocol key is rejected;
unexpected value types fail closed. PowerShell tests passed for null, empty
JSON object, empty dictionary, non-empty JSON binding, non-empty dictionary,
and invalid scalar cases. The full runner passes the PowerShell parser and
`git diff --check` passes. This is a second Preview validation false negative,
not evidence of a published port or Docker configuration drift.

**Status at this point in the sequence:** the updated runner still needed to
be copied to the Windows host and run with `-Action Preview`. This intermediate
status was superseded by the third Preview follow-up below; the production cutover had not yet run at this point.


## Third Cutover Preview follow-up — null network Links and successful preflight

The next Windows PowerShell 5.1 Preview reached the attached-network checks and
stopped because Docker inspect represented an unset endpoint `Links` field as
JSON null. The previous `@(...).Count`-style check treated that null as one
legacy link. This was another PowerShell null-array false negative, not evidence
of a Docker network link.

The runner now filters null and whitespace-only `Links` entries before testing
the count. Actual non-empty legacy link values remain a hard failure and are
included in the error message. The bundled PowerShell test passed all four
cases: null, empty array, null/blank entries, and a real legacy link
(`LINKS_NULL_PASS`, `LINKS_EMPTY_PASS`, `LINKS_BLANK_PASS`,
`LINKS_NONEMPTY_REJECT_PASS`). `git diff --check` passed.

The owner copied this exact updated runner from the active container to the
Windows host and ran `-Action Preview`. Final output:

- Active container ID matched the reviewed path-guidance deployment.
- Candidate image ID matched the pinned MCP-UI-headless candidate.
- Both expected Docker networks were present.
- `PREFLIGHT_PASS; no container lifecycle or volume operation performed.`

**Status at this point in the sequence:** all read-only cutover preflight checks passed, but the production cutover had not yet been run. This intermediate state was superseded by the successful production cutover and post-cutover runtime acceptance recorded below.


## Production cutover — 2026-11-04

The owner ran the Windows-host cutover runner after its read-only Preview passed and supplied the exact typed confirmation. The runner staged and promoted the candidate, ran the guarded Repo2 runtime-config bootstrap, checked the live package and both canonical Guard Previews, and emitted `DOCKER_CUTOVER_PASS`.

- Active container: `fortis-repo-test`, ID `1f67b67cacf3d4435982df9c0606dcb1a89d99f3f8ac73d365f3e6bb3d2f658b`.
- Active image: `fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104`, ID `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`.
- Rollback container: `fortis-repo-test-pre-mcp-ui-headless-20261104`, preserving the prior path-guidance container. The older `fortis-repo-test-pre-path-guidance-20261104` remained separate.
- Cutover output included `GUARDED_RUNTIME_CONFIG_REPAIR_PASS`, `REPO1_GUARD_PREVIEW_PASS`, `REPO2_GUARD_PREVIEW_PASS`, and `DOCKER_CUTOVER_PASS`.
- The runner reported that no named volume was deleted and no Windows profile or tunnel lifecycle action was requested. The guarded runtime-config bootstrap does not start a tunnel.

## Post-cutover live Repo2 runtime verification

After the owner reconnected Fortis Repo in this ChatGPT account, the current Repo2 session directly called `get_config` and ran read-only runtime probes.

- `get_config`: Desktop Commander `0.2.52`; client `openai-mcp 1.0.0`; Linux Docker; Node.js `22.23.3`; UID/GID `1000`; allowed directories `/workspace/repo`, `/workspace/repos`, `/workspace/files`; container hostname prefix `1f67b67cacf3`.
- A live `start_process` check confirmed `DESKTOP_COMMANDER_DISABLE_MCP_UI=1`.
- The installed package runtime probe passed: `shouldShowMcpUiPreviews()` returned `false`; `listUiResources()` returned `[]`; reads of `CONFIG_EDITOR_RESOURCE_URI` and `FILE_PREVIEW_RESOURCE_URI` returned `null`.
- The `get_config` experiment summary still lists the `showMCPUi` A/B variant at 100%. This is not the effective UI decision: the explicit environment opt-out takes precedence and the live runtime returns `false` with no UI resources.

## Acceptance boundary and remaining checks

Both Repo1 and Repo2 Guard Previews passed during cutover. The current ChatGPT Repo2 connection subsequently reconnected and passed the live runtime checks above. Repo1 post-cutover reconnection is owner-confirmed. Qwen reconnection is not required for acceptance by owner decision. The switch suppresses MCP UI presentation and is not a security boundary.
