# Windows-артефакт и ручная передача

## UC-CONT-015

**Когда:** владелец должен выполнить на Windows конкретный артефакт, который нельзя передать обычным Git main.

**Цель:** подготовить один проверяемый безопасный пакет и минимальный owner-run шаг.

**Как:** хранить исходники в своём Git repo; transfer copy — в `/workspace/repo/Workfiles/_fortis_windows_transfer_tmp/<task>/`. Один entrypoint/ZIP из точного списка, SHA-256, проверка состава, никаких tokens, grants, DB, private keys. Предоставить PowerShell-блок с проверкой hash/exit и минимальным согласованным действием. Штатные исходники доставлять через [UC-CONT-002](delivery.md#uc-cont-002) и [UC-CONT-005](delivery.md#uc-cont-005). Рабочий шаблон находится в `/workspace/repo/README.md`.

**Готово:** bytes/hash подтверждены владельцем, изменения runtime отдельно проверены; hash сам по себе не авторизует запуск.

**Не для произвольных Windows-команд:** если нужен именно host-only шаг, а не артефакт, [UC-CONT-025](host-operations.md#uc-cont-025) владеет общим маршрутом.
