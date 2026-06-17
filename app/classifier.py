import asyncio
import json
import logging
from pydantic import ValidationError
from app.gemini_client import GeminiClient
from app.models import ClassifiedRequest

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Ти — класифікатор запитів до AI-юніту компанії.
Проаналізуй запит і визнач:
- category: одна з категорій (автоматизація, інтеграція, звіт/аналітика, баг/підтримка, питання/консультація, поза скоупом)
- target_department: відділ який надіслав запит (маркетинг, продажі, аналітика, HR, PM тощо) або порожній рядок якщо невідомо
- priority: low/medium/high — виводь з тону (ГОРИТЬ = high, теоретичне питання = low)
- short_summary: суть одним коротким реченням українською
- requested_actions: список конкретних дій які просять (порожній список якщо нічого конкретного)
- needs_clarification: true якщо запит надто розмитий щоб братись за нього без уточнень"""


def build_prompt(row: dict) -> str:
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Канал: {row['channel']}\n"
        f"Час: {row['timestamp']}\n"
        f"Запит: {row['raw_text']}"
    )


async def classify_one(
    client: GeminiClient,
    row: dict,
    semaphore: asyncio.Semaphore,
) -> ClassifiedRequest | None:
    async with semaphore:
        try:
            raw_json = await client.classify(build_prompt(row))
            data = json.loads(raw_json)
            if data.get("target_department") == "":
                data["target_department"] = None
            return ClassifiedRequest(
                id=row["id"],
                channel=row["channel"],
                timestamp=row["timestamp"],
                raw_text=row["raw_text"],
                **data,
            )
        except (ValidationError, json.JSONDecodeError) as e:
            logger.error("Validation error for %s: %s", row["id"], e)
            return None
        except Exception as e:
            logger.error("Unexpected error for %s: %s", row["id"], e)
            return None


async def classify_all(rows: list[dict]) -> list[ClassifiedRequest]:
    client = GeminiClient()
    semaphore = asyncio.Semaphore(5)
    tasks = [classify_one(client, row, semaphore) for row in rows]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
