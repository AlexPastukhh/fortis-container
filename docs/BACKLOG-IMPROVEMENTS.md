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

**E1.0 — выбранный source-путь к ревью (проверка 2026-11-23;
до owner merge и runtime release не является установленным provider):**
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
  Регрессия в связанном Approvals source PR E1.0; если PR ещё открыт,
  факт `SOURCE_FIT_PASS` означает тест, не merged code.
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
| **E1.0 — выбор API-пути** | Один provider и один API: штатный `extensions/` + `Provider/Operation`/Core/Owner Portal, trusted AF_UNIX transport; native candidate остаётся диагностикой. | 🟡 **SOURCE_FIT_PASS / OWNER_MERGE_PENDING**: same-UID R7/Unix/schema3 + extension/Core/Policy V2 regression; не live, PR ещё требует CI/owner merge. | Owner принимает source test+решение; перепроверить E1.1–E5 после merge; реальные UID/packaged runtime — E1.1/E1.3. |
| **E1.1 — packaged Registry provider** | Image-owned `integrations/registry/extension.py`, typed READ `Operation`, штатные `/v1/integrations/catalog|call|result`, существующий Repo extension client, проверенный owner-bound AF_UNIX handler, единственный `registry` service ID. | ⬜ **NOT_PACKAGED**; тестовый provider существует только в source fixture; /v1/reads остаётся историческим seam. | Реальная trusted injection/socket binding, schemas/result, source image/manifest, exact actor config, conflict DENY, no WRITE/grants/alternative native public route. |
| **E1.2 — Owner Portal acceptance** | Packaged Registry методы показаны в реальном source-composed Owner inventory, policy edit V2/WebAuthn, DENY/ASK/ALLOW и revoke, scoped actor/target; editor не выдаёт новый machine grant. | ⬜ **NOT_PACKAGED**; E1.0 проверил этот путь **только** с синтетическим owner и тестовым adapter. | Проверить реальные schema/handler, authorized policy admission, реальную owner-cryptographic проверку в CI и связку штатного UI; без нового policy engine. |
| **E1.3 — non-Production Docker pilot** | Owner-approved отдельный Registry image/process и AF_UNIX, защищённая SQLite+backup/restore, pinned Gateway source/image, реально разные UID/GID и kernel Repo-denial. | ⬜ **HOST_BLOCKED**; не проверены реальные peer/UID и нет live Registry. | Доверенная source→image binding для Unix reader, service UID/socket/permissions, backups, deployment/recovery по UC-GW-005; независимый EACCES/EPERM. |
| **E1.4 — live extension READ** | Настоящий Repo `extensions.client` → TLS Gateway `/v1/integrations/call|result` → Core/Registry provider → AF_UNIX → SQLite → Repo; original UUID, restart, grants/revoke и Repo-denial. | ⬜ **NOT_LIVE**: старый `/v1/reads` пробник вернул `FORTIS_HTTP_403`; это другой маршрут, не доказательство extension READ. | Владелец принимает независимый host live readback/deny и restart; candidate данные не называются authoritative Desired. |
| **E2 — P5 Desired** | Owner-reviewed настоящий GitHub merge → существующий GitHub provider + authenticated Collector/evidence → отдельный planner-only `registry.ingest_merged` → single-writer Desired → **тот же** Registry extension READ. | ⬜ **NOT_STARTED_LIVE**, offline fixture существует. | Новый reviewed WRITE `Operation` через тот же Core: preview/receipt/lookup, ID/CAS/UNKNOWN, first forward-only enrollment и отдельный owner WRITE grant; valid no-deployment=0. Отдельно доказать устойчивую Core `createdAt` ↔ первый PENDING audit timestamp связь при переходе через границу секунды (тестовая фиксация часов не является runtime-исправлением). |
| **E3 — P6/P7** | Отдельно разрешённый manual `REPORTED_COMPLETE` → immutable event; Board отдельно отображает Desired / OwnerReported / VerifiedInstalled / UNKNOWN. | ⬜ **NOT_STARTED_LIVE**. | Owner event+receipt; никакого `DEPLOYED` без controller proof и независимого target readback. |
| **E4 — P8** | Второй реальный merge supersedes Desired, оставляет pending; Release Batch группирует зависимости/build units и предлагает **ручные** UC. | ⬜ **NOT_STARTED_LIVE**. | Реальная сохранность очереди, version provenance, отказные сценарии, без CD execution. |
| **E5 — Functional V1 acceptance** | E2–E4 целиком с cold restart, duplicate UUID, rejected source, missing CI, restore, revoke, no-deployment, UNKNOWN и owner proof. | ⬜ **NOT_ACCEPTED**. | Отдельный scoped non-Production `FUNCTIONAL_V1_GO`; PR/CI/host E1 сами по себе не GO. |

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
