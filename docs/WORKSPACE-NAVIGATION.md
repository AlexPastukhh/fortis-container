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
Наличие `origin` или локальных коммитов в `fortis-container` само по себе
не даёт права на GitHub-операции. Проверяй live Gateway capabilities:
если repo не зарегистрирован, сохраняй изменения в локальном linked worktree
и следуй UC-CONT-018; **не** публикуй напрямую через Git/PAT/коннектор.
