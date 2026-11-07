# Git workflow and recovery boundaries

## Supported GitHub route

Начать с [главного реестра](use-cases/README.md) и полностью прочитать
[UC-CONT-002](use-cases/delivery.md#uc-cont-002) /
[UC-CONT-003](use-cases/delivery.md#uc-cont-003).
GitHub READ, fetch, push и PR выполняются только через установленный typed
`fortis_approvals.workflow.client.default_client()`; provider credential остаётся
в Gateway. Token scope и live capabilities проверяются для каждого repo/operation.
Нет доступа — STOP по [UC-CONT-018](use-cases/delivery.md#uc-cont-018).
Существующий Git clone или прежний credential-helper не дают обходного маршрута.
Не восстанавливать PAT/helper ради публикации и не использовать прямой сетевой Git.

## Workspace and task recovery

Canonical directory layout и Windows delivery принадлежат
[Mirror WORKFLOW](https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md).
Git membership проверяется через `git worktree list --porcelain`, не имя папки.
Docker primary остаётся на чистом `main`; edit/test/stage/commit — только в
registered task worktree. Исторические изменения сначала сохранить и сверить,
затем перенести в отдельную задачу по [UC-CONT-019](use-cases/worktrees.md#uc-cont-019).
Без автоматического reset/clean/stash, force-push и очистки чужих задач.
После owner UI merge использовать `workspace.update_main_from_pr` по UC-CONT-002.

При restart/recreate сначала проверить persistent workspace, repositories,
установленный client, публичный TLS trust и machine endpoint/capabilities.
Наличие исходников не доказывает наличие machine grant, работоспособность
Gateway или совпадение deployed image. Recovery credentials/state принадлежит
[Gateway recovery UC](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/recovery.md).
Не читать секреты для диагностики и не копировать их в workspace/чат/артефакты.

## Legacy credentials

Старые Repo credential stores могли сохраниться в persistent workspace.
Это остаточный риск, а не поддерживаемая инструкция работы с GitHub.
В этой документационной задаче их содержимое, Git config и отзыв не меняются.
Rotation/removal — отдельный owner-controlled шаг с проверкой зависимостей;
[backlog](BACKLOG-IMPROVEMENTS.md#a2-authentication-and-credential-isolation)
и [authorization boundaries](AUTHORIZATION-AND-APPROVALS.md).
GitHub credential, machine grant, TLS identity, Sonar token и owner WebAuthn
имеют разные роли и не заменяют друг друга.

## Windows, transfers and backups

Windows clones — отдельные каталоги, не filesystem mirror Docker. Доставлять
approved merged source; source pull не является установкой userscript/image
или restart. Парное обновление Tunnel / Script Center сохраняет собственный
[Windows runbook](https://github.com/AlexPastukhh/script-control-center/blob/main/docs/GIT-WINDOWS-SOURCE-OF-TRUTH.md).

Для host-only шага применять [UC-CONT-025](use-cases/host-operations.md#uc-cont-025),
для разового файла — [UC-CONT-015](use-cases/handoff.md#uc-cont-015).
SHA-256 доказывает совпадение байтов, не разрешение запуска.
Git/image не являются backup persistent volumes, DB, TLS identity и WebAuthn;
[UC-CONT-022](use-cases/docker.md#uc-cont-022) ведёт к точному владельцу backup.
