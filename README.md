# Shop Policy Assistant

Telegram FAQ-ассистент на Python и aiogram. GPT-6 Luna извлекает факты вопроса через Structured Outputs; бизнес-правила и формирование ответа выполняются в приложении.

## Запуск

Настройки — в [.env.example](.env.example). Модель по умолчанию — `gpt-6-luna`.

```sh
docker compose up -d --build
```

## Архитектура

Clean Architecture по подходу Evrone: `controller` — Telegram, `usecase` — сценарий, `service` — правила, `entity` — модели, `repo/webapi` — LLM-адаптер. Зависимости собираются в `app.py`.

База условий: [knowledge.json](resources/knowledge.json). Промпт классификатора: [system_prompt.txt](resources/system_prompt.txt).

## Проверки

```sh
pip install -e '.[test]'
pytest -q
python -m shop_assistant.evaluate
```

`pytest` проверяет правила и обработку ошибок без внешних вызовов. `evaluate` прогоняет 20 сценариев через API; [результаты](docs/crash-test.json).
