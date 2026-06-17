import json
from collections import Counter
from pathlib import Path
from app.models import ClassifiedRequest, Stats


def build_stats(results: list[ClassifiedRequest]) -> Stats:
    return Stats(
        total=len(results),
        by_category=dict(Counter(r.category for r in results)),
        by_priority=dict(Counter(r.priority for r in results)),
        by_department=dict(Counter((r.target_department or "невідомо").lower() for r in results)),
        needs_clarification=[r.id for r in results if r.needs_clarification],
    )


def save_output_json(results: list[ClassifiedRequest], path: str = "output.json") -> None:
    Path(path).write_text(
        json.dumps([r.model_dump() for r in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_report_md(results: list[ClassifiedRequest], stats: Stats, path: str = "report.md") -> None:
    lines = [
        "# Звіт по класифікованих запитах\n",
        f"**Всього оброблено:** {stats.total}\n",
        "## По категоріях",
        *[f"- {k}: {v}" for k, v in stats.by_category.items()],
        "\n## По пріоритету",
        *[f"- {k}: {v}" for k, v in stats.by_priority.items()],
        "\n## По відділах",
        *[f"- {k}: {v}" for k, v in stats.by_department.items()],
        "\n## Потребують уточнення",
        *([f"- **{r.id}**: {r.short_summary}" for r in results if r.needs_clarification] or ["- немає"]),
    ]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
