# Работа в ветке репозитория

## UC-CONT-019

**Цель:** начать или продолжить работу в отдельной ветке, сохранив другие задачи
и стабильный primary clone.

**Как:** выбрать repo и точный linked task worktree по следующей схеме.

| Где | Путь | Назначение |
| --- | --- | --- |
| Docker primary | `/workspace/repo/Repos/<repo>` | Постоянный Git anchor на `main` |
| Docker task worktree | `/workspace/repo/Worktrees/<repo>/<task>` | Файлы выбранной task-ветки; здесь edit/test/stage/commit |
| Windows зеркало | `%USERPROFILE%\Repos\<repo>` | Получатель одобренного merged `main` |

Каталоги в Fortis Repo: [Repos](/workspace/repo/Repos/) и
[Worktrees](/workspace/repo/Worktrees/). Windows-путь — отдельный clone на хосте,
не Docker mount. В обычном зеркальном workflow Windows task worktrees не создаются
и feature-ветки туда не доставляются: зеркало остаётся на `main`.

1. По [UC-CONT-001](orientation.md#uc-cont-001) прочитать repo/AGENTS, проверить
   branch/status/HEAD и `git worktree list` в primary и выбранном worktree.
   Записать точные repo, ветку и путь задачи. Наличие папки ещё не доказывает
   linked Git worktree; второй независимый clone вместо него не создавать.
2. Продолжить существующий worktree нужной ветки либо создать новый с уникальным
   task path и проверенным base. Для принятого native scope использовать typed
   `create_task` по [контракту][native]; для других repo — применимый
   [Mirror workflow][mirror] и разрешённый маршрут [UC-CONT-003](delivery.md#uc-cont-003).
   Не переключать primary с `main`, не переносить/stash/reset чужие изменения.
   **Инвариант Fortis: основной `main` всегда должен оставаться чистым.**
   Не вести разработку и не копить незакоммиченные изменения в
   `/workspace/repo/Repos/<repo>`; edit/test/stage/commit проводить только в
   зарегистрированном task worktree. `workspace.create_task` требует **чистый**
   primary `main` даже при создании независимой linked ветки: иначе новая
   задача возьмёт только Git-коммит и незаметно не получит
   staged/unstaged/untracked изменения primary. Существующую историческую
   грязь разбирать отдельно: сверить полный Git status, сделать проверенную
   recovery-копию, перенести изменения в зарегистрированный task worktree,
   зафиксировать и опубликовать PR. Не скрывать грязь через `.gitignore` и не
   очищать primary до сохранения и сверки точного состава файлов. Не применять
   автоматические `stash/reset/clean`, не обходить Gateway прямым GitHub API.
   Обе операции обновления `main` требуют clean primary; наличие нужного
   client/API проверять по live capabilities и native contract.
   Одна ветка не должна быть одновременно checkout в двух worktrees.
3. Выполнять edit, проверки, stage/commit именно в выбранном task path. Для
   параллельной задачи выбрать другой worktree/ветку; каждый раз явно проверять
   target. Политики публикации и approvals остаются у [UC-CONT-003](delivery.md#uc-cont-003).
4. Для PR/CI/merge, обновления Docker main, получения Windows main и завершения
   задачи очисткой worktree перейти к [UC-CONT-002](delivery.md#uc-cont-002),
   шаг 6. Не принимать выбор
   ветки для просмотра в Mirror за checkout или выбор Docker worktree: текущие
   ограничения GUI описаны только в [Mirror workflow][mirror].

**Готово:** известны точные task path/branch/HEAD; изменения и проверки относятся
к этому worktree, primary остаётся на `main`, другие задачи сохранены. Windows
получает source только после принятого merge по [UC-CONT-005](delivery.md#uc-cont-005).

[mirror]: https://github.com/AlexPastukhh/docke-windows-mirror/blob/main/docs/WORKFLOW.md
[native]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/NATIVE-WORKTREE-GATEWAY-2026-11-06.md
