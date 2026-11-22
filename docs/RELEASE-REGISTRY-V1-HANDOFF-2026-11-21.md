# Fortis Release Registry V1 — передача работы новому чату (2026-11-21)

> **Датированный snapshot, не текущий статус на 2026-11-22.** После него
> слиты container PR #44/#45 и approvals PR #211 (source READ checkpoint),
> а owner-policy V3 source принят в approvals PR #216. Позднее source-only
> Registry READ/peer milestone #219/#220/#222/#223 тоже слиты. На 2026-11-22
> уточнён продуктовый план: ограниченная функциональная V1 event accounting
> и Board предшествуют отдельному anti-rollback hardening checkpoint/witness;
> решение **не** предоставляет действующий runtime GO. Для актуального
> состояния и порядка работ открыть **единственный**
> [P5–P8 roadmap](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue);
> точные спецификации — в ссылках ниже. Не создавать второй план по этому handoff.

**Проверенный исходный рубеж:** `fortis-approvals` [PR #210](https://github.com/AlexPastukhh/fortis-approvals/pull/210)
слит в `main` с merge SHA
`dba87732383e49f4cbff2076c7e62b4d22290253`.
Его точный HEAD `3fbbc58cb198d69f38acadb1d357f26c6d964771`
прошёл `offline-tests`, `audit-projections`, `release-impact` и
`p5-retained-impact`. Локальный чистый `fortis-approvals/main`
синхронизирован с этим merge через Gateway; cleanup PR #210 выполнен
(`EXECUTED`). Эти факты — **приёмка исходников**, не Registry release.
`fortis-container/main` перед **этим документационным PR**:
`3a404cd61df842641a68ed508dd4177ea0267bef`. После его
owner merge новый чат обязан сверить оба актуальных remote/main и
не принимать приведённые здесь SHA за живые данные.

**Краткий итог:** P1 и P2 завершены; P3 one-shot Publisher и P4 scoped
Deployments READ были приняты владельцем; P5 дошёл до offline
first-enrollment cutover preflight **в исходниках**, но **не запущен
и не прошёл отдельную owner runtime acceptance**. P6, P7 и P8 не
реализованы. Production, текущие Gateway/Publisher routes, GitHub
Deployments WRITE и live Registry WRITE этим циклом не изменялись.
Никакой реальный Registry enrollment или baseline для учёта релизов
пока **не был принят**.

## 1. Авторитетные документы — с чего начинать

1. Прочитать `/workspace/repo/README.md`, `/workspace/repo/AGENTS.md`,
   краткий вход [главного UC Registry](use-cases/README.md), **полностью**
   [UC-CONT-002](use-cases/delivery.md#uc-cont-002) и
   [UC-CONT-003](use-cases/delivery.md#uc-cont-003) и
   [UC-GW-009](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009).
   Не обходить Gateway через прямой Git push или GitHub connector.
2. **Единственный живой план:** [Fortis Release Planning / CD Queue](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue);
   нормативная модель/форматы: [Release Planning Contract](RELEASE-PLANNING-CONTRACT.md#post-merge-cd-queue-and-fortis-release-board).
   Датированный handoff — навигация и snapshot, **не второй roadmap**.
3. Архитектура D1–D7 и принятые пилотные решения:
   [P5 Design](RELEASE-REGISTRY-P5-DESIGN.md).
   Действующая offline реализация находится **в репозитории**
   [fortis-approvals/fortis_approvals/registry](https://github.com/AlexPastukhh/fortis-approvals/tree/main/fortis_approvals/registry);
   [typed/storage/owner-boundary contract](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/RELEASE-REGISTRY-P5-TYPED-BOUNDARY.md)
   и [retained collector / lineage contract](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/RELEASE-REGISTRY-P5-POST-MERGE-GATEWAY-CONTRACT.md)
   описывают реализованные source-инварианты и их пределы.
4. Более ранние offline-модели в `fortis-container` — самостоятельные
   **исторические прототипы**, не уже запущенная очередь:
   [component restrictions](RELEASE-REGISTRY-P5-COMPONENT-RESTRICTIONS.md),
   [durable restrictions](RELEASE-REGISTRY-P5-DURABLE-CONSTRAINTS.md),
   [desired preview](RELEASE-REGISTRY-P5-DESIRED-PREVIEW.md),
   [desired store](RELEASE-REGISTRY-P5-DESIRED-STORE.md),
   [readiness](RELEASE-REGISTRY-P5-POST-MERGE-EVIDENCE.md).
   [Handoff 2026-11-20](RELEASE-REGISTRY-V1-HANDOFF-2026-11-20.md)
   — **архивный**, с устаревшими тогдашними статусами/403, не
   инструкция продолжать ту старую task-ветку.

## 2. Что сделано в P5 после первоначального дизайна

Основной scope пилота: **только**
`AlexPastukhh/fortis-approvals`; учёт **forward-only** с первой
отдельно принятой владельцем Registry release/enrollment. Никакого
backfill исторических PR/CI/инсталляций. С момента этого будущего
cutover должна быть доказана полная непрерывная post-baseline
first-parent lineage; неизвестный actual остаётся UNKNOWN. Источник
учёта — Fortis Registry, а не GitHub Deployments.

**В `fortis-approvals` слиты source-only PR:**

| PR | Проверенная в исходниках часть P5 |
| --- | --- |
| [#194](https://github.com/AlexPastukhh/fortis-approvals/pull/194)–[#196](https://github.com/AlexPastukhh/fortis-approvals/pull/196) | Закрытая typed boundary, retained collector candidate, forward-only lineage |
| [#197](https://github.com/AlexPastukhh/fortis-approvals/pull/197)–[#199](https://github.com/AlexPastukhh/fortis-approvals/pull/199) | Registry-specific review/CI policy candidate и retained evidence, pinned component/environment bindings |
| [#200](https://github.com/AlexPastukhh/fortis-approvals/pull/200)–[#203](https://github.com/AlexPastukhh/fortis-approvals/pull/203) | Детерминированный initial/suffix план, SQLite schema v1/v2, неизменяемые операции/receipt и supersession |
| [#204](https://github.com/AlexPastukhh/fortis-approvals/pull/204)–[#206](https://github.com/AlexPastukhh/fortis-approvals/pull/206) | Inactive backup readback, **offline** owner checkpoint CAS, read-only checkpoint/recovery reconciliation |
| [#207](https://github.com/AlexPastukhh/fortis-approvals/pull/207)–[#209](https://github.com/AlexPastukhh/fortis-approvals/pull/209) | Unix `SO_PEERCRED` source boundary, Linux process/volume isolation preflight, реальные `os.open` denial probes **только в специально запущенном соответствующим principal процессе** |
| [#210](https://github.com/AlexPastukhh/fortis-approvals/pull/210) | Genesis-only first-enrollment cutover preflight с exact main/baseline, owner checkpoint и согласованными offline host observations |

Условие не менялось ни в одном из этих PR:
**offline success ≠ independently authenticated owner/host ≠ live
Registry authority**. Входы для позитивных тестов synthetic/injected,
совпадение SHA256 двух локальных JSON не доказывает происхождение
kernel evidence, прав владельца или защищённость свидетеля.
Сама Registry v2 SQLite, owner CAS и host denial probes сейчас
существуют как source-кандидаты, а не развёрнутые отдельные
процессы с независимо доказанной изоляцией.
Вся новая логика Registry вне current image inputs через
`fortis-approvals/release/targets.yaml::noDeploymentPaths`.
Источник до #210 проходит локальные/CI регрессии; не объявлять
результат CI доказательством реального Windows/Docker E2E.

## 3. Что ещё нужно до P5 GO (в порядке реальных зависимостей)

Сверять при исполнении с [живым roadmap](BACKLOG-IMPROVEMENTS.md#fortis-release-planning--cd-queue).
**Не устранять пробел безопасности новыми флагами `verified=true`
или копиями одного SQLite под тем же UID.**

1. **Owner-reviewed runtime и настоящий trust boundary.** Подготовить
   конкретную минимальную deployable архитектуру отдельного Registry
   процесса и независимого owner checkpoint service/volume,
   UID/GID/userns/mount/backup topology, encrypted-at-rest и
   provisioning/restart/retirement runbook. Ни один host path,
   credential или volume не считается уже существующим. Требуется
   отдельный owner GO для реальных host/Windows/Docker изменений.
2. **Защищённый, нероллбэкный checkpoint и authenticated origin.**
   Реальный Registry writer/Repo/Gateway/Publisher не должны иметь
   возможность менять owner ledger или продвинуть CAS без отдельного
   owner-решения. Нужны independently retained owner evidence,
   original pending operation readback, защита от отката *обеих*
   локальных копий, crash/lost ACK/restart/restore negative E2E и
   защищённый способ owner acceptance. Текущий offline CAS и
   Linux preflight **этого не гарантируют**.
3. **Trusted collector + typed Registry runtime.** Доверенное
   получение immutable reviewed merge/CI/Release Impact/catalog
   evidence, непрерывная lineage и dependency closure; отдельный
   planner principal и read-only reader с exact repo scope.
   Реализовать bounded API: capabilities, preview, list/get,
   original operation lookup и единственный узко авторизованный
   `ingest_merged`; никаких raw SQL, caller-paths, actor claims,
   GitHub tokens в Registry. WRITE/публичный REST пока DENY.
4. **Protected first enrollment.** Владелец *отдельно* принимает
   точный исходный main/catalog/component/policy и защищённый genesis
   через WebAuthn/owner-controlled ceremony. Проверить, что main
   **не изменился между выбором и активацией**; иначе доказать все
   промежуточные merges как post-baseline, а не молча сменить baseline.
   Не объявлять текущий `dba877...` будущим enrollment baseline:
   это только исходный SHA source-ветки на дату handoff.
5. **Inactive backup/restore + один non-Production E2E.** Проверить
   отдельные идентичности и реальные EACCES/EPERM для Registry и
   Repo, ownership/namespace, закрытые publisher/Gateway права,
   source/readback и duplicate/stale/pending/rolled-back receipt
   сценарии; проверить нулевые записи для валидного no-deployment и
   непустую PLANNED_UNVERIFIED очередь на полном accepted evidence.
   Backup в неактивный экземпляр; switchover только по owner GO.
   Только после этого принимать live P5. Это не автоматический CD.

**Отдельный долг безопасности GitHub:** на дату проверки
`fortis-approvals/main → protected:false` (также
`fortis-container/main → protected:false`). Четыре CI для #210
реально завершились SUCCESS, но GitHub не требовал этих результатов
перед Merge. Включить и независимо проверить GitHub branch
protection/ruleset — отдельная owner/GitHub settings задача.
До реального enforcement проверять четыре exact-HEAD CI вручную
перед каждым owner merge; не говорить «гейт включён».

## 4. После P5: не перескакивать этапы

- **P6:** scoped append-only `REPORTED_COMPLETE` по точному
  report владельца, target/environment/desired SHA и original
  operationId с revision CAS. Это *не* `DEPLOYED` и не изменение
  actual без protected controller receipt + independent target readback.
- **P7:** собственная **Fortis Release Board** читает Registry,
  показывает UNKNOWN/blocked и классы доказательств, не запускает
  install. GitHub Projects/Deployments не источник очереди.
- **P8:** Release Batch группирует изменения, target и shared
  build units; execution остаётся ручным по существующим UC.
- **Post-V1:** unattended CD orchestration/автоматический сбор
  technical receipts — **не авторизованы**.

Релизные ограничения по компонентам/shared resources моделируются
как **активные запреты конкретных операций**, а не как allowlist
обычной работы. Отсутствие ограничения никогда не даёт разрешения.
Не реконструировать старые GitHub branch rules и PR body ради baseline;
принята Registry-specific protected policy/CI альтернативная модель,
но защищённое исполнение/owner acceptance ещё впереди.

## 5. Операционный маршрут следующего чата

1. Сверить через **typed Gateway** remote `main`, PR/CI по точному
   HEAD, действующие capabilities и локальный clean primary обоих
   проектов. Перечитать актуальный roadmap, не полагаться на dated SHA.
   Никакого `git push`, GitHub connector или смены токена в обход
   Gateway. Старые worktrees других задач не удалять.
2. Если этот документационный PR ещё **OPEN**, сначала довести его
   CI/owner review/merge и штатно синхронизировать
   `fortis-container/main` через `update_main_from_pr`; cleanup
   только его точного зарегистрированного task-worktree.
   Не создавать второй PR для той же пары head/base.
3. **Следующая предметная задача P5:** owner-reviewed source design
   и runbook *реального* owner-isolated checkpoint/Registry runtime
   с identity/storage/transport/provisioning/rollback proof,
   возможно сначала в `fortis-container` для решения D1/D6.
   После review — конкретный узкий implementation PR в
   `fortis-approvals` и real host acceptance **только по
   отдельному owner GO**. Приоритет — устранить отсутствие
   независимой реальной authority, а не писать ещё один
   synthetic preflight с флагами false.
4. При очередном source PR пройти test/diff/source manifests,
   typed Gateway stage/commit/push/PR, от владельца — merge
   **только после всех required exact-head checks**. Для
   `fortis-approvals`: `offline-tests`, `audit-projections`,
   `release-impact`, `p5-retained-impact`.
   Описать честный Release Impact. GitHub merge ≠ deployment.
5. После owner merge: проверить exact PR head, remote merge SHA,
   clean local main, GitHub CI, выполнить
   `workspace.update_main_from_pr` и guarded `cleanup_task`.
   Windows sync, Primary/Publisher release, смена policy/grants,
   credentials, runtime volumes и отдельный E2E — только при
   конкретном scope и owner authorization; docs-only такой sync
   не требует.

**Доставка этой передачи:** она написана в отдельном task-worktree
`fortis-container`. Её принятие определяется **новым**
документационным PR/четким CI/owner merge, а не фактом существования
файла в Docker. При подозрении на другой активный PR readback-first
по UC-CONT-003/UC-GW-009. Фактические PR и commit этого handoff
проверять в GitHub, не угадывать номер.
