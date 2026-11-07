# Авторизация и подключение клиентов

## UC-CONT-007

**Когда:** поручено действие, требующее Gateway ALLOW/ASK/DENY или WebAuthn.

**Цель:** пройти одну штатную авторизацию без повторного вопроса на отправку ASK.

**Как:** проверить live policy, actor, repo/target, grant и request ID. Разрешённое ALLOW выполняется в пределах поручения; ASK отправляется через typed Gateway-клиент и ждёт **owner WebAuthn**; DENY/unknown не обходится другим credential или интерфейсом. При timeout/UNCERTAIN — read status/reconcile, не повторять эффект слепо. Защищённое решение владельца не подменяется его фразой в чате. Точное API — [Gateway agent guide][guide] и [native policy][native].

**Готово:** получен проверяемый receipt/status, либо STOP с конкретным ограничением, без утечки provider token.

## UC-CONT-008

**Когда:** нужно подключить AI, MCP или machine-клиента к Fortis.

**Цель:** выдать клиенту только требуемый ограниченный доступ.

**Как:** определить transport/endpoint и actor в [карте AI][ai], разделить machine TLS grant и provider credential, проверить trusted provisioning и live capabilities. Новому клиенту не передаются Gateway-only токены. Не выводить возможность операции из доступности инструмента или общего UID. **Различать новый machine actor/клиент, новую typed операцию и новое внешнее API:** новый actor требует точного TLS grant/политики; новый метод уже существующего клиента — закрытой request/result schema на сервере, проверки ingress/adapter/worker, сохранения старых методов и тестов отказов; внешний provider — отдельного extension contract. Для добавления операции/endpoint применять [UC-GW-003][operation], для нового provider — [UC-GW-002][provider], для credential — [UC-GW-004][credential]. Новое имя метода в Repo source не означает, что работающий образ умеет его выполнять: проверить установленный API и необходимость owner-managed image release по точному source SHA.

**Готово:** разрешённый READ подтверждён через рабочий Gateway, непроверенные операции явно указаны.

[guide]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/GATEWAY-AGENT-GUIDE.md
[native]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/NATIVE-WORKTREE-GATEWAY-2026-11-06.md
[ai]: ../AI-INTEGRATIONS.md
[provider]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-002
[operation]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-003
[credential]: https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/credential-lifecycle.md#uc-gw-004
