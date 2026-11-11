# Backlog improvements — Fortis Container

**Status:** ACTIVE BACKLOG. Завершённые этапы отмечаются отдельно с evidence; будущие пункты **не разрешают** выполнять runtime operations без owner review. Это единственный backlog репозитория. Исторические source/plan записи здесь не являются текущим live state.

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

## Future: CI, GitHub Actions и сценарии настройки

**Release workflow V1 / PARTIALLY IMPLEMENTED:** [shared format](RELEASE-PLANNING-CONTRACT.md), JSON Schemas, common offline validator and `release-schema-ci.yml` are owner-merged, with five source catalogs on `main`. **Not yet active:** shared cross-repo PR gate (new `.github/actions/release-impact-v1/` and `tools/release/ci_entry.py` source candidate), the necessary private GitHub Actions sharing access, pilot and per-repo wrappers/required checks, automatic Labels, Projects queue, typed Gateway Project/Deployment API, Release Batches, live deployment evidence. Validate and merge shared composite action first, owner-enable private action sharing if acceptable, then pilot exact-head PR checks; preserve existing project CI. Extend UC-CONT-018/002/027 only for accepted behavior, register UC-CONT-028 when ready. Existing Gateway/Windows security contracts remain authoritative.

**PLANNED:** подробнее разобрать модель CI/GitHub Actions и оформить повторяемый
путь создания и изменения CI для нового или существующего репозитория.

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
