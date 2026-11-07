# Desktop Commander 0.2.52 — MCP UI suppression

**Status: DEPLOYED; CUTOVER PASS; LIVE REPO2 RUNTIME ACCEPTANCE PASS; REPO1 RECONNECT OWNER-CONFIRMED (2026-11-04).** Repo1 and Repo2 Guard Previews passed during cutover. Qwen reconnect is not required for acceptance by owner decision.

This is a separate follow-up to the completed path-guidance patch. It keeps
the G2-tested environment contract:

`DESKTOP_COMMANDER_DISABLE_MCP_UI=1`

The original G2 wrapper in `tunnel/runtime/host-g2/g2-stdio-gate.py` sets
this variable for the Desktop Commander child. G2 acceptance records 26
tools, zero UI metadata and zero UI resources. The G2 installed
`server.js` / `headless-mode.js` implementation is not archived in the
mounted source repositories, so this is a behavior-compatible Docker
implementation of the same opt-out contract, not a byte-for-byte port.

## Why both code paths are patched

Desktop Commander 0.2.52 has two independent UI exposure paths:

1. `utils/mcp-ui-ab-test.js` decides whether `tools/list` includes UI
   metadata. Its normal feature-flag result is currently `showMCPUi`.
2. `ui/resources.js` supplies `resources/list` and resource reads. The
   server's `ListResources` handler calls `listUiResources()` directly,
   independently of the A/B decision.

The patch makes the exact value `'1'` an explicit opt-out:
- `shouldShowMcpUiPreviews()` returns false before consulting A/B flags.
- `listUiResources()` returns an empty list.
- `readUiResource()` refuses both UI resource URIs while disabled.

Unset or non-`1` values preserve existing behavior. The A/B assignment,
normal tool catalog, and non-UI MCP functionality are not changed.

## Source pins and disposable test

Package: `@wonderwhy-er/desktop-commander@0.2.52`

| File | Original SHA-256 | Patched SHA-256 |
|---|---|---|
| `dist/utils/mcp-ui-ab-test.js` | `978c72e71812e555f6e90cf107d936be5777f60f2e2658109af92513a2a06a42` | `df2837d2169abd6cd467e34fdc6f5cfc482845a316126d55d052ced5f35d8455` |
| `dist/ui/resources.js` | `7d4bd8fc68b75333176d4dc8363b92323fc63d19334cc6727d8348d56b1879ee` | `73dd05506000a4cbb71c8c1dfb4001b8cb8d67705f0a1a93cbd4b153b757c311` |

The deployed path-guidance file remains byte-identical:
`system-info.js` SHA-256
`128c7f8c29dab1dd95e277d7929bc6dc05ade62a00d0df8b345bf04d7929c2f1`.
The common `index.js` is unchanged; its SHA-256 remains
`a4145198dc75cd34e7c7452c2054b4cc0d29e199ae1459961a17e4da25a13500`.
The patch also pins the reviewed UI wiring context:
- `server.js`: `dacffa416d0a46351aa553e6b05e51a10638bd190821eda03032de045b9f2aaf`
- `ui/contracts.js`: `47559cdf2b1e806dbda0cef8d7e9eda4a42b3b32df0ce10b418b3ca37c501bad`


At candidate stage, the patch was applied to a disposable copy under `/tmp`. Its test passed for metadata suppression, empty resource listing, denied resource reads, normal behavior when unset/`0`, existing A/B show/hide behavior, and preservation of the path-guidance hash. The production package was subsequently supplied through the deployed candidate image rather than modified in place.

## Deployed image lineage

The Dockerfile derives from the currently deployed path-guidance image:
`fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104`,
image ID
`sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750`.

It adds only:
- the two source patches above;
- image default `ENV DESKTOP_COMMANDER_DISABLE_MCP_UI=1`.

Using the image-level default means Repo1, Repo2 and other
container-side Desktop Commander children inherit the same switch without
editing their Windows launchers or the shared Guard. The existing
`NODE_OPTIONS` quiet-log preload is left unchanged. The variable is a UI
presentation opt-out, not a security boundary.

Deployed image tag:
`fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104`.

## Candidate build procedure — Windows Docker Host (historical)

Run from an ordinary PowerShell window on the Docker Host:

```powershell
$script = Join-Path $env:TEMP 'fortis-build-mcp-ui-headless-candidate.ps1'
docker cp fortis-repo-test:/workspace/repos/fortis-container/patches/desktop-commander-0.2.52-mcp-ui-headless/build-candidate.ps1 $script
if ($LASTEXITCODE -ne 0) { throw 'Could not copy candidate builder from Docker.' }
& $script
```

The builder pins the currently active container ID, path-guidance image tag
and image ID, read-only rootfs, and confirms neither the container nor base
image explicitly overrides the UI variable. Docker may report
`Config.Image` as either the tag or the immutable SHA-256 reference depending
on how the container was created; the builder accepts both forms but always
requires the actual container `Image` ID and the base tag's resolved ID to
equal the pinned SHA-256. It builds with `--network=none
--pull=false`, then verifies that user, command, entrypoint, workdir and all
base image environment entries are preserved, with exactly one new
`DESKTOP_COMMANDER_DISABLE_MCP_UI=1` entry.

**Candidate-build scope:** this builder did not create, start, stop, restart or replace any container. Production deployment was performed later by the separate owner-approved cutover documented below.


## Candidate build and pre-cutover verification — 2026-11-04 (historical)

Owner-run Windows Docker Host build:

- Base image: `fortis-repo-mode:dc-0.2.52-fortis-path-guidance-20261104`,
  ID `sha256:1b582246edf85fa885736d1d9c325cc33697ab7cd511c73dcfb3394ed7b76750`.
- Candidate: `fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104`,
  ID `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`.
- Builder output: `PASS: MCP UI patch candidate built; only the reviewed
  environment default was added.`

A disposable candidate runtime test passed all four assertions: image
environment inherited; UI metadata disabled; UI resource list empty; UI
resource reads blocked. The test checked the config-editor and file-preview
resource URIs, ran with `--network none --read-only --user 1000:1000`, and
used `--rm`; the disposable container was automatically removed.

A separate normalized read-only Windows pre-cutover inspection passed active,
base, candidate and rollback identity; environment; image defaults; security;
all four named-volume mounts and both networks; resource limits; restart
policy; no host binds, `VolumesFrom` or published ports; and both tmpfs
entries. The first aggregate check's false negatives were corrected as
PowerShell array/null handling and a `$home`/`$HOME` variable-name collision,
not Docker configuration drift. See the dated [verification audit](../../docs/audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md).

## Production deployment and post-cutover acceptance — 2026-11-04

**Deployment: PASS.** The owner ran `tools/Invoke-FortisMcpUiHeadlessCutover.ps1 -Action Cutover` on the Windows Docker Host after the read-only Preview passed and supplied the exact typed confirmation. The runner staged and promoted the candidate, ran the guarded Repo2 runtime-config bootstrap, checked the live package and both canonical Guard Previews, and emitted `DOCKER_CUTOVER_PASS`.

- Active container: `fortis-repo-test`, ID `1f67b67cacf3d4435982df9c0606dcb1a89d99f3f8ac73d365f3e6bb3d2f658b`.
- Active image: `fortis-repo-mode:dc-0.2.52-fortis-mcp-ui-headless-20261104`, ID `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`.
- Rollback container: `fortis-repo-test-pre-mcp-ui-headless-20261104`; it preserves the prior path-guidance container. The older `fortis-repo-test-pre-path-guidance-20261104` was not repurposed.
- Owner-run output included `GUARDED_RUNTIME_CONFIG_REPAIR_PASS`, `REPO1_GUARD_PREVIEW_PASS`, `REPO2_GUARD_PREVIEW_PASS`, and `DOCKER_CUTOVER_PASS`.
- The runner reported no named volume deletion and no Windows profile or tunnel lifecycle action. The guarded runtime-config bootstrap does not start a tunnel.

After the owner reconnected Fortis Repo in this ChatGPT account, live MCP checks reported Desktop Commander `0.2.52`, client `openai-mcp 1.0.0`, Linux Docker, Node.js `22.23.3`, UID/GID `1000`, and the expected workspace paths. A live process check confirmed `DESKTOP_COMMANDER_DISABLE_MCP_UI=1`. A direct probe of the installed package passed all four checks: `shouldShowMcpUiPreviews()` returned `false`; `listUiResources()` returned `[]`; reads of `CONFIG_EDITOR_RESOURCE_URI` and `FILE_PREVIEW_RESOURCE_URI` returned `null`.

The `get_config` experiment summary still lists the `showMCPUi` A/B variant at 100%. This is not the effective runtime decision: the explicit environment opt-out takes precedence and the live function returns `false`. The switch suppresses UI presentation; it is not a security boundary.

**Client acceptance boundary:** both Repo1 and Repo2 Guard Previews passed during cutover. The current ChatGPT Repo2 MCP connection subsequently reconnected and passed the live runtime checks above. Repo1 post-cutover reconnection is owner-confirmed. Qwen reconnection is not required for acceptance by owner decision; no Qwen reconnect confirmation is outstanding for this deployment item. The detailed evidence and limitations are in the [dated verification audit](../../docs/audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md).
