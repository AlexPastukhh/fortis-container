# Docker disk retention — maintenance handoff, 2026-11-26

Status: **OWNER-REPORTED host evidence / source-reviewed plan; cleanup incomplete**.
The [single backlog](BACKLOG-IMPROVEMENTS.md#docker-disk-budget-backup-retention-and-release-performance--2026-11-26)
owns task status. This handoff records the dated evidence, not a new runtime
contract or authorization. Start with workspace README/AGENTS, UC-CONT-002/003,
UC-GW-009 and [UC-CONT-021/022/023](use-cases/docker.md); host operations use
[UC-CONT-025](use-cases/host-operations.md#uc-cont-025).

## Scope and current baseline

Owner wants disk capacity back on Windows, not RAM, and does not require
restoration of arbitrary old releases. Preserve current operation, supported
rollback, future release prerequisites, original Registry genesis and protected
evidence. Other volumes, images, Repo worktrees, source, models and tools are
out of cleanup scope for now.

- Windows last measured C: 12.25 GiB free, Docker data VHDX 181.33 GiB.
  Docker Desktop CLI 4.98.0, WSL 2.7.14.0, only docker-desktop distro listed;
  Hyper-V Get-VHD and Optimize-VHD available. No independent full VHDX backup
  confirmed. No host compaction has been performed.
- After first cleanups Docker reported 305 images, 77 containers (11 running),
  126 volumes (73 active), local volumes 132.5 GB, images 23.16 GB, build cache
  1.096 GB. These are dated logical/accounting measurements, not host free space.
- Approvals clean main at eac07e20274885a75bbbaf01a6955c90e091d673 (#273).
  Current Primary source record 4893b415962e492aa35de111f70f57d2;
  previousPrimaryRecord 2538f9e8c8e1489db82a61ced74622ad.
  Primary backup pointer a4bf11646b144cd1b5de4adee5e4776f.
- Running Gateway cc412395ba14c94b8950d3a3e73c664d53300beb86b424fd0803fa451c194f5e,
  image sha256:15778778842717504ed5c860c8b66fd999a6c9e80303607920eab2305dc823f9;
  managed Registry f25b793c84d965b5e57e4c4184e19249f359a6aa33a420fa1a01a9d25acfdf2e,
  image sha256:e240e88098b3789c67cc45c832e7d11f433dcf14fcc053db443b46e3b017c43e.
  Both unless-stopped. Original Registry instance
  08ef25a7-defb-4c7a-ac83-26ba8f994fc0, revision 0, original genesis/cursor.
  v4 reader cold restart accepted, no manual reseal; old v3 reserve stale.
- Read-only typed census: 12 UNCERTAIN and one historical CLAIMED
  (2df32a24-efb1-4dac-97f6-3b66147d8944, no confirmed heartbeat).
  Do not reconcile/retry/close them as part of maintenance.
  E2–E5 remain open. Do not merge unrelated Approvals PRs while genuine
  pre-merge review is pending.

## Completed maintenance

- Five rehearsal volumes and four exited holders removed under separate
  owner GO, REHEARSAL_CLEANUP_5_VERIFIED; ~11.7 GB inside Docker.
  OwnerEvidence/rehearsal-cleanup-f6ad10d0add14f6b9cdc71ac866290b6
  retains the plan, original inventory, metadata and bounded logs.
- FileQuarantine verified cleanup of 12 inbox duplicates: 5.416 GB,
  zero errors, one unmatched file retained, quarantine store read-only.
  Total ~17.1 GB released inside Docker; Windows VHDX length unchanged.
- 17 registered Gateway backups matched their manifests and Collector
  receipts. One unmapped volume retained. Hash-manifest match is not
  RESTORE_TESTED or off-host recovery. Historical state audit found only one
  private-state match among 11 checked; activation marker is outside backup.
  No further historical state deletion is in scope.
- Identical pair 65e17cc75c1a42ab824f7095d835fdbb and
  8bb7098761344c7ea5451a6a5cac48f7: all six source/binding/receipt fields equal.
  Unmapped backup 8172b06c9ed14325be0a690ba5e525fd: 700 native files,
  closest registered backup has 724; partial clone check stopped on three
  metadata differences. Keep; no more repetitive audits without new evidence.

## Backup retention audit (not a deletion plan or executable authorization)

18 volumes ~32.16 GB. Retain six conservatively, pending supported recovery
review: current a4bf11646b144cd1b5de4adee5e4776f, previous
066d856383f14cb98c0134b46d160cf8, historical Registry recovery reserves
bc02db3a237f4a0b8cf3c5263676e57b and c6b438661bce41f18315a61812093464,
9b68a01f47f24907adaecade09896c45, and unmapped 8172b06c9ed14325be0a690ba5e525fd.
Not a proven minimal set.

Historical candidate IDs (volume prefix fortis-gateway-backup-):

| ID | Approximate decimal GB |
| --- | ---: |
| 049e219a874943a48c6e3dc796992c0d | 1.140 |
| 30922883e2db4f1db7c771ea37c2a91d | 1.188 |
| 48bccff435b546a8bed759d9a28c9295 | 1.320 |
| 65e17cc75c1a42ab824f7095d835fdbb | 1.188 |
| 70fb043402c542aea208e7ab42e54a8f | 1.269 |
| 87bf1b19418f478b83d98515a99773a9 | 1.422 |
| 8bb7098761344c7ea5451a6a5cac48f7 | 1.188 |
| 9a8f06649433464f8738d2c4dbc5d498 | 1.706 |
| b3bb44ee1a3c4afd8dffe2fb6f9b9ecb | 2.015 |
| bf0218ec39ac46c2a016bbee4debf179 | 1.127 |
| c5944dc11c954690b8e3d8bcfe459f65 | 2.065 |
| cc7ab40d29ef49109c12add803e9345b | 2.057 |
| Total | 17.685 |

Last successful Windows read-only audit:
`/workspace/repo/Workfiles/_fortis_windows_transfer_tmp/backup-retention-plan-8e2f6a4c17b9/Backup-Retention-Plan.ps1`,
SHA256 bac1f18f2316a302478bdba2d805740eec61b81e61609b06417e5091341a1ae3.
BACKUP_RETENTION_PLAN_COMPLETE: candidates=12, ready=0, scanned=231,
primaryUnchanged=true, registryUnchanged=true, deleted=false.
No other release record refs, holders or current incident attestations in
the checked scope; each references the earlier rehearsal cleanup plan.
Source review confirmed that plan contains a historical inventory, not an
operational dependency. It still needs a supported retention decision and
fresh preconditions before any effect. The owner consented to the exact
12-candidate scope in the chat; no deletion occurred.

**Blocker:** existing Primary-Gateway.ps1 emergency Promote enumerates matching
primary-backup-* records and verifies each referenced volume. Leaving a
missing volume under an active matching record can break recovery. Controller
does not expose BackupRetention. Prior tool call preparing a destructive
cleanup script was blocked by OpenAI; no script/path was created.
Do not repeat or route around that blocked call, including in a new chat.
Keep original records/receipts and supported rollback; design a reviewed
retention lifecycle without weakening admission. No blanket prune or
unreviewed record/pointer edits. Previous historical backup retention
requirements need explicit reconciliation with the new owner decision.

## Next work and measurements

1. Prefer independent, safe host-space recovery if cleanup remains blocked:
   verify VHDX type/location, restart policies, owner downtime and external
   backup availability; only supported offline compaction with restart and
   complete readback. WSL shutdown affects Docker and the Repo connector.
   No resize of a live filesystem; no reset/unregister. Quantify actual
   Windows free space before/after. No promise that logical cleanup equals
   reclaimed host bytes.
2. Review and implement supported retention at the owning Approvals repo.
   Preserve active/previous recovery and incomplete-attempt dependencies,
   historical metadata, incident evidence, and protected pointers.
   Use separate owner review, preflight, recovery tests, and verified effect;
   do not automatically clean on failed release. Avoid new heavy releases
   until sufficient host headroom. No archived full history required.
3. Set disk budget only after measurement. Peak previous release had
   roughly three additional 2.496 GB copies (7.488 GB) excluding build/cache
   growth. Reserve space for release peak and host/OS; do not use the
   virtual ext4 free-space figure as host capacity or guess a hard cap.
4. CI: source-ci.yml offline-tests ~7m50 for #271, ~5m44 for #273;
   scripts/test-source.sh uses many separate unittest processes sequentially.
   Benchmark serial vs bounded two workers on local 2-core/4-GiB runtime.
   Preserve exact suites, isolation, fail-closed behavior, workflow/required
   checks and source manifest. Job log second-page read denied; no bypass.
5. Release latency: github_pilot_helpers.py file_hash and clone_state use
   whole-file read_bytes and repeated source/target receipts, native bundle
   verification and fsync. Instrument per stage; stream hashing/copy and
   reduce redundant passes only with equivalent integrity/preservation tests.
   No weakening of protected Check/Apply, source mutation detection or recovery.
6. Resume Registry E2 genuine Core pre-merge review, then merge evidence,
   planner-only ingestion, Desired/original receipt, E3–E5. Preserve existing
   genesis and all historical Registry records, including accepted gap.

No additional host operation, source deployment or owner merge is asserted
by this handoff.
