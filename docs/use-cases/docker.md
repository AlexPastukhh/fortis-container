# Docker runtime и безопасное изменение инфраструктуры

## UC-CONT-014

**Когда:** меняется Docker runtime, mount, image, сеть или контейнер Fortis Repo / связанные сервисы.

**Цель:** применить изменение только к нужному runtime без ненужных контейнеров или потери данных.

**Как:** сначала [UC-CONT-021](#uc-cont-021) и [UC-CONT-016](orientation.md#uc-cont-016). Найти source owner в [карте][sources], сверить [хранение][storage], [сборку][build] и реальные launchers/Guards. Согласовать owner-run entrypoint, затем проверить идентичность runtime/mount/коннекторы. Доступ к Linux Repo не равен доступу к Windows Docker Engine.

**Готово:** exact target, реальные mounts/health и подключения проверены; candidate/render не назван deployment.

## UC-CONT-021

**Когда:** предполагаются создание/изменение/перезапуск/переименование/удаление контейнера, тома, сетевого маршрута или Docker-инфраструктуры.

**Цель:** выбрать минимальный безопасный план изменения **до первой мутации**.

**Как:** read-only инвентаризировать по точным ID и owner records: name, image digest, health, restart policy, published ports, mounts и RW writers, конфигурацию/Compose ownership, consumers, зависимости, requests in-flight и rollback-контракт. Определить source image/SHA, точный target, достаточные preflight/backup/verification, согласованную последовательность и STOP-сигналы. **Не создавать новый контейнер по умолчанию**: если цель достигается безопасным изменением существующего — предпочесть его. Изолированный staging/restore/новый image может обосновывать новый контейнер. Никаких `docker rename`, `compose up`, stop или миграции как побочного эффекта Plan. Gateway specifics — [Primary owner][primary].

**Готово:** известны точные ресурсы, действие, влияние, допустимые альтернативы, границы rollback и необходимые approvals; при недостающих данных `UNKNOWN/STOP`, не угадывать.

## UC-CONT-022

**Когда:** перед рискованным переключением, обновлением или очисткой нужна подтверждённая копия состояния.

**Цель:** обеспечить подтверждённый backup и честно оценить восстановимость.

**Как:** из [UC-CONT-021](#uc-cont-021) взять точный источник; учесть persistent state вне Git, секреты, owner/WebAuthn и volumes. Проверить **реальные argv/mount flags** копирующего процесса, exit codes и безопасно редактированный stderr; не скрывать причину Docker 125. Сделать отдельную копию, независимо сверить состав и целостность, источник, protected record, volume ID и readback. Различать `BACKUP_CREATED`, `BACKUP_VERIFIED`, `RESTORE_TESTED` (в изоляции), `DISASTER_RECOVERY_VERIFIED` (off-host). Последние статусы не следуют из первых. Не публиковать содержимое секретов. Для Gateway использовать единственный [операционный Backup][primary], не новый сценарий копирования.

**Готово:** точный immutable/защищённый receipt и уровень подтверждения; при неудаче/неясном источнике `STOP` до Promote/cleanup.

## UC-CONT-023

**Когда:** старый container/image/volume/backup больше не используется штатным клиентом.

**Цель:** разделить безопасную остановку (`RETIRED`) и необратимую очистку (`CLEANUP_VERIFIED`).

**Как:** после [UC-CONT-021](#uc-cont-021) и [UC-CONT-022](#uc-cont-022) подтвердить рабочую замену, отсутствие пользователей старого endpoint, отсутствие активных writers/requests и retention/recovery зависимостей. `Retire`: только exact ID, policy без autostart, stop и post-stop readback Primary; образ/volumes/records сохранить. `Cleanup`: **отдельное** разрешение владельца, полный список ID, требуемый срок хранения, достаточный restore/backup, отсутствие ссылок из release records; удалить лишь проверенные объекты, заново проверить результат. Не применять `docker system prune`/`docker volume prune` как способ очистки Fortis. Не считать stopped синонимом disposable и не смешивать cleanup с Promote.

Для state volume завершённой попытки `Returned` без активации допустимо
сохранить исходную запись о попытке для аудита. Контроллер подтверждает
отсутствие ссылок из других
защищённых записей и внешних recovery-зависимостей, проверяет состояние
самого тома и исключает повторный Return этой попытки с момента начала
очистки, включая частичный результат. Остальные условия Cleanup действуют.

**Готово:** `RETIRED` с retained inventory или `CLEANUP_VERIFIED` с точным перечнем удалённого, доказательствами и явными неизвестными.

[sources]: ../SOURCE-MAP.md
[storage]: ../CONTAINERS-AND-VOLUMES.md
[build]: ../CONTAINER-BUILD-PROVENANCE.md
[primary]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/PRIMARY-GATEWAY-OPERATIONS.md

## UC-CONT-026

**Когда:** разрабатывается, собирается или заменяется **образ самого `fortis-repo-test`** (общий для Repo1/Repo2/Qwen).

**Цель:** раздельно доказать source → image и image → guarded runtime, не потерять существующие подключения.

**Как:** сначала [UC-CONT-021](#uc-cont-021) и [UC-CONT-025](host-operations.md#uc-cont-025). Сверить [build provenance](../CONTAINER-BUILD-PROVENANCE.md): первоначальный Windows Dockerfile/context не доказан как воспроизводимый — не объявлять неподтверждённый полный rebuild. Использовать только конкретный source/patch SHA, допущенный context и owner-run Windows image-only build с inspect digest, offline smoke и проверкой `--pull`/base provenance; image build **не** меняет `fortis-repo-test`.

**Перед применением в runtime** повторно инспектировать exact container/image/mounts/network/ports/user/security/restart/RW writers, выполнить оба owner-run read-only Guard Previews по каноническому `tunnel/runtime/windows-repo/current/launchers/shared/FortisContainerPolicy.ps1`, проверить Repo1/Repo2 source manifest и раздельные профили, сохранить rollback и план reconnect (учесть Qwen). При несовпадении effective flags, неполном bootstrap/build context, unknown mounts или отсутствующем Guard PASS — **STOP**; не отключать Guard ради запуска.

**Готово:** image digest/offline smoke отдельно от live deployment; после owner-controlled смены exact runtime оба Guard PASS + Repo1/Repo2 reconnect/readback (и status Qwen) отдельно подтверждены. Нужные Windows процедуры — [Tunnel Windows Repo mirror](https://github.com/AlexPastukhh/tunnel/blob/main/runtime/windows-repo/README.md) и [container Guard baseline](../audits/REPO-CONTAINER-GUARD-BASELINE-2026-11-04.md). Не дублировать их policy таблицу.
