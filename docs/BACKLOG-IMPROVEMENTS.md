# Backlog improvements — Fortis Container

**Status:** ACTIVE BACKLOG. Завершённые этапы отмечаются отдельно с evidence; будущие пункты **не разрешают** выполнять runtime operations без owner review. Это единственный backlog репозитория. Исторические source/plan записи здесь не являются текущим live state.

## Mirror unified API — P0 review (2026-11-15)

UC-CONT-003 содержит узкое **activation-gated proposal**, не разрешение
делегировать GitHub через произвольный собственный API. Owner security review
[MIRROR_API_CONTRACT_V1][mirror-unified-p0], согласование UC-GW-012 и source PR
предшествуют P1; до owner acceptance новый путь не включать. Отдельно принять
model B signing/verification boundary и сохранить обычный native GitHub
workflow Repo. Live READ/ASK, Windows/Gateway releases и port/DB rollback
подтверждаются владельцами проектов; source contract не заменяет эти gates.

[mirror-unified-p0]: https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/MIRROR_API_CONTRACT_V1.md

## Priority group A — tool isolation, credentials and Git

These three topics belong next to each other because they share the same trust boundary.

### A1. Tool isolation and metadata accuracy

- **Completed 2026-11-04 — Fortis path-guidance correction:** the hash-pinned Desktop Commander 0.2.52 derivative was deployed to `fortis-repo-test`; post-cutover Docker verification passed, both Repo1/Repo2 Guard Previews passed, Repo2 live MCP metadata was verified and Repo1's corrected description was owner-confirmed. The path-guidance plan item is closed. The old container remains stopped for rollback; Qwen reconnect is not required for acceptance by owner decision, while the separate source-provenance observation remains non-blocking. See the [deployment record](../patches/desktop-commander-0.2.52/README.md) and [GO3 baseline audit](audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md).
- **Completed 2026-11-04 — Desktop Commander MCP UI suppression:** the behavior-compatible 0.2.52 patch preserves the deployed path-guidance behavior and adds the G2-proven `DESKTOP_COMMANDER_DISABLE_MCP_UI=1` image default. Candidate build, disposable runtime checks and normalized Windows-host pre-cutover checks passed; the owner then executed the typed-confirmation cutover successfully. Both Repo1/Repo2 Guard Previews passed; Repo2 live runtime directly verified the environment switch, false UI-preview decision, empty UI-resource list and blocked reads for both UI resources; Repo1 post-cutover reconnect is owner-confirmed. The former path-guidance container is preserved as rollback; no named volume was deleted and no Windows profile or tunnel lifecycle action was requested. Qwen reconnect is not required for acceptance by owner decision. See the [verification audit](audits/DOCKER-MCP-UI-HEADLESS-2026-11-04.md), [AI integrations](AI-INTEGRATIONS.md) and the [deployment record](../patches/desktop-commander-0.2.52-mcp-ui-headless/README.md).
- Define separate capability profiles for read, write, process execution and deployment.
- Decide whether ChatGPT and Qwen need separate Linux identities, containers, mounts or workspace roots.
- Separate shared project files from credentials, runtime state and owner-only files.
- Treat MCP tool filtering as an interface restriction, not an OS security boundary.
- Add lightweight unit tests for pure allowlist/policy decisions, while keeping OS permissions as the actual enforcement layer; validate real container boundaries manually rather than building Docker mocks.

#### Optional host PowerShell and container-control bridge (PLANNED)

The normal execution path remains inside the existing Repo container. Investigate a separately brokered, least-privilege path for the occasional task that genuinely needs the Windows host or needs to rebuild/manage the agent's own container. Do not expose an unrestricted host shell as the shortcut.

- Compare a dedicated non-admin Windows service account plus NTFS ACLs, PowerShell JEA, Constrained Language Mode, WDAC/AppLocker and a small typed-operation broker. Protected owner directories and secrets must deny the AI identity both read and write access; verify inherited ACLs, traversal, junctions/reparse points and alternate paths.
- Prefer typed operations with fixed verbs, validated parameters and canonicalized paths over arbitrary `powershell -Command`, CMD, script text or free-form command strings. Keep the broker out of the owner's interactive profile and credentials.
- If a command-policy layer is added, parse PowerShell syntax/AST and validate the full execution chain: aliases, encoded/dynamic invocation, child processes, external executables, environment variables, working directory, file paths and network destinations. A text blocklist alone is not an enforcement boundary.
- Use deterministic deny-by-default policy as the enforcement layer. A second local or remote model may provide risk scoring/explanations, but must be advisory only; it must never turn a policy-denied command into an allowed command. Unknown or high-impact operations require explicit owner approval and an auditable receipt.
- For container self-management, use a narrow host-side broker for a named agent-owned target and an allowlisted build context. Never mount the Docker socket/named pipe or grant generic Docker API/CLI access to the AI. Deny host binds, privileged mode, host namespaces/network, devices, `VolumesFrom`, published ports and volume deletion; require owner approval for stop/start/recreate or other lifecycle changes. Account for the fact that the current Repo container is shared by Repo1, Repo2 and Qwen.
- Design egress separately: allow only required external services through a controlled proxy/VPN with fail-closed behavior; block private/LAN, link-local, metadata and host-gateway destinations except explicitly approved API endpoints. Do not claim anonymity from a VPN alone; review DNS, timezone, locale and host-identifying metadata.
- Acceptance must include adversarial tests proving that protected files cannot be listed/read/written, command-policy bypasses fail closed, child processes inherit restrictions, and the broker cannot escape its target container or approved network/API surface.

### A2. Authentication and credential isolation

- **Verified 2026-11-07:** token-scoped multi-repo Gateway публикация проверена
  для `fortis-approvals`, `fortis-container`, Mirror, Tunnel, Script Center и
  Tab Notifier. Прежний 403 у `fortis-container` преодолён; remote сам по себе
  не доказывает permissions. Для каждого нового repo/operation проверять
  token scope и live policy по [UC-CONT-018](use-cases/delivery.md#uc-cont-018).
- Остаточный риск: старые Repo credentials могут сохраняться в shared workspace;
  наличие нового маршрута не доказывает их отзыв/удаление. Отдельно проверить
  зависимости и выполнить owner-controlled rotation/removal, не читая token
  bytes и не возвращая helper как fallback.
- Включить Repo Observatory token и machine grant в credential inventory;
  `0600`/`0700` и read-only mount не изолируют процессы с одним UID.
- Complete migration of remaining repository-specific GitHub routes to the scoped Gateway native workflow; do not enable direct network Git publication.
- Avoid placing long-lived credentials in the common workspace.
- Give each agent or service its own machine identity and least-privilege scopes where appropriate.
- Review the Repo machine grant exposure to same-UID processes.
- Keep Gateway Sonar token, machine grant, TLS identity, owner WebAuthn and GitHub PAT as separate credential domains.
- Define rotation, revocation, backup and incident-response procedures.

### A3. More controlled Git workflow

- Protect `main` for repositories where a PR-based model is appropriate.
- Use feature branches for substantial work and true parallel development.
- Use Pull Requests, required CI and explicit review boundaries.
- Add CODEOWNERS or equivalent ownership metadata for shared source boundaries.
- Define when direct-to-main remains acceptable and who can authorize it.
- Use worktrees deliberately for parallel tasks; avoid uncontrolled branch/worktree proliferation.
- Route GitHub publication through Gateway with explicit repository and operation scopes.
- Explicitly prohibit force-push, history rewriting and cleanup of another task's worktree.

The ordinary project workflow uses primary main plus task worktrees, PR review and approved merge. See [UC-CONT-002](use-cases/delivery.md#uc-cont-002).

## Priority group B — source boundaries and releases

- **Completed 2026-11-03:** source inventory, original SHA-256 manifest and owner-approved standalone `fortis-approvals` repository at `/workspace/repos/fortis-approvals`; the original RDG subtree remains untouched. See the [source extraction audit](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/audits/SOURCE-EXTRACTION-2026-11-03.md).
- **Completed 2026-11-03:** selected offline/static regression run on the extracted candidate: 198 tests passed across 26 suites. Two historical-pointer test suites were corrected to read the preserved archive originals and verify the deploy-path archive pointers separately. This is not a full-suite or live Gateway/Sonar acceptance; missing `cryptography` and `fido2` still block additional WebAuthn-dependent tests. See the [test report](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/TEST-RESULTS-2026-11-03.md).
- **Historical owner decision 2026-11-03:** the extracted tree became the canonical standalone `fortis-approvals` source and the original RDG subtree remained untouched. The old *no commit/no remote* status is superseded: canonical source is published and the active Gateway scope is recorded in [current state](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/guides/FORTIS-APPROVALS-SECURE-DEVELOPMENT.md).
- **Historical 2026-11-03 proposed Compose naming, superseded for active Primary:** the draft named a Compose `gateway` service and `fortis-approvals-*` resources; the owner ultimately promoted the existing container in place to `fortis-gateway` on 2026-11-07. Do not use former Compose names to locate, launch or rename the active runtime. See [naming proposal](NAMING-AND-RENAME-PLAN-ARCHIVE-2026-11-04.md) (history) and [verified cutover](https://github.com/AlexPastukhh/fortis-approvals/blob/main/fortis_approvals/evidence/FORTIS-PRIMARY-CUTOVER-LIVE-20261107.md).
- **Original Compose-level rename proposal — superseded as a Primary cutover plan:** the render-only Compose candidate `fortis_approvals/deploy/compose-fortis-approvals-dryrun.yaml` remains a historical candidate, not a live launcher. On 2026-11-07 the owner instead promoted the *existing* Gateway in-place to `fortis-gateway`, verified autostart and stopped/retained Legacy; see [cutover evidence](https://github.com/AlexPastukhh/fortis-approvals/blob/main/fortis_approvals/evidence/FORTIS-PRIMARY-CUTOVER-LIVE-20261107.md). No broad Compose/volume renaming is implied or authorized by that migration.
- **Owner decision 2026-11-03:** do not create a separate Qwen repository or move its files now. Keep `/workspace/files/Qwen-Fortis-MCP` in place; revisit ownership only if the integration later needs independent release/versioning.
- **Completed 2026-11-05:** ChatGPT / Qwen MCP documentation consolidation;
  `AI-INTEGRATIONS.md` owns the shared catalog, Qwen README owns its transport.
  The route remains OWNER-REPORTED; full schema comparison is not archived.
- Naming-only completion of 2026-11-05 is retained in the
  [historical record](FUTURE-IMPROVEMENTS-ARCHIVE-2026-11-05.md#fortis-approvals-gateway-naming-cleanup-completed--2026-11-05).
  It does not describe the active Primary after the 2026-11-07 cutover.
- Review stale module docstrings in `fortis_approvals/repo_action_contract.py` and `fortis_approvals/sonar.py` as a separate code-maintenance task; do not infer deployed behavior from old comments.
- Separate canonical source, development worktree, deployed image and historical snapshot in release manifests.
- Add reproducible build metadata and source-to-image provenance.
- Keep runtime secrets and state out of source repositories.

## Priority group C — backup and recovery

- Define per-volume backup policy and retention.
- Test restore into an isolated environment before relying on backups.
- Preserve image digests, Compose references, source manifests and required package versions.
- Document recovery of Repo workspace, Git credentials, Gateway state, TLS identity, machine grants and Sonar credentials separately.
- Add post-restore integrity and connectivity checks.

## Priority group D — Approval and multi-agent growth

- Extend actor-specific machine identities and scopes.
- Expand typed service operations only with explicit policy and tests.
- Preserve the human owner as the authority for ASK operations.
- Add audit receipts and reconciliation for any new mutation.
- Do not add autonomous schedulers or multi-agent writes without a separate safety review.

## Implementation gates

Before changing any item:
1. Confirm the current deployed source and target.
2. Review the relevant threat model and owner scope.
3. Prepare a read-only Preview and rollback plan.
4. Use proportionate validation: simple unit/static checks for pure logic; manual owner verification for Docker CLI, volumes, Windows HOST, TLS, WebAuthn and live external APIs. Do not build heavy automation solely to imitate those environments.
5. Obtain explicit owner approval for runtime, credential or Windows changes.
6. Update this document and the current-state evidence after acceptance.

## Fortis Release Planning / CD Queue

**Fortis Release Planning / CD Queue — CURRENT ROADMAP (решения 2026-11-14).**
Нормативный источник правил классификации, `release/targets.yaml` и Release Impact:
[Release Planning Contract](RELEASE-PLANNING-CONTRACT.md).
Исполняемый код вычисления Release Labels и read-only admission:
[fortis-release-impact-action](https://github.com/AlexPastukhh/fortis-release-impact-action).
Gateway-контракт изменения labels:
[UC-GW-011](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-011).
Этот раздел — **единственный живой план** дальнейших работ, не отдельный новый нормативный контракт, не release receipt и не разрешение на runtime-изменения.

### Принятый продуктовый результат

После owner merge PR в `main` Fortis должен показать, **какие CD-действия ожидаются**,
для каких `repository / target / environment`, на каком source SHA и по каким
изменениям. После защищённого применения и независимой проверки Fortis должен
отразить **что действительно установлено**. Пользователь на Windows сможет читать
общие опубликованные GitHub-данные напрямую через GitHub REST API с подходящей
аутентификацией; ИИ продолжает обращаться к GitHub **только через Fortis Gateway**
с разрешёнными typed READ. Собственная **Fortis Release Board** отображает те
же данные; GitHub Projects не нужен и **исключён из текущего плана**.

Объект учёта — не только репозиторий: **repository + deployment target +
environment + desired source/artifact identity**. Репозиторий — агрегированное
представление очереди. Один репозиторий может содержать несколько targets;
несколько targets могут использовать один build unit/image. PR и merge — входные
события и ссылки на изменения, но не отдельная единица физической установки:
один проверенный deployment может покрыть несколько merged PR. Queue и Board
должны также группировать по repo, action, status и release batch.

### Текущие факты и граница готовности (P1 проверен 2026-11-16)

- **Уже принято в source**: общий Release Impact v1, каталоги targets в пяти
  enrolled проектах, точный PR HEAD/full merge-base diff, вычисление
  `release:*` / `build:*` labels, read-only admission с обязательными
  `Source CI` и `Fortis Release Impact`, полный latest attempt/jobs,
  Gateway snapshots, trusted preview и необязательный owner-ASK sender.
  В `fortis-release-impact-action/main` это commit
  `27bdc57c160fb5535b624003b88122d0169fe079` (PR #8).
- **Live Gateway READ проверен**: `get_pr_release_impact_evidence`,
  `list_repository_labels`, `list_pr_labels`,
  `get_pr_release_label_context`. Release Labels mutations
  `create_release_label`, `add_pr_release_labels`,
  `remove_pr_release_label` доступны с `policy=ASK`,
  `unknownEffect=STOP`, `automaticPublisher=NOT_ACTIVE`,
  `scope=registered-open-same-repo-task-PR-only`. Это не автоматический
  publisher и не deployment-сервис.
- **P1 PASS — live pilot проверен 2026-11-16**: на
  [fortis-approvals PR #76](https://github.com/AlexPastukhh/fortis-approvals/pull/76)
  при точном HEAD `217af4744bb927062bb987c5ef0e5361b70816c5` и исходных
  labels `[]` независимо пересчитан `release:no-deployment`.
  Source CI `43241792280`, attempt 1, jobs `offline-tests` / `audit-projections`,
  и Release Impact `43241792742`, attempt 1, job `release-impact`, успешны.
  Одна ASK `ac487c24-600e-4bae-a878-5c655bce2025` получила owner WebAuthn
  approval и Core `EXECUTED`; полная история `PENDING → APPROVED → DISPATCHED
  → EXECUTED` и original-UUID-bound GitHub receipt проверены. Независимый
  readback подтвердил прежний HEAD и ровно `release:no-deployment`.
- **Завершение source workflow после пилота**: владелец слил PR #76 через
  GitHub UI. Merge/main `60686553d49f6bd94baffc36f1ccf63c6d8d8f2e` принят в
  чистый Docker main через `workspace.update_main_from_pr`, request
  `22600bee-e184-4f1a-9b85-1ac75e5cef87`, `EXECUTED`. Защищённая очистка
  pilot worktree, его локальной task-ветки и регистрации подтверждена request
  `7a09c5f0-a396-40b2-bee4-a823f14fbd5a`, `EXECUTED`, и локальным readback.
  Windows sync для этого docs-only пилота не требовался.
- **Обнаруженный gap P2**: inspector ошибочно требовал соседние глобальные
  audit IDs внутри одной заявки. Полнота P1 audit отдельно проверена
  по страницам; исправление и отрицательные регрессии опубликованы в
  [fortis-approvals PR #101](https://github.com/AlexPastukhh/fortis-approvals/pull/101).
  Это source review, а не утверждение об установленном Gateway image.
- **Не готово**: полное закрытие P2 для label-specific recovery/reconciliation,
  автоматический label publisher, post-merge CD queue, typed Gateway
  GitHub Deployments READ/WRITE, verified deployment publisher и Release Board.
  Принятый Repo intent coordinator уже ведёт durable journal и историю
  попыток; P2 должен использовать его и проверить недостающие label cases.
  Метка и успешный CI не являются доказательством runtime deployment.

### Предлагаемые источники и потоки данных (DESIGN; не live capability)

1. **Планируемое:** PR metadata/merge evidence и проверенный Release Impact;
   каталог `release/targets.yaml`; точный Git SHA и полный набор изменённых
   путей; требуемые actions/build units; обязательные CI. Нормативная
   классификация остаётся у Release Planning Contract и одного pinned
   validator, а не дублируется в Gateway/Board.
2. **Публикуемая CD-проекция:** предложено использовать GitHub **Deployments
   API + deployment statuses** (например `queued`, `in_progress`,
   `success`, `failure`) с явной версионированной схемой метаданных для
   `repository, target, environment, desiredSha, buildUnit, actions,
   linkedPRs, immutableOperationId`. Точный способ кодировать target
   (environment naming / payload), поддерживаемый набор states, права
   API и поведение GitHub deployment events требуют отдельного прототипа
   и review. `queued` — ожидаемая доставка, а не уже начатое применение;
   `success` — только после подтверждённой установки. Не создавать
   deployment на каждый PR автоматически без стратегии объединения
   изменений/versions. При новом `main` SHA старый `success` не покрывает
   новый desired version автоматически.
3. **Фактически применённое:** защищённые Fortis deployment receipts +
   independent target/environment readback (source SHA, image/package digest,
   actual installed identity, verification evidence). Сначала исследовать,
   достаточны ли уже существующие records; Windows controller не менять,
   не запускать `Check/Apply/Return/Backup/Promote` в рамках планирования.
   Если record недостаточен, отдельно согласовать минимальное дополнение
   соответствующего controller/contract. Никакого GitHub PAT внутри
   контроллера или недоверенного PR.
4. **Publication boundary:** отдельный trusted Deployment Publisher
   преобразует подтверждённую защищённую квитанцию в узкую typed
   GitHub-операцию через Fortis Gateway. Публикация в GitHub может
   отставать от реального состояния. Ошибка публикации НЕ делает успешное
   применение неуспешным; discrepancy становится `UNKNOWN/RECONCILE`
   с оригинальным UUID и без повторения deployment.
5. **Чтение:** собственная Fortis Release Board получает опубликованные
   GitHub Deployments/statuses через GitHub API (Windows/operator) или
   будущие Gateway typed READ (AI); она read-only по отношению к источнику
   доказательств. Для полной наблюдаемости показывать provenance,
   freshness, pending/blocked/unknown, а не выдавать отсутствие записи
   GitHub за подтверждение `NOT_DEPLOYED`. Никакой обязательной GitHub
   Projects-доски и отдельной базы на старте.

### Очередь и семантика статусов — требования к проектированию

- **PLANNED/QUEUED:** принятое изменение требует CD, точный desired
  target/environment/version известен; ещё нет соответствующей подтверждённой
  успешной установки. Если evidence неполно — `UNKNOWN`, не безусловное
  `QUEUED`.
- **IN_PROGRESS:** есть проверенное событие начала действия; оно не доказывает
  достижение нужной версии.
- **APPLIED/DEPLOYED (verified):** установлен именно desired
  source/artifact target/environment и существует допустимый protected
  receipt + независимый readback; GitHub `success` — опубликованное
  представление этого факта.
- **FAILED:** доказанная ошибка конкретной попытки; новая попытка — отдельная
  авторизованная операция, не автоматический retry неизвестного эффекта.
- **UNKNOWN / NEEDS_RECONCILIATION:** stale/отсутствующие records, потерянный
  GitHub ACK, SHA race, `UNCERTAIN`, неполный readback либо расхождение
  desired/actual. Это блокирует ложный `success` и слепой retry.
- **NO_DEPLOYMENT:** изменения не требуют CD по проверенному контракту и не
  создают фиктивный queued deployment; это не статус установки.
- При нескольких PR и последовательных main SHA использовать
  immutable provenance, lineage и supersession. Обеспечить readback
  относительно конкретной версии, а не «последнего зелёного» статуса
  target. GitHub deployment status timeline — не готовая агрегированная
  очередь; правила выбора **актуального** состояния реализуются отдельно.

### Порядок реализации и критерии выхода (последовательно, без shortcuts)

**P1 — Release Labels owner-ASK пилот (DONE, PASS 2026-11-16).**
Выполнены свежий exact-HEAD/diff/body/labels/CI/policy preflight, одна ASK,
owner WebAuthn, проверка original UUID/audit/receipt и независимый GitHub
readback. Результат и закрытие worktree зафиксированы выше. Владелец слил
PR #76 после подтверждения пилота; P1 не требуется повторять.

**P2 — Надёжное source-only UUID/receipt reconciliation (NEXT).**
Использовать уже принятый
[Repo intent coordinator](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/NATIVE-WORKTREE-GATEWAY-2026-11-06.md#automatic-read-retries-and-intent-continuation-repo-source),
сохраняя один logical intentId и immutable requestId каждой попытки.
Не создавать второй параллельный журнал или publisher authority.
Первый scoped PR #101 исправляет полноту audit при перемежающихся событиях
разных заявок. Затем проверить label-specific pre-submit journal,
immutable expected SHA/body/labels fingerprints, request/details/audit/receipt
lookup и bounded independent GitHub readback с исходами
`CONFIRMED_APPLIED` / `CONFIRMED_NOT_APPLIED` / `UNKNOWN_STOP`.
Негативные тесты: lost ACK, stale PR, partial jobs, unknown effect,
duplicate requests и ошибочные receipts. Никаких новых полномочий
и privileged PR workflow; P2 пока не объявлен завершённым.

**P3 — Trusted Release Label Publisher.**
Отдельное security/owner review для principal, scheduler/trigger,
exact-HEAD data-only recomputation, обоих mandatory CI, безопасного
reconciliation managed labels и ограниченных Gateway writes. На первом
этапе ASK остаётся допустимым обязательным контролем. Автоматическое
вычисление не является автоматическим разрешением изменения.
Запрет GitHub credentials и привилегированных вызовов в
недоверенном `pull_request` workflow. Проверить разные action classes,
несколько targets, сохранность human labels и races.

**P4 — Проект CD Queue / GitHub Deployments API contract.**
Выбрать минимальную identity-схему для target/environment/desired version,
read pagination, lifecycle statuses и merged-PR lineage; проверить GitHub
Deployments semantics и event-trigger safety (запись планового состояния
не должна самопроизвольно запускать CD). Добавить типизированные Gateway
READ, затем отдельно ASK/owner-reviewed WRITE с receipt и reconciliation;
права и live rollout только по UC-GW-003/005. Read-only агрегатор должен
строить repo/target/action/env views и отделять known pending от unknown.
Сначала dry-run и контрактные тесты, затем controlled pilot.

**P5 — Post-merge queue publication.**
После достоверного owner-merged GitHub `main` и полного release impact
зафиксировать desired CD target/version; поместить его в GitHub CD
projection через bounded publisher, а `no-deployment` исключать.
Предотвращать duplicate/superseded entries при нескольких PR,
одинаковых build units и новых main SHA. Независимый readback доказывает
только сохранение записи в GitHub, не фактическое развёртывание.

**P6 — Verified deployment-to-GitHub publication.**
Исследовать готовые receipts каждого контроллера; при необходимости
предложить ограниченное дополнение в отдельном scope. Publisher читает
и проверяет исходный protected receipt, actual target/environment state,
связывает его с desired deployment identity и только тогда публикует
`success` через Gateway. Проверить failed/unknown/rollback,
lost status ACK, поздний receipt, несоответствие SHA и несколько targets.
Любое Production/Windows изменение — отдельный owner-approved проект,
не часть текущего Release Labels пилота.

**P7 — Fortis Release Board (собственный UI; GitHub Projects НЕ нужен).**
Read-only board со списком repository/target/environment/desired source,
required actions, confirmed actual state, linked PRs, latest GitHub
deployment/status, provenance/freshness и исходом reconciliation.
Фильтры: `repositories awaiting CD`, `targets awaiting CD`,
action (`image-rebuild`, `config-deploy`, `windows-update`,
`package-build`, `migration-required`), environment, queued,
in-progress, failed, unknown и confirmed. Windows direct GitHub READ
и AI through Gateway typed READ должны давать сопоставимые результаты
с явным указанием недостаточности evidence. Доска не должна сама
назначать `success` или исполнять CD.

**P8 — Release Batch (после работающей очереди).**
Группировка накопившихся merged changes по source SHA, targets,
shared build units, dependencies и environment; один batch может
включать несколько PR, но не может опустить изменения уже принятого
`main` без отдельно согласованной стратегии выбора source.
План/билд/установка/проверка — разные статусы. Фактическое применение
остаётся у соответствующих отдельно утверждённых контроллеров.

### Непереходимые границы

- Никаких GitHub Projects в текущей архитектуре: собственная Board потребляет
  Gateway/GitHub API; GitHub — публично читаемая или авторизованная
  **проекция** CD, protected receipts/readback — доказательства установки.
- Никаких прямых GitHub REST/PAT/Git push вызовов от ИИ, даже если
  операторский Windows-клиент может читать GitHub API напрямую.
- Release Labels и GitHub Deployments не дают разрешения на Production.
  Source merge, успешный CI, staged build, owner ASK и
  проверенный deployment — отдельные факты.
- Не менять Windows Mirror, `Manage-Integrations.ps1`, Windows controller
  и Production Gateway ради pilot P1. Scope других чатов не затрагивать.
- При `UNCERTAIN`, потерянном ACK или 403/timeout на effect path сначала
  сохранить исходные UUID и выполнить independent readback. Продолжение
  определяется [UC-CONT-003](use-cases/delivery.md#uc-cont-003) и
  [UC-GW-009](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009):
  старый UUID не переисполнять; новая попытка допускается только с новыми
  проверками безопасности, предусловий и действующей авторизацией.
  Выдавать `DEPLOYED` при недостаточных доказательствах запрещено.
- Этот roadmap — **план**, а не доказательство наличия возможностей P3–P8
  в live Gateway. Изменять release contract, capability grants, deployment
  controller и runtime только отдельными проверяемыми owner-reviewed этапами.

**Следующая конкретная задача:** P2 — review/CI/owner merge scoped
исправления inspector в PR #101, затем label-specific recovery/reconciliation
и отрицательные тесты на базе существующего intent coordinator. Publisher
и GitHub Deployments остаются последующими отдельными этапами P3–P6.

## Future: CI, GitHub Actions и сценарии настройки

**PLANNED:** подробнее разобрать модель CI/GitHub Actions
и оформить повторяемый путь настройки CI для нового или существующего
репозитория. Это самостоятельная задача, не prerequisite P1.

- Определить минимальные проверки по стеку и риску: что выполняется локально,
  что в Actions, какие нужны runners/dependencies/cache/artifacts и когда
  дополнительные jobs только дублируют проверки.
- Разобрать triggers (`pull_request`, `push`, ручной запуск), workflow/job names,
  permissions, secrets и доверие к PR-коду; выбрать required checks и правила
  защиты `main`, учесть skipped/pending/re-run и привязку к точному HEAD SHA.
- Сначала сверить существующий [UC-CONT-004](use-cases/delivery.md#uc-cont-004)
  (чтение результата Actions) и владельцев workflow source; улучшить его либо
  добавить отдельный UC настройки/изменения CI по
  [UC-CONT-024](use-cases/orientation.md#uc-cont-024). Не превращать readback UC
  в копию YAML каждого проекта; связать новый маршрут с
  [созданием repo](use-cases/repositories.md#uc-cont-027).
- Предусмотреть typed Gateway публикацию `.github/workflows/*` с действующей
  policy/ASK, проверку первого exact-head run и owner настройку required checks.
  Оценить reusable workflows/templates только там, где они уменьшают поддержку.

**Ожидаемый результат:** понятный маршрут от выбора нужных проверок до первого
подтверждённого run и required checks, с применимыми UC и ссылками на source.
Общий процесс остаётся здесь; YAML и конкретные команды — у repo-владельцев.

## Future: reproducible Fortis Repo image and Guard preflight

- Establish a reviewed, versioned canonical Docker build context and immutable base/package provenance before promising a deterministic **full** rebuild; the current historical source context and `.dockerignore` are not fully established. A narrow derivative build may use its own reviewed source and SHA guards.
- Create one owner-run Windows PowerShell 5.1 **image-only build** script with exact pinned build context, image ID readback and offline smoke; do not stop/recreate `fortis-repo-test` during a build. An image exists is not the same as a deployed runtime.
- Before **any** Fortis Repo container runtime change, require read-only previews of **both** Repo1 and Repo2 Guards against the proposed effective mounts/networks/identity/resource settings (and account for shared Qwen). `tunnel/runtime/windows-repo/current/launchers/shared/FortisContainerPolicy.ps1` is the only shared policy owner. Reconnect is a separate owner operation after checks.
- General host-only actions should follow `UC-CONT-025`; Fortis Repo image and Guard review is `UC-CONT-026`. Keep owner commands short, deterministic, reviewable, and fail closed. Do not grant AI generic Windows shell/Docker API or edit protected runtime records.

## Future: автоматизация изменений Gateway integrations

**PLANNED / оценить целесообразность:** сократить повторяемые ручные действия
при подключении и изменении API через Gateway:

- **Новый API/provider** — собственный или сторонний:
  переиспользовать существующий scaffold, оценить генерацию связанного каркаса
  schemas, adapters, typed client и проверок по
  [UC-GW-002](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-002).
- **Новый токен/credential для Gateway:** оценить единый guarded путь подготовки
  конфигурации, проверки необходимых scopes и проверки доступа по
  [UC-GW-004](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/credential-lifecycle.md#uc-gw-004).
  Ввод и хранение секрета остаются на стороне владельца/Gateway, без передачи в Repo или чат.
- **Добавление или изменение доступных методов существующего API** — своего
  или стороннего, например Sonar: оценить согласованное обновление schemas, routes, handlers,
  клиентских методов, policy и проверок совместимости по
  [UC-GW-003](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-003),
  с учётом различий native и extension операций.

Предпочтительный результат — короткий детерминированный plan/preflight:
что уже поддержано, что меняется в source/config/credentials, нужен ли image
build/deploy, какие точные команды должен выполнить владелец вне контейнера
и как проверить live результат. Сначала переиспользовать существующие helpers;
не пересобирать image без необходимости и не расширять права автоматически.
Этот пункт принадлежит контейнерному backlog как улучшение общего процесса;
реализация Gateway остаётся в `fortis-approvals`. Процедуры и контракты по ссылкам
не дублировать здесь; при выделении конкретной разработки перенести её
в backlog репозитория-владельца со ссылкой отсюда.
