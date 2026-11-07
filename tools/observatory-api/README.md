# Fortis Repo → Observatory API (регистрация выполнена, применение ожидается)

**Состояние 04.11.2026:** владелец запустил `Enable-FortisObservatoryRepoClient.ps1 -AllowWrites`; скрипт сообщил `REPO_GATEWAY_CLIENT=ADDED`, `REPO_ALLOWED_CHATS=9`, `REPO_WRITE_ACCESS=True`, `GATEWAY_CONFIG_BACKUP=CREATED`. **На диске запись создана, но Gateway ещё не перезапускался и авторизованный запрос из Repo не проверен.** Из Fortis Repo метаданными подтверждено: отдельный ключ существует в каталоге `0700`, файл `0600`, UID/GID `1000:1000`; сам ключ не читался и не выводился.

Действующий Gateway владелец восстановил после перезагрузки: Windows health OK и 9 Repo-сессий. Из Repo подтверждён TCP к `host.docker.internal:18756`: `Host: host.docker.internal:18756` → 403, `Host: fortis-observatory-api:18756` без ключа → 401. Для применения разрешений требуется **отдельный явный перезапуск только `fortis-observatory-api`**; затем — чтение `health` и `sessions`.

Эти файлы — отдельный клиентский инструмент, не конфигурация Docker Engine. Сеть и порты не менялись, Repo/Viewer контейнеры не пересоздавались.

## Настройка Windows (делает владелец)

1. Скопировать `Enable-FortisObservatoryRepoClient.ps1` из `fortis-repo-test:/workspace/repo/Repos/fortis-container/tools/observatory-api/` во временный файл на Windows и проверить код/контрольную сумму.
2. Запустить скрипт с нужными правами: без аргумента — только `read:metadata` и `read:history`; с `-AllowWrites` — дополнительно `write:events`, `write:messages`.
3. Скрипт создаёт отдельный Repo-токен в `/workspace/repo/.fortis-observatory-repo-client/token` (0700/0600), передаёт **только SHA-256** и список текущих зарегистрированных чатов в **отдельный приватный Docker volume Gateway**. Токен Windows остаётся в owner-private каталоге Windows. Клиент `fortis-repo` не получает `scope=all_registered` и не может выполнять Windows owner API. Скрипт создаёт резервную копию `clients.json`, но не перезапускает Gateway.
4. Только после просмотра вывода и **отдельного решения владельца** выполнить `docker restart fortis-observatory-api`. Это требуется, поскольку Gateway читает `clients.json` при старте. **Не** перезапускать `fortis-repo-test`, Viewer или Docker Desktop.
5. Из подключённого Fortis Repo выполнить read-only smoke:

```sh
python3 -B /workspace/repo/Repos/fortis-container/tools/observatory-api/fortis_observatory_client.py health
python3 -B /workspace/repo/Repos/fortis-container/tools/observatory-api/fortis_observatory_client.py sessions
```

## Клиентские команды

```sh
python3 -B fortis_observatory_client.py health
python3 -B fortis_observatory_client.py sessions
python3 -B fortis_observatory_client.py events rs_<32hex>
python3 -B fortis_observatory_client.py history rs_<32hex> task_<32hex>
python3 -B fortis_observatory_client.py receipt req_<32hex>
python3 -B fortis_observatory_client.py stage-event /path/to/event.json
python3 -B fortis_observatory_client.py stage-message /path/to/message.json
```

POST использует JSON в существующем формате Gateway, с устойчивым `request_id`. Он только ставит событие/ответ AI в очередь; `staged_only` не доказывает принятие архивом. **Только после явно разрешённого действия следует отправлять боевой POST.** Тесты намеренно не создают производственных сообщений.

Ограничение текущего Gateway: клиенту Repo можно дать точный список **всех существующих** зарегистрированных Chat ID (без ручного выбора одного), но **новые** сессии не попадают в этот список автоматически. Повторное расширение требует безопасного обновления области доступа и перезапуска Gateway.

## Безопасность и тесты

- Токен Repo **не в Git**, не в Windows-ключах Viewer и не в выводе скрипта. Однако он находится в общем `fortis-repo-workspace` томе: другой контейнер с доступом ко **всему** этому тому под UID 1000 потенциально может прочитать ключ несмотря на режим 0600. Для более строгой изоляции потребуется отдельный secret-volume и согласованное пересоздание Repo с новым mount; этот кандидат этого не делает.
- Адрес `host.docker.internal` работает в проверенной Docker Desktop конфигурации, но это не сетевой firewall/изоляция. Авторизация Gateway обязательна.
- Разрешения выдавать по минимуму; скрипт не добавляет произвольные API-действия Windows Viewer, Notifier или Send.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_repo_client` — 5/5 offline. Windows PowerShell provision и Gateway config reload ещё не тестировались на целевом хосте.
