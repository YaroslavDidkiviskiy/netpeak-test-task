import csv
import io
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from app.classifier import classify_all
from app.models import ClassifyResponse
from app.report import build_stats, save_output_json, save_report_md

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Request Classifier")


@app.post("/classify", response_model=ClassifyResponse)
async def classify(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files accepted")

    contents = await file.read()
    try:
        rows = list(csv.DictReader(io.StringIO(contents.decode("utf-8"))))
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to parse CSV")

    if not rows:
        raise HTTPException(status_code=400, detail="CSV is empty")

    required = {"id", "channel", "timestamp", "raw_text"}
    if missing := required - set(rows[0].keys()):
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    results = await classify_all(rows)

    if not results:
        raise HTTPException(status_code=422, detail="All requests failed classification")

    stats = build_stats(results)
    save_output_json(results)
    save_report_md(results, stats)

    return ClassifyResponse(results=results, stats=stats)
