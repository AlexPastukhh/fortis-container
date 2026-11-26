# Docker → GitHub → Actions → Windows (при необходимости)

## UC-CONT-002

**Когда:** согласованное изменение требуется довести до принятого результата.

**Цель:** выполнить **полный цикл разработки и доставки** — от решения начать
конкретное изменение до приёмки всех затронутых targets и завершения task.
**Релиз** — отдельная часть этого цикла: от Check принятой версии до live
приёмки, подтверждённого backup/Promote (где применимо) и решения по
retention с проверенным Cleanup допустимых ресурсов. Если допустимых
ресурсов нет — зафиксировать обоснованное сохранение. Подготовка source,
PR/CI/merge и Mirror sync до Check не входят в измерение времени релиза.

**Как:**

Состав действий выбирается по фактическому scope: подготовка и разработка,
локальные проверки, commit/publication, PR/CI, owner merge, синхронизация
Docker/Windows, сборка и развёртывание нужных targets, live acceptance,
проверка rollback/retention и закрытие task. Не создавать ненужные сборки,
синхронизации или runtime releases для `no-deployment`/source-only изменений.
Для нескольких targets учитывать зависимости и общий build unit по
[Release Planning Contract](../RELEASE-PLANNING-CONTRACT.md); конкретные
команды и approvals остаются у владельцев target. Recovery и Cleanup —
условные действия с отдельными допусками, не автоматическая часть deployment.

При анализе скорости различать полный цикл разработки и собственно релиз.
Для релиза измерять Check → Apply → live acceptance → Backup → Promote →
retention/Cleanup readback (или соответствующие действия владельца target),
отдельно активное время, ожидание owner, повторные попытки и downtime
(включая backup). SelfTest и прочие предпосылки до Check учитывать отдельно.
Использовать существующие timestamps/receipts/markers; не суммировать
параллельные jobs как wall time. Отсутствующее измерение — UNKNOWN,
не повод для искусственного релиза или обхода проверок. Перед затратными
действиями проверить host и guest capacity по UC-CONT-021/025, после
принятого runtime — необходимость отдельного обслуживания по UC-CONT-023.

Порядок выполнения:

1. [UC-CONT-001](orientation.md#uc-cont-001): установить контекст;
   [UC-CONT-019](worktrees.md#uc-cont-019): выбрать/создать linked task worktree,
   сохраняя primary на main.
2. Изменить source, выполнить [проверки](orientation.md#uc-cont-016), stage/commit
   выбранных файлов. Опубликовать настоящие Git-коммиты выбранной task-ветки
   через [UC-CONT-003](#uc-cont-003), сохранив SHA и preconditions.
3. **До создания PR в проекте с принятым Release Impact CI** прочитать
   [единый Release Planning Contract](../RELEASE-PLANNING-CONTRACT.md#canonical-source-formats),
   каталог проекта `release/targets.yaml` и действующую схему/пример. По
   полному diff к merge-base и точному HEAD выбрать реальные затронутые
   targets и их actions; в **body PR** передать ровно один YAML-блок
   `releaseImpact` между `<!-- fortis-release-impact:start -->` и
   `<!-- fortis-release-impact:end -->` в fenced `yaml`. Указать
   `schemaVersion: 1`, `classification`, обоснование, targets,
   dependencies и verification. Шаблон GitHub PR **не заполняет body**
   при typed Gateway `create_pull_request`: ИИ обязан передать блок сам.
   `no-deployment` допустим только при подтверждённых каталогом
   неразвёртываемых изменениях; при затронутом Windows-контроллере
   проверять Windows target/`windows-update`, не маскировать его как docs-only.
   Затем создать обычный PR через typed Gateway, если draft не нужен.
   Политика создания PR берётся из действующего контракта;
   [UC-CONT-007](gateway.md#uc-cont-007)
   исключает предварительное устное разрешение на штатный ALLOW/ASK для **создания PR**.
   Передать владельцу ссылку GitHub на PR, точный HEAD SHA и статус CI. **Не
   отправлять от имени ИИ ASK на `github.merge_pull_request`**: наличие такого
   ASK — запрет свободного машинного merge, а не обязательный удобный способ
   публикации. Владелец самостоятельно просматривает и нажимает Merge в GitHub.
4. [UC-CONT-004](#uc-cont-004): проверить обязательные CI для точного PR HEAD,
   включая **Source CI и Fortis Release Impact**, если они приняты в проекте.
   Если Release Impact CI сообщает `PR: one release-impact block required`,
   исправить **body того же PR** через разрешённую typed Gateway-операцию
   и проверить новую попытку CI; не обходить проверку, не подменять
   классификацию на `no-deployment` и не просить owner merge при красном CI.
   После owner GitHub UI merge проверить PR/head/merge и текущий remote `main`,
   затем вызвать typed **`workspace.update_main_from_pr`** для чистого Docker
   primary. Условия доказательства merge и параметры принадлежат
   [native contract][native], а не этому общему UC. Старый `workspace.update_main`
   требует Gateway merge receipt и не подходит после UI merge; не создавать
   фиктивную ASK. Для нового client/API — [UC-GW-003][api-change].
   При HTTP `500`, `UNCERTAIN`, timeout или `403` сначала проверить исходный
   UUID и фактический результат по [UC-CONT-003](#uc-cont-003) и
   [UC-GW-009][incidents]. Достигнутый результат не повторять; при
   недостигнутом результате применять только операционно-безопасный
   ограниченный повтор с новыми проверками SHA и действующей авторизацией.
   `reconcile` — отдельная операция, не read-only просмотр заявки.
5. **Если проекту требуется обновлённый Windows clone**, применить
   [UC-CONT-005](#uc-cont-005) через Mirror. Если пользователь не просил
   Windows-исходники и нет конкретного Windows consumer/test/deploy,
   зафиксировать «Windows sync: не требуется» и не запускать Mirror
   ради формального совпадения SHA. Pull исходников не собирает image
   и не обновляет запущенное приложение.
6. Выполнить требуемое развёртывание и приёмку у владельца target, если это
   входит в цель. Для Gateway — [UC-GW-005](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005)
   и [UC-GW-007](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/primary.md#uc-gw-007), включая
   SelfTest, Check, отдельно подтверждённый Apply, live readback, Backup,
   Promote, проверку сохранённых поколений и решение по отдельному Cleanup.
   Для остальных targets — их собственные UC; не переносить команды Gateway
   на другие сервисы. При STOP/UNCERTAIN сохранять исходные receipts и
   recovery resources, не считать релиз завершённым.
7. Завершить свою задачу очисткой выбранного task worktree: сверить repo,
   task и фактический HEAD, убедиться, что работа закончена и source path не
   нужен deployment/recovery records или другой активной задаче. По
   [контракту очистки][cleanup] проверить live capability и вызвать typed
   `workspace.cleanup_task`; решение ALLOW/ASK принимает Gateway, порядок
   approvals — [UC-CONT-003](#uc-cont-003). Проверить receipt `EXECUTED`,
   отсутствие выбранного worktree и его локальной task-ветки.
   **При HTTP 500/timeout/UNCERTAIN не оставлять незавершённую очистку только
   из-за неизвестного исхода исходного UUID.** Проверить целевой worktree,
   точные repo/task/HEAD, чистоту (включая ignored), регистрацию, отсутствие
   активного worker и live policy; если каталог/ветка ещё на месте и все
   предусловия сохраняются — выполнить **новую штатную `cleanup_task` с новым
   requestId** по общему правилу ниже. Если оба уже удалены — цель достигнута,
   нового WRITE не нужно. Если удаление частичное или состояние противоречиво —
   STOP и конкретная диагностика. Не обходить отказ через force/reset/clean.
   Это не массовая очистка других задач, remote branches или Docker volumes.

**Готово:** PR/CI/merge и Docker main подтверждены по точным SHA;
для требуемой Windows-синхронизации Mirror уже показал проверенный
`EXECUTED`/readback либо Windows явно не входил в задачу.
Не запрашивать дополнительную PowerShell-команду, скриншот или
ручное сообщение SHA после успешного Mirror readback. Необходимое
развёртывание прошло [UC-CONT-012](operations.md#uc-cont-012), если оно было целью;
все требуемые targets приняты по соответствующим evidence,
retention/recovery проверены, необязательные отложенные действия обоснованы.
При блокере обязательного действия соответствующий цикл остаётся PARTIAL/BLOCKED.
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
сохраняются для status/evidence и разрешённого контрактом повторного опроса.
При `UNCERTAIN` не переисполнять исходный UUID и не путать polling
с новым push/commit. Новое штатное обращение допустимо только после
readback, новых предусловий и проверки безопасности операции ниже. ALLOW
выполняется в пределах поручения, ASK
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
**GitHub-операции ИИ выполняются только через Gateway.** Если repo/операция ещё не
зарегистрированы, Gateway недоступен или вернул DENY, остановиться; перейти к
[UC-CONT-018](#uc-cont-018), а не подменять маршрут прямым Git или иным клиентом.
Токены GitHub не читать, не передавать в Repo и не конфигурировать в локальном Git.
Универсальные команды `git fetch/push` из схемы директорий в Mirror описывают
организацию Git, **но не дают разрешения** обращаться к GitHub напрямую:
в принятом native scope удалённые Git-эффекты выполняются типизированным
клиентом Gateway. Локальные `git status/diff` в task worktree не являются
GitHub API. Не использовать GitHub connector, старый credential helper,
прямые сетевые Git-команды или сторонний API-клиент вместо Gateway.

**Делегированный Mirror API — узкий P0 proposal, activation gated.** После
owner security review [единого Mirror contract][mirror-unified] и принятия
versioned provider допускается только маршрут
`Repo AI → typed Gateway mirror operation → Windows Mirror Core` для
закрытых Mirror READ и guarded Windows main Pull с ASK. Mirror выбирает
фиксированные Windows Git/gh операции и использует Windows owner-managed
авторизацию; ИИ не получает credential, команду, URL, path/ref или shell.
До принятия contract, отдельного owner release и fresh live catalog/READ
новый делегированный маршрут **не разрешён**; прежний strict READ v1 сохраняется.
AI Pull требует отдельно принятой model B/dispatch proof и live ASK acceptance;
Bearer или UUID сами по себе не разрешение. Metadata fetch — не pure READ,
для AI остаётся DENY до отдельного review. Нативные GitHub branch/commit/PR/
publish в Repo по-прежнему только через существующий typed Gateway workflow.
Этот узкий scope не распространяется на другие собственные API, GitHub
push/merge/settings, произвольные Windows-команды или Owner Shell.

[mirror-unified]: https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/MIRROR_API_CONTRACT_V1.md

Первичный Windows `git clone` нового repo выполняет владелец по готовой команде
из чата — [UC-CONT-027](repositories.md#uc-cont-027). Это отдельный owner-run
bootstrap, не доступ ИИ к Windows credentials или прямому Git из Docker.

**Автоматические READ-повторы и продолжение интента.** В Repo-клиенте с
поддержкой `default_client().intents` использовать штатные команды, а не
воспроизводить проверки ниже вручную после каждого сбоя. READ повторяется
ограниченно при 429, временных 5xx/сетевых сбоях и доказанном throttling 403,
без поиска результата WRITE; учитываются Retry-After/reset и пауза.
Один `intentId` обозначает цель, **каждая новая попытка получает новый
`requestId`**. Идентификаторы сохраняются для evidence, не для повторного
исполнения старого UUID. Повтор одинаковой команды продолжает журнал;
`client.intents.retry(intentId)` явно запрашивает следующий ограниченный
раунд и сам создаёт UUID после readback/preconditions. ИИ не подбирает UUID.
Автоматически — до трёх попыток в раунде; обычный повтор вызова не сбрасывает
исчерпанный бюджет. DONE/WAITING/STOP/RETRY_EXHAUSTED и фактические attemptIds
возвращаются клиентом. Для PENDING/активного worker не создавать замену;
реальные DENY, изменённые SHA и неполный READ не обходить.
Точный scope операций, журнал, первая доставка queued job, ограничения
reconcile и совместимость старого Gateway принадлежат [native contract][native].
Это source-возможность клиента, а не заявление о развёрнутом Gateway image.

Первый вызов поддержанной команды не требует ручного UUID. Для push + PR
использовать `client.git_delivery.submit(...)`: он возвращает один parent
`intentId`, а push/PR продолжаются теми же координаторами. После сбоя или
восстановления соединения достаточно `client.intents.retry(intentId)`;
в CLI — `python3 -B -m fortis_approvals.workflow.client retry --intent-id INTENT_ID`,
без stdin. Бюджеты дочерних этапов сохраняются; завершённый push не повторяется
при продолжении PR. Ответ содержит фактические UUID, историю и `nextAction`.
После подтверждённого `EXECUTED` недоступный receipt READ даёт `WAITING` /
`RETRY_READ`: продолжение дочитывает исходный результат и не делает новый WRITE.
Для неизвестного исхода по-прежнему возможна безопасная новая попытка.
Общего deadline интента нет; обязательный backoff не сбрасывается повтором.
При новой capability клиент сам делает адресные READ ветки и пары head/base,
со старым Gateway использует полные списки. Проверки ниже нужны для ручного
расследования и legacy-клиента; штатный координатор не надо дублировать вручную.

**HTTP 403, HTTP 429, HTTP 500, timeout, `UNCERTAIN`: сначала результат, затем действие.**
HTTP `500`, как timeout или потерянный ответ, сам по себе не доказывает,
что WRITE не выполнился, и не означает `DENY`. Для него действует тот же
readback-first порядок ниже: если цель уже достигнута — не повторять; если
не достигнута — применять существующее ограниченное правило повтора с новой
проверкой SHA/preconditions и действующей авторизацией. Не отправлять WRITE
вслепую.

Не считать единичный `403` постоянной потерей token scope и не менять PAT,
policy или маршрут доступа наугад. Зафиксировать исходный UUID, endpoint,
typed operation, actor, repo, SHA и безопасные `stage/code`. Проверить
`status/details` и receipt через [UC-GW-009][incidents], затем разрешённым
Gateway READ — фактический GitHub/Repo state. `WORKFLOW_DENIED` — общий отказ
Gateway (policy, validation, stale preflight и др.); `GITHUB_HTTP_403` —
ответ upstream. Явный `DENY` или доказанная нехватка прав означает **STOP**,
не повторить WRITE другим credential или инструментом. READ-повторы `403`
допустимы только при распознанном throttling/backoff, с учётом обязательной
паузы; обычный `403` не является таким признаком. После исправления
конфигурации явное продолжение заново проверяет условия и авторизацию;
удачный GET не означает разрешение на запрещённый WRITE.

**Главное после ошибки — решить, можно ли безопасно продолжать задачу.**
Порядок решения: **(1)** readback фактического целевого состояния;
**(2)** оценить идемпотентность/ограничения конкретной операции (CAS,
точный SHA/identity, проверяемый конечный эффект, допустимость дубля);
**(3)** при недостигнутой цели и допустимых свежих предусловиях выполнять
новую штатную попытку с новым requestId, не более трёх в автоматическом раунде;
**(4)** STOP только при конкретном препятствии — действующий DENY,
изменившиеся предусловия, активное конкурирующее выполнение, неполный
существенный readback или небезопасный повтор. **Почему пропал старый ответ
и удалось ли доказать исторический исход исходного UUID — не главный критерий
разрешения новой попытки.** HTTP 500, `OUTCOME_UNCONFIRMED` или отсутствие
receipt не являются самостоятельными STOP-причинами. Технический разбор
старого UUID нужен для evidence и поиска конкурирующей работы, не вместо
проверки возможности продолжить задачу.

**Защита Fortis и восстановление.** Core связывает UUID с immutable
fingerprint, worker — с durable journal, GitHub-адаптер — с receipt.
Завершённый UUID Fortis самостоятельно **не исполняет позже заново**; повтор
`status/details/inspect` — чтение, а не повтор POST. При потерянном HTTP-ответе
уже переданный GitHub запрос всё же может завершиться без Fortis receipt;
поэтому сверять фактическую цель, а не ждать абстрактного «окончания сети».
Агент не запускает старый claim/`resume` ради нового эффекта и не выдаёт
успешное конечное состояние за receipt старого UUID.

**Быстрый readback по операции (через typed `default_client().github`).**
При поддержке `githubTargetReads` для branch/commit/push — `get_branch`,
для PR — полный адресный `find_pull_requests` по той же паре head/base;
без capability — `list_branches(repo)` и `list_pull_requests(repo,state='all')`.
Для найденного PR дополнительно использовать
`get_pull_request(repo,number)`; для merge — `get_pull_request` с
`merged=True`, HEAD и GitHub `main`; для локального `update_main_from_pr`
— `git rev-parse HEAD`, `git status --porcelain`, Git reflog и worker
journal в разрешённом Repo-контексте. По возможности инспектор UC-GW-009
делает эти READ автоматически. Если цель уже достигнута, **не повторять**.
Если цель не достигнута, оригинальный local worker имеет durable `FAILED`
(не `CLAIMED`), Git/readback и preconditions однозначны, либо конкретная
GitHub операция защищена уникальной branch/ref identity и SHA/CAS,
допускается **новое штатное обращение** после новой live проверки политики,
прав/предусловий: максимум **три попытки в автоматическом раунде**, считая исходную, с
короткой паузой и readback после каждой. Новый requestId — новая операция и
при `ASK` новое решение owner; старую запись/receipt не переписывать.
Если задача выполняется другим actor, действующая авторизация остаётся
обязательной. При `CLAIMED` с возможным активным эффектом, изменённых SHA,
неполном GitHub READ, неоднозначном CREATE без устойчивой идентичности
или реальном DENY — **STOP** и конкретные evidence, не обход.

**PR после UNCERTAIN / HTTP 500 / CLOSED_UNCONFIRMED — продолжить задачу.**
`OUTCOME_UNCONFIRMED`, отсутствие receipt и `retryAuthorization=NONE`
означают, что инспектор не вправе автоматически переисполнить *старый UUID*;
это **не вечный запрет создать нужный PR новой авторизованной заявкой**.
Проверить через полный поиск той же пары head/base (при новой capability —
`find_pull_requests`, иначе `list_pull_requests(repo,state='all')`) и
`get_pull_request` все PR по **той же** паре `head/base`, точному
`head SHA`, включая закрытые и уже merged. Если требуемый PR найден —
использовать его, не создавать второй. Если PR не найден при полной
проверке, опубликованная task-ветка всё ещё у нужного SHA, нет
активного `CLAIMED` и policy/preconditions допускают CREATE — **создать
PR новой штатной операцией с новым requestId**, не требуя доказательства
невозможности любого позднего эффекта старого UUID. GitHub не допускает
два одновременно открытых PR для одной и той же пары head/base; при
гонке с поздним CREATE повтор может получить конфликт «PR already exists» —
в этом случае **снова READ и использовать найденный PR**, а не повторять
бесконечно. Не заявлять, что это доказывает исторический исход старого UUID.
Лимит до трёх попыток в раунде и новая проверка авторизации остаются в силе.

**Issue после UNCERTAIN / HTTP 500 — допускается новая публикация
с риском дубля.** Для `github.publish_visual_review` Gateway навсегда
резервирует пару `(repository,runId)` перед первым GitHub WRITE; повторная
заявка с прежним `runId` может дать `VISUAL_REVIEW_RUN_ALREADY_RESERVED`.
**В новой попытке разрешается выбрать новый уникальный `runId` вместе
с новым requestId** (старые runId/UUID и audit не изменять). Это новый
отдельно авторизованный intent, не replay старого запроса и не обход
реального policy DENY. При полной read-only проверке, отсутствии
уже опубликованного нужного Issue и отсутствии других STOP-причин
не требовать доказательства, что старый POST никогда не завершится:
риск позднего второго Issue **принят для этого сценария**. После
успешной публикации требуется **отдельная ручная проверка копий**; автоматический
retry-координатор её не запускает и возвращает `manualDuplicateCheckRequired=true`.
При ручной проверке пройти **все open/closed Issue**:
все известные `runId`, точные title/body и устойчивый идентификатор
исходной задачи, поскольку у двух попыток маркеры `runId` различаются.
Если их два — показать оба номера/URL, обозначить канонический,
не удалять и не закрывать автоматически. Лимит попыток и условия
ALLOW/ASK/DENY сохраняются. Если исходный `CLAIMED` ещё может
исполняться, результаты READ неполны или есть иной реальный STOP —
не создавать новую заявку до прояснения.

**Issue: экспресс-поиск дубликатов (включая закрытые).** Для Fortis visual
review основной ключ — `runId`, записанный в начале body как
`<!-- fortis-visual-review:RUN_ID -->`. Проверить `list_issues(repo,
state='all',page=...,per_page=30)` — его `items[*].runIdMarker`, а найденные
номера подтвердить `get_issue(repo,number)`, сравнив полный body и runId.
Пример — только Gateway READ, не отдельный GitHub token:

```python
from fortis_approvals.workflow.client import default_client
c = default_client()
run_id = 'ТОЧНЫЙ_RUN_ID_ИСХОДНОЙ_ЗАЯВКИ'  # заменить исходным runId
hits = []
for page in range(1, 11):
    response = c.github.list_issues('visual-workspace', state='all',
                                    page=page, per_page=30)
    hits += [i['number'] for i in response['items']
             if i['runIdMarker'] == run_id]  # исходный стабильный runId
    if not response['hasNextPage']:
        break
else:
    raise RuntimeError('ISSUE_INVENTORY_INCOMPLETE')
issues = [c.github.get_issue('visual-workspace', n)['issue'] for n in hits]
# Сопоставить runIdMarker, title, body и URLs; >1 — кандидаты в дубликаты.
```

Для обычного Issue без Fortis-маркера сначала отфильтровать свежие
`list_issues(...,state='all')` по точному title/времени, затем сравнить
`get_issue(...)` body по характерной строке или идентификатору задачи;
одинаковый title сам по себе недостаточен. Если найдено два — указать оба
URL и один канонический, не удалять автоматически. Если страницы не покрыты,
GET недоступен или результат неоднозначен — явно отметить неполноту.
Не тратить время на повторные тяжёлые поиски без нового evidence.

**Граница:** повторная проверка не равна повторной мутации. Нет
универсальной гарантии GitHub exactly-once для любых двух разных POST/UUID,
особенно для Issue, комментариев и запуска workflow. Отсутствие старого
receipt не доказывает исход UUID, но **не должно блокировать новую безопасную
публикацию PR или принятую пользователем попытку Issue** по правилам выше.
Различать доказательство старого UUID и достижение цели задачи.
Другие операции не наследуют эти допуски. Действовать по конкретным
предусловиям и [UC-GW-009][incidents]; без них — STOP, не слепой повтор.
`403` при `/v1/git/artifact` до создания action/ASK требует проверки
bundle identity, remote branch и Gateway admission, а не Owner Portal.


**Готово:** получен проверенный typed result/receipt нужного действия; токен не
попал в Repo/payload/log. Политики не переписываются в этом сценарии: [native][native].

## UC-CONT-004

**Цель:** понять, что произошло в Actions именно с проверяемым изменением.

**Как:** через GitHub-клиент получить workflow runs и сопоставить repo, workflow,
event, HEAD SHA, attempt и завершение. Ожидание отличать от failure/cancelled и
success. Проверить **все обязательные** для проекта workflows и завершение
каждого required job на актуальной попытке, а не выбирать старый зелёный run.
Для принятого Release Impact CI ошибки отсутствующего/невалидного body,
неверных targets или неохваченных diff-файлов исправлять в исходном PR
по [Release Planning Contract](../RELEASE-PLANNING-CONTRACT.md), не снижая
проверки и не считая метки доказательством успешного CI.
Логи/jobs/annotations/artifacts читать только поддержанными typed операциями.
Дополнительный [analysis profile][analysis] требует отдельной конфигурации;
наличие его клиента в source не означает доступность в live Gateway.
Sonar/analysis/PR binding дополнительно проверяется по [UC-GW-001](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/sonar.md#uc-gw-001).

**Готово:** есть статус обязательных проверок для точного SHA либо явно записано,
какой evidence недоступен. Required CI IDs и доступные операции — у владельца контракта.

## UC-CONT-005

**Цель:** по запросу или реальной потребности обновить Windows primary
clone до одобренного merged main; получить подтверждение из самого Mirror.

**Как:** открыть Mirror, выбрать точный repo и проверить фактические Windows
branch/HEAD/origin/dirty status, GitHub main и направление ancestry. Выбранная
для просмотра ветка не является checkout. Windows должна быть на чистом main,
без собственных коммитов ahead; ожидаемый SHA должен соответствовать принятому merge.
Использовать guarded Pull Windows main: повторный preflight, fetch точного ref,
проверка FETCH_HEAD и fast-forward. При расхождении, dirty, unknown или неверном
origin остановиться без reset/stash. CLI-эквивалент должен сохранять те же проверки.

**Готово:** Mirror подтверждает `Pull Windows` как `EXECUTED` и
показывает Windows `main` readback = проверенному GitHub `main` SHA,
либо сообщает конкретный STOP/unknown. Mirror сам сверяет SHA, branch,
origin и clean: **после успешного Mirror readback не давать владельцу отдельную
команду на «подтверждение SHA», не требовать копировать SHA в чат**.
Если результат неясен, использовать `Проверить результат`/receipt и
read-only сверку Mirror, не повторять Pull вслепую. Если Windows не нужен,
этот UC пропускается — проверенный Docker/GitHub цикл уже завершён.
Подробная UI/CLI процедура и ограничения GUI — [Mirror workflow][mirror].
Не использовать GUI Stage/Commit/Push как будто он уже выбирает Docker task worktree.

## UC-CONT-018

**Когда:** нужно подключить уже созданный repo к Gateway workflow. Полное
создание нового repo и Windows-клона — [UC-CONT-027](repositories.md#uc-cont-027).

**Цель:** включить ещё один repo в авторизованный GitHub/CI/Windows маршрут.

**Как:** проверить наличие remote и доступ, repo ownership, allowed local roots,
права Gateway credential, требуемые workflow IDs и доступные native bindings.
При текущем `dynamicRepositories=true` отдельной allowlist репозиториев **нет**:
проверить `github.list_repositories(owner)`, разрешения **текущего токена** для
нужного repo, `GET repository` у Gateway, `main`/owner, canonical Git origin,
существующие `/workspace/repo/Repos/<repo>` и `Worktrees/<repo>` и действующую
политику конкретной операции. Если достоверно установлено отсутствие upstream token scope —
не обходить через PAT/GitHub connector: требуется owner-reviewed
scope/credential change. Сам по себе `403` либо отсутствие repo в списке
не доказывает причину; сначала разделить Gateway DENY/preflight, конкретный
target и ответ реального GitHub (UC-CONT-003). Если local worktree или repo
отсутствует, это **другой** prerequisite, не автоматическая публикация. При
legacy `dynamicRepositories=false` прежний single-repo scope сохраняется,
и расширение требует принятого source/config + rollout. Не выдавать ALLOW всем
репозиториям только потому, что они видны по API.
Первичный Windows-клон — [UC-CONT-027](repositories.md#uc-cont-027),
последующее обновление — [UC-CONT-005](#uc-cont-005).

**Готово:** repo явно поддержан контрактом и live capabilities, выполнен нужный
GitHub/CI цикл. Отсутствующий remote и отказ в доступе различаются; `Repository
not found` сам по себе не доказывает причину.

[mirror]: https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md
[native]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/NATIVE-WORKTREE-GATEWAY-2026-11-06.md
[cleanup]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/NATIVE-WORKTREE-GATEWAY-2026-11-06.md#task-worktree-cleanup
[api-change]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-003
[guide]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/GATEWAY-AGENT-GUIDE.md
[analysis]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/ANALYSIS-REVIEW-CONTRACT.md

[incidents]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009
