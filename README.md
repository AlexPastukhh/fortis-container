# Fortis Container — юзкейсы и документация

**Для каждого нового чата:** сначала учти исходное сообщение пользователя,
затем открой [главный реестр Fortis](docs/use-cases/README.md) и прочитай его
короткий вступительный маршрут. **Полностью прочитай только обязательные**
[UC-CONT-002 — Docker → GitHub → CI → Windows/Mirror](docs/use-cases/delivery.md#uc-cont-002)
и [UC-CONT-003 — GitHub только через Gateway](docs/use-cases/delivery.md#uc-cont-003).
**Просматривать всю таблицу реестра не нужно.** Выбор одного, нескольких, нового
репозитория или работы без репозитория — [UC-CONT-001](docs/use-cases/orientation.md#uc-cont-001).
Выбранные локальные use cases читаются по необходимости.

Документация ведётся через юзкейсы: цель → способ/ссылки → критерий завершения.
Новый общий сценарий сначала регистрируется там, затем ведёт к техническим
документам-владельцам. Подробности не копируются в каждый сценарий.

## Навигация по задаче

- [Главный реестр и каталог локальных реестров](docs/use-cases/README.md).
- [UC-CONT-001 — определить контекст](docs/use-cases/orientation.md#uc-cont-001).
- [UC-CONT-021 — Docker preflight](docs/use-cases/docker.md#uc-cont-021),
  [UC-CONT-022 — verified backup](docs/use-cases/docker.md#uc-cont-022),
  [UC-CONT-023 — retire/cleanup](docs/use-cases/docker.md#uc-cont-023).
- Gateway, Sonar, credentials и Primary-specific release —
  [локальный Gateway Registry](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/README.md) (принят в `main`; live Gateway проверен).
- Mirror UI и Windows sync — [Mirror Registry](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/use-cases/README.md) (до появления в `main` — [публикация PR #4](https://github.com/AlexPastukhh/docke-windows-mirror/pull/4)).

Общие сценарии принадлежат `fortis-container`, предметные — их собственному
репозиторию. Для проектов без реестра пользоваться их действующим README/картой
документации; не создавать фиктивный реестр.

## DRY и источники

Документация должна облегчать работу и оставаться простой в сопровождении,
а не становиться обузой. Соблюдать DRY: один факт или правило — один документ-владелец,
в остальных местах — ссылки. Предпочитать короткую правку существующего документа
новому файлу; отдельный документ нужен для самостоятельной цели. Не требовать
новых отчётов, регламентов и копий статуса для каждой мелкой правки. Убирать
лишние дубли из действующих инструкций и упрощать навигацию.

- Юзкейс владеет целью и маршрутом; технический контракт — деталями операции.
- Текущее состояние, evidence и будущий план имеют разных владельцев.
- Gateway code/operations/policies/deployment принадлежат `fortis-approvals`;
  точное Git/Mirror поведение — `docke-windows-mirror`; здесь общая навигация.
- Исторические audits/снимки сохраняются с датой и не становятся live инструкцией.
- Docker и Windows — разные среды. Source, успешный CI, установленный image и
  реально подтверждённый эффект — отдельные результаты.

Операционные README/AGENTS в корне workspace — управляемая навигационная проекция:
[как установить и проверить](docs/WORKSPACE-NAVIGATION.md).
Проверки выбираются по [validation policy](docs/VALIDATION-POLICY.md).
