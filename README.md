# Request Classifier

Мікросервіс для автоматичної класифікації вхідних запитів до AI через Gemini 2.5 Flash.

## Запуск

### Docker (рекомендовано)
cp .env.example .env
# вписати GEMINI_API_KEY в .env
docker compose up --build


### Локально
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload


## Використання

POST /classify — завантажити CSV файл, отримати класифікацію

Через Swagger UI: http://localhost:8000/docs

Через curl:
curl -X POST http://localhost:8000/classify \
  -F "file=@input_requests.csv"


Результат:
- output.json — повна класифікація всіх запитів
- report.md — агрегати по категоріях, пріоритетах, відділах + список що потребують уточнення

## Змінні середовища

| Змінна | Опис |
|--------|------|
| GEMINI_API_KEY | API ключ з https://aistudio.google.com |

## Обмеження

**Невалідний вивід LLM** — Pydantic валідує кожну відповідь. Якщо модель повернула невалідний JSON або невідоме значення — запит логується і пропускається, решта обробляється далі.

**Недетермінізм** — `temperature=0.1` і `response_schema` з фіксованими enum значеннями мінімізують варіативність відповідей.

**Rate limits** — `Semaphore(5)` обмежує паралельні запити, exponential backoff на 429 (10с, 20с, 30с).

**Великий обсяг** — async + `gather` дає паралельну обробку. На 500+ запитів варто додати батчування з паузами між батчами щоб не спалити rate limit.

**Вартість токенів** — використовується Gemini 2.5 Flash, доступний на безкоштовному tier. Точна кількість токенів залежить від довжини запитів, при великому обсязі варто моніторити витрати в Google AI Studio.

## Що зробив би далі

- Telegram дайджест з підсумком після обробки
- Запис результату в Google Sheets
- CLI аргументи (--input, --output) замість фіксованих шляхів
- Retry на конкретних запитах що впали замість skip

<img width="1426" height="890" alt="image" src="https://github.com/user-attachments/assets/e138ba9d-96f0-4134-af08-09f369afb197" />
<img width="1307" height="403" alt="image" src="https://github.com/user-attachments/assets/0b05340b-103b-4abc-a9c6-36aacb866c4e" />

