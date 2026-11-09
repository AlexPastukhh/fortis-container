# Новый репозиторий: GitHub владельца → Docker → Windows

## UC-CONT-027

**Когда:** согласовано создание самостоятельного проекта с новым Git-репозиторием
и Windows-зеркалом. Для уже существующего repo —
[UC-CONT-018](delivery.md#uc-cont-018), для обычной новой задачи —
[UC-CONT-019](worktrees.md#uc-cont-019).

**Цель:** получить одну историю Git, чистый Docker primary на `main`,
GitHub `origin`, **пустую папку будущих worktrees** и Windows-клон
в зеркальной папке. Первый task worktree и PR не входят в bootstrap.

**Статус:** проверяемый ручной bootstrap, не автоматический provisioner.
**Владелец** создаёт GitHub repo с начальным коммитом и даёт HTTPS URL;
**ИИ** выполняет доступные Docker-действия самостоятельно, использует
typed Gateway для GitHub READ/fetch и выдаёт готовую Windows-команду;
**владелец** запускает первичный `git clone` на Windows.
Создание локального Git (`git init`) не требует нового метода Gateway.
Границы GitHub-действий — [UC-CONT-003](delivery.md#uc-cont-003).

**Как:** проверить существующий GitHub `main` по URL владельца, самостоятельно
подготовить Docker Git и пустую папку будущих worktrees, получить историю
через Gateway, затем выдать Windows-команду и проверить отчёт владельца.
Первый task worktree и PR — только при отдельной задаче.

### Предварительные условия

- По [UC-CONT-001](orientation.md#uc-cont-001) установить назначение, GitHub owner,
  имя, visibility, авторство коммитов и необходимость отдельного repo.
  Не выбирать публичность или лицензию молча.
- Применять [схему директорий](worktrees.md#uc-cont-019): Docker primary
  `/workspace/repo/Repos/<repo>`, task root `/workspace/repo/Worktrees/<repo>`,
  Windows `%USERPROFILE%\Repos\<repo>`. Windows-клон — отдельный каталог хоста.
- Проверить, не существуют ли уже каталог, GitHub repo, remote или worktree
  этого проекта. Не делать вложенный `.git`, второй primary или повторный clone.
  Существующие файлы/историю сначала разобрать и сохранить; импортировать
  исходники в task worktree после bootstrap, не терять их при создании anchor.

### Порядок

1. **Получить URL от владельца и проверить GitHub.** Владелец заранее
   создаёт repo через [GitHub UI](https://github.com/new), сам выбирает
   owner/visibility/лицензию, включает начальный README-коммит в `main`
   и даёт URL `https://github.com/<owner>/<repo>`. Без URL или GitHub
   `main` с коммитом — STOP, а не попытка вызвать отсутствующий
   `create_repository`, применить GitHub connector/PAT или придумать SHA.
   ИИ **до локальных записей** через typed Gateway `get_repository` /
   `list_branches` сверяет точный owner, имя, private/public, default
   branch `main`, archived/disabled, существующий SHA, token scope
   и live capabilities. READ не доказывает права на будущий push.

2. **Самостоятельно подготовить Docker anchor и пустую task-папку.**
   Проверить allowed roots, существующие пути/истории, symlink, чужой
   Git-корень, отсутствие занятого target; сверить aliases
   `/workspace/repo/Repos` и `/workspace/repos`, не делать дубликатов.
   В свободных местах создать **два** каталога: primary
   `/workspace/repo/Repos/<repo>` и root для будущих worktrees
   `/workspace/repo/Worktrees/<repo>`. **Последний оставить пустым**:
   не создавать подкаталог задачи, task-ветку и linked worktree, не вызывать
   `workspace.create_task` в ходе bootstrap. В пустом primary локально
   выполнить `git init --initial-branch=main`; согласованные
   `user.name`/`user.email` при необходимости задать лишь для этого
   repo. GitHub credentials не нужны. Пока `main` unborn, не делать
   независимого initial commit, не класть проектные файлы в primary
   и не вести там разработку.

3. **Связать remote и проверить доступ Gateway.** Добавить локальный `origin`
   с точным HTTPS URL `https://github.com/<owner>/<repo>.git` без credentials;
   существующий несовпадающий origin не перезаписывать. По
   [UC-CONT-018](delivery.md#uc-cont-018) проверить owner/repo, token scope,
   live capabilities и получить точный SHA GitHub `main` через typed client.
   Доступ зависит от токена, отдельный список разрешённых repo не добавлять.
   Если новый repo не доступен, владелец меняет scope через
   [UC-GW-004][credentials]; token не передаётся в чат или Repo. Ошибка доступа
   не доказывает, что repo отсутствует.

4. **Получить ту же историю в Docker.** Вызвать
   `workspace.fetch` с `ref=main` и проверенным `expectedSha` по
   [native contract][native]; дождаться `EXECUTED` и проверить
   `refs/remotes/origin/main`. Fetch идёт через Gateway, не сетевой Git из Docker.
   Только если локальный `main` ещё unborn и primary пустой, связать его с
   полученной историей: локальный
   `git switch --create main --track origin/main`. Это первоначальное создание
   локального `main`, не замена `workspace.update_main_from_pr` для существующей
   истории. Проверить branch `main`, HEAD = ожидаемый SHA, чистый status,
   upstream `origin/main`, точный origin и самостоятельный `.git` primary.
   Не использовать reset/force и не делать независимый initial commit.

5. **Создать Windows-клон командой из чата.** Только после проверенного
   Docker `main` ИИ подготавливает короткий готовый
   блок для Windows PowerShell 5.1 по
   [UC-CONT-025](host-operations.md#uc-cont-025), подставляя реальные URL, имя
   и ожидаемый SHA. Владелец запускает его на Windows. Основное действие —
   `git clone --branch main --single-branch -- <HTTPS-URL> <полный-Windows-путь>`
   в `%USERPROFILE%\Repos\<repo>`; это схема команды, а не блок с placeholders
   для передачи пользователю. Перед clone проверить наличие Git и родительской
   папки `Repos`, отсутствие целевого каталога; родитель при необходимости
   создать. После каждого native command проверить `$LASTEXITCODE` и остановиться
   при ошибке. Windows Git использует авторизацию владельца на Windows;
   Gateway token/machine grant туда не копируются и в команду не включаются.
   Если нужен вход, владелец выполняет его локально, секреты в чат не присылает.
   Этот owner-run bootstrap не разрешает AI прямой сетевой Git из Docker.

   После clone проверить canonical `origin`, checkout `main`, HEAD = согласованный
   GitHub SHA, upstream `origin/main` и чистый status; выдать понятный
   PASS/STOP и фактический Windows path. До ответа владельца считать
   Windows состояние `PENDING`, а не подтверждённым. Если remote успел измениться,
   сначала сверить новый main, а не сбрасывать clone к прежнему SHA. При повторном
   запуске существующий clone проверить по [UC-CONT-005](delivery.md#uc-cont-005),
   не клонировать поверх него. Указать путь владельцу для выбора в Mirror;
   не предполагать автоматическую регистрацию папки в UI. Windows task worktrees
   не создавать. Clone не запускает приложение, сборку или deployment.

### После bootstrap — отдельно начать разработку

**Не создавать первый task worktree и PR автоматически.** Когда появится
порученная задача, сначала сверить чистый Docker `main` с текущим GitHub
`main`, затем создать `/workspace/repo/Worktrees/<repo>/<task>`
через зарегистрированный `workspace.create_task` по
[UC-CONT-019](worktrees.md#uc-cont-019). Все project source,
edit/test/stage/commit — только в task worktree. В первом изменении
при необходимости дополнить README, `.gitignore` и единственный
`docs/BACKLOG-IMPROVEMENTS.md`; лицензию выбирает владелец.
Дальнейший publish/PR/применимые exact-SHA CI/owner GitHub UI merge,
обновление Docker и Windows main и cleanup идут по
[UC-CONT-002](delivery.md#uc-cont-002). Отсутствующий CI
не выдавать за успешный. Ни первый task, ни CI, ни PR не являются
условием завершения создания репозитория.

### Остановиться и сверить состояние

Непонятный owner/visibility, занятый или dirty путь, другая история, отсутствие
GitHub main, неизвестный scope/operation, несовпавшие origin/SHA или ошибка clone
означают STOP на этой фазе. Не удалять существующий каталог и не повторять
создание/эффект вслепую. При `PENDING` ждать той же заявки; при `UNCERTAIN`
сначала result/reconcile того же UUID по native contract. При частичном
bootstrap продолжать с проверенной фазы без нового repo, force/reset или
автоматического удаления созданных ресурсов.
При передаче незавершённой работы указать достигнутую фазу, не объявлять весь
сценарий выполненным.

**Готово:** проверены owner/repo/visibility и канонический origin,
GitHub доступен через Gateway, Docker имеет самостоятельный Git primary
с чистым `main` и ожидаемым GitHub SHA; каталог
`/workspace/repo/Worktrees/<repo>` создан и **пуст**.
ИИ выдал готовую Windows PowerShell-команду с настоящими URL, путём и SHA.
После её выполнения владельцем отдельно подтверждены Windows `origin`,
чистый `main`, SHA, upstream и путь клона для Mirror.
Если Windows ещё не проверен, сообщить `DOCKER_READY / WINDOWS_PENDING`,
не объявлять весь сценарий завершённым. Готовность будущих task worktrees
не означает создание worktree или PR. Source sync, CI и работа приложения
подтверждаются раздельно.

[native]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/NATIVE-WORKTREE-GATEWAY-2026-11-06.md
[credentials]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/credential-lifecycle.md#uc-gw-004
