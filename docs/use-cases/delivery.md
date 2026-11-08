# Docker → GitHub → Actions → Windows

## UC-CONT-002

**Цель:** доставить проверенное изменение из Docker в Windows main.

**Как:**

1. [UC-CONT-001](orientation.md#uc-cont-001): установить контекст;
   [UC-CONT-019](worktrees.md#uc-cont-019): выбрать/создать linked task worktree,
   сохраняя primary на main.
2. Изменить source, выполнить [проверки](orientation.md#uc-cont-016), stage/commit
   выбранных файлов. Опубликовать настоящие Git-коммиты выбранной task-ветки
   через [UC-CONT-003](#uc-cont-003), сохранив SHA и preconditions.
3. Создать обычный PR через typed Gateway, если draft не нужен. Политика создания
   PR берётся из действующего контракта; [UC-CONT-007](gateway.md#uc-cont-007)
   исключает предварительное устное разрешение на штатный ALLOW/ASK для **создания PR**.
   Передать владельцу ссылку GitHub на PR, точный HEAD SHA и статус CI. **Не
   отправлять от имени ИИ ASK на `github.merge_pull_request`**: наличие такого
   ASK — запрет свободного машинного merge, а не обязательный удобный способ
   публикации. Владелец самостоятельно просматривает и нажимает Merge в GitHub.
4. [UC-CONT-004](#uc-cont-004): проверить обязательные CI для точного PR HEAD.
   После owner GitHub UI merge проверить PR/head/merge и текущий remote `main`,
   затем вызвать typed **`workspace.update_main_from_pr`** для чистого Docker
   primary. Условия доказательства merge и параметры принадлежат
   [native contract][native], а не этому общему UC. Старый `workspace.update_main`
   требует Gateway merge receipt и не подходит после UI merge; не создавать
   фиктивную ASK. Для нового client/API — [UC-GW-003][api-change]. При
   `UNCERTAIN` сначала reconcile того же UUID, без слепого повтора эффекта.
5. [UC-CONT-005](#uc-cont-005): получить этот merged main в Windows. Source pull
   не заменяет image build/deploy или перезапуск приложения.
6. Завершить свою задачу очисткой выбранного task worktree: сверить repo,
   task и фактический HEAD, убедиться, что работа закончена и source path не
   нужен deployment/recovery records или другой активной задаче. По
   [контракту очистки][cleanup] проверить live capability и вызвать typed
   `workspace.cleanup_task`; решение ALLOW/ASK принимает Gateway, порядок
   approvals — [UC-CONT-003](#uc-cont-003). Проверить receipt `EXECUTED`,
   отсутствие выбранного worktree и его локальной task-ветки. Если очистка
   заблокирована или worktree ещё нужен, явно указать причину сохранения;
   не обходить отказ через force/reset/clean. Это не массовая очистка других
   задач, remote branches или Docker volumes.

**Готово:** PR/CI/merge и Docker/Windows SHA проверены раздельно; необходимое
развёртывание прошло [UC-CONT-012](operations.md#uc-cont-012), если оно было целью.
Task worktree удалён с подтверждённым receipt либо указан конкретный повод
его сохранить; завершённые задачи не остаются висеть без причины.
Детальные команды и правила директорий принадлежат [Mirror workflow][mirror],
native операции и политика — [native contract][native].

## UC-CONT-003

**Цель:** выполнить нужную GitHub-операцию с авторизацией и правильной политикой.

**Как:** прочитать [agent guide][guide] и контракт выбранного клиента. Для
зарегистрированного native repo использовать
`fortis_approvals.workflow.client.default_client()`
и его typed GitHub methods; клиент передаёт machine grant по TLS в Gateway,
а GitHub credential остаётся в Gateway. Стабильный requestId, target и SHA
сохраняются для retry/status. ALLOW выполняется в пределах поручения, ASK
сразу создаёт PENDING и ожидает решения в портале; DENY не обходится.
Исключение для **маршрута публикации**: ИИ не вызывает `merge_pull_request` и не
создаёт соответствующую ASK; после PR/CI владелец сливает через GitHub UI по
[UC-CONT-002](#uc-cont-002).

Поддержка repo проверяется через live capabilities и контракт, не по наличию Git clone. В активном режиме `dynamicRepositories=true`
текущий Gateway использует **token-scoped** доступ GitHub, а не второй список
разрешённых имён. Доступ на чтение сам по себе не доказывает разрешение записи:
нужны точный local checkout/worktree, repo ownership/origin, защита `main` и
допустимая typed operation. Отсутствующий token scope => STOP, а не изменение
другого allowlist.
**GitHub-операции выполняются только через Gateway.** Если repo/операция ещё не
зарегистрированы, Gateway недоступен или вернул DENY, остановиться; перейти к
[UC-CONT-018](#uc-cont-018), а не подменять маршрут прямым Git или иным клиентом.
Токены GitHub не читать, не передавать в Repo и не конфигурировать в локальном Git.
Универсальные команды `git fetch/push` из схемы директорий в Mirror описывают
организацию Git, **но не дают разрешения** обращаться к GitHub напрямую:
в принятом native scope удалённые Git-эффекты выполняются типизированным
клиентом Gateway. Локальные `git status/diff` в task worktree не являются
GitHub API. Не использовать GitHub connector, старый credential helper,
прямые сетевые Git-команды или сторонний API-клиент вместо Gateway.

**Готово:** получен проверенный typed result/receipt нужного действия; токен не
попал в Repo/payload/log. Политики не переписываются в этом сценарии: [native][native].

## UC-CONT-004

**Цель:** понять, что произошло в Actions именно с проверяемым изменением.

**Как:** через GitHub-клиент получить workflow runs и сопоставить repo, workflow,
event, HEAD SHA, attempt и завершение. Ожидание отличать от failure/cancelled и
success. Проверить требуемый workflow, не выбирать просто последний зелёный run.
Логи/jobs/annotations/artifacts читать только поддержанными typed операциями.
Дополнительный [analysis profile][analysis] требует отдельной конфигурации;
наличие его клиента в source не означает доступность в live Gateway.
Sonar/analysis/PR binding дополнительно проверяется по [UC-GW-001](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/sonar.md#uc-gw-001).

**Готово:** есть статус обязательных проверок для точного SHA либо явно записано,
какой evidence недоступен. Required CI IDs и доступные операции — у владельца контракта.

## UC-CONT-005

**Цель:** обновить Windows primary clone до одобренного merged main.

**Как:** открыть Mirror, выбрать точный repo и проверить фактические Windows
branch/HEAD/origin/dirty status, GitHub main и направление ancestry. Выбранная
для просмотра ветка не является checkout. Windows должна быть на чистом main,
без собственных коммитов ahead; ожидаемый SHA должен соответствовать принятому merge.
Использовать guarded Pull Windows main: повторный preflight, fetch точного ref,
проверка FETCH_HEAD и fast-forward. При расхождении, dirty, unknown или неверном
origin остановиться без reset/stash. CLI-эквивалент должен сохранять те же проверки.

**Готово:** Windows main readback равен ожидаемому SHA и остаётся чистым.
Подробная UI/CLI процедура и фактические ограничения GUI — [Mirror workflow][mirror].
Не использовать GUI Stage/Commit/Push как будто он уже выбирает Docker task worktree.

## UC-CONT-018

**Цель:** включить ещё один repo в авторизованный GitHub/CI/Windows маршрут.

**Как:** проверить наличие remote и доступ, repo ownership, allowed local roots,
права Gateway credential, требуемые workflow IDs и доступные native bindings.
При текущем `dynamicRepositories=true` отдельной allowlist репозиториев **нет**:
проверить `github.list_repositories(owner)`, разрешения **текущего токена** для
нужного repo, `GET repository` у Gateway, `main`/owner, canonical Git origin,
существующие `/workspace/repo/Repos/<repo>` и `Worktrees/<repo>` и действующую
политику конкретной операции. Если token не имеет доступа (`403`/not listed) —
не пытаться добавить второй список или обойти через PAT/GitHub connector; нужен
отдельный owner-reviewed scope/credential change. Если local worktree или repo
отсутствует, это **другой** prerequisite, не автоматическая публикация. При
legacy `dynamicRepositories=false` прежний single-repo scope сохраняется,
и расширение требует принятого source/config + rollout. Не выдавать ALLOW всем
репозиториям только потому, что они видны по API.
Windows-получатель подключается по [UC-CONT-005](#uc-cont-005).

**Готово:** repo явно поддержан контрактом и live capabilities, выполнен нужный
GitHub/CI цикл. Отсутствующий remote и отказ в доступе различаются; `Repository
not found` сам по себе не доказывает причину.

[mirror]: https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md
[native]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/NATIVE-WORKTREE-GATEWAY-2026-11-06.md
[cleanup]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/NATIVE-WORKTREE-GATEWAY-2026-11-06.md#task-worktree-cleanup
[api-change]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-003
[guide]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/GATEWAY-AGENT-GUIDE.md
[analysis]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/ANALYSIS-REVIEW-CONTRACT.md
