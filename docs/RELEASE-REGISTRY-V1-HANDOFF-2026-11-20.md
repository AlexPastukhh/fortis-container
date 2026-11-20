# Fortis Release Registry V1 — handoff нового чата (2026-11-20)

**Status: PRODUCT DECISION ACCEPTED BY OWNER; DESIGN/SOURCE/REGISTRY IMPLEMENTATION NOT ACCEPTED.**
Эта передача не разрешает CD automation, GitHub Deployments WRITE, смену Gateway
policy/credentials, Windows/Docker execution или релиз нового image.
Единый владелец roadmap: [Fortis Release Planning / CD Queue](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue).
Normative identity/evidence boundaries: [Release Planning Contract](RELEASE-PLANNING-CONTRACT.md#post-merge-cd-queue-and-fortis-release-board).

## 1. Принятое пользователем желаемое поведение V1

1. После **подтверждённого владельцем merge PR** в GitHub `main` Fortis
   сопоставляет full Release Impact и `release/targets.yaml`, определяет
   target/environment/actions/desired main SHA и формирует очередь **в своём
   собственном Fortis Registry**, а не в GitHub Deployments.
2. Несколько merged PR могут вести к одному необходимому релизу конкретного
   target/environment с выбранным **полным** main SHA. Дубликаты не создавать;
   новая версия supersedes прежнюю, но старая запись и история сохраняются.
3. Владелец вручную выполняет существующий Use Case и reusable-скрипты; AI
   помогает составить процедуру, выполнить read-only проверки и истолковать
   результаты. Никакой самостоятельной установки или запуска контроллера из
   Registry, Gateway API или Board в V1 нет.
4. После сообщения владельца «релиз выполнен» AI сверяет исходную очередь,
   target/environment, desired SHA, связанные PR и доступные evidence. Через
   **будущий отдельный authorized typed Registry API** он фиксирует
   `REPORTED_COMPLETE`, привязку к исходной записи, источник утверждения и
   неизменяемое событие журнала. Без такого API **нельзя утверждать**, что
   сообщение в чате сохранено в реестре; пока API не реализован.
5. `REPORTED_COMPLETE` **не равно** `VERIFIED/DEPLOYED`. Последние допустимы
   только при matching protected controller receipt + independent current
   target readback. V1 не требует универсального автоматического collector.
   Если результат неизвестен, неполон либо SHA не совпадает — UNKNOWN/STOP.
6. В будущем автоматический CD будет вызывать *те же* существующие
   owner-reviewed контроллеры/UC с самостоятельными admission, audit и
   recovery gates; это отдельная работа после V1, не разрешённая сейчас.

## 2. Что именно уже выпущено

- P1 Release Labels ASK pilot и P2 UUID/receipt reconciliation приняты.
- P3/P3.4 Release Label Publisher: только owner-invoked one-shot E2E;
  не unattended, не Deployment Publisher и не CD Queue.
- **P4 GitHub Deployments READ — RELEASE COMPLETE по отчёту владельца**
  (2026-11-20). Четыре typed GET: `list_deployments`, `get_deployment`,
  `list_deployment_statuses`, `get_deployment_status`; scope `fortis-approvals`,
  `writeEnabled=false`. Отдельный [PR #159](https://github.com/AlexPastukhh/fortis-approvals/pull/159)
  (merge `585211b0240fd543b475d2196edc0bd4efb83951`) исправил UC-GW-013
  emergency Promote. По отчёту владельца Primary `running/healthy`, Promote
  завершён, новый image `sha256:8612794533d75e7dd1351924d5bff3735e79aec18d04ff91c88e31f5a181bb1c`.
  Эти Docker-факты **не проверялись** из текущего Repo-контейнера.
- Исторический original image прежнего Gateway отсутствовал. Emergency rescue
  **не доказал restore**; `DISASTER_RECOVERY_VERIFIED=NO`. Не удалять old
  Gateway/rescue TAR/image/backup, не повторять P4 Apply/Backup/Promote.
  Сохранены исторические 15 `UNCERTAIN` и 1 `CLAIMED` (по owner report).

## 3. Действующий release путь, с которым должна интегрироваться V1

- [UC-CONT-002](use-cases/delivery.md#uc-cont-002): source branch → PR →
  validated exact HEAD Release Impact/CI → owner UI merge → подтверждённый main
  → Windows Mirror только при реальной необходимости. Merge != deployment.
- [UC-GW-005](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005):
  Gateway owner Windows PowerShell 5.1 `SelfTest → Check (-Auto) → Apply (-Auto)
  → live readback → Backup (-Auto) → Promote (-Auto) → host inspect`, отдельные
  owner GO, исходные protected records и полноценные STOP gates.
- [UC-GW-006](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/recovery.md#uc-gw-006):
  на неопределённом Apply/Backup/Promote читать исходный attempt; без blind retry.
- Другие targets (Windows/Mirror, Feedbrain, RDG и т.д.) используют **свои**
  контракты установки; не распространять Gateway Check/Apply/Backup/Promote
  как универсальный протокол. Их receipts и формат readback исследовать позднее.

## 4. Границы модели и требования к V1

- Record: canonical repo, catalog-pinned target, environment, desired full 40-hex
  main SHA, catalog SHA, artifact/build identity или явно unknown/not-built,
  полный validated PR lineage, required actions, UC pointer, provenance,
  revision, audit, links to attempts. Source version != deployed version.
- Состояния/представления должны различать `QUEUED` (если достаточная evidence),
  planning with unknown installed state, `IN_PROGRESS` reported, `BLOCKED`,
  `REPORTED_COMPLETE`, `VERIFIED/DEPLOYED`, `FAILED` и `UNKNOWN`; точные enum,
  allowed transitions и invariants — **открытая design decision**, не готовый API.
- Manual mark: explicit owner statement, exact target/SHA, actor grant,
  immutable event, idempotency/revision (CAS) и readback. Owner report не
  должен мимикрировать под controller receipt. Ошибка сети не разрешает
  дублировать/переписывать history без reconcile оригинального operationId.
- `NO_DEPLOYMENT` требует полного verified releaseImpact и не создаёт задачу.
  Изменение SHA с сохранением старого результата не означает новую установку.
- Никаких direct GitHub REST/PAT/Git writes от ИИ. Existing GitHub Deployments
  READ — полезная дополнительная интеграция; GitHub Deployments WRITE/POST
  **не является prerequisite для V1** и не разрешён. Эти POST порождают
  deployment events, которые могут вызвать сторонние CD consumers.
- Не использовать Github Deployment status `success`, PR label, CI success,
  локальный чат или ручной `REPORTED_COMPLETE` как доказательство установки.

## 5. Roadmap после решения владельца

- **P5:** durable Fortis Registry + read-only post-merge planning and queue.
- **P6:** typed authorized manual result marking, append-only audit, optional
  technical evidence attachment; без автоматического релиза/collector.
- **P7:** Fortis Release Board на canonical Registry, не GitHub Projects.
- **P8:** группировка Release Batch и план ручных UC-релизов.
- **Post-V1:** отдельная программа CD automation, которая повторно использует
  существующие контроллеры и их безопасные gates.

## 6. Следующему чату: порядок действий (source-only)

1. Начать с `/workspace/repo/README.md` и `AGENTS.md`, прочитать полностью
   UC-CONT-002, UC-CONT-003 и UC-GW-009; затем применимые UC-CONT-019/024,
   UC-GW-005/006 и текущий Release Planning Contract/roadmap.
2. Проверить `fortis-container/main` и task worktree **до** изменения файлов;
   не редактировать primary `main`. Не считать этот handoff нормативным main,
   пока PR/CI/owner merge не приняты.
3. Сначала утвердить durable storage owner/location, authority, read/write
   actor policy, minimum DTO, idempotency/CAS, owner statement provenance,
   error/UNKNOWN handling, supersession and backup/recovery. Не выбирать
   GitHub Deployments как хранилище очереди.
4. Затем разработать source-only registry API and tests с negative fixtures:
   duplicate merge, same SHA, newer SHA, incomplete lineage, missing catalog,
   concurrent mark, stale record, forged report, unknown actual, lost ACK,
   repeat mark, restore. Не затрагивать Production/Windows.
5. Доставка source: task worktree → tests → commit → **typed Gateway**
   GitHub push/PR/CI → owner UI merge → exact-main readback. Новые права,
   runtime release и CD требуют отдельного owner GO.

## 7. Статус документационного изменения

Источник на момент подготовки: `fortis-container/main` =
`8710c45b8a4e786dccbd641f824ddf698269586a`; Gateway source main =
`585211b0240fd543b475d2196edc0bd4efb83951`.
Task: `task/release-registry-v1-handoff-20261120`.
Этот task меняет только `docs/BACKLOG-IMPROVEMENTS.md`,
`docs/RELEASE-PLANNING-CONTRACT.md` и этот handoff. **На момент передачи**:
файлы локально изменены в зарегистрированном task worktree, `git diff --check`
и проверка существования локальных ссылок PASS; staging/commit/PR/CI/owner
merge **не выполнялись**. Штатный Gateway `workspace.inspect` для этого task
вернул `FORTIS_HTTP_403`; ни прямым Git, ни GitHub plugin этот отказ не обходить.
Следующему чату сначала безопасно выяснить причину доступа по UC-CONT-003/
UC-GW-009 с исходными facts; только после штатного допуска продолжить PR.
Также отдельный Gateway owner current-state guide / P4 runbook содержит
исторические «not yet live» формулировки; для синхронизации потребуются
свой task worktree `fortis-approvals`, source-only review и owner acceptance.
Не утверждать, что продуктовые документы приняты в GitHub main,
пока не подтверждены PR/CI/merge.
