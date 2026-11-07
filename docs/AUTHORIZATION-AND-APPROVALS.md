# Authorization and approvals

Этот документ владеет общей картой границ Fortis Container. Typed операции,
policy и deployment принадлежат
[Gateway agent guide](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/GATEWAY-AGENT-GUIDE.md)
и [native contract](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/NATIVE-WORKTREE-GATEWAY-2026-11-06.md).
Не поддерживать здесь вторую матрицу разрешений или текущих container IDs.

## Do not conflate these mechanisms

| Механизм | Назначение | Граница |
| --- | --- | --- |
| Repo machine grant | Аутентифицирует клиента в Gateway machine ingress | Не GitHub/Sonar token и не owner approval |
| Gateway TLS identity | Аутентифицирует Gateway для Repo | Private key остаётся в Gateway; Repo получает public trust |
| GitHub / Sonar credentials | Аутентифицируют Gateway перед конкретным provider | Не передаются в Repo, request payload или логи |
| Owner WebAuthn | Подтверждает решение человека по точной ASK | AI не вызывает owner routes и не подтверждает свою заявку |
| Старые Repo Git credentials | Остаточный credential risk | Не поддерживаемый маршрут GitHub; отсутствие отзыва проверяется отдельно |

## Machine authentication and approval

Machine ingress требует аутентификацию независимо от ALLOW/ASK. ALLOW исполняется
в scope задачи, ASK создаёт immutable preview и PENDING для Owner Portal,
DENY/unknown останавливает действие. Approval не добавляет missing provider scope.
Для локального workspace effect upstream token может не требоваться, но
machine authentication, operation policy и worker receipt остаются обязательны.
Обычные Desktop Commander file/process операции — отдельная capability,
а не автоматически Gateway-controlled действие.

Primary machine endpoint установленного typed client —
`https://host.docker.internal:19204`; старый Legacy 19104 не использовать как
fallback. Client/endpoint/capabilities проверять перед новым target; точные
mounts и deployment records находятся у Gateway owner, не в этом документе.

## GitHub is mediated by Gateway

В принятом multi-repo режиме provider token определяет доступные GitHub repos;
второй repo allowlist не требуется. Дополнительно проверяются owner/origin,
canonical local roots, clean main, task/branch/SHA preconditions и live policy.
Чтение не доказывает Contents write. Публикация — по
[UC-CONT-003](use-cases/delivery.md#uc-cont-003); после PR/CI владелец сливает
через GitHub UI, AI не создаёт merge ASK.

## Shared-process limitation

Machine grant может быть доступен процессам с тем же UID в Repo; `0600`/`0700`
и read-only mount не создают per-agent isolation. Исторические Repo PAT stores
могли сохраниться. Документация и миграция маршрута не доказывают их отзыв.
Не читать/копировать секреты и не восстанавливать helper; дальнейшая isolation,
inventory и owner-controlled rotation/removal — в
[единственном backlog](BACKLOG-IMPROVEMENTS.md).
