# Owner-run операции Windows, недоступные из Fortis Repo Docker

## UC-CONT-025

**Когда:** для порученной задачи необходимы Windows Docker Engine, build/publish image, Guard Preview/launcher, ACL/shortcut, browser/WebAuthn или иной host-only шаг, которого не может выполнить Linux MCP контейнер.

**Цель:** выполнить ровно нужную host-операцию владельцем, не придумывая доступ из Docker и не повторяя ручные эксперименты.

**Как:** AI делает всё доступное **в Docker** (read-only source/tests, exact SHA, проверка контрактов), различает *проверку*, *сборку образа* и *изменение runtime*. Затем даёт один ограниченный owner-run блок под Windows PowerShell 5.1: проверка корректного host/source/identity/expected SHA, заранее известные точные действия, стоп-условия и безопасные PASS-маркеры, без параметров с секретами; `LastExitCode`/native stderr учитываются, ошибки не скрываются. Предпочтение готовому проверенному source entrypoint, а не длинному ad-hoc скрипту. Если требуется **передача файла**, использовать [UC-CONT-015](handoff.md#uc-cont-015): approved source → temp copy в Docker → `docker cp` + SHA256 на Windows. Если действие уже доступно через Gateway typed API, **не** пытаться заменить его host-командой.

**Границы:** никакого `docker.sock`, прямого Windows shell/PowerShell через Repo MCP, сетевого обхода Gateway/GitHub, приватных токенов в логах/argv или записи в защищённые records. Owner confirmation нужна перед реальным stop/recreate/credential/Windows mutation; read-only проверки и image-only build не дают автоматического разрешения на cutover. При ошибке state/receipt сначала диагностировать, **не повторять эффект**.

**Готово:** owner-reported завершение точного действия и постусловия; отдельно указаны `SOURCE_VERIFIED`, `IMAGE_BUILT`, `RUNTIME_HEALTHY` и `UNKNOWN`. Сценарий Fortis Repo image + Repo1/2 Guards: [UC-CONT-026](docker.md#uc-cont-026).
