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

**Различать с принятым Machine ASK V1:** Windows Executor теперь имеет отдельный активированный owner-approved ASK-only путь и проверенные Get-Date/Reject E2E. Нижеследующее исследование относится к **другому**, ограниченному OS/container-control broker с отдельными ACL/JEA/WDAC/security gates. Наличие Machine ASK не делает произвольный shell безопасным и не даёт ИИ Docker host control.

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

**Fortis Release Planning / CD Queue — CURRENT ROADMAP (product decision 2026-11-20; P1–P4 history retained).**
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
изменениям. В **V1 релиз выполняется вручную владельцем** по существующему Use Case и
reusable controller scripts. ИИ помогает пройти процедуру, а после сообщения
владельца может **отдельной авторизованной операцией** отметить исходный релиз
в собственном Fortis Registry. Ручная отметка — `REPORTED_COMPLETE`, а не
проверенное `DEPLOYED`: последнее требует protected receipt и independent
runtime readback. Не вводить в V1 новый исполнитель CD или универсальный
сборщик всех controller receipts. Позднее CD автоматизирует запуск существующих
контроллеров и технический readback, не заменяя их правила допуска.

**Fortis Registry — канонический источник очереди и отметок V1.** GitHub
Deployments/statuses остаются необязательной внешней проекцией/READ-интеграцией;
их отсутствие или задержка не меняют локальную очередь. ИИ получает доступ к
изменению Registry только через отдельный reviewed typed API с ограниченными
правами, audit и проверяемыми предусловиями; текущей live write capability нет.
Собственная **Fortis Release Board** показывает Registry; GitHub Projects
исключён из текущего плана.

Объект учёта — не только репозиторий: **repository + deployment target +
environment + desired source/artifact identity**. Репозиторий — агрегированное
представление очереди. Один репозиторий может содержать несколько targets;
несколько targets могут использовать один build unit/image. PR и merge — входные
события и ссылки на изменения, но не отдельная единица физической установки:
один проверенный deployment может покрыть несколько merged PR. Queue и Board
должны также группировать по repo, action, status и release batch.

### Текущие факты и граница готовности

**P4 Gateway Deployments READ — owner-reported RELEASE COMPLETE (2026-11-20).**
Владелец сообщил о полном `Check → Apply → Backup → Promote` нового Primary,
`running/healthy`, repository scope `fortis-approvals`, только четыре
GitHub Deployments GET и disabled WRITE. Принят [PR #159](https://github.com/AlexPastukhh/fortis-approvals/pull/159)
(merge SHA `585211b0240fd543b475d2196edc0bd4efb83951`), исправивший
emergency UC-GW-013 Promote. Это owner runtime evidence, не результат
самостоятельной проверки Windows Docker из этого task. Исторический old image
отсутствовал; `DISASTER_RECOVERY_VERIFIED=NO` и retained rescue/history
сохраняются. `P4 READ` НЕ разрешает CD Queue WRITE или повторный релиз.

**P3.4 owner live E2E — PASS (2026-11-19).** Отдельный one-shot Publisher
`release-label-publisher-v1` прошёл изолированный owner-run `preview → request`,
один ASK и WebAuthn для [approvals PR #118](https://github.com/AlexPastukhh/fortis-approvals/pull/118).
Исходный request `ed0dce76-8402-4230-941e-a89b5639460d` завершён
`EXECUTED`; проверены original UUID-bound receipt и независимое наличие
`release:no-deployment` при неизменном PR HEAD
`c6f6cf09cecf825c0d4c7595a2bdb153b129ce00`.
Это доказательство *одного ручного добавления метки*, не автоматического
Publisher, не удаления метки и не CD. Точная эксплуатационная граница —
[Gateway current state](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/guides/FORTIS-APPROVALS-SECURE-DEVELOPMENT.md).
Исторические P1/P2 evidence ниже сохраняются.

### Исторические P1 / P2 source-факты (проверены 2026-11-16)

- **Уже принято в source**: общий Release Impact v1, каталоги targets в пяти
  enrolled проектах, точный PR HEAD/full merge-base diff, вычисление
  `release:*` / `build:*` labels, read-only admission с обязательными
  `Source CI` и `Fortis Release Impact`, полный latest attempt/jobs,
  Gateway snapshots, trusted preview и необязательный owner-ASK sender.
  Базовый Release Labels/admission source принят commit
  `27bdc57c160fb5535b624003b88122d0169fe079` (PR #8); актуальное
  завершение P2 зафиксировано ниже. P2 не менял pinned SHA CI callers.
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
- **P2 PASS — source-only, проверен 2026-11-16**: исправление global audit IDs
  принято в [fortis-approvals PR #101](https://github.com/AlexPastukhh/fortis-approvals/pull/101).
  [PR #102](https://github.com/AlexPastukhh/fortis-approvals/pull/102) добавил
  проверку полного label receipt против исходного fingerprint и независимый
  bounded typed readback с `releaseLabelReconciliation`:
  `CONFIRMED_APPLIED` / `CONFIRMED_NOT_APPLIED` / `UNKNOWN_STOP`.
  Принятый Repo intent coordinator сохраняет один logical intentId, immutable
  requestId каждой попытки и durable pre-submit journal; второй журнал и
  новые полномочия не создавались.
- **P2 caller и отрицательные проверки**:
  [fortis-release-impact-action PR #9](https://github.com/AlexPastukhh/fortis-release-impact-action/pull/9)
  сохраняет original intent, все attempt UUID, действительный owner requestId
  и связь позднего receipt с его исходной попыткой. Проверены lost ACK, restart,
  duplicate pending, недоступный/ошибочный receipt, stale fingerprints,
  partial/latest CI jobs, сохранность human labels и concurrent readback.
  `writeConfirmed=false` и `automaticRetryAllowed=false` у caller;
  read-only inspector оставляет `retryAuthorization=NONE`.
- **P2 validation и owner acceptance**: владелец слил PR #102 и #9 через
  GitHub UI после успешного exact-head CI. В approvals прошёл полный source
  набор **961 тест / 84 группы**, включая **22 label-specific теста**;
  Source CI `43894815633`, attempt 1, jobs `offline-tests` / `audit-projections`,
  и Release Impact `43894815823`, attempt 1, job `release-impact`, успешны.
  В action прошли **127 offline тестов** и CI `43893103057`, attempt 1,
  job `validator-tests`. Принятые main имеют тот же tree, что проверенные PR
  HEAD `891013644527a41c389394f559c13895574bcdc4` и
  `f8816df1fe08195728b95d02ba8d468cd02c4278` соответственно.
- **P2 source workflow завершён**: чистые Docker main синхронизированы:
  approvals `c52736aec5861c67b7ce2b2a58304a821cf8e413`, request
  `3760e181-91c9-4e6d-a730-aa7f926d8687`; action
  `6627da85cab34dec75333676ec6215de8e0130ff`, request
  `7dadcdf6-8687-42c8-b77c-c6a54b4dea30`.
  Защищённые `cleanup_task` requests
  `a1953267-6da8-4a17-85e5-7f61df172dc2` и
  `e297c3b3-8f0f-4ab5-8d9f-0d061d74d9ee` удалили только
  завершённые P2 worktrees, их локальные ветки и регистрации. Все четыре
  receipts `EXECUTED`; независимый readback подтвердил SHA, чистоту main
  и отсутствие этих task-объектов.
- **Граница P2**: принятый Repo source повторно подтвердил original P1 Core
  receipt/audit как `CONFIRMED_EXECUTED`. При отключённом provider readback
  текущая label-проекция остаётся `UNKNOWN_STOP`; знание исходного исполнения
  не теряется и разрешение на повтор не появляется. Это не новый Gateway
  outcome resolver и не доказательство установленного image.
- **Граница на 2026-11-19:** one-shot Publisher прошёл отдельный owner
  E2E после P2; unattended trigger/scheduler и автоматическое право на
  изменение меток **не приняты**. Post-merge CD Queue, typed GitHub
  Deployments READ/WRITE, verified deployment publisher, Release Board и
  Release Batch **не реализованы**. Для Publisher label WRITE по-прежнему
  действует `ASK`/WebAuthn. Метка и CI не являются deployment receipt.

### Предлагаемые источники и потоки данных (Registry V1 — DESIGN; не live capability)

1. **Планируемое:** PR metadata/merge evidence и проверенный Release Impact;
   каталог `release/targets.yaml`; точный Git SHA и полный набор изменённых
   путей; требуемые actions/build units; обязательные CI. Нормативная
   классификация остаётся у Release Planning Contract и одного pinned
   validator, а не дублируется в Gateway/Board.
2. **Canonical Fortis Registry (V1, proposed):** персистентная очередь по
   точным `{repository,target,environment,desiredSourceSha,catalogSha}` с
   source/artifact identity по доступности, PR lineage, actions, Use Case,
   state и append-only history. После подтверждённого owner merge и validated
   impact формируется *плановая* запись, не GitHub Deployment. При неоднозначном
   merge/impact — `UNKNOWN/STOP`, не ложный `NO_DEPLOYMENT`. Путь хранения,
   owner процесса и ACL/backup/transaction model ещё не приняты.
3. **Manual release (V1):** владелец выполняет применимый UC и reusable scripts
   в предусмотренной среде, например Gateway [UC-GW-005](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005)
   с отдельными Check, Apply, live readback, Backup, Promote и host inspect.
   Это не универсальная процедура для Windows/Mirror/Feedbrain. Ни Registry,
   ни UI, ни ИИ сами не запускают Docker, Windows или GitHub Deployments POST.
4. **Отметка результата (V1):** по конкретному поручению владельца ИИ вызывает
   отдельный разрешённый typed Registry API: exact target/desired SHA,
   оригинальная release/attempt identity, источник утверждения и append-only
   event `REPORTED_COMPLETE`. Можно приложить ссылки на evidence, но отметка
   **не подделывает** исходный controller receipt и не становится `VERIFIED`.
   Если результат противоречив или target/SHA не установлен — STOP/UNKNOWN.
   При записи подтверждённого controller result отдельный оригинальный
   receipt + проверка фактического артефакта **на шаге релиза** позволяют
   сохранить lastVerifiedInstalled; при следующем merge используется
   сохранённое событие. Это не постоянный опрос Docker/Windows.
5. **Внешняя GitHub-проекция (не обязательна в V1):** P4 четырёхоперационный
   typed Deployments READ активирован только для `fortis-approvals`; будущие
   Gateway WRITE/Publisher требуют отдельного security review, owner grants,
   event consumer inventory и выпуска. GitHub events могут запускать CD;
   запрещены тестовые POST до принятия event-safety gate. GitHub Deployment
   не является контроллером установки, protected receipt или хранилищем
   исходной очереди. Board V1 читает Fortis Registry, а не требует GitHub API.

### Очередь и семантика статусов — требования к проектированию

- **PLANNED_UNVERIFIED:** desired по проверенному merge известен, но
  нет допустимого последнего verified installed event; это видимый
  пункт плана для владельца, а не доказанный mismatch.
- **QUEUED:** desired и все source/dependency proofs приняты, а
  сохранённое **последнее технически подтверждённое событие установки**
  для данного target/environment содержит другой SHA/artifact. Для
  обычного нового merge свежий live readback хоста **не требуется**;
  при drift/restore/UNKNOWN требуется отдельная reconciliation.
- **IN_PROGRESS:** отдельное подтверждение начала ручного релиза; источник
  отмечается, это не доказательство исполнения или результата.
- **REPORTED_COMPLETE (V1):** owner-authorized append-only событие exact
  record/source сохраняет **lastOwnerReported**, но никогда не записывает
  `verifiedInstalled` и не закрывает более новый desired. Board явно
  отличает сообщение владельца от подтверждённой установки.
- **APPLIED/DEPLOYED (verified):** в момент релиза original protected
  controller receipt и независимый target readback подтвердили source/
  artifact/target/env. Registry сохраняет это **неизменяемым событием
  lastVerifiedInstalled** со временем и происхождением; новый merge
  не требует повторной live проверки. GitHub `success` — проекция.
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

### Этапы и критерии выхода — сначала Functional V1, затем hardening

**P1–P4 приняты в указанном ограниченном scope, их исторические
receipts/CI описаны выше; не повторять завершённые пилоты.**

| Этап | Принятый рубеж | Чего он не разрешает |
| --- | --- | --- |
| **P1** | Owner-ASK Release Labels live pilot, PASS 2026-11-16. | CD/Registry WRITE. |
| **P2** | Source-only UUID/receipt reconciliation, PASS_SOURCE_ONLY 2026-11-16. | Повторный effect при UNCERTAIN, unattended scheduler. |
| **P3** | Owner-authorized one-shot Label Publisher, PASS 2026-11-19. | Массовую публикацию, CD. |
| **P4** | Scoped GitHub Deployments GET (4 метода), owner-reported RELEASE COMPLETE 2026-11-20. | GitHub Deployments WRITE и Registry authority. |

**P5 — Fortis Release Registry (SOURCE MERGED THROUGH APPROVALS PR #236; RUNTIME NOT LIVE).**

**Пилот:** только `AlexPastukhh/fortis-approvals`; учёт `forward-only`
с первого **отдельно принятого владельцем** enrollment по exact
`main/catalog/bindings/policy`. Ни один merged PR и SHA из handoff не
являются enrollment baseline. Без проверенного evidence — STOP/UNKNOWN;
до cutover не делать backfill старых PR/CI/installed.

**Проверенная версия исходников (2026-11-23; не deployed capability):**

| Approvals PR | Принято в source и offline E2E |
| --- | --- |
| [#194–#223](https://github.com/AlexPastukhh/fortis-approvals/pull/223) | Typed evidence/policy/lineage, исторический SQLite **schema v1/v2** с original UUID/CAS, backup и source-only checkpoint/Unix/host preflight; owner checkpoint и witness **не работают как live authority**. |
| [#224–#230](https://github.com/AlexPastukhh/fortis-approvals/pull/230) | Отдельный функциональный SQLite **schema 3** (`FunctionalV1CandidateJournal`), initial/suffix, local event chain, original collector method pin, WAL-safe inactive backup; два настоящих **локальных тестовых** Core/collector merge → желаемые записи и supersession (GitHub/owner verifier — fixtures). |
| [#231–#233](https://github.com/AlexPastukhh/fortis-approvals/pull/233) | Исполняемый private AF_UNIX **candidate READ** процесс; owner-run probe для настоящих cross-UID отказов; Broker/Core + `/v1/reads` → socket → schema 3 в локальных тестах. `SOURCE_ONLY_CANDIDATE_READ`, никакой авторитетной очереди или активированных machine grants. |
| [#234](https://github.com/AlexPastukhh/fortis-approvals/pull/234) | Real UID/GID, supplementary groups, capabilities/no-new-privs/seccomp и tracer fail-closed reader guards; source regression, **не** настоящий host proof. |
| [#235](https://github.com/AlexPastukhh/fortis-approvals/pull/235) | Typed Repo candidate client + явный opt-in R7 factory → Core/Broker → Unix → schema 3; тестовые policy/grants, source-only. Оба PR **MERGED**, exact-HEAD Source CI, P5 Retained Impact, Fortis Release Impact SUCCESS. |
| [#236](https://github.com/AlexPastukhh/fortis-approvals/pull/236) | **MERGED**: bounded Repo→typed Gateway READ с pin selected-main SHA, original operation UUID, revision/page/head readback и source-only CLI. Exact HEAD `7c89fc29b2529a07f48290bfcfd6edeed08108a1`, merge main `827e2eee388d9eb430aa8db9ba1a25c7dd90a916`; Source CI, P5 Retained Impact и исправленный Release Impact **SUCCESS**. R7→Unix→schema-3 source regression 50/50 PASS; на установленном Gateway `FORTIS_HTTP_403`: Registry READ **не** активирован. Это не host E1 PASS, не authoritatively persisted Desired и не E2 WRITE. |

**Проверка связанного плана:** [container PR #48](https://github.com/AlexPastukhh/fortis-container/pull/48)
**MERGED**, docs main `a8966253a66946764d2e60b09e2e3cff152a2757`,
Release schema source checks SUCCESS. Эта строка закрывает фактическую
ошибку статуса в #48, где #236 ещё значился ожидающим принятия.
Дальнейший source merge должен отражаться в этом единственном roadmap
только после независимого GitHub readback (PR+exact-head CI+main).


Точные схемы и инварианты принадлежат
[Approvals typed/storage boundary](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/RELEASE-REGISTRY-P5-TYPED-BOUNDARY.md)
и [collector/lineage contract](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/RELEASE-REGISTRY-P5-POST-MERGE-GATEWAY-CONTRACT.md);
архитектурные D1–D7 — [P5 Design](RELEASE-REGISTRY-P5-DESIGN.md).
[Handoff 2026-11-23](RELEASE-REGISTRY-V1-HANDOFF-2026-11-23.md) —
датированный вход для следующего чата, **не второй roadmap**.
Старые container offline-модули и handoff — исторические прототипы;
не копировать из них второй Registry writer, owner policy/ASK или pipeline.

**Статус сейчас:** source accepted; `registry.ingest_merged`/`registry.list_records`
и `report_manual_complete` **не активированы**; нет доказанного
cross-UID host, trusted live collector/owner acceptance, рабочей
постоянной очереди, первого enrollment, Board или batch.
Совпадающий hash локальных файлов, CI SUCCESS, same-UID Unix tests и
успешный PR merge **не удостоверяют host/owner origin и не дают GO**.
В GitHub `main.protected=false` в последнем readback; это не
доказательство отсутствия rulesets, но обязательность CI тоже не
установлена. До отдельного enforcement review вручную сверять четыре
exact-HEAD Approvals CI перед owner merge.

**Обновлённый порядок (архитектурная сверка UC, 2026-11-23): одна
пользовательская вертикаль, затем расширение того же Registry.** Перед
Docker E1 pilot обязателен закрытый выбор **существующего** механизма
provider/операций Gateway; одно лишь `RepoIntentBroker.read_adapters`
не регистрирует управляемую операцию в Owner Portal. Каждый шаг проверяет
сквозной путь до читаемого результата, исходные UUID/receipts и отказы.
Новый journal, policy engine, Owner Portal или общий proxy ради Registry
не создавать. Source-кандидат и его диагностика не являются live Desired.

**E1.0 — принятый source-путь (проверка 2026-11-23;
Approvals PR #237 + Container PR #50 OWNER-MERGED и main синхронизирован;
не является установленным runtime provider):**
- [UC-GW-002](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-002)
  и [UC-GW-003](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-003)
  задают существующий контракт `Provider/Operation`, trusted
  executor, actor/target, Core policy, owner review и receipts.
  [UC-GW-012](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/own-api.md#uc-gw-012)
  применяется **если у Registry появится собственный HTTP API**;
  его DOCKER-HTTPS/443 manifest **не** доказывает AF_UNIX.
- **Предпочтён штатный `extensions/` provider `registry`**:
  уже существуют `ExtensionRuntime` (регистрирует в `core.adapters`,
  policies и grants), `/v1/integrations/catalog|call|result`,
  `extensions.client.default_client()`, Owner Inventory, Policy V2 и
  WebAuthn. В source-only R7 fit-test уже работающий
  `GatewayRegistryUnixCandidateRead` был вызван из обычного
  `Operation.execute(ctx)` без новых Core/Owner механизмов:
  локальная SQLite schema 3 → настоящий Unix socket → extension
  request/result; DENY→ALLOW, ASK до исполнения, DENY после
  отзыва, wrong actor/target, original Core UUID проверены.
  **Проверка WebAuthn/UID/Unix peer здесь синтетическая**, host не принят.
  Регрессия принята в Approvals PR #237 (`8c382a6416e1a7af519e878598fda676b6854d17`),
  exact-head Source/P5/Release Impact CI SUCCESS; roadmap решение
  принято в Container PR #50 (`c4da75916158d966c26e7f9d182b9a536eda1476`).
  Оба merge не являются live Registry. В E1.1 провайдер уже
  определяется реальным image-owned `extension.py`, не тестовым объектом.
- **Native `/v1/reads` не выбираем как публичный V1 API**:
  нынешний `registry_candidate_reader` живёт только в
  `broker.read_adapters`, не устанавливает provider в
  `core.adapters`/Owner Portal; доведение потребовало бы
  второго registration/client path при уже работающем extension.
  Сохраняем его историческим source-diagnostic candidate до E2
  accepted readback; **запретить одновременный публичный вызов
  одного `registry` через native и extension**.
- **AF_UNIX остаётся специальным reviewed private transport** между
  Gateway и отдельным Registry, **не** generic HTTP/JSONAPI:
  E1.1 должен сделать source-packaged `integrations/registry/extension.py`
  с именованными READ `Operation`, закрытыми schemas, реальным
  `Context.request_id`, доверенной host-only binding существующего
  Unix adapter, строгой origin/socket/peer identity и **никакой**
  публичной path/URL/policy/actor injection. Обычный scaffold
  не создаёт защищённый AF_UNIX transport автоматически. E1.3
  доказывает реальные UID/GID, pinned socket и deny на host;
  source fit этого не удостоверяет.
- Уже допустимые `provider+operation+actor+target` политики
  принадлежат **только** существующим Core/Owner Policy V2; editing
  не выдаёт machine grants, Repo никогда не получает Registry
  writer credential, Registry `WRITE` в E1 не регистрируется.
  Обновить source manifest, packaging и exact release impact
  только при фактическом изменении Gateway image inputs.

| Этап | Принимаемый результат / критерий | Фактический статус на 2026-11-23 | Что осталось |
| --- | --- | --- | --- |
| **E0 — foundation** | Fixture merge → Core/collector → schema 3 desired, supersession, original UUID, backup → candidate Unix READ. | ✅ **SOURCE_REHEARSAL_DONE** (#224–#236), исключительно source/fixtures; не host. | Не повторять прототипы; не объявлять live. |
| **E1.0 — выбор API-пути** | Один provider и один API: штатный `extensions/` + `Provider/Operation`/Core/Owner Portal, reviewed AF_UNIX; native candidate остаётся диагностикой. | ✅ **SOURCE_ACCEPTED**: Approvals #237 и Container #50 owner-merged, exact-head CI SUCCESS, оба main синхронизированы; не host/production. | Принятый маршрут сохранять; реальные UID/registry runtime и owner grants позже, не скрывать их в source. |
| **E1.1 — packaged Registry provider** | Image-owned `integrations/registry/extension.py`: три закрытые candidate READ `Operation`; стандартные `/v1/integrations/catalog|call|result` и Repo IntegrationClient; `Provider.api` связывается лишь с проверенным host-owned Unix reader, единственный `registry` ID. | ✅ **SOURCE_MERGED, NOT_LIVE**: Approvals #238 (`425ba39e5bbdb57f44f42eac748b05f83e63bf8d`) и Container roadmap #51 (`c47438c8b1e06cd2c026cab1ebb13e29f779c99b`) owner-merged; exact-head Source/P5/Release Impact/schema CI SUCCESS; main синхронизированы. Ready=false до trusted binding; тесты AF_UNIX/SQLite/Owner Inventory — только offline. | E1.2 принято в source PR #239/#53; E1.3 — отдельный host bootstrap и Registry image. Нет установленного Registry/новых machine grants/WRITE; `/v1/reads` не используется как параллельный публичный V1 API, candidate не authoritative Desired. |
| **E1.2 — Owner Portal source acceptance** | Стандартный **packaged Registry** виден в owner inventory; owner `/v1/owner/policy/editor/*` использует реальную P-256 WebAuthn/UV-проверку, закрытые actor/target, DENY→ALLOW→ASK→DENY/revoke и оригинальный readback. Policy edit не создаёт machine grants. | ✅ **SOURCE_MERGED, NOT_LIVE**: Approvals #239 (head `1763688b721a2e343ea925d56c5d39330b33dcea`, merged main `f10ae3fbf37ad81e70cec7c2f36c0613d38bb27e`) и Container #53 (head `2a9e05c6e089aafae17d52ce3fbc85ae07728a62`, merged main `55ee7074fc9a731a3024bf7bd3c915a645f1429d`) owner-merged, exact-head Source/P5 Retained/Release Impact/schema CI SUCCESS; 39 local crypto/Registry tests PASS, main синхронизированы. | Не повторять source-прототип. Host UID/peer в этом тесте синтетический; E1.3 — реальные UID/GID, socket, image, backup и изоляция Repo. E1.4 — реальный browser Owner Portal и человеческий passkey в установленном Gateway. Нет новых grants/WRITE/Production. |
| **E1.3 — non-Production Docker pilot** | E1.3a — owner-fixed Gateway R7 READ bootstrap, separate Registry candidate-only non-Production image, immutable source/release/peer pins without new API/owner policy; E1.3b — separately owner-approved real host UID/GID/Unix/SQLite/backup/Repo denial. | ✅ **SOURCE_MERGED; HOST_NOT_ACCEPTED**: Approvals #240 (head `c21976e9f48c4edbf7875975c63e6c2015b7c071`, main merge `4c00b16d8e34bbaa4967b421ada0e4a9cde4258e`) и Container #54 (head `e96dc7f7e97eb9aa1ba26da3f22519117864c71a`, main merge `eacce2077a0532599621eb28ba60a4220a5f23c0`) owner-merged; exact-head Source CI/P5 Retained/Fortis Release Impact/schema checks SUCCESS; full local source suite PASS; main синхронизированы. Дополнительно **E1.3b source #241** (head `02887afbfeb9b068857a579a8847b7b2cadf2d42`, merged main `4900cf244da502a48d5e1a8f4eda5fc690a461ab`) и **roadmap #57** (head `51beb9e682dc07294e30cca02f6aeecbe0511b91`, merged main `81689876a63b15f3bbb8435f0f24a11d2a6f8884`) приняты 2026-11-23; source включает kernel pidfd/nonce volumes/owner manual controller, **без host GO**. Следом **Approvals #242** (head `fe4456c8b8ef0584f1bf952e7d02566555fd36b1`, main `faebc20ec309014e293ea7ac082ba2341e64a328`) и **Container #58** (head `29099dbbf8051231a213809447d6bc3080fb5b14`, main `41ab1d50602ff379bd094d90460a91e44fec104f`) owner-merged; Source CI/offline-tests, Windows audit-projections, Release Impact, P5 Retained Impact и Container schema **PASS на точных PR HEAD**. Это не установка на Windows или host acceptance. Дополнительно **Approvals #244** (`5876ceee852cb3cb628da77e03f1d676415ef651` → owner-merged `fd1c033bae41b60e6054efcd047170520c580a84`) и **Container #60** (`bd2f38413f99767a2e10a9efb31414d82bc85110` → owner-merged `1ab489b1d08b1a7dc9185cd3a2447ea6d9935d1c`) приняты 2026-11-23; exact-head Source/P5 Retained/исправленный Release Impact и Container schema CI PASS, Docker primary `main` синхронизированы. Новый owner schema-3 bootstrap core — только source, **не Windows install / не новый Registry image / не host acceptance**. Дополнительно owner-merged [Approvals #245](https://github.com/AlexPastukhh/fortis-approvals/pull/245) (head `96fcfeeb038ac25fea561a7a07e73147c251a743`, merge/new Docker `main` `9d6abc51ae17f3f8f32440b650e02a1300a3cac7`) и [Container #62](https://github.com/AlexPastukhh/fortis-container/pull/62) (head `e6944ecd367ed4ca5ae0878d7a1e3a8f5fde25a8`, merge/new Docker `main` `9def21bebcad2a5544076ae0feb6e32b17b6f529`) — exact-head Source CI `45156938296`, Fortis Release Impact `45156938020`, P5 Retained `45156938111` и Container schema `45157084210` **SUCCESS**. Windows launcher присутствует только в source; host installation/build/acceptance не выполнялись. **Последующее отдельное owner evidence (2026-11-23):** Windows `main` exact 9d6abc51ae17f3f8f32440b650e02a1300a3cac7 clean, PowerShell 5.1 launcher `Plan` `REGISTRY_BOOTSTRAP_PLAN_SOURCE_ONLY` и `E13B_OWNER_PLAN_REVIEW_COMPLETE` PASS; UC-CONT-021 read-only `desktop-linux`/Linux Engine 29.9.2 inventory 46 containers (10 running, 36 exited), live Gateway healthy/unchanged, Registry not installed, named Registry state/config/socket volumes not present; scoped owner GO на один локальный Registry **image-only build**, `--pull=false --no-cache --network=none`, UID:GID `20002:20002`, local base sha256:673719e071ecf27434fd2635bbd8d00f49f4fdd81f243143438a42ced8bedf60; postbuild readback `E13B_REGISTRY_IMAGE_ONLY_BUILD_PASS`, new image sha256:a4ac4df8b1125f377dd49a41050dd6bb74e314dee29ebeb2ae0a7ca09688e577 (tag `fortis-registry-pilot:e13b-9d6abc51ae17`), exact source label 9d6abc51ae17f3f8f32440b650e02a1300a3cac7, Linux/AMD64, Gateway instance/image still unchanged. **IMAGE_BUILT; not RUNNING/HOST_ACCEPTED**, upstream base provenance not independently attested. **Следующее owner read-only evidence (2026-11-23):** [Container #64](https://github.com/AlexPastukhh/fortis-container/pull/64) exact head `38948de22a56391ce685fc21290d041b5b18450e` owner-merged as clean Container `main` `d4187482cbd852463b073e8830134e0b2ad1c4ba`, exact-head schema CI `45172506109` SUCCESS; typed Docker main sync `7b91596b-0eb9-4395-a1dc-82c8db8df31f` EXECUTED. Windows `desktop-linux` metadata `SecurityOptions=[seccomp builtin,cgroupns]`, `fortis-gateway` id `03992c685e9abd2e3a65cf2071e57fa9f0bbdf83ad31f129a22b8f0ce8e0a8f1` `running`, Config.User `10001:10001`, image `sha256:2039987ce7c7b15d6fd6dea8111c79bf27098cdf5e9754ddea1a8034d3f20d50`; `fortis-repo-test` id `1f67b67cacf3d4435982df9c0606dcb1a89d99f3f8ac73d365f3e6bb3d2f658b` `running`, Config.User `1000:1000`, image `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`; both `HostConfig.UsernsMode=""`; `GroupAdd` rendered `[null]` by PowerShell null-array wrapper, **not observed process groups**. Named Registry volume candidates `0`; `E13B_HOST_IDENTITY_METADATA_READONLY_COMPLETE` PASS. **Only Docker metadata accepted; real mapped UID/GIDs, effective supplementary groups, volume ownership and new image-internal runtime remain UNKNOWN; no new GO.** **Later checkpoint:** Owner Windows **new Registry image** one-shot probe (2026-11-23, UC-CONT-021/025/016): separately owner-run exact `sha256:a4ac4df8b1125f377dd49a41050dd6bb74e314dee29ebeb2ae0a7ca09688e577` with `docker run --rm --pull=never --network=none --read-only --user 20002:20002 --cap-drop ALL --security-opt no-new-privileges:true --pids-limit 64 --memory 128m`, `python -I -B -c`, no mounts/listener/SQLite. Linux real/effective/saved `UID=(20002,20002,20002)`, `GID=(20002,20002,20002)`, supplementary groups `[20002]`; `/proc/self/uid_map` and `gid_map` rows `[[0,0,4294967295]]` map 20002 to 20002 **inside Docker Linux VM only**. Image-packaged owner bootstrap and reader imports PASS, actual `_runtime_confinement()` PASS (all caps zero/NoNewPrivs/seccomp/tracer), `os.pidfd_open(self)` PASS; `E13B_REGISTRY_ISOLATED_IMAGE_PROBE_PASS`; unchanged `fortis-gateway` instance/image running healthy `E13B_GATEWAY_UNCHANGED_PASS`. **This is isolated IMAGE runtime evidence, not Windows ACL/volume ownership/actual Gateway+Repo effective process groups/live peer or HOST_ACCEPTED.** **Later checkpoint:** Owner Windows **live process EUID/EGID readback** (2026-11-23; UC-CONT-021/025): `docker top -eo pid,euid,egid,comm` on running `fortis-gateway` container `03992c685e9abd2e3a65cf2071e57fa9f0bbdf83ad31f129a22b8f0ce8e0a8f1`, image `sha256:2039987ce7c7b15d6fd6dea8111c79bf27098cdf5e9754ddea1a8034d3f20d50`, reports `docker-init` PID 1091 and `python` PID 1257 EUID=EGID **10001**. Running `fortis-repo-test` container `1f67b67cacf3d4435982df9c0606dcb1a89d99f3f8ac73d365f3e6bb3d2f658b`, image `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`, reports `sleep` PID 1025 and three `node` PIDs 20682/22000/21604 EUID=EGID **1000**. Both `Privileged=false`, read-only root, `SecurityOpt=no-new-privileges`, `UsernsMode=""`, empty configured `GroupAdd` (NOT effective Linux supplementary groups). Gateway owns one `/state` RW mount plus seven other RO mounts; Repo RW mounts **the same** `fortis-repo-workspace` volume at `/workspace/files`, `/workspace/repo`, `/workspace/repos`, alongside separate `fortis-r7-client` RO. Do not expose any existing workspace or Gateway state volume to Registry. Named Registry state/config/socket candidate volumes still absent (`REGISTRY_VOLUME_CANDIDATES=0`); `E13B_LIVE_PROCESS_METADATA_READONLY_PASS`. This verifies live EUID/EGID observed by Docker Engine, NOT supplementary kernel groups, all host writers, owner volume/ACL, Windows host identity, or Registry socket/pidfd/Repo denial. Registry NOT_INSTALLED; E1.3b HOST_NOT_ACCEPTED. **Owner merged private-volume source contract (2026-11-23):** [Approvals #246](https://github.com/AlexPastukhh/fortis-approvals/pull/246) exact PR head `bea1c9b9d9ec10280c5bdc90c3a259f08ea80130`, merge/current clean Approvals `main` `16a2558580e142f5bf3f9fe43fcb176be83d5704`, owner exact-head Source CI `45181764625`, Release Impact `45181927229`, P5 Retained `45181764646` all SUCCESS. Owner merged [Container #68](https://github.com/AlexPastukhh/fortis-container/pull/68) head `4070c48a0caa909dbf109a4c255e724a4545a710`, merge/current clean Docker `main` `949dc79e3e928fafab6b234f69ba0356ebd7924c`, exact-head schema CI `45182752482` PASS. Typed Docker `main` sync receipts Approvals `6450cf91-6174-474d-b9cf-52955f5ec09c`, Container `d93dfa0d-f42d-42f9-b1fb-c7b78eaadbf4` EXECUTED. Source contract fixes 3 private volumes: state/config `20002:20002`/`0700`, socket `20002:10001`/`02710`; no host owner volume preparer or actual volumes exist. [Approvals #247](https://github.com/AlexPastukhh/fortis-approvals/pull/247) merged after whitespace-only correction at exact head `e0a99bb711ba16f818676a734dc0a2dc42be58a8`, merge `7f83f35c303b0e0fa2e6d97a971fe33fa57295c7`, Source CI `45186811270`, Release Impact `45186811383`, P5 Retained `45186811375` SUCCESS; typed sync `f06269b2-b441-42aa-920b-4dbffdbdbec2`. [Container #69](https://github.com/AlexPastukhh/fortis-container/pull/69) head `a39c1353c1955ebc3c8c66c773f2254974569a88`, merge `8a58078f2de544dcf37f90c4155fe8f66320789d`, schema CI `45185719218` SUCCESS, typed sync `5b869a85-6939-478d-8d8c-5b544c651cdc`. First owner Windows Plan PASS, Inventory failed with `PropertyNotFoundStrict` on missing mount `Name`; no PASS marker. [Approvals #248](https://github.com/AlexPastukhh/fortis-approvals/pull/248) guards optional bind/tmpfs Name/Source and rejects malformed volume/unknown Type, head `e44ce7a0bac300984aa8f0aaf42850d41fe58398`, owner merge/current clean Approvals `main` `aa2b103228cb8409f311adb89839daa697a078d0`, Source CI `45195615938`, Release Impact `45195616135`, P5 Retained `45195616120` SUCCESS, sync `17b8bda2-d822-46c8-a959-93dda8ea9344` EXECUTED. **Owner Windows PS5.1 corrected Inventory PASS (2026-11-24; UC-CONT-021/025):** exact clean source `aa2b103228cb8409f311adb89839daa697a078d0` (historical built Registry image source revision `9d6abc51ae17f3f8f32440b650e02a1300a3cac7`, image `sha256:a4ac4df8b1125f377dd49a41050dd6bb74e314dee29ebeb2ae0a7ca09688e577`), exact existing Gateway/Repo container/image pins validated; Gateway healthy, Repo running at post-read. Owner-selected suffix `9c2a71ef`: `fortis-registry-state-e13b-9c2a71ef`, `fortis-registry-config-e13b-9c2a71ef`, `fortis-registry-read`. `E13B_CONTAINER_METADATA_SCANNED=46`, `E13B_DOCKER_SECURITY_OPTIONS=["name=seccomp,profile=builtin","name=cgroupns"]`, `E13B_OWNER_VOLUME_METADATA_READONLY_PASS`, then expected `E13B_USERNS_GROUPS_OWNERSHIP_WRITER_FENCE_UNKNOWN_STOP_BEFORE_CREATE`. At the readback, no target-name or mount-name/source collision found by the accepted metadata scan and no target attachments. Not an atomic writer fence, not proof of root ownership, supplementary groups/userns translations, Windows ACL, upstream base provenance or a live Registry peer. No volumes created by this action; no host writes, Preview, Provision, listener or Gateway cutover.** **Owner-merged executable volume-helper source (2026-11-24):** [Approvals #249](https://github.com/AlexPastukhh/fortis-approvals/pull/249), exact HEAD `ada14d80401326d83006fcc0bba22d97d4060d40`, merge/current clean Docker `main` `ad5216ec33515292a5b749106c5e72100cbab53d`, Source CI `45321536467`, Windows PowerShell 5.1 source fixture CI `45321536360`, P5 Retained `45321536306`, Release Impact `45321536263` all SUCCESS. Owner-approved push receipt `b1dab83d-d915-4e26-b796-94d10f36cb52` EXECUTED; typed main sync `5a027ffe-6dd8-45e1-9bf6-070026420c6f` EXECUTED. Separate owner-only `scripts/registry_owner_volume_controller.ps1` Plan/Prepare/Inspect and pinned independent Python helper sources merged; 41 offline tests PASS, no Docker effects in CI. Prepare uses three distinct fresh local volumes with no adoption, prechecked exact mounts and 0:10001 with CHOWN/FOWNER only; Inspect separate 20002:20002, zero capabilities, exact RO mounts and independent root stat. Helpers retained; no automatic retry or cleanup. Existing Registry image unchanged. Live Gateway/Repo groups now observed; their actual userns maps, other active principals/writers, exclusive change fence and upstream image provenance still UNKNOWN. Independently reviewed evidence files and distinct owner GO mandatory; no volume creation or host admission.** E1.3b **HOST_NOT_ACCEPTED**; E1.4–E5 blocked. **Owner Windows controller Plan and live groups readback (2026-11-24):** exact clean Approvals Windows `main` `ad5216ec33515292a5b749106c5e72100cbab53d` checked before no-effect `E13B_VOLUME_CONTROLLER_SOURCE_PLAN_ONLY_NO_HOST_GO`; exact Docker Desktop Linux context/named-pipe endpoint and original Gateway/Repo IDs pinned. Owner `docker top -eo pid,uid,gid,euid,egid,supgid,comm` returned Repo `sleep` PID 1023, `node` PIDs 3558/3583, each UID/GID/EUID/EGID 1000 and SUPGID 1000; Gateway `docker-init` PID 1022, `python` PID 1164, each UID/GID/EUID/EGID 10001 and SUPGID 10001; `E13B_LIVE_GROUP_METADATA_READONLY_COMPLETE`. No group 10001 or 20002 observed on listed Repo processes. This is actual observed process supplementary groups, not a kernel mapping proof for live peers, exhaustive other-writer census, immutable process pin or owner-exclusive change fence. Earlier isolated Registry UID/GID 20002/groups 20002 and identity maps remain separate evidence. No host effect or approval of Prepare/Inspect.** **Latest owner host checkpoint (2026-11-24):** Container [#71](https://github.com/AlexPastukhh/fortis-container/pull/71) head `f02ab960f9eacd75d9186025c04a1134f4686ddf`, merged `06c61697591530711e453396310d13ebb7401820`, schema CI `45323390430` SUCCESS, typed main sync `3aa9580b-dbde-4b07-a335-5916c0b6cc3c` EXECUTED. Official upstream amd64 layer lineage and actual live peer userns maps verified; separate owner-approved Prepare and independent RO Inspect both PASS for all three fresh local volumes (see steps 3, 4, 7 below for exact evidence). Earlier no-volume/UNKNOWN observations are historical, superseded for these exact resources and this window. **VOLUME_ROOTS_PREPARED_AND_INDEPENDENTLY_VERIFIED; HELPERS_RETAINED; HOST_NOT_ACCEPTED.** | E1.3b **HOST_BLOCKED / EXACT HELPER CLEANUP + SCHEMA3 + OWNER PIDFD PIN + RELEASE ADMISSION GATE**: owner sandbox подтвердил `SO_PEERCRED pid=0`, но работающий cross-namespace `SO_PEERPIDFD` с уникальным process inode и liveness; общий PID namespace НЕ нужен; до отдельного owner GO и реальных доказательств по `RELEASE-REGISTRY-FUNCTIONAL-V1-PILOT.md`: non-root distinct mapped UID/GID, SO_PEERCRED UID/GID + live pidfd process inode и pinned kernel boot ID (PID=0 без независимого owner pin=STOP), socket `02710` setgid + `0660` и pinned device/inode, kernel Repo EACCES/EPERM (не ENOENT), schema3 private DB/backup/inactive restore, отдельный UC-GW-005 owner release. Четыре Release Impact target (Gateway/Registry/Publisher images и Windows controller) были учтены: **только отдельный Registry candidate image-only build** выполнен владельцем после отдельного GO; прочие image rebuild, Windows controller deployment и Gateway release не выполнялись. Никаких новых grants/WRITE/Production. |
| **E1.4 — live extension READ + owner UI** | Настоящий Repo `extensions.client` → TLS Gateway `/v1/integrations/call|result` → Core/Registry provider → AF_UNIX → SQLite → Repo; original UUID, restart, grants/revoke и Repo-denial; в **установленном** Owner Portal отображение и изменение методов через реальные browser UI + owner passkey. | ⬜ **NOT_LIVE**: E1.1 проверил WSGI extension routes offline, E1.2 source-only подписанные owner HTTP transitions; прежний `/v1/reads` probe вернул `FORTIS_HTTP_403` и не проверяет extension READ. | Owner live source/readback/denial, browser UI/real owner WebAuthn credential, independent actor/grant revoke, restart, real peer. Candidate данные не называть authoritative Desired. |
| **E2 — P5 Desired** | Owner-reviewed настоящий GitHub merge → существующий GitHub provider + authenticated Collector/evidence → отдельный planner-only `registry.ingest_merged` → single-writer Desired → **тот же** Registry extension READ. | ⬜ **NOT_STARTED_LIVE**, offline fixture существует. | Новый reviewed WRITE `Operation` через тот же Core: preview/receipt/lookup, ID/CAS/UNKNOWN, first forward-only enrollment и отдельный owner WRITE grant; valid no-deployment=0. Отдельно доказать устойчивую Core `createdAt` ↔ первый PENDING audit timestamp связь при переходе через границу секунды (тестовая фиксация часов не является runtime-исправлением). |
| **E3 — P6/P7** | Отдельно разрешённый manual `REPORTED_COMPLETE` → immutable event; Board отдельно отображает Desired / OwnerReported / VerifiedInstalled / UNKNOWN. | ⬜ **NOT_STARTED_LIVE**. | Owner event+receipt; никакого `DEPLOYED` без controller proof и независимого target readback. |
| **E4 — P8** | Второй реальный merge supersedes Desired, оставляет pending; Release Batch группирует зависимости/build units и предлагает **ручные** UC. | ⬜ **NOT_STARTED_LIVE**. | Реальная сохранность очереди, version provenance, отказные сценарии, без CD execution. |
| **E5 — Functional V1 acceptance** | E2–E4 целиком с cold restart, duplicate UUID, rejected source, missing CI, restore, revoke, no-deployment, UNKNOWN и owner proof. | ⬜ **NOT_ACCEPTED**. | Отдельный scoped non-Production `FUNCTIONAL_V1_GO`; PR/CI/host E1 сами по себе не GO. |

**E1.3b — единая контрольная таблица после каждого шага (checkpoint 2026-11-24; owner readbacks vs source):**

| № | Шаг и критерий | Текущее доказательство | Осталось / STOP |
| --- | --- | --- | --- |
| 1 | Exact source merge + CI + guarded Windows update | ✅ Approvals [#245](https://github.com/AlexPastukhh/fortis-approvals/pull/245) exact head `96fcfeeb038ac25fea561a7a07e73147c251a743`, merged/current clean Docker `main` `9d6abc51ae17f3f8f32440b650e02a1300a3cac7`; Container [#62](https://github.com/AlexPastukhh/fortis-container/pull/62) merged `9def21bebcad2a5544076ae0feb6e32b17b6f529`, [#63](https://github.com/AlexPastukhh/fortis-container/pull/63) merged `b7af66e9bd05b178ce10a131e0cf649bc890f223`, [#64](https://github.com/AlexPastukhh/fortis-container/pull/64) head `38948de22a56391ce685fc21290d041b5b18450e` owner-merged/current clean Container `main` `d4187482cbd852463b073e8830134e0b2ad1c4ba`, typed sync receipt `7b91596b-0eb9-4395-a1dc-82c8db8df31f` EXECUTED; exact-head Approvals Source/Release Impact/P5 Retained CI success and Container #64 schema `45172506109` SUCCESS. Windows exact Approvals SHA/clean main/PowerShell `Plan` PASS; separate owner GO completed only Registry image-only build `sha256:a4ac4df8b1125f377dd49a41050dd6bb74e314dee29ebeb2ae0a7ca09688e577`. **Latest owner-merged Container [#65](https://github.com/AlexPastukhh/fortis-container/pull/65)** head `13cdde02d06c7accd0ab55751ebd4565c330b272`, merged `1666e5272deb84662ac846103f058b9ab85d1ced` (typed sync `4b40634e-9254-4281-b60f-92e18a98f9ad`, schema CI `45174124416` PASS) and **[#66](https://github.com/AlexPastukhh/fortis-container/pull/66)** head `d64ed5989003f7bd8cf600594011a5ebeb600506`, merged/current clean Docker `main` `ead65794c4afe32f9c718108fdf6c5973ef5cbd5` (sync `983f5fdb-096e-4209-b761-dd3e01d9abd5`, exact-head schema CI `45176369428` SUCCESS). Owner Windows live EUID/EGID readback passed. **Owner merged** [Approvals #246](https://github.com/AlexPastukhh/fortis-approvals/pull/246) head `bea1c9b9d9ec10280c5bdc90c3a259f08ea80130`, merge/clean `main` `16a2558580e142f5bf3f9fe43fcb176be83d5704`, exact-head Source/Release Impact/P5 Retained CI PASS. Owner merged [Container #68](https://github.com/AlexPastukhh/fortis-container/pull/68) head `4070c48a0caa909dbf109a4c255e724a4545a710`, merge/current clean main `949dc79e3e928fafab6b234f69ba0356ebd7924c`, schema CI PASS. [Approvals #247](https://github.com/AlexPastukhh/fortis-approvals/pull/247) merged after whitespace-only correction at exact head `e0a99bb711ba16f818676a734dc0a2dc42be58a8`, merge `7f83f35c303b0e0fa2e6d97a971fe33fa57295c7`, Source CI `45186811270`, Release Impact `45186811383`, P5 Retained `45186811375` SUCCESS; typed sync `f06269b2-b441-42aa-920b-4dbffdbdbec2`. [Container #69](https://github.com/AlexPastukhh/fortis-container/pull/69) head `a39c1353c1955ebc3c8c66c773f2254974569a88`, merge `8a58078f2de544dcf37f90c4155fe8f66320789d`, schema CI `45185719218` SUCCESS, typed sync `5b869a85-6939-478d-8d8c-5b544c651cdc`. First owner Windows Plan PASS, Inventory failed with `PropertyNotFoundStrict` on missing mount `Name`; no PASS marker. [Approvals #248](https://github.com/AlexPastukhh/fortis-approvals/pull/248) guards optional bind/tmpfs Name/Source and rejects malformed volume/unknown Type, head `e44ce7a0bac300984aa8f0aaf42850d41fe58398`, owner merge/current clean Approvals `main` `aa2b103228cb8409f311adb89839daa697a078d0`, Source CI `45195615938`, Release Impact `45195616135`, P5 Retained `45195616120` SUCCESS, sync `17b8bda2-d822-46c8-a959-93dda8ea9344` EXECUTED. Corrected owner Windows Inventory PASS; source-only acceptance is not host admission. **Owner-merged executable volume-helper source (2026-11-24):** [Approvals #249](https://github.com/AlexPastukhh/fortis-approvals/pull/249), exact HEAD `ada14d80401326d83006fcc0bba22d97d4060d40`, merge/current clean Docker `main` `ad5216ec33515292a5b749106c5e72100cbab53d`, Source CI `45321536467`, Windows PowerShell 5.1 source fixture CI `45321536360`, P5 Retained `45321536306`, Release Impact `45321536263` all SUCCESS. Owner-approved push receipt `b1dab83d-d915-4e26-b796-94d10f36cb52` EXECUTED; typed main sync `5a027ffe-6dd8-45e1-9bf6-070026420c6f` EXECUTED. Separate owner-only `scripts/registry_owner_volume_controller.ps1` Plan/Prepare/Inspect and pinned independent Python helper sources merged; 41 offline tests PASS, no Docker effects in CI. Prepare uses three distinct fresh local volumes with no adoption, prechecked exact mounts and 0:10001 with CHOWN/FOWNER only; Inspect separate 20002:20002, zero capabilities, exact RO mounts and independent root stat. Helpers retained; no automatic retry or cleanup. Existing Registry image unchanged. Live Gateway/Repo groups now observed; their actual userns maps, other active principals/writers, exclusive change fence and upstream image provenance still UNKNOWN. Independently reviewed evidence files and distinct owner GO mandatory; no volume creation or host admission.** **Owner Windows controller Plan and live groups readback (2026-11-24):** exact clean Approvals Windows `main` `ad5216ec33515292a5b749106c5e72100cbab53d` checked before no-effect `E13B_VOLUME_CONTROLLER_SOURCE_PLAN_ONLY_NO_HOST_GO`; exact Docker Desktop Linux context/named-pipe endpoint and original Gateway/Repo IDs pinned. Owner `docker top -eo pid,uid,gid,euid,egid,supgid,comm` returned Repo `sleep` PID 1023, `node` PIDs 3558/3583, each UID/GID/EUID/EGID 1000 and SUPGID 1000; Gateway `docker-init` PID 1022, `python` PID 1164, each UID/GID/EUID/EGID 10001 and SUPGID 10001; `E13B_LIVE_GROUP_METADATA_READONLY_COMPLETE`. No group 10001 or 20002 observed on listed Repo processes. This is actual observed process supplementary groups, not a kernel mapping proof for live peers, exhaustive other-writer census, immutable process pin or owner-exclusive change fence. Earlier isolated Registry UID/GID 20002/groups 20002 and identity maps remain separate evidence. No host effect or approval of Prepare/Inspect.** Latest Container #71 exact-head CI `45323390430` SUCCESS; merged/current Docker main `06c61697591530711e453396310d13ebb7401820`, sync `3aa9580b-dbde-4b07-a335-5916c0b6cc3c` EXECUTED. Owner Prepare/Inspect under exact #249 source subsequently PASS (step 7). | Source merge is not host GO. Current source/Windows Plan verified; distinct Prepare and Inspect GO consumed only for step 7. Future cleanup, Preview, Provision and releases remain separately gated. |
| 2 | Gateway pre-seal source digest and image-only build | ✅ Owner Windows image `sha256:97cf261f777bb389a90902654fa8a5c6ca59ff3f46423a4b7aff5d0dacf455cc` c revision=source SHA; `gatewaySourceDigest=7ac243a39ce9264e6330dea1288ba733d792f54a7cd892b40354de67932723a8`; рабочий Gateway **не переключён** | Digest ещё нужно связать с независимым host peer/nonce seal до Check |
| 3 | Registry base image and separate image-only build | ✅ **IMAGE_BUILT / OWNER-REPORTED EXACT POSTBUILD READBACK:** local `python:3.11-slim` Linux/AMD64 base `sha256:673719e071ecf27434fd2635bbd8d00f49f4fdd81f243143438a42ced8bedf60` independently checked as local ID (not upstream provenance). Previous Registry candidate `sha256:597152e7160930682a98f676f093243a5b18ebf70c3724bdbae98de21bb1402b` retained as historical, **not** the new bootstrap image. With narrow owner GO, Docker build from clean Approvals `9d6abc51ae17f3f8f32440b650e02a1300a3cac7` using `Dockerfile-Registry-Read-Candidate`, `--pull=false --no-cache --network=none`, build args `REGISTRY_UID=20002`, `REGISTRY_GID=20002`, passed and installed local tag `fortis-registry-pilot:e13b-9d6abc51ae17`; **new Docker image inspect ID `sha256:a4ac4df8b1125f377dd49a41050dd6bb74e314dee29ebeb2ae0a7ca09688e577`**, source revision label `9d6abc51ae17f3f8f32440b650e02a1300a3cac7`, `linux/amd64`, `Config.User=20002:20002`, base tag unchanged. `E13B_REGISTRY_IMAGE_ONLY_BUILD_PASS`; same Gateway container ID/image `sha256:2039987ce7c7b15d6fd6dea8111c79bf27098cdf5e9754ddea1a8034d3f20d50`, running/healthy after build. **2026-11-24 owner official upstream lineage PASS:** `docker buildx imagetools inspect` official `docker.io/library/python` OCI index `sha256:673719e071ecf27434fd2635bbd8d00f49f4fdd81f243143438a42ced8bedf60`, linux/amd64 manifest `sha256:6d10e720318bd84cc3d88af92bb5a47189222e17620a2fd214da6445e4afb679`, Python 3.11.18-slim-trixie, upstream revision `83054588043b3a7ac1ce8324c9242164b632beb9`. All four official `.Image.rootfs.diff_ids` equal all local base `.RootFS.Layers` and the first four of eleven Registry layers, in order. Attestation manifest present, signature not verified. Owner evidence summary SHA256 `efe97bf2aef9d89558aaa232cd396d96de6a31bf6b9f30bd41bcca13a6d724ff` bound to reviewed Prepare/Inspect (step 7). | Exact existing image retained. Isolated runtime probe PASS (step 4), no persistent listener or Gateway release. No rebuild/pull implied; any new image requires separate GO. |
| 4 | Реальные Linux runtime credentials, groups, self pidfd | ✅ **NEW_IMAGE_ISOLATED_PROBE_PASS / LIVE_PEER_MAPS_AND_ACTIVE_INVENTORY_PASS:** UC-CONT-021 owner read-only Engine `desktop-linux`, Linux 29.9.2, `SecurityOptions=[name=seccomp,profile=builtin;name=cgroupns]`. Current `fortis-gateway` exact container `03992c685e9abd2e3a65cf2071e57fa9f0bbdf83ad31f129a22b8f0ce8e0a8f1` running, `Config.User=10001:10001`, unchanged image `sha256:2039987ce7c7b15d6fd6dea8111c79bf27098cdf5e9754ddea1a8034d3f20d50`; `fortis-repo-test` exact container `1f67b67cacf3d4435982df9c0606dcb1a89d99f3f8ac73d365f3e6bb3d2f658b` running, `Config.User=1000:1000`, image `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`. Both `HostConfig.UsernsMode=""`; `GroupAdd` PowerShell `[null]` means null metadata, **not** verified Linux groups. Exact name filter returned `REGISTRY_VOLUME_CANDIDATES=0`, final `E13B_HOST_IDENTITY_METADATA_READONLY_COMPLETE`. Historical isolated **old-image** one-shot runtime probe showed `20002:20002`, groups `[20002]`, caps/NNP/seccomp/pidfd; not evidence for new image or live service. **NEW-IMAGE EVIDENCE:** Owner Windows **new Registry image** one-shot probe (2026-11-23, UC-CONT-021/025/016): separately owner-run exact `sha256:a4ac4df8b1125f377dd49a41050dd6bb74e314dee29ebeb2ae0a7ca09688e577` with `docker run --rm --pull=never --network=none --read-only --user 20002:20002 --cap-drop ALL --security-opt no-new-privileges:true --pids-limit 64 --memory 128m`, `python -I -B -c`, no mounts/listener/SQLite. Linux real/effective/saved `UID=(20002,20002,20002)`, `GID=(20002,20002,20002)`, supplementary groups `[20002]`; `/proc/self/uid_map` and `gid_map` rows `[[0,0,4294967295]]` map 20002 to 20002 **inside Docker Linux VM only**. Image-packaged owner bootstrap and reader imports PASS, actual `_runtime_confinement()` PASS (all caps zero/NoNewPrivs/seccomp/tracer), `os.pidfd_open(self)` PASS; `E13B_REGISTRY_ISOLATED_IMAGE_PROBE_PASS`; unchanged `fortis-gateway` instance/image running healthy `E13B_GATEWAY_UNCHANGED_PASS`. **This is isolated IMAGE runtime evidence, not Windows ACL/volume ownership/actual Gateway+Repo effective process groups/live peer or HOST_ACCEPTED.** **CURRENT LIVE PROCESS READBACK:** Owner Windows **live process EUID/EGID readback** (2026-11-23; UC-CONT-021/025): `docker top -eo pid,euid,egid,comm` on running `fortis-gateway` container `03992c685e9abd2e3a65cf2071e57fa9f0bbdf83ad31f129a22b8f0ce8e0a8f1`, image `sha256:2039987ce7c7b15d6fd6dea8111c79bf27098cdf5e9754ddea1a8034d3f20d50`, reports `docker-init` PID 1091 and `python` PID 1257 EUID=EGID **10001**. Running `fortis-repo-test` container `1f67b67cacf3d4435982df9c0606dcb1a89d99f3f8ac73d365f3e6bb3d2f658b`, image `sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`, reports `sleep` PID 1025 and three `node` PIDs 20682/22000/21604 EUID=EGID **1000**. Both `Privileged=false`, read-only root, `SecurityOpt=no-new-privileges`, `UsernsMode=""`, empty configured `GroupAdd` (NOT effective Linux supplementary groups). Gateway owns one `/state` RW mount plus seven other RO mounts; Repo RW mounts **the same** `fortis-repo-workspace` volume at `/workspace/files`, `/workspace/repo`, `/workspace/repos`, alongside separate `fortis-r7-client` RO. Do not expose any existing workspace or Gateway state volume to Registry. Named Registry state/config/socket candidate volumes still absent (`REGISTRY_VOLUME_CANDIDATES=0`); `E13B_LIVE_PROCESS_METADATA_READONLY_PASS`. This verifies live EUID/EGID observed by Docker Engine, NOT supplementary kernel groups, all host writers, owner volume/ACL, Windows host identity, or Registry socket/pidfd/Repo denial. Registry NOT_INSTALLED; E1.3b HOST_NOT_ACCEPTED. **Owner Windows controller Plan and live groups readback (2026-11-24):** exact clean Approvals Windows `main` `ad5216ec33515292a5b749106c5e72100cbab53d` checked before no-effect `E13B_VOLUME_CONTROLLER_SOURCE_PLAN_ONLY_NO_HOST_GO`; exact Docker Desktop Linux context/named-pipe endpoint and original Gateway/Repo IDs pinned. Owner `docker top -eo pid,uid,gid,euid,egid,supgid,comm` returned Repo `sleep` PID 1023, `node` PIDs 3558/3583, each UID/GID/EUID/EGID 1000 and SUPGID 1000; Gateway `docker-init` PID 1022, `python` PID 1164, each UID/GID/EUID/EGID 10001 and SUPGID 10001; `E13B_LIVE_GROUP_METADATA_READONLY_COMPLETE`. No group 10001 or 20002 observed on listed Repo processes. This is actual observed process supplementary groups, not a kernel mapping proof for live peers, exhaustive other-writer census, immutable process pin or owner-exclusive change fence. Earlier isolated Registry UID/GID 20002/groups 20002 and identity maps remain separate evidence. No host effect or approval of Prepare/Inspect.** **2026-11-24 owner actual peer mapping and active census:** after WSL `/proc` PID visibility STOP, separately scoped non-root `docker exec` read actual peer process uid_map/gid_map/status/user namespace and checked unchanged exact IDs/images/process lists. Gateway PID 1/7 UID/GID/groups 10001; Repo PID 1/350/364 UID/GID/groups 1000; both namespace `user:[4026531837]`, identity uid/gid map `0 0 4294967295`; `E13B_LIVE_PEER_MAP_READONLY_COMPLETE`. Active inventory 10 containers/23 processes: 7 containers UID/GID/groups 10001 (Gateway plus six RDG/Feedbrain), 2 at 1000, 1 at 70; no observed 0/20002; `E13B_ACTIVE_PRINCIPAL_METADATA_READONLY_COMPLETE`. UID 10001 is NOT unique to Gateway; exact socket attachment and kernel peer pins remain mandatory. Writer metadata: 10 active, no privileged/host PID/explicit devices, only extra CAP_NET_BIND_SERVICE (RDG proxy), only reported bind read-only Caddyfile; no direct Docker socket/root bind observed, Docker root `/var/lib/docker`, seccomp builtin/cgroupns. `E13B_WRITER_ACCESS_METADATA_READONLY_COMPLETE`. Owner confirmed exclusive no-concurrent-change window, not an atomic lock. Evidence SHA256 identity `f76a3be3e63c9bec4028f936e2240acabadc411ade36e659ccb6fa76464bbbcd`, fence `133b0a6209a020038ea383b60f5b9bf7c6f36a237c397cc4dca734c9e72b479b`; reviewed separately for Prepare/Inspect (step 7). | Identity evidence accepted for observed processes and exact image in this window; no claim of Windows ACL or permanent exclusive fence. Reconfirm fence/identities before later effects. Live Registry peer/pidfd and real Repo denial still pending. |
| **5** | **Новый source task — Registry owner bootstrap core** | ✅ **SOURCE_MERGED, HOST_NOT_ACCEPTED**: Approvals [#244](https://github.com/AlexPastukhh/fortis-approvals/pull/244), source head `5876ceee852cb3cb628da77e03f1d676415ef651`, merge `fd1c033bae41b60e6054efcd047170520c580a84`; Source CI `45148481628`, P5 Retained Impact `45148481655`, исправленный Fortis Release Impact `45149446959` **SUCCESS**. [Container #60](https://github.com/AlexPastukhh/fortis-container/pull/60), source head `bd2f38413f99767a2e10a9efb31414d82bc85110`, merge `1ab489b1d08b1a7dc9185cd3a2447ea6d9935d1c`, exact-head schema checks `45149825561` **SUCCESS**. Image-packaged owner-only `Preview` / distinct `Provision` (schema-3 SQLite + one private config) / inactive `Verify` source, 37 focused offline tests PASS; no completed owner host effect. `workspace.inspect` request `ddab75e1-1597-4258-8f33-153b21bddead` remains **UNCERTAIN**; prior UUID-less `403` was invocation error, not a proven permission block. | Historical old candidate `sha256:597152e7…` is obsolete; current exact new image and bootstrap imports PASS (steps 3–4). Owner launcher merged (step 6), fresh roots prepared/independently inspected (step 7); exact cleanup, Preview, Provision, backup/restore and live socket gates remain. |
| 6 | **Windows owner bootstrap launcher source** + exact host preflight | ✅ **SOURCE_MERGED / WINDOWS_PLAN_PASS / IMAGE_BUILT / NEW_IMAGE_PROBE_PASS / LIVE_PROCESS_EUID_EGID_PASS / HOST_NOT_ACCEPTED:** owner-merged Approvals #245 main `9d6abc51ae17f3f8f32440b650e02a1300a3cac7`, exact-head Source/Release Impact/P5 Retained CI PASS; Container #64 merged clean main `d4187482cbd852463b073e8830134e0b2ad1c4ba`, schema CI PASS. Windows PowerShell 5.1 launcher `-Action Plan` PASS under clean exact source SHA. UC-CONT-021: 46-container static inventory, new identity metadata on live Gateway/Repo with users `10001:10001`/`1000:1000`, current named Registry volume candidates `0`; metadata readback PASS. New owner GO-scoped image-only build `sha256:a4ac4df8b1125f377dd49a41050dd6bb74e314dee29ebeb2ae0a7ca09688e577` from current source, UID `20002:20002`, Gateway remains healthy unchanged. **Latest owner probe:** exact new image real UID/GID/groups, Linux VM maps, imports, actual confinement guard and self-pidfd PASS; no volumes/network/listener and Gateway unchanged. Owner Windows `docker top` confirms Gateway `docker-init`/`python` EUID=EGID `10001`, Repo `sleep`/three `node` EUID=EGID `1000`; exact unchanged running IDs/images, `Privileged=false`, read-only roots, NNP, Registry volume candidates zero. Owner volume plan #246 now merged, but the Windows bootstrap launcher is unchanged. Independent metadata-only `scripts/registry_owner_volume_preflight.ps1` (#247/#248 merged) ran on Windows successfully after the missing Name repair. **Owner Windows PS5.1 corrected Inventory PASS (2026-11-24; UC-CONT-021/025):** exact clean source `aa2b103228cb8409f311adb89839daa697a078d0` (historical built Registry image source revision `9d6abc51ae17f3f8f32440b650e02a1300a3cac7`, image `sha256:a4ac4df8b1125f377dd49a41050dd6bb74e314dee29ebeb2ae0a7ca09688e577`), exact existing Gateway/Repo container/image pins validated; Gateway healthy, Repo running at post-read. Owner-selected suffix `9c2a71ef`: `fortis-registry-state-e13b-9c2a71ef`, `fortis-registry-config-e13b-9c2a71ef`, `fortis-registry-read`. `E13B_CONTAINER_METADATA_SCANNED=46`, `E13B_DOCKER_SECURITY_OPTIONS=["name=seccomp,profile=builtin","name=cgroupns"]`, `E13B_OWNER_VOLUME_METADATA_READONLY_PASS`, then expected `E13B_USERNS_GROUPS_OWNERSHIP_WRITER_FENCE_UNKNOWN_STOP_BEFORE_CREATE`. At the readback, no target-name or mount-name/source collision found by the accepted metadata scan and no target attachments. Not an atomic writer fence, not proof of root ownership, supplementary groups/userns translations, Windows ACL, upstream base provenance or a live Registry peer. No volumes created by this action; no host writes, Preview, Provision, listener or Gateway cutover.** **Owner-merged executable volume-helper source (2026-11-24):** [Approvals #249](https://github.com/AlexPastukhh/fortis-approvals/pull/249), exact HEAD `ada14d80401326d83006fcc0bba22d97d4060d40`, merge/current clean Docker `main` `ad5216ec33515292a5b749106c5e72100cbab53d`, Source CI `45321536467`, Windows PowerShell 5.1 source fixture CI `45321536360`, P5 Retained `45321536306`, Release Impact `45321536263` all SUCCESS. Owner-approved push receipt `b1dab83d-d915-4e26-b796-94d10f36cb52` EXECUTED; typed main sync `5a027ffe-6dd8-45e1-9bf6-070026420c6f` EXECUTED. Separate owner-only `scripts/registry_owner_volume_controller.ps1` Plan/Prepare/Inspect and pinned independent Python helper sources merged; 41 offline tests PASS, no Docker effects in CI. Prepare uses three distinct fresh local volumes with no adoption, prechecked exact mounts and 0:10001 with CHOWN/FOWNER only; Inspect separate 20002:20002, zero capabilities, exact RO mounts and independent root stat. Helpers retained; no automatic retry or cleanup. Existing Registry image unchanged. Live Gateway/Repo groups now observed; their actual userns maps, other active principals/writers, exclusive change fence and upstream image provenance still UNKNOWN. Independently reviewed evidence files and distinct owner GO mandatory; no volume creation or host admission.** **Owner Windows controller Plan and live groups readback (2026-11-24):** exact clean Approvals Windows `main` `ad5216ec33515292a5b749106c5e72100cbab53d` checked before no-effect `E13B_VOLUME_CONTROLLER_SOURCE_PLAN_ONLY_NO_HOST_GO`; exact Docker Desktop Linux context/named-pipe endpoint and original Gateway/Repo IDs pinned. Owner `docker top -eo pid,uid,gid,euid,egid,supgid,comm` returned Repo `sleep` PID 1023, `node` PIDs 3558/3583, each UID/GID/EUID/EGID 1000 and SUPGID 1000; Gateway `docker-init` PID 1022, `python` PID 1164, each UID/GID/EUID/EGID 10001 and SUPGID 10001; `E13B_LIVE_GROUP_METADATA_READONLY_COMPLETE`. No group 10001 or 20002 observed on listed Repo processes. This is actual observed process supplementary groups, not a kernel mapping proof for live peers, exhaustive other-writer census, immutable process pin or owner-exclusive change fence. Earlier isolated Registry UID/GID 20002/groups 20002 and identity maps remain separate evidence. No host effect or approval of Prepare/Inspect.** Subsequent independent evidence and separate owner GO resulted in successful actual Prepare/Inspect (steps 3, 4, 7); previous no-volume and UNKNOWN claims describe earlier checkpoints only. | Bootstrap launcher source and Plan accepted. Next retain both exact helper receipts, separately approve exact-ID removal of only the two successful stopped helpers and verify zero target-volume attachments; no volume removal. Then independently select owner instance/scope/spec and separately approve Preview. No bootstrap GO yet. |
| 7 | Owner-selected instance/scope + schema-3 Provision | 🟡 **VOLUME_ROOTS_PREPARED_AND_INDEPENDENTLY_VERIFIED / SCHEMA3_NOT_PROVISIONED:** Approvals #246 merged; #247/#248 merged, corrected Windows read-only Inventory PASS. **Owner Windows PS5.1 corrected Inventory PASS (2026-11-24; UC-CONT-021/025):** exact clean source `aa2b103228cb8409f311adb89839daa697a078d0` (historical built Registry image source revision `9d6abc51ae17f3f8f32440b650e02a1300a3cac7`, image `sha256:a4ac4df8b1125f377dd49a41050dd6bb74e314dee29ebeb2ae0a7ca09688e577`), exact existing Gateway/Repo container/image pins validated; Gateway healthy, Repo running at post-read. Owner-selected suffix `9c2a71ef`: `fortis-registry-state-e13b-9c2a71ef`, `fortis-registry-config-e13b-9c2a71ef`, `fortis-registry-read`. `E13B_CONTAINER_METADATA_SCANNED=46`, `E13B_DOCKER_SECURITY_OPTIONS=["name=seccomp,profile=builtin","name=cgroupns"]`, `E13B_OWNER_VOLUME_METADATA_READONLY_PASS`, then expected `E13B_USERNS_GROUPS_OWNERSHIP_WRITER_FENCE_UNKNOWN_STOP_BEFORE_CREATE`. At the readback, no target-name or mount-name/source collision found by the accepted metadata scan and no target attachments. Not an atomic writer fence, not proof of root ownership, supplementary groups/userns translations, Windows ACL, upstream base provenance or a live Registry peer. No volumes created by this action; no host writes, Preview, Provision, listener or Gateway cutover.** Planned state/config roots `20002:20002` mode `0700`; socket `20002:10001` mode `02710` (setgid). Actual roots and ownership NOT_CREATED/UNKNOWN. **Owner-merged executable volume-helper source (2026-11-24):** [Approvals #249](https://github.com/AlexPastukhh/fortis-approvals/pull/249), exact HEAD `ada14d80401326d83006fcc0bba22d97d4060d40`, merge/current clean Docker `main` `ad5216ec33515292a5b749106c5e72100cbab53d`, Source CI `45321536467`, Windows PowerShell 5.1 source fixture CI `45321536360`, P5 Retained `45321536306`, Release Impact `45321536263` all SUCCESS. Owner-approved push receipt `b1dab83d-d915-4e26-b796-94d10f36cb52` EXECUTED; typed main sync `5a027ffe-6dd8-45e1-9bf6-070026420c6f` EXECUTED. Separate owner-only `scripts/registry_owner_volume_controller.ps1` Plan/Prepare/Inspect and pinned independent Python helper sources merged; 41 offline tests PASS, no Docker effects in CI. Prepare uses three distinct fresh local volumes with no adoption, prechecked exact mounts and 0:10001 with CHOWN/FOWNER only; Inspect separate 20002:20002, zero capabilities, exact RO mounts and independent root stat. Helpers retained; no automatic retry or cleanup. Existing Registry image unchanged. Live Gateway/Repo groups now observed; their actual userns maps, other active principals/writers, exclusive change fence and upstream image provenance still UNKNOWN. Independently reviewed evidence files and distinct owner GO mandatory; no volume creation or host admission.** **Owner Windows controller Plan and live groups readback (2026-11-24):** exact clean Approvals Windows `main` `ad5216ec33515292a5b749106c5e72100cbab53d` checked before no-effect `E13B_VOLUME_CONTROLLER_SOURCE_PLAN_ONLY_NO_HOST_GO`; exact Docker Desktop Linux context/named-pipe endpoint and original Gateway/Repo IDs pinned. Owner `docker top -eo pid,uid,gid,euid,egid,supgid,comm` returned Repo `sleep` PID 1023, `node` PIDs 3558/3583, each UID/GID/EUID/EGID 1000 and SUPGID 1000; Gateway `docker-init` PID 1022, `python` PID 1164, each UID/GID/EUID/EGID 10001 and SUPGID 10001; `E13B_LIVE_GROUP_METADATA_READONLY_COMPLETE`. No group 10001 or 20002 observed on listed Repo processes. This is actual observed process supplementary groups, not a kernel mapping proof for live peers, exhaustive other-writer census, immutable process pin or owner-exclusive change fence. Earlier isolated Registry UID/GID 20002/groups 20002 and identity maps remain separate evidence. No host effect or approval of Prepare/Inspect.** **2026-11-24 actual owner host actions (UC-CONT-021/025/016):** operation `dfba6213-f83f-42ca-a136-d269289dcc09`, independently reviewed evidence pins in steps 3–4 and exact #249 source/image pins. Prepare GO review SHA256 `fbffabc359fa7460b1a0be36a34f4df3fc3612fc5acd4ad1b1abe27177be911a`; repeat 46-container Inventory PASS immediately before first create. All three exact local volumes created, operation label, no adoption. Preparer exact ID `62f866307f13d69685c9a1982c272ef40aa496274de88b45bad96f42bcca0201`, 0:10001, CHOWN/FOWNER only, RW exact mounts, exited 0; `E13B_VOLUME_ROOT_PREPARE_PASS` and `E13B_VOLUME_PREPARE_OWNER_READBACK_PASS_INSPECT_REQUIRED`. Separate Inspect GO review SHA256 `13a1b4475cc1021965478f0328b534074977076390c1f8781602eca7e06da502`; inspector ID `7472332ea2083ed227bf7d4ba2fb9b4b2b30ef5ae19c2beb7fc73a8246ec28fe`, 20002:20002 zero caps, exact RO mounts, exited 0. `E13B_VOLUME_ROOT_INSPECT_READONLY_PASS`, `E13B_VOLUME_INSPECT_OWNER_READBACK_PASS`. Both receipts exact device 2112, state `/run/fortis-registry-state` inode 622121 UID:GID 20002:20002 mode 448=0700; config `/run/fortis-registry-runtime` inode 622287 20002:20002 mode 448=0700; socket `/run/fortis-registry-read` inode 622294 20002:10001 mode 1480=02710. All three roots independently verified empty, distinct and identical device/inode; baseline and attachment checks passed before/after. Both helpers retained stopped; `E13B_HELPERS_RETAINED_SEPARATE_OWNER_CLEANUP_REQUIRED_NO_BOOTSTRAP_GO`. No schema DB, listener or Gateway change. Evidence summary files/reviews remain private owner records; hashes bind bytes, not independent authority. | **NEXT / STOP:** retain exact logs and readbacks; separate GO for removal of only the two exact successful stopped helper IDs (no `-v`, force, volume removal, prune or retry); verify three named volumes and zero attachments, unchanged Gateway/Repo. Owner independently selects canonical instance/scope/spec; separate Preview GO, then separate schema3 Provision GO; later Verify, backup/restore, live peer/Repo denial, nonce seal, UC-GW-005. No HOST_ACCEPTED. |
| 8 | SQLite backup verified + independent inactive restore | 🔒 HOST GO REQUIRED (UC-CONT-022) | Owner private retention, correct SQLite WAL snapshot, digest and manifest, independently mounted inactive restore; `verify_inactive_local_backup()` alone is **not** restore |
| 9 | Socket/runtime/peer and real Repo-denial | 🔒 HOST GO REQUIRED | Socket dir `02710`/socket `0660`, no shared PID/socket privileges; independent live `SO_PEERPIDFD`+`SO_PEERCRED`+boot/socket inode, Repo EACCES/EPERM for socket and SQLite |
| 10 | Owner-sealed nonce-specific Gateway READ profile | 🔒 HOST GO REQUIRED | Unique fresh UUIDv4, exact pre-seal digest, owner-held separate RO profile volume, original history retained; reject RW/replaced peer/inode |
| 11 | UC-GW-005 manual Check/Apply/live readback/Backup/Promote | 🔒 SEPARATE GO PER EFFECT | Existing current/primary/attempt/history preserved, Check `-Build` and Apply checked image **without Build**, no `-Auto` initial activation; Return per UC-GW-006 |
| **12** | **E1.3b HOST_ACCEPTED** | ❌ **NOT_ACCEPTED**, Registry **NOT_INSTALLED** | Required independent complete E1.3b host evidence only; E1.4–E5 remain blocked |

**Обязательная актуализация P5 после каждого завершённого шага и в КАЖДОМ PR:**
(1) обновить именно эту таблицу и E0–E5 статус по подтверждённым фактам;
(2) показать все оставшиеся и STOP; (3) сверить порядок, зависимости и
критерии с применимыми UC, при необходимости изменить **будущие шаги**, а
не только пометку PASS; (4) проверить Release Impact и различить
`SOURCE_READY / PR_MERGED / WINDOWS_INSTALLED / IMAGE_BUILT / HOST_ACCEPTED /
FUNCTIONAL_V1_GO`; (5) перед merge проверить точные HEAD/CI и ещё раз
сопоставить roadmap с реальным состоянием. Source PR в Approvals должен
сопровождаться связанным обновлением **этого** нормативного Container
roadmap; не создавать второй authoritative plan. Пока PR находится в review,
не отмечать его как merged. После merge фиксировать реальный SHA, а не
предполагаемый. Если связанный roadmap PR оказался merged **раньше** source
checkpoint/readback, корректировать единственный нормативный roadmap
отдельным минимальным Container PR, не переписывая уже merged историю.
Нет подразумеваемого host GO от изменения документации.

**E1.3b — cross-check against EXISTING Gateway release admission (2026-11-23; SOURCE_REVIEW, NO HOST GO):**
The current owner-managed `fortis_approvals/deploy/Manage-Integrations.ps1`
creates a Gateway pilot with `--init`, `--read-only`, `--cap-drop ALL`,
`no-new-privileges`, fixed source/image/mounts and **without** `--pid`.
The active (not merely historical) `deploy/github_pilot_helpers.py::admit()`
**requires** `HostConfig.Init == true`, **empty** `PidMode`, **no**
`UsernsMode`/host binds/devices, and an **exact** allowlist of mounted
volumes. Only separately owner-approved Publisher and PowerShell mount
variations are recognized. Neither the new Registry activation mount nor
an alternative PID namespace is currently in that admission allowlist.
The separate E1.3 Functional V1 owner runbook explicitly says **do not
silently switch to shared or host PID namespaces**. UC-GW-005 requires
protected, source-pinned owner Check/Apply/Backup/Promote and separate
approval for new mounts/identities; container UC security boundaries
prohibit AI access to the Docker socket or arbitrary host namespaces.
**Therefore: current accepted controller SOURCE does not yet admit a live
Registry activation under the existing release contract, irrespective of
sandbox SO_PEERCRED PASS.** The exact controller SHA installed on Windows
has not been independently read back during this task; do not claim a
verified installed-controller capability from repository source alone.
A source-accepted Gateway image and Registry image do not automatically
extend the owner controller's allowlist or authorize Windows changes.

The earlier assumption “Gateway Python is PID 1” was **incorrect for the
reviewed release path**, because Docker `--init` inserts the PID 1 init
process. The actual Gateway Python PID remains to be verified on host;
current `PrivateCandidateReadService._real_peer` rejects `pid <= 1` and
therefore normally can admit a positive Gateway Python peer PID under the
required `--init` topology. This is not a substitute for kernel evidence.
`r7_unified_server.main()` still requires an **already running** Registry
socket and owner-sealed source/release/peer pins before starting Owner/Core.
Its requirement of startup ordering is an intended existing source contract,
not a reason to install a second Registry/API or authorization service.

**Rejected for the existing owner release contract:**
- `Gateway --pid=container:Registry`: Registry namespace init stop/restart
  can kill Gateway; no independent lifecycle.
- `Registry --pid=container:Gateway`: current Gateway startup requires a
  prebound Registry socket; there is a cold-start cycle. `--init` also means
  Gateway Python is not necessarily PID 1. Resolving this would require a
  source/runtime hot-start redesign AND owner security-policy change.
- Extra independent PID namespace anchor: the temporary shared-PID sandbox
  proved positive kernel peer PID, **but** a third runtime and a nonempty
  Gateway `PidMode` violate current owner release admission. Also introduces
  shared process visibility, anchor/owner restart dependency, and new
  lifecycle/rollback controls. **Not the recommended next experiment.**

**E1.3b — owner FORTIS_M cross-PID-namespace pidfd experiment (KERNEL_MECHANISM_PASS / IDENTITY_NOT_ACCEPTED):**
Владелец проверил два временных non-Production контейнера на Linux Docker
Desktop с **разными** PID namespaces `pid:[4026533244]` и
`pid:[4026533170]`. Оба ядром подтверждённых `SO_PEERCRED`
показали `pid=0` при правильных UID/GID; `SO_PEERPIDFD` вернул
pidfd с inode реального удалённого процесса, совпавшим с
независимо полученным `os.pidfd_open(getpid())`:
client увидел server inode `100438`, server увидел client inode
`100502`; маркеры `CROSS_NAMESPACE_PIDFD_IDENTITY_MATCH_PASS`,
`PEERPIDFD_PROCESS_EXIT_PASS`, `SERVER_PIDFD_CHECK_PASS` присутствуют.
Без `--pid`, новых capabilities, сети, image pulls и приватных mounts;
не было изменения действующих Gateway/Repo или owner grants.
**Технически межконтейнерная сверка процесса и фиксация его завершения
работают без shared namespaces.** Но взаимный обмен self-reported inode
в этом probe **не является owner authentication**; same-UID
подставной процесс сам может сообщить корректный inode. E1.3b остаётся
`HOST_NOT_ACCEPTED`.
Следующий единый source-cut (не новый API/policy engine): использовать
`SO_PEERPIDFD` с точным `fstat` inode и проверкой pidfd на живость;
обязательно сравнить с независимым owner-observed process inode,
закреплённым в отдельном immutable/read-only R7 mount, source/release
nonce, kernel boot UUID, Registry UID/GID и socket inode; недоверенный
Registry ответ **не** может выдавать себе pin. Отдельная серверная
проверка реального Gateway UID/GID и живого pidfd должна работать при
`SO_PEERCRED pid=0` без ослабления текущей RO/ACL политики. Закрывать
fd во всех ветках, сверять до/после ответа; при exit/restart/boot change
fail closed и повторное owner seal/restart. Нужно расширить строго
owner-reviewed Gateway release mount allowlist, иначе `UC-GW-005`
остановит поставку даже при прошедших pidfd тестах. Registry service
config `profile.json` (UID сервиса 0700/0600) сегодня не имеет
доказанного RO bind mount: не использовать его как доверенный
**owner pin** без отдельной защищённой границы. Источник owner-observed
pidfd inode и надёжное boot-id закрепление должны пройти independent
review; произвольное self-report/путь/env/Repo не допускаются.
**Source WIP E1.3b (NOT_MERGED / NOT_DEPLOYED):** в отдельной
авторизованной Approvals task worktree
`registry-e13b-pidfd-identity-source-20261123` локально изменены
**существующие** R7 Registry reader, readonly owner-mounted profile v2
(`registryPidfdInode`, `registryKernelBootId`, exact release/source pin),
Registry AF_UNIX listener с обязательным kernel pidfd + реальными
Gateway UID/GID даже при `SO_PEERCRED pid=0`; cross-UID owner probe
переведён на процесс/boot pin schema v2, Registry image COPY/catalog,
Functional V1 owner runbook, source manifests и отрицательные тесты.
Сохранён числовой PID **только** для legacy offline diagnostic
constructor, но v2 owner mount не может выбрать downgrade.
`SO_PEERPIDFD` требует Linux pidfs >=6.9 (64-bit), отсутствие
опции/pin, wrong UID/GID/boot или peer exit = STOP; каждый fd закрывается.
**97 совместных профильных тестов PASS** (Registry Unix, cross-UID probe,
owner R7 profile v2, Extension Provider, Owner Policy/WebAuthn, R7 TLS);
`source manifest --check` PASS. Исходники сохранены штатным Gateway
**только локальным WIP checkpoint** `c47eb031badff07a93ea00a89f45ba23a97ffda0`
в Approvals task branch; **никакого push/PR/owner merge**.
Полный `test-source.sh`, exact-head Source CI и Release Impact ещё
не выполнялись; source и host/owner release остаются не приняты.
Это **не** owner host admission: необходим независимый owner
process inode attestation, seal/restart/boot/Socket validation,
реальные cross-principal Repo denial/SQLite backup, и отдельная
**защищённая поддержка точного Registry readonly mount в
`Manage-Integrations.ps1`/`github_pilot_helpers.admit`**;
нынешний release controller его НЕ пропускает.
Не создавать PR на каждую проверку; собрать единый tested source cut
с корректным Release Impact и security review, не затрагивая live host.
**Переоценка оставшихся E1.4–E5:** E1.4 после E1.3b host + live
extension READ/browser Owner passkey, E2–E5 по-прежнему отдельные
Collector/WRITE → manual Board → Batch → owner GO, без CD/нового API.

**E1.3b follow-up source work — exact two-mount admission / owner process observation (WIP, NO RELEASE):**
После локального checkpoint `c47eb031...` текущая *та же* Approvals
task worktree дополнилась **отдельным read-only owner-invoked**
`registry/owner_candidate_pidfd_observation.py`: owner independently
выбирает процесс по Docker Engine `inspect/top`, инструмент сверяет
реальный live `pidfd_open(selectedPid)` с kernel `SO_PEERPIDFD`
**фактически соединённого Unix socket**, `/proc` security/process
start ticks, UID/GID, boot ID, socket mode/inode и owner-config mode.
Результат `SOURCE_ONLY_..._OBSERVATION` имеет
`containerImageVerified=false`, `ownerAcceptanceVerified=false`,
`profileSealed=false`, `releaseAdmitted=false`, не читает SQLite,
не запускает Registry и не запечатывает pin автоматически.
Инструмент работает только **после отдельного разрешения владельца**
и обязательной независимой Docker image/source/provenance сверки;
подмена `selectedPid` или spoofed listener должны давать STOP.
В Gateway `r7_registry_reader_mount.py` появился source-only
`reviewed_registry_reader_mount_digest()`: строгая загрузка
уже owner-sealed profile v2 + live socket kernel pidfd и SHA256
профиля, **без создания** mount/grant/volume.
Источник `github_pilot_helpers.admit()` теперь принимает лишь
**точную пару read-only mount**, но с защитой будущего rollback:
`fortis-r7-registry-reader-<owner-releaseNonce-UUIDv4-without-dashes>`
→ **фиксированный** `/run/r7-registry-reader`, и
`fortis-registry-read` → `/run/fortis-registry-read`.
Profile SOURCE volume уникален для каждого checked release; старый
запечатанный профиль нельзя переписать при новом `Check`/возврате.
Socket volume остаётся тем же, Registry — его единственный reviewed
writable владелец; private SQLite **не монтируется** в Gateway/Repo.
Partial pair, RW, arbitrary bind, wrong nonce, shared/host PID
и доп. capabilities STOP. Это проверка принятого security-контракта,
а не установка на Windows.
**Новый локальный (NOT_MERGED / NOT_WINDOWS_TESTED) owner controller
source-cut:** `Manage-Integrations.ps1` теперь имеет
**только manual** `-EnableRegistryMount -RegistryReleaseNonce <UUIDv4>`
при owner-approved source `Check -Build` → protected checked-image
`Apply -CheckedImageRecord` (nonce и digest профиля в точной Check
binding). `Image-RegistryMount-Preflight` в isolated non-root
Gateway image без TCP и image pull перепроверяет readonly owner
mount, installed source digest, live pidfd/kernel peer, socket inode
и возвращает SHA256 точных profile bytes. `Admit` повторяет
проверку старого и нового Gateway/при возврате; owner nonce в
`Runtime.releaseNonce` не генерируется повторно. Provider
`registry` и activation mount обязательны одновременно;
`-Auto` не активирует Registry, silent downgrade и reuse
nonce текущего source запрещены. Это **SOURCE_WIP**, без
PowerShell 5.1 SelfTest, actual source-image build, host-provisioned
nonce/profile и независимой owner attestation; не утверждать
готовность установленного Windows controller.
**Новый важный dependency gate:** профиль должен быть sealed
владельцем **до защищённого Check**, поэтому installed source
digest образа должен быть независимо доказан заранее из точного
approved source/image. Владелец ещё должен проверить отсутствие
реиспользования nonce во всей retained release history,
документированный startup/rollback с прежним профилем,
registry socket-writer provenance и невозможность mount mutation;
ни само имя volume, ни self-reported Registry inode этого
не доказывают. Нет второго Authorization/API или auto-CD.
**Сверка по нормативным release use cases (UC-GW-005/006/013,
UC-CONT-021/022; P3.4 owner Publisher mount), 2026-11-23:**
действующий UC-GW-005 **уже определяет** owner merge → guarded
Windows Mirror → PowerShell 5.1 SelfTest → manual exact
`Check -Build` → immutable checked-image record (image SHA, source
SHA, config/probe/scope) → отдельное owner GO →
`Apply -CheckedImageRecord` **без второй сборки** →
owner live readback → Backup → Promote. Первичный opt-in
mount/grant нельзя создавать через обычный `-Auto`;
P3.4 показал точный fixed read-only owner volume,
offline source-image digest preflight, Check/Apply binding
и повторную проверку без новых grants от source merge.
`UC-GW-006` требует original protected attempt, original
image/container/state IDs, protected pointers и один owner
Return/Resume без слепого повторного Apply. `UC-GW-013`
при отсутствующем previous image **не является штатным обходом**.
`UC-CONT-021/022` требуют точного owner Docker inventory,
RW-writer/consumer/rollback preflight и различения
BACKUP_CREATED, BACKUP_VERIFIED, RESTORE_TESTED/DR.
**Но эти UC НЕ содержат** операции, которая выдает
`gatewaySourceDigest` **до** Check/owner seal:
активный `r7_unified_server._installed_policy_source_digest()`
строит SHA256 canonical списка per-file SHA256 **Python/static
в реально собранном Gateway image**, это НЕ git source SHA,
НЕ Docker image ID, НЕ `MODULARIZED-SOURCE-MANIFEST.sha256`.
Значит до seal нужен отдельный owner-reviewed exact-image/source
*offline* readback этого digest из independently reviewed
owner image-only build/attestation, с последующим Check на
точной принятой исходной версии и строгой сверкой одинакового
внутреннего digest; незаявленный image build или self-reported
Registry digest не допускается. Нужно проверить возможность
этого протокола в самом owner runbook/Windows SelfTest, не
объявлять его уже выполненным.
Для rollback сохранение per-release named volume и SHA256
профиля в protected runtime/check **нужно, но недостаточно**:
требуются owner readback отсутствия RW writer/подмены,
revalidate старого live pidfd/boot/socket profile при Return,
previous image retention и история nonce; exit/restart
Registry или несоответствие старого profile — STOP с
оригинальным attempt, а не auto reseal.
**Эта проверка не меняет E1.4–E5:** после E1.3b host gate
только live READ/Owner WebAuthn (E1.4), затем независимый
authenticated Collector/granted WRITE (E2), manual Board (E3),
manual batching (E4), отдельный scoped GO (E5).
Второй локальный Approvals source checkpoint
`3ce4bd436d58c8d2d707ed9cbea4a16fc123a988`
сохранил этот инструмент, ровно два fixed read-only mount и
`reviewed_registry_reader_mount_digest()` со сверкой live peer,
сопутствующие отрицательные тесты, runbook, release target и
source manifest. **74 профильных теста PASS** после новой правки
owner process security (не допускаются неожиданные supplementary
groups), реально подключённый Unix listener отвергает другой
живой same-UID selected PID. `source manifest --check`, syntax,
`git diff --check` PASS; Approvals task branch чистая.
**Полный `scripts/test-source.sh` НЕ завершён и НЕ PASS:** он
добровольно остановлен после длинной группы native workflow;
запущенные test shell/unittest descendants затем адресно завершены,
другие процессы и WIP не затронуты. В журнале до остановки
явных FAIL не зафиксировано, но это **не** полный source acceptance.
**Третий локальный SOURCE_WIP checkpoint E1.3b —
`670a0b41a4c2d9f4fd9c10fd1182b4d57fc3fc6f` (NOT_PR /
NOT_MERGED / NOT_WINDOWS_TESTED):**
ручной `Manage-Integrations.ps1` `Check -Build` →
protected checked-image `Apply -CheckedImageRecord` требует явный
`-EnableRegistryMount -RegistryReleaseNonce`; nonce v4, отдельный
**per-release** readonly profile volume, fixed readonly socket
volume, обязательное совпадение `registry` provider и mount,
source-image/live pidfd/profile digest preflight **до остановки
старого Gateway**, повторный защищённый admission source/target/Return,
`registryReleaseNonce = Runtime.releaseNonce`. Runtime record и
checked-image binding хранят nonce, SHA256 профиля и оба volumes;
`-Auto`, silent downgrade, reuse nonce исходного Registry release,
несовпадение runtime nonce и расширение PID/privileges STOP.
Стандартный выпуск без Registry и Backup/Promote/Return сохранены.
Windows owner `SelfTest` дополнен offline record/flag tests, но
**не выполнялся на Windows**.
**230 итоговых профильных Registry/R7/WebAuthn/Owner/release
тестов PASS**, source manifests `--check`, git diff `--check`
PASS; task branch чиста после локального Gateway commit.
Полный `scripts/test-source.sh` остаётся **NOT_COMPLETE**;
нет actual Windows PowerShell 5.1 `SelfTest`, build/readback
точного Gateway + Registry image, independently attested Registry
process/source, owner-sealed profile, read-only socket mount и
реальных EACCES/SQLite backup/restore, exact-head Source/Release
Impact CI, owner merge, Windows sync или host GO.
**Проверка следующего порядка по E0–E5:** сначала ещё раз
security-review исходников E1.3b, проверить собственно **Windows
SelfTest/nonce/rollback semantics** на принятом source (после
одного содержательного GitHub PR/CI/owner merge и Windows guarded
sync); затем отдельное host owner GO на реальный nonprod Registry
listener, independent kernel pidfd/image attest + immutable profile
перед Check, исходный и новый Gateway release с сохранённым
rollback, Repo socket/SQLite EACCES/EPERM, schema3 backup/inactive
restore. **Только после доказанного E1.3b HOST acceptance — E1.4**
реальный Repo→TLS Gateway→Registry READ, browser WebAuthn и
revokes. E2 — отдельно authenticated GitHub Collector и
owner-granted planner-only WRITE (original UUID/CAS/UNKNOWN,
первый PENDING audit timestamp), E3 manual Board,
E4 ручные batch/supersession, E5 scoped Functional V1 GO.
Никаких новых API/policy/авто-CD или преждевременного
перехода к E1.4–E5.

**Local read-only SO_PEERPIDFD feasibility on 2026-11-23 (NOT_HOST_EVIDENCE):**
Fortis Repo's *development container* reported Linux
`6.18.33.2-microsoft-standard-WSL2`, Python `3.11.2` (the Python
`socket.SO_PEERPIDFD` symbol absent). An unprivileged, isolated
`AF_UNIX socketpair` call with native Linux optname `77` returned a
real kernel pidfd; `fstat` yielded a positive inode, `poll` reported
its referenced process alive, and `/proc/self/fdinfo` showed its local
PID. An independent same-process test obtained both `os.pidfd_open(getpid())`
and `getsockopt(SO_PEERPIDFD=77)` pidfds; their positive `fstat().st_ino`
values matched and initial poll was empty, with no processes signalled. No Docker Engine, Windows host, Registry, Gateway or credentials
were accessed. **This does not test independent PID namespaces and is not
an owner-pinned process identity**. Linux pidfs inode is documented as a
stable process identifier for 64-bit kernels >=6.9 for the current boot,
but source/runtime must prove the owner-trusted identity and restart
invalidation separately; never accept a self-reported inode alone.
Next owner-run isolated test: two ephemeral different-PID-namespace
containers with `SO_PEERCRED` expected `pid=0`, *positive*
`SO_PEERPIDFD` on both ends, `pidfd_open(getpid())` inode cross-
comparison and `poll` on peer exit. The test uses existing image,
no pulls/live mounts/network/grants or shared namespaces. Failures STOP.
**After-step E1.4–E5 review:** E1.4 remains behind actual owner E1.3b
identity, allowlisted mount, ACL and backup acceptance. E2–E5 remain
separate Collector WRITE, Board/manual reporting, batch and scoped GO,
unchanged. Preserve all existing release policy and source dependencies.

**Preferred research direction aligned with current architecture:**
keep independent Docker PID namespaces and reuse the existing fixed
owner-bound AF_UNIX mount, closed Registry provider/Core/Owner Policy V2,
exact source/instance/scope/UID/GID/socket inode, host access denial and
owner-controlled grants. Investigate whether the target Docker Desktop Linux
kernel supports **`SO_PEERPIDFD`** (Linux 6.5+) as a real kernel peer-process
handle across PID namespaces, and how an **owner-pinned, non-replayable**
Registry process identity can be checked against that handle. A pidfd merely
showing that *some* peer is alive does **not** by itself prove the approved
Registry instance. Treat absence of the option, insufficient identity proof,
unsupported Python interface, PID/restart ambiguity, or weakened owner
pinning as **STOP**, not a reason to compare UID/GID alone or accept `pid=0`.
Do not alter the accepted reader, listener, release controller or owner
profiles until this source/security design is reviewed and separately
approved. **If viable**, one scoped implementation cut must update the
existing Gateway and Registry identity contract, negative tests, owner
runbook, and exact Gateway controller admission for the *specific* readonly
Registry mount, preserving all current release gates. No parallel API or CD.
A later owner-run isolated two-container *no live mounts/no image pulls*
feasibility test for `SO_PEERPIDFD` may be used after source review and
explicit approval; do not repeat the three-container anchor experiment.

**After-step future E1.4–E5 review:** E1.4 remains blocked until identity,
owner mount/release controller support and real E1.3b host ACL/SQLite/backup
are independently accepted. E2 authenticated Collector/planner-only WRITE,
E3 manual event/Board, E4 manual batch and E5 scoped Functional V1 GO remain
unchanged, without a new authority service or unattended CD. Reassess future
stages after each verified source or actual host result, not only status.

**E1.3b — owner sandbox SO_PEERCRED 2026-11-23 (SEPARATE_PID_FAIL / SHARED_PID_PASS / HOST_STOP):**
На FORTIS_M владелец запустил временный тест **без image pull**, отдельной
сетью `--network none`, `--read-only`, `--cap-drop ALL`,
`--security-opt no-new-privileges`, двумя отдельными default Docker PID
namespaces и временным Unix socket/volume; действующие Gateway/Repo и
Registry runtime не менялись. Оба процесса установили соединение:
`CLIENT_OWN_PID=1`, `CLIENT_SEES_SERVER pid=0 uid=12002 gid=12002`,
`SERVER_READY own_pid=1`,
`SERVER_SEES_CLIENT pid=0 uid=10001 gid=10001`.
`RESULT=SERVER_PID_NOT_VISIBLE` подтвердил, что peer UID/GID видны,
но **PID другой стороны недоступен** в namespace проверяющего.
В повторном sandbox-тесте с `--pid=container:<temporary-server>`
(оба **временных** контейнера, `--network none`, `CapDrop=ALL`,
без image pull) `CLIENT_PID=7`, `SERVER_PID=1`,
обе стороны показывают `pid:[4026533170]`;
`CLIENT_SEES_SERVER pid=1 uid=12002 gid=12002` и
`SERVER_SEES_CLIENT pid=7 uid=10001 gid=10001`,
`SHARED_PID_NAMESPACE_TEST_PASS`. Это **только**
доказательство положительного kernel peer PID внутри общего namespace,
не admission Registry и не проверка restart.
Strict `GatewayRegistryUnixCandidateRead` требует именно тройку
`(registryPid>0, registryUid, registryGid)` и отказал бы при `pid=0`.
**Следовательно, topology с независимыми PID namespaces непригодна
для E1.3b; host pilot и E1.4 не начинать.** Никакие `CAP_*`,
`--pid=host`, игнорирование PID или подмена его Docker `State.Pid`
не разрешены. Следующий дизайн-gate **после успешного sandbox** —
security-review shared PID topology, namespace init/lifecycle,
independent restart, owner repinning and Repo denial. При отказе
от этой топологии потребуется отдельный owner-reviewed source/topology
fix с сохранением fail-closed kernel identity. Успех sandbox сам по себе
не является разрешением на изменение работающего Gateway или релиз.
**Критический риск жизненного цикла:** в PASS-тесте тестовый Registry-сервер
был `PID 1` общего пространства имён, а reader присоединился к нему.
Согласно Linux `pid_namespaces(7)`, завершение namespace init
`PID 1` приводит к `SIGKILL` остальных процессов в namespace.
Поэтому прямое `Gateway --pid=container:Registry` потенциально роняет
Gateway при остановке/рестарте Registry и **не принято**.
Изоляция `UID/GID` и `CapDrop=ALL` сохраняется на уровне соответствующих
проверок, но общая видимость `/proc`/процессов и зависимость от init
снижают прежнюю независимость жизненных циклов.
До нового релиза нужен review архитектуры PID owner, restart, pin
`registryPid` и inode при каждом restart, отката Gateway,
защиты от чужих процессов, сохранения `no-new-privileges`,
отдельных credentials/volumes. Рассмотреть отдельный стабильно
управляемый PID anchor **лишь как вариант**, не вводить автоматически
новый обязательный runtime, или owner-reviewed fail-closed
source/topology redesign без ослабления идентификации.
**Пересмотр будущих E1.4–E5:** E1.4 остаётся заблокирован до проверки
реального E1.3b host, E2–E5 не меняются; после нового измерения
пересмотреть весь оставшийся план, не только статус.

**E1.3b — owner Windows Docker inventory 2026-11-23 (PARTIAL_HOST_EVIDENCE / STOP):**
Владелец выполнил *только* read-only `docker version/info/ps -a/inspect` на
`FORTIS_M` (Windows PowerShell 5.1, Docker Engine 29.9.2). По его выводу
running `fortis-gateway` healthy, image
`sha256:2039987ce7c7b15d6fd6dea8111c79bf27098cdf5e9754ddea1a8034d3f20d50`,
user `10001:10001`, `Privileged=false`, `ReadonlyRootfs=true`, restart
`unless-stopped`, `PIDMode` и `UsernsMode` пустые; mounted `/state`
RW + существующие защищённые RO volumes, **без**
`/run/r7-registry-reader`. `fortis-repo-test` running, image
`sha256:f6d21fea25a8b67da533a8400f6eb7923a3d22605a00a784d35e3625253496d9`,
user `1000:1000`, тоже unprivileged и readonly rootfs; его RW
`fortis-repo-workspace` и RO `/run/fortis-client` не совпадают с
приватными Gateway mounts. Отдельный Registry container в предоставленном
`docker ps -a` не показан. Второй owner read-only `docker info/inspect`:
Docker Desktop Linux Engine `x86_64`; `fortis-gateway` Docker Engine PID
`1091`, `CapDrop=[ALL]`, `CapAdd=[]`, `GroupAdd=[]`,
`no-new-privileges:true`, `IPC=private`, `Network=bridge`;
`fortis-repo-test` Engine PID `1025`, те же снятые capabilities и
`no-new-privileges`, `IPC=private`, отдельная сеть
`fortis-repo-egress`. `Config.User` показывает заданные UID/GID, но
**не доказывает** реальный kernel `getresuid/getresgid` и supplementary
groups; Docker Engine PID — не PID peer внутри Gateway namespace.
Это **owner-reported output**, не независимое
Linux kernel/host readback и не доказательство запрета доступа Repo.
**Критическое уточнение E1.3b ДО image build/Check/Apply:** пустой
`PIDMode` у Gateway означает штатную Docker PID-изоляцию, при которой
`SO_PEERCRED` из будущего *другого* namespace может вернуть `PID=0`
или PID, не совпадающий с pinned `registryPid`. Утверждать точную
межконтейнерную PID-видимость без измерения нельзя; `State.Pid` из
Docker Engine **не** является значением `SO_PEERCRED` в Gateway.
Read-only `PidMode/UsernsMode/CapDrop/SecurityOpt` inventory **получен**;
следующий gate — отдельно owner-approved изолированный non-Production
feasibility test **двух временных контейнеров без участия существующего
Gateway/Repo и без новых Docker privileges**: точный kernel SO_PEERCRED
как видит reader при разных PID namespaces. До owner GO никаких новых
контейнеров, volumes, image pulls или runtime-команд.
Если точный положительный PID/UID/GID и device/inode
не доказаны без ослабления policy, **STOP и исправить E1.3b source/topology
в существующей архитектуре до release**, а не включать `--pid=host`,
CAP_* или пропускать проверку ради PASS. Нет owner host GO, Registry
image/volume/socket/SQLite и backup/restore admission.
**Сверка оставшихся E1.4–E5:** зависит от успешной E1.3b topology/host
приёмки; порядок collector WRITE → manual events/Board → manual batch →
scoped owner V1 GO остаётся прежним. После следующего owner host readback
пересмотреть план снова, а не только сменить статус.

**E1.3b — read-only preflight 2026-11-23 (NOT_HOST_EVIDENCE / STOP):**
После owner merge #55 и fast-forward `fortis-container/main` проверены единый
roadmap и фактические возможности текущего доступа. Fortis Repo выполняет
shell **в Docker-контейнере разработки**, не в установленном non-Production
Registry/Gateway host: здесь нет Docker CLI, Docker socket и трёх приватных
путей `/run/r7-registry-reader`, `/run/fortis-registry-runtime`,
`/run/fortis-registry-read`. Эти наблюдения **не доказывают отсутствие**
Registry/сокетов на целевом Windows/Linux host. Gateway native capability
предоставляет Repo/GitHub/read-only request inventory, **не** host Docker
inventory; PowerShell machine broker `policy=ASK`,
`machineExecutionAutoApprove=false`. Ни произвольный PowerShell submit, ни
Docker host call, ни owner Check/Apply/Backup/Promote не отправлялись.
**E1.3b HOST_NOT_ACCEPTED остаётся без изменений.** Следующая проверка —
отдельный owner-controlled `UC-CONT-021` inventory точного non-Production host
(контейнеры/image digests, PID/userns, реальные mount/UID/GID, private volumes,
backup/recovery), затем только по отдельному owner GO — `UC-GW-005`
owner-controlled release и независимая OS/peer/Repo-denial/restore приёмка по
`RELEASE-REGISTRY-FUNCTIONAL-V1-PILOT.md`. Не подменять отсутствующее
host-доказательство source/CI и не выдавать новые machine grants/Registry
WRITE ради preflight. **Пересмотр E1.4–E5:** порядок и условия без изменений;
E1.4 начинается лишь после принятой E1.3b на реальном host, E2/3/4/5 остаются
отдельными. Следующий выполненный шаг снова требует пересмотра будущего плана.

**Сверка после owner merge E1.3 source (#240 + #54; нет host GO):**
Оба исходных PR проверены по точным HEAD и merge-коммитам; обязательные
Source CI, P5 Retained, исправленный Release Impact с четырьмя target и docs
schema CI успешны. В рабочих `main` включён только source-код E1.3, не
Registry runtime, host permissions, новая машина или отдельный WRITE.
Реальные capabilities Gateway `registry`/`registryRead` по-прежнему не
появились; `SOURCE_MERGED` нельзя превращать в `HOST_ACCEPTED` или `LIVE`.
После source-сверки повторно проверены E1.4–E5: **E1.4** требует сначала
приёмки E1.3b на действительном host, затем штатного Repo→Gateway
`/v1/integrations/*`→Registry READ и owner browser/passkey/revoke, а не
native `/v1/reads`; **E2** остаётся отдельным authenticated Collector/
planner-only Registry WRITE/UUID/UNKNOWN; **E3–E5** — manual reports/Board,
batch и отдельный scoped owner FUNCTIONAL_V1_GO. Новых API, owner policy,
checkpoint/witness как условия Functional V1 и автоматического CD не нужно.
После реальной E1.3b host-проверки снова проверить и при необходимости
исправить **будущие** E1.4–E5 в этой же таблице/roadmap.

**Пересмотр будущих этапов после E1.3 source bootstrap (source != host):**
Архитектура не меняется: по UC-GW-002/003 остаются штатный `registry`
image-owned `Provider/Operation`, Core/Owner Policy V2 и существующие
`/v1/integrations/*`. Нового owner auth, публичного Registry HTTP, CD/WRITE
или второго источника истины не нужно. **Уточнён E1.3**, так как исходный
listener использовал непривилегированный `chown` для чужой группы: замена на
host-owned каталог **mode 02710** с наследованием GID и socket 0660 позволяет
работать без CAP_CHOWN/членства Registry в группе reader. Реальная установка
должна проверить права обеих сторон и что Linux наследует group на выбранном
filesystem. **Отдельно явен PID namespace gate**: Gateway pin `SO_PEERCRED`
должен быть реальным и согласованным с его namespace (PID=0/другой PID = STOP).
Для Functional V1 owner-pilot применима отдельная краткая **процедура**
`fortis-approvals/docs/RELEASE-REGISTRY-FUNCTIONAL-V1-PILOT.md`, а прежний
checkpoint/witness runbook принадлежит лишь HARDENING, не является E1.3
обязательным требованием. Новый non-Production build target плюс изменение каталога затрагивают
**четыре** release target при Impact учёте: `fortis-gateway`,
`fortis-registry-pilot`, `gateway-owner-controller` и
`release-label-publisher`. Учёт `image-rebuild`/`windows-update` не является
разрешением на сборку, Windows update или deployment.
**E1.4** по-прежнему требует после host acceptance настоящий Repo → TLS Gateway
`/v1/integrations/*` → Registry READ и реальный owner browser/passkey/revoke.
**E2–E5** сверены: separate trusted Collector/WRITE, manual report/Board,
P8 batch и scoped FUNCTIONAL_V1_GO без изменений порядка. После реального
E1.3 host pilot повторно пересмотреть E1.4–E5 на основе фактов, а не
только сменить статус.

**Повторная проверка единого roadmap после owner merge E1.2 (#239 + #53):**
Оба exact-head PR owner-merged, Source/P5 Retained/Release Impact/schema CI
SUCCESS; оба clean canonical `main` синхронизированы через typed Gateway,
только завершённые task worktree очищены. **E1.2 закрыт лишь как source**.
Live capabilities Gateway `registry`/`registryRead`/`registryCapabilities`
по-прежнему отсутствуют; новые machine grants и WRITE запрещены в E1.
Пересмотр E1.3–E5: E1.3 должен отдельно ввести owner-reviewed trusted
`r7_unified_server` reader bootstrap, изолированный Registry process/image,
private AF_UNIX/SQLite/backup и реальные разные UID/GID + независимый kernel
Repo-denial; virtual-key WebAuthn это не доказывает. E1.4 остаётся live
`/v1/integrations/*` READ и действительным browser/passkey Owner Portal
с actor/grant/revoke/restart и peer readback. Для E2–E5 сохранены original
Collector, отдельный planner WRITE/UNKNOWN, manual report/Board, P8 batch и
owner FUNCTIONAL_V1_GO: новых механизмов, изменения порядка или CD не нужно.
После E1.3 снова пересмотреть **будущие** E1.4–E5, а не только статус.

**Пересмотр будущих шагов после E1.2 (реальный cryptographic source fit; не live):**
Пакет `Registry` через существующий owner inventory и Owner Policy V2
оказался совместим с криптографическим **P-256 виртуальным** WebAuthn
и существующим `/v1/owner/policy/editor/*`, без правки production API,
policy engine, машинных grants и browser JavaScript. Тесты включают
точечный DENY→ALLOW, ASK до Unix IO, возврат DENY, отказ чужому
actor/target/session/CSRF/host/origin/UV, stale revision и one-use proof.
Source E1.2 не доказывает реальное устройство owner, host UID/peer или
браузерное отображение на установленном Gateway. Поэтому **E1.3**
остаётся отдельным owner bootstrap/isolated Registry runtime, а **E1.4**
уточнён: вместе с live machine READ обязателен явный owner browser UI
и реальный passkey check/deny/revoke. **E2–E5** снова сверены по
существующим UC: менять порядок, переносить WRITE в E1 или добавлять
новый сервис / API нет оснований.

**Повторная сверка оставшихся E1.2–E5 после owner merge #238/#51:**
E1.1 закрыт **только как принятый source**; installed Gateway capabilities
`registry`/`registryRead` отсутствуют, поэтому E1.4 по-прежнему NOT_LIVE.
Исправлена последовательность E1.2/E1.3: E1.2 проверяет **packaged**
provider, Owner Portal и настоящую криптографию WebAuthn в контролируемой
source-композиции **без требования live host**; отдельный owner-reviewed
host-bound Unix reader bootstrap в `r7_unified_server`, UID/GID/ACL,
backup и image release принадлежат E1.3. Так устранена циклическая
зависимость «Owner Portal до Docker, но с уже установленным host reader».
E1.4 по-прежнему требует live `/v1/integrations/*` readback, grants/revoke,
real peer и отдельное owner acceptance. E2 требует отдельный trusted
planner-WRITE, исходный merge/evidence, UUID/UNKNOWN и timestamp review;
E3, E4, E5 сверены — порядок/границы без изменений. Никаких новых
автоматических прав, второго Registry API или CD execution не добавлено.

**Сверка со старым планом (не терять уже принятые требования):**
D1–D7, единый writer, отдельный persistent Registry/backup, точный
`AlexPastukhh/fortis-approvals` forward-only enrollment, полный
collector/CI/review/catalog lineage, `no-deployment=0`, immutable UUID/CAS,
`UNKNOWN`, P6 owner report ≠ technical installed, P7 Board и P8 manual
batch **сохранены**. Старый E1 ошибочно начинался с host/socket, не
проверяя регистрацию Registry как управляемого provider. Старые
`candidate_*` и Unix/E1 probes — **source диагностика**, а не готовый
`registry.list_records` или ALLOW в Owner Portal. В выбранный extension
маршрут мигрировать клиент/адаптер только через review и совместимые
версии; удалять устаревший candidate path **после** accepted E2 readback,
не заранее. Проверки owner WebAuthn и policy grants нельзя заменить
синтетической регистрацией `core.adapters['registry']=object()`.
Provider credentials/CA через существующий [UC-GW-004](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/credential-lifecycle.md#uc-gw-004),
Gateway image activation — только [UC-GW-005](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005);
отдельная Registry runtime/backup установка остаётся owner-only.
Hardened checkpoint/witness и автоматический CD **после** Functional V1,
без удаления их source-кандидатов и без навязывания их E1.

**Обязательное правило после КАЖДОГО шага: статус + пересмотр всего
оставшегося плана (с 2026-11-23).** Каждый implementation PR обязан
иметь связанную правку **этой единственной таблицы** в `fortis-container`
(для кода из `fortis-approvals` — связанный docs PR). Проверить сначала
**реально выполненное** по SHA, CI, runtime/grants/owner receipts, затем
**актуальность каждого будущего E1–E5 шага**: соответствует ли он
существующим UC/Provider/Core/Owner Portal, нет ли дублирования API,
изменившихся зависимостей, устаревшего транспорта, неверного порядка,
ненужных этапов или новых доказанных STOP-gates. Если план всё ещё
корректен — добавить только проверенный результат и остаток; если
нет — в **том же** plan update заменить/удалить/переставить
будущие пункты и записать техническую причину. Не копировать roadmap
в другие документы; текущий task и следующий шаг выбираются по
актуализированной версии, а не по историческому handoff.
До owner merge не писать `MERGED`/`HOST_PASS` про открытый PR;
перед merge docs PR повторно сверять точные source SHA/exact-head CI,
фактический merge и live Gateway capabilities, после merge —
обновить main и статусы. После каждого завершённого шага показывать
пользователю таблицу E0–E5, выполненное, оставшееся и **что изменилось
в будущем плане (либо «не требуется»)**. Ни source CI, ни PR merge
не являются runtime/owner GO.

**Порядок ответственности:** E1.0–E1.2 — Gateway provider/Owner Policy
owner и UC review; E1.3–E1.4 — host/runtime owner с независимыми
UID/ACL/backup и отдельным Gateway release; E2 — Registry single-writer /
trusted collector + **существующий** Gateway Core/Owner Portal;
E3–E4 — тот же Registry/события и отдельные разрешения на P6 actions.
Новые Gateway methods, actor grants, machine credentials, first enrollment,
Windows/Production и изменение source image/volume только с отдельным
review и owner approval. В ИИ нет прямого SQL, shell executor, PAT,
GitHub POST или прав на Docker host.

**P6 — ручная отметка (PLANNED):** только immutable
`REPORTED_COMPLETE` для exact record/target/environment/source, с owner
statement, original operation UUID и CAS. Обновляет `lastOwnerReported`,
но не `lastVerifiedInstalled`; настоящий verified installed создаётся
только из protected controller receipt и независимого target readback
**на момент установки** (не из регулярного Docker-поллинга после merge).

**P7 — Fortis Release Board (PLANNED):** читает только принятый Registry;
показывает `desired`, `lastOwnerReported`, `lastVerifiedInstalled`,
pending/blocked/UNKNOWN, original PR/use-case и evidence class.
Не скрывает новейший desired за предыдущим owner report и не
присваивает `DEPLOYED` без технических доказательств.
GitHub Deployments — необязательная внешняя READ-проекция; GitHub
Projects **не** источник очереди.

**P8 — Release Batch (PLANNED):** строит план ручного выпуска по
repo/target/environment, shared build unit и зависимостям; владелец
выполняет существующие UC отдельно. Не добавлять в Board/Registry
автоматический controller/scheduler или универсальный CD executor.

**После Functional V1:** отдельный `HARDENED_REGISTRY_GO` —
защищённый owner checkpoint process + **независимый monotonic witness
вне общего rollback-domain**, совместный rollback/restore тест,
верифицированный Core owner-operation binding и hardening по
[owner runtime runbook](RELEASE-REGISTRY-P5-OWNER-RUNTIME-RUNBOOK.md).
Ни один источник с `rollbackProtected=false` не получает эту гарантию;
нельзя заявлять её как условие **уже достигнутой** Functional V1.
Не выбрасывать существующие hardened source-кандидаты, но и не
блокировать ими ограниченный ручной продукт. Автоматический CD —
ещё более поздний, отдельно авторизованный этап.

**Непереходимые границы:** ни GitHub Deployments WRITE, ни Production,
ни unattended CD, ни повтор physical install после lost ACK.
При `UNCERTAIN`/403/timeout читать исходную UUID/receipt и действовать
по [UC-CONT-003](use-cases/delivery.md#uc-cont-003) и
[UC-GW-009](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009).
Любой новый effect проходит обычный Gateway review; не создавать
вторую машину owner authorization. Technical integrity/details в
нормативных документах выше; **только этот раздел владеет очередностью**.

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

<a id="api-onboarding-workflow"></a>

## Future: автоматизация изменений Gateway integrations

**PLANNED / OWNER-REVIEWED DESIGN REQUIRED (2026-11-18).** Общая программа Fortis/Repo и владельца: подключение следующего API должно выглядеть как **мастер с проверяемыми шагами** для владельца и typed `propose/inspect` workflow для ИИ, а не как ручное переписывание инструкций. Это backlog общего процесса и Repo ergonomics, **не** второй Gateway policy store/approval UI или новый deploy controller. Технические задачи и owner Portal UI принадлежат [Gateway backlog](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/BACKLOG-IMPROVEMENTS.md#api-onboarding-program). Исторический Workfile P0 (`Workfiles/fortis-api-onboarding-priority-20261110/PLAN.md`) от 10 ноября не переносится дословно: Action Core и Machine ASK продвинулись; для Action Core есть план/hand-off 17 ноября.

**Что уже работает:** зарегистрированные typed Gateway providers/машинные actor scopes, owner ASK/WebAuthn, Core audit/receipts, provider scaffold/config/CLI, существующий `Manage-Integrations.ps1`, отдельные UC-GW-002/003/004/012. Наш Windows Executor положительный и Reject E2E доказывают **конкретный ASK-only route**, не установку произвольного API одним кликом. Сейчас **нет** owner UI управления всеми provider operations и ASK/ALLOW; machine catalog показывает только разрешённые данному actor операции.

### Общий user journey — последовательность, которую позже автоматизировать

1. **Выбрать направление и контракт:** Fortis → существующий upstream через [UC-GW-002](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-002), own Windows/Docker READ через [UC-GW-012](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/own-api.md#uc-gw-012), добавить native/extension метод через [UC-GW-003](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-003). Новый AI/machine client → Gateway — **другой** [UC-CONT-008](use-cases/authorization.md#uc-cont-008); по прежнему без конкретного consumer DEFERRED.
2. **Собрать входной пакет:** service/owner/environment, проверяемые по источнику и версии docs/OpenAPI как недоверенные данные, fixed origin/transport/CA, метод и expected response, READ/WRITE risk, actor/target/scopes, receipt/readback/preconditions и безопасный test target. Только публичные aliases, секреты вводит owner локально ([UC-GW-004](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/credential-lifecycle.md#uc-gw-004)).
3. **Получить детерминированный dry-run:** что поддерживается из trusted source, `SUPPORTED_AS_IS / NEEDS_TRUSTED_TRANSPORT / INSUFFICIENT_SPEC / UNSAFE_WRITE`, точный diff provider/source/config/permissions/credential aliases, необходимые Windows/Docker/CA/ACL работы, CI/Release Impact, rollback, независимые acceptance checks. Генерация — в зарегистрированном task worktree; URL/spec не становятся исполняемым plugin/HTTP proxy.
4. **Подготовить source и ревью:** reusable scaffold, schemas/routes/typed client and negative fixtures; [UC-CONT-002/003](use-cases/delivery.md#uc-cont-002) для task → commit → exact-SHA PR/CI → owner merge. Применение прав `ASK/ALLOW/DENY` и секретов не выполняется Repo workflow: ИИ может предложить точный diff, **владелец** выбирает, подтверждает WebAuthn и выполняет отдельную installation/activation по UC-GW-005.
5. **Проверить live и сохранить handoff:** source/merged/deployed/upstream-ready/live-verified — разные milestones. Gateway catalog, negative actor/target/auth, одноразовый READ; effect отдельно с immutable preview/owner ASK, bound receipt, uncertain без replay. Отсутствие проверяемого upstream proof → STOP/NOT_VERIFIED, а не «подключено».
6. **После пилотов — UI и AI assistant:** единый read-only экран inventory (полный только для owner; actor-scoped для ИИ), просмотр всех providers/операций/версий/actor/target/effective policy, owner-only изменения `ASK/ALLOW/DENY` с fresh WebAuthn на exact change и проверкой stale/race. Мастер «Добавить API» использует те же шаги, что и typed AI proposal, но не выдаёт ИИ прав на policy/secret/grant/release. UI должен различать native и extensions, а не вызывать один generic arbitrary endpoint.

### Очередь именно контейнера (не дублировать Gateway реализацию)

- [ ] **P0 (общий workflow):** один короткий entrypoint/шаблон intake и report, ссылки на UC, детерминированный staged plan, STOP/UNKNOWN, terminal vs resumable status; reuse текущих helpers и отдельные SOURCE/IMAGE/LIVE markers. Для пилота сначала Action Core READ с его собственными owner network/release gates, затем **второй независимый API** для доказательства переносимости. Без них не обещать «универсальный installer».
- [ ] **P1 (Repo-side assistant):** typed read-only discovery собственных capabilities + source fixtures; proposal на provider/operation/policy и проверяемый exact diff/PR, без прямого редактирования grants/owner config и credential bytes. Отдельно спроектировать resume оригинального UUID при ASK/UNKNOWN без повторной команды.
- [ ] **P2 (owner UX integration):** навигационная точка к Gateway Owner Portal providers/policies и к wizard; сохранить единый owner UI, без второй машины approval/политики. Проверить interoperability ChatGPT/Qwen в рамках их actor grants; не считать разные UI источником новых прав.
- [ ] **Границы безопасности и тесты:** никакого прямого provider token, host Docker socket, arbitrary Windows shell/HTTP, небезопасного privileged workflow; fail-closed default DENY, owner ASK на спорные операции, secrets только protected owner/Gateway. Негативные schema/transport/policy, provenance/rollback, in-flight UNCERTAIN и readback обязательны до автоматизации активации.

**Owner of record:** `fortis-container` — только общий Repo intake, orchestration ergonomics, ссылки/состояния; `fortis-approvals` — provider registry, owner-only inventory/Portal/WebAuthn policy UI, contracts, effects/release. Существующие UC-CONT-007/008 и UC-GW-002/003/004/005/012 остаются нормативными; этот план **не делает** будущие функции доступными. Не запускать runtime/credential update из документационного изменения.
