# README/AGENTS workspace как проекция

Владелец общего реестра — `fortis-container/docs/use-cases/README.md`.
Операционные `/workspace/repo/README.md` и `/workspace/repo/AGENTS.md` находятся
в постоянном workspace, вне Git repo. Они ведут к реестру, не дублируя каталог. Проекция в начале каждого чата
не требует даже просмотра полного списка ID. Она ведёт через короткий вход
к полному чтению UC-CONT-002/003, затем к нужным локальным реестрам.
Источник standing agent rules — `workspace/AGENTS.md` этого repo.

`python3 tools/install-workspace-navigation.py` устанавливает только помеченные
блоки в эти два файла, сохраняя остальной текст. `--check` проверяет их без записи.
Источник берётся из точного checkout, откуда запущен installer. До принятия
изменений в primary main допускается ссылка на его linked docs worktree;
не очищать этот worktree, пока operational entrypoints от него зависят.
После интеграции переустановить проекцию из принятого main.

Registry — навигация. Операционный раздел разовой передачи Workfiles пока
остаётся в корневом README; UC-CONT-015 ссылается на него, не копируя полный шаблон.
Наличие `origin` или локальных коммитов само по себе не доказывает GitHub
permissions. В token-scoped multi-repo режиме проверять live capabilities,
provider scope, owner/origin и canonical local roots по UC-CONT-018.
Недоступный repo/operation — STOP; не добавлять второй allowlist и не
публиковать напрямую через Git/PAT/коннектор.
