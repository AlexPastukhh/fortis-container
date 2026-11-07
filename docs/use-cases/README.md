# Fortis — главный реестр Use Cases

Этот реестр — **маршрутизатор**, не обязательный каталог для построчного
прочтения. Use Case отвечает: когда появляется повторяемая ситуация, как выбрать
подходящий путь и что считать результатом. Кодовые контракты и live состояние
остаются у собственных владельцев.

## Обязательное чтение каждого нового чата

1. Учитывать исходное сообщение пользователя (включая то, которое вызвало чтение README).
2. **Полностью прочитать [UC-CONT-002 — Docker → GitHub → CI → Windows/Mirror](delivery.md#uc-cont-002)**
   и **[UC-CONT-003 — GitHub только через typed Gateway-клиент](delivery.md#uc-cont-003)**.
3. Определить контекст по [UC-CONT-001](orientation.md#uc-cont-001): один,
   несколько, новый репозиторий после согласования или работа без репозитория.
   README, открытый для ориентации, **не означает** владение текущей задачей.
4. При необходимости открыть **только применимый локальный реестр** и выбранные
   UC/технические owners. Нужный repo нельзя определить, но он обязателен —
   спросить одним вопросом; репозиторий не нужен — продолжить без него.

**Не нужно читать или даже просматривать весь главный реестр или реестры всех
проектов.** При неподдерживаемом Gateway repo/scope действует
[UC-CONT-018](delivery.md#uc-cont-018), а не GitHub PAT или прямой push.

## Быстрый маршрут

| Ситуация | Выбрать |
| --- | --- |
| Контекст, один/несколько/новый repo или работа без repo | [UC-CONT-001](orientation.md#uc-cont-001) |
| Сквозное изменение GitHub/CI/Windows | [UC-CONT-002](delivery.md#uc-cont-002), [UC-CONT-003](delivery.md#uc-cont-003) |
| Изменение Docker / backup / retire & cleanup | [UC-CONT-021](docker.md#uc-cont-021), [UC-CONT-022](docker.md#uc-cont-022), [UC-CONT-023](docker.md#uc-cont-023) |
| Fortis Repo image / Repo1+Repo2 Guards / owner-run Windows | [UC-CONT-026](docker.md#uc-cont-026), [UC-CONT-025](host-operations.md#uc-cont-025) |
| Новый UC / документация DRY и карта исходников | [UC-CONT-024](orientation.md#uc-cont-024), [UC-CONT-017](orientation.md#uc-cont-017) |
| Gateway/Sonar/credentials/Primary | [Gateway registry](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/README.md) |
| Mirror/Windows/UI/API | [Mirror registry](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/use-cases/README.md) |

## Каталог локальных реестров

Один проект может содержать несколько реестров. Главный реестр содержит **ссылки
на реестры**, не копирует их UC. `ACTIVE` — реестр уже существует в текущем
repo; `PREPARED` — создан в отдельном task worktree, но ещё не принят в main;
`NO REGISTRY` — проект использует другой действующий индекс.

| Репозиторий / область | Реестр / owner | Статус |
| --- | --- | --- |
| `fortis-approvals` | [Gateway use cases](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/README.md) | ACTIVE (`UC-GW-001…008` в `main`, PR №29/30 merged) |
| `docke-windows-mirror` | [Mirror use cases](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/use-cases/README.md) | PREPARED до одобренного merge |
| `tunnel` | [Tunnel use cases](https://github.com/AlexPastukhh/tunnel/blob/main/docs/use-cases/README.md) | PREPARED до одобренного merge |
| `script-control-center` | [Script Center use cases](https://github.com/AlexPastukhh/script-control-center/blob/main/docs/use-cases/README.md) | PREPARED до одобренного merge |
| `obs-planning-docs` — repository | [Planning repository registry](https://github.com/AlexPastukhh/obs-planning-docs/blob/main/planning/use-case-registry.md) | ACTIVE |
| `obs-planning-docs` — OBS — session | [local registry](https://github.com/AlexPastukhh/obs-planning-docs/blob/main/planning/session/use-case-registry.md) | ACTIVE |
| `obs-planning-docs` — OBS — documentation | [local registry](https://github.com/AlexPastukhh/obs-planning-docs/blob/main/planning/documentation/use-case-registry.md) | ACTIVE |
| `obs-planning-docs` — OBS — application planning | [local registry](https://github.com/AlexPastukhh/obs-planning-docs/blob/main/planning/documentation/application-planning/use-case-registry.md) | ACTIVE |
| `obs-planning-docs` — OBS — architecture planning | [local registry](https://github.com/AlexPastukhh/obs-planning-docs/blob/main/planning/documentation/architecture-planning/use-case-registry.md) | ACTIVE |
| `obs-planning-docs` — OBS — testing planning | [local registry](https://github.com/AlexPastukhh/obs-planning-docs/blob/main/planning/documentation/testing-planning/use-case-registry.md) | ACTIVE |
| `obs-planning-docs` — OBS — workspace planning | [local registry](https://github.com/AlexPastukhh/obs-planning-docs/blob/main/planning/documentation/workspace-planning/use-case-registry.md) | ACTIVE |
| `obs-planning-docs` — OBS — documentation workbench | [local registry](https://github.com/AlexPastukhh/obs-planning-docs/blob/main/planning/areas/documentation-workbench/use-case-registry.md) | ACTIVE |
| `obs-planning-docs` — OBS — planning system | [local registry](https://github.com/AlexPastukhh/obs-planning-docs/blob/main/planning/areas/planning-system/use-case-registry.md) | ACTIVE |
| `obs-planning-docs` — all methodology domains | [Documentation registry map](https://github.com/AlexPastukhh/obs-planning-docs/blob/main/planning/documentation/use-case-registry-map.md) | ACTIVE; подреестры связаны там |
| `ai-conspects` | [Knowledge/learning registry](https://github.com/AlexPastukhh/theory_conspects_and_banks/blob/main/documentation/use-case-registry.md) | ACTIVE |
| `gendocen` | [Generated UC view](https://github.com/AlexPastukhh/gendocen/blob/main/docs/USE_CASES.md) / [JSON source](https://github.com/AlexPastukhh/gendocen/blob/main/spec/registries/USE_CASE_REGISTRY.json) | ACTIVE |
| `research_and_bank` — freelance method | [JSON source](https://github.com/AlexPastukhh/research_and_bank/blob/main/freelance_research_system_feature_architecture_red_tests/CORE/USE_CASE_REGISTRY.json) / [generated view](https://github.com/AlexPastukhh/research_and_bank/blob/main/freelance_research_system_feature_architecture_red_tests/REFERENCE/USE_CASE_REGISTRY.md) | ACTIVE |
| `gdoc-replacement-review-20260803` — game planning | [Use-case map](https://github.com/AlexPastukhh/gdoc/blob/main/game-planning-use-case-map.md) | локальный файл есть; проверить remote/публикацию |
| `rd-graphs` | [Current docs policy](https://github.com/AlexPastukhh/rd-graphs/blob/main/docs/DOCS-POLICY.json) | NO REGISTRY — не создавать без нужды |
| `visual-workspace` | `README.md` | NO REGISTRY — пока нет автономных UC |

Для проекта, отсутствующего в таблице, сначала искать в его README/AGENTS и
картe исходников. Не объявлять весь workspace полностью проинвентаризированным;
проверять полноту каталога при обнаружении нового действующего реестра.

## Общие сценарии

| ID | Ситуация / цель | Владелец |
| --- | --- | --- |
| UC-CONT-001 | Контекст задачи, репозитории и worktrees | [orientation](orientation.md#uc-cont-001) |
| UC-CONT-002 | Docker → GitHub → exact-SHA CI → Windows/Mirror | [delivery](delivery.md#uc-cont-002) |
| UC-CONT-003 | GitHub только через Gateway | [delivery](delivery.md#uc-cont-003) |
| UC-CONT-004 | GitHub Actions для нужного SHA | [delivery](delivery.md#uc-cont-004) |
| UC-CONT-005 | Принятый Windows main | [delivery](delivery.md#uc-cont-005) |
| UC-CONT-006 | Сонар — исторический ID, новый Gateway owner | [compat](quality.md#uc-cont-006) |
| UC-CONT-007 | Авторизация ALLOW/ASK/DENY | [authorization](authorization.md#uc-cont-007) |
| UC-CONT-008 | Новый AI/machine-клиент | [authorization](authorization.md#uc-cont-008) |
| UC-CONT-009 | Provider — исторический ID | [compat](extensions.md#uc-cont-009) |
| UC-CONT-010 | Операция provider — исторический ID | [compat](extensions.md#uc-cont-010) |
| UC-CONT-011 | Credentials — исторический ID | [compat](extensions.md#uc-cont-011) |
| UC-CONT-012 | Gateway release — исторический ID | [compat](operations.md#uc-cont-012) |
| UC-CONT-013 | Gateway recovery — исторический ID | [compat](operations.md#uc-cont-013) |
| UC-CONT-014 | Общее изменение Docker runtime | [docker](docker.md#uc-cont-014) |
| UC-CONT-015 | Windows handoff/артефакт | [handoff](handoff.md#uc-cont-015) |
| UC-CONT-016 | Пропорциональные проверки и evidence | [orientation](orientation.md#uc-cont-016) |
| UC-CONT-017 | DRY, навигация, структура исходников | [orientation](orientation.md#uc-cont-017) |
| UC-CONT-018 | Регистрация нового GitHub repo | [delivery](delivery.md#uc-cont-018) |
| UC-CONT-019 | Docker task worktree | [worktrees](worktrees.md#uc-cont-019) |
| UC-CONT-020 | Primary lifecycle — исторический ID | [compat](operations.md#uc-cont-020) |
| UC-CONT-021 | Подготовить Docker-изменение | [docker](docker.md#uc-cont-021) |
| UC-CONT-022 | Проверить backup/restore readiness | [docker](docker.md#uc-cont-022) |
| UC-CONT-023 | Вывести Legacy / сделать безопасный cleanup | [docker](docker.md#uc-cont-023) |
| UC-CONT-024 | Создать или улучшить Use Case | [orientation](orientation.md#uc-cont-024) |
| UC-CONT-025 | Owner-only Windows/host action unavailable in Docker | [host operations](host-operations.md#uc-cont-025) |
| UC-CONT-026 | Fortis Repo image + both Repo Guards | [docker](docker.md#uc-cont-026) |

[Совместимость старых ID](legacy-aliases.md) сохраняет старые якоря без копии
процедур. Детальные Gateway/Windows сценарии — в их собственных реестрах.

## Поддержка реестров

Новый UC создавать по [UC-CONT-024](orientation.md#uc-cont-024); упрощение,
владельцы, структура кода и архив — по [UC-CONT-017](orientation.md#uc-cont-017).
**Не превращать документацию в перечень каждой функции:** краткая карта модулей,
их роли, границы и ссылки на код/тесты полезны даже если реализацию можно
самостоятельно прочитать. Один факт — один владелец. Запуск проверки:
`python3 tools/check-use-cases.py`. [Технические владельцы](../README.md).
