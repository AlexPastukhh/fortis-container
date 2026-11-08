# Новый репозиторий: Docker, GitHub и Windows

## UC-CONT-027

**Когда:** согласовано создание самостоятельного проекта с новым Git-репозиторием
и Windows-зеркалом. Для уже существующего repo —
[UC-CONT-018](delivery.md#uc-cont-018), для обычной новой задачи —
[UC-CONT-019](worktrees.md#uc-cont-019).

**Цель:** получить одну историю Git, чистый Docker primary на `main`, GitHub
remote, Windows-клон в зеркальной папке и рабочий маршрут дальнейших изменений.

**Статус:** ручной bootstrap с проверками; это не автоматический provisioner.
GitHub-действия ИИ выполняются по [UC-CONT-003](delivery.md#uc-cont-003).
Первичный Windows `git clone` выполняет владелец по команде из чата.

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

1. **Подготовить пустой Docker anchor.** Проверить реальные allowed roots,
   отсутствие symlink и чужого Git-корня в целевом пути. Создать новый primary
   directory и отдельный task root. В *пустом* primary выполнить локальный
   `git init --initial-branch=main`; задать согласованные `user.name` и
   `user.email` в конфигурации **этого** repo. Инициализация и авторство не
   требуют GitHub credentials. Пока `main` unborn, не создавать в нём свою
   отдельную историю или проектные файлы. Это разовый bootstrap, а не разрешение
   разрабатывать в primary.

2. **Создать GitHub repo и начальный `main`.** Сначала проверить, существует ли
   такая typed операция в live Gateway. Если её нет, дать владельцу ссылку на
   [New repository](https://github.com/new) и точные owner/name/visibility; владелец создаёт repo
   в GitHub UI **с начальным README-коммитом**, затем сообщает URL. Проверить
   default branch `main`. Не оставлять remote совсем без коммитов: обычные
   native task/publish операции требуют существующий GitHub `main`.
   Не выдумывать `create_repository` и не обходить Gateway connector/токеном.
   Если repo уже создан, сверить его identity и продолжить с фактической фазы.

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

5. **Создать Windows-клон командой из чата.** AI подготавливает короткий готовый
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
   GitHub SHA, upstream `origin/main` и чистый status. Если remote успел измениться,
   сначала сверить новый main, а не сбрасывать clone к прежнему SHA. При повторном
   запуске существующий clone проверить по [UC-CONT-005](delivery.md#uc-cont-005),
   не клонировать поверх него. Указать путь владельцу для выбора в Mirror;
   не предполагать автоматическую регистрацию папки в UI. Windows task worktrees
   не создавать. Clone не запускает приложение, сборку или deployment.

6. **Начать обычную работу.** Убедиться, что Docker `main` чистый и соответствует
   текущему GitHub main; создать зарегистрированный task worktree через
   `workspace.create_task` по [UC-CONT-019](worktrees.md#uc-cont-019) с точным base.
   Все проектные файлы, импорт существующего source, edit/test/stage/commit —
   только там. В первом изменении оформить полезный README с назначением,
   запуском/проверками и ссылкой на главный Fortis registry, подходящий
   `.gitignore` и единственный `docs/BACKLOG-IMPROVEMENTS.md`. README направляет
   к обязательным UC-CONT-002/003; локальные UC/AGENTS добавлять по реальной
   потребности, не копировать общий регламент. Лицензия — по решению владельца.

7. **Доставить первое изменение и продолжить.** Применить
   [UC-CONT-002](delivery.md#uc-cont-002): commit/publish task через Gateway,
   PR, применимые проверки точного SHA, owner merge в GitHub UI, обновление
   Docker main и guarded получение принятого main в Windows. Отсутствие
   настроенного CI не выдавать за зелёный CI; выбор проверок —
   [UC-CONT-016](orientation.md#uc-cont-016), чтение Actions —
   [UC-CONT-004](delivery.md#uc-cont-004), развитие сценариев настройки CI —
   [backlog](../BACKLOG-IMPROVEMENTS.md#future-ci-github-actions-и-сценарии-настройки).
   Завершённый task убрать по шагу 6 UC-CONT-002 либо указать причину сохранения.
   Следующая задача начинает работу в новом/своём worktree, оба primary остаются
   чистыми на принятом `main`.

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

**Готово:** проверены owner/repo/visibility и origin; Docker и Windows имеют одну
начальную историю, чистый `main` и ожидаемый SHA. Известны Windows path,
Gateway scope и путь task worktree; первое изменение прошло обычный PR workflow,
принятый SHA получен в Docker/Windows, завершённый worktree убран либо указан
конкретный повод сохранения. Следующая задача следует обычному workflow.
Source sync, CI и работа приложения подтверждаются раздельно.

[native]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/NATIVE-WORKTREE-GATEWAY-2026-11-06.md
[credentials]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/credential-lifecycle.md#uc-gw-004
