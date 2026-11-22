# Fortis Release Registry V1 — передача следующему чату (2026-11-23)

> **Датированный readback, не live dashboard и НЕ второй план.**
> Единственная очередность E0–E5 — в
> [CD Queue roadmap](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue).
> Схемы и границы авторизации — в существующих технических контрактах.
> Перед любым действием заново проверь remote/CI/capabilities.

## 1. Проверенная точка передачи

- `fortis-approvals/main`: `6ba8027209aa3d7349e12902c8e1e2746a336a4e`,
  clean local main после штатного Gateway `update_main_from_pr`,
  PR [#233](https://github.com/AlexPastukhh/fortis-approvals/pull/233)
  **MERGED**, head `feb27afc0b463c8f747251f4e1d7e9ecc1340746`.
  Все четыре **последние exact-head** CI SUCCESS:
  `offline-tests`, `audit-projections`, `p5-retained-impact`,
  `release-impact`. Cleanup только задачи #233 — EXECUTED.
- `fortis-container/main` **до этого docs PR**:
  `6a9cd7fe3b90e51046079dba1fdc2fe7685aa88c`, clean.
  После owner merge этого документа обязательно сверить новый remote/main
  и синхронизировать контейнер через Gateway; SHA выше устареет.
- GitHub branch API показывал `protected:false` для обоих main;
  наличие/эффективность ruleset не подтверждены. CI был фактически
  проверен, но GitHub-enforced merge gate **не доказан**.

## 2. Что работает в исходниках, а что нет

- **P1–P4:** owner-accepted ограниченные Release Labels, source UUID
  reconciliation, one-shot Publisher и scoped GitHub Deployments READ.
  Это **не** Registry/CD authority.
- **P5 source до #230:** immutable post-merge Core/collector evidence,
  first-parent initial/suffix planner, SQLite history/CAS/original UUID,
  supersession, inactive WAL-safe backup. **Functional schema 3**
  (`FunctionalV1CandidateJournal`, PR #225+) — текущий *локальный*
  desired path; прежний SQLite **v1/v2** и owner-checkpoint CAS —
  исторические/отдельные source candidates, **не** live release DB.
  PR #230 проверил две записи настоящими локальными тестовыми методами
  Core/collector; provider GitHub и verifier владельца — fixtures.
- **#231–#233:** отдельный AF_UNIX candidate READ процесс, source probe
  реального cross-UID доступа и **Broker/Core + `/v1/reads` →
  Unix socket → schema 3** в интеграционных тестах. У Broker есть
  source actor/grant/policy enforcement; **не установлены новые live
  Registry routes/actor grants**, нет owner-approved host placement.
- **Фактических runtime P5–P8 нет:** не провели real host/UID pilot,
  original trusted GitHub/Core collector admission, first enrollment,
  Registry `ingest_merged`/`list_records`, P6 owner report, P7 Board
  или P8 batch. `SOURCE_ONLY_CANDIDATE_READ` — не пустая authoritative
  очередь и не verified installed. Registry WRITE и автоматический
  CD **DENY**, `FUNCTIONAL_V1_GO` и `HARDENED_REGISTRY_GO` не выданы.
- В `fortis-container/tools/registry/release_state_projection.py`
  есть только **offline** P5→P6→P7 projection fixture; не запускать
  его как второй Registry writer.

## 3. Продолжение: вертикальные E2E, не очередная серия offline cuts

**Следующий эффектный результат — E1+E2**, см. точную таблицу E0–E5
в [единственном roadmap](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue).

1. **E1: host-to-Broker READ до реального ответа.** Owner выбирает
   non-Production host, отдельно утверждает UID/GID, private SQLite,
   socket directory, encrypted backup, review source/image и grants.
   Из принятых #231/#232/#233 выполнить Broker `/v1/reads` → настоящий
   AF_UNIX → persisted schema 3 candidate; разные real UID, kernel
   `EACCES/EPERM` для Repo, reboot/backup/readback, DENY malformed,
   revoked grant, missing DB. **No WRITE**, еще `SOURCE_ONLY`.
2. **E2: полезная P5 вертикаль в том же pilot.** После отдельного
   owner-approved source/host security review: реальный owner-reviewed
   merged PR → authenticated original collector/CI/review/catalog →
   проверенный forward-first-parent lineage → **scoped**
   `registry.ingest_merged` → persistent desired → Gateway Registry
   READ в одном repo/target/env; exact UUID/idempotent recovery,
   missing evidence/unknown outcome = STOP, valid no-deployment = 0
   target records. First enrollment pin только по свежему accepted
   main/catalog/policy, **не по SHA этого handoff**.
3. **E3/E4:** продолжать **этот же E2E**, не создавать второй контур:
   owner manually executes existing release UC → отдельно разрешённый
   `REPORTED_COMPLETE` (P6) → minimum Board desired/reported/verified
   (P7) → второй real merge supersedes desired → pending остаётся,
   P8 строит *ручной* batch. Без controller receipt + independent
   installation-time readback `verifiedInstalled=UNKNOWN`.
4. **E5:** неполное CI, пропущенный merge, lost ACK/duplicate UUID,
   restart/restore, конфликты revision/catalog, socket/grant revoke,
   stale owner report, actual UNKNOWN не могут стать ложным SUCCESS.
   **Только отдельный owner `FUNCTIONAL_V1_GO`**, не merge PR.

## 4. Источники, ограничения и порядок доставки

- Начать с `/workspace/repo/README.md`, `/workspace/repo/AGENTS.md`,
  [UC-CONT-002](use-cases/delivery.md#uc-cont-002),
  [UC-CONT-003](use-cases/delivery.md#uc-cont-003) и
  [UC-GW-009](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009).
  Любые GitHub/commit/task/PR операции — **только typed Gateway**,
  с exact-head prerequisites; прямой push/GitHub connector не использовать.
- [Release Planning Contract](RELEASE-PLANNING-CONTRACT.md) владеет
  статусами/версиями/блоком Release Impact; [P5 Design](RELEASE-REGISTRY-P5-DESIGN.md)
  владеет D1–D7; [Approvals typed boundary](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/RELEASE-REGISTRY-P5-TYPED-BOUNDARY.md)
  и [collector contract](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/RELEASE-REGISTRY-P5-POST-MERGE-GATEWAY-CONTRACT.md)
  — точными source schemas. [Owner runbook](RELEASE-REGISTRY-P5-OWNER-RUNTIME-RUNBOOK.md)
  — **поздний hardened checkpoint/witness**, не prerequisite
  ограниченной Functional V1. Старые handoff 2026-11-20/21 —
  архивные snapshots, не указания продолжать их task.
- Существующий Core/Owner Portal — единственный источник ASK/WebAuthn;
  checkpoint/witness, когда появятся, относятся к **целостности**,
  а не к новой машине авторизации. Runtime volume, grants, deployment,
  enrollment и Prod/Windows требуют отдельных owner approvals.
  `REPORTED_COMPLETE` ≠ `DEPLOYED`. Unknown actual не скрывать.
- **Сохранить чужой незавершённый WIP:** approvals worktree
  `registry-checkpoint-one-shot-listener-20261122`,
  последнее наблюдение: модифицирован
  `fortis_approvals/registry/owner_peer_boundary.py`.
  Не чистить, не коммитить, не публиковать его из задач V1.
- Для нового implementation cut: **одна функциональная вертикаль,
  один implementation+docs PR** в принадлежащем коде repo, не отдельный
  PR ради повторения спецификаций. Проверить CI на точном SHA:
  `offline-tests`, `audit-projections`, `p5-retained-impact`,
  `release-impact`; owner делает Merge в GitHub UI.
  После — Gateway `update_main_from_pr` и cleanup только своей
  завершённой worktree. После merge этого docs PR не выполнять
  Windows sync/Registry activation: нет Windows consumer/runtime GO.

