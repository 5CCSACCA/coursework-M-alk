#!/usr/bin/env python3
"""
Stage 3: FastAPI Service
This script exposes the models through a simple API that allows external requests
to reach the models and return predictions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form
from app.services.yolo_service import detect_objects
from app.services.bitnet_service import analyze_text
import uvicorn

app = FastAPI(title="Milo – AI Nutrition Analyzer (Stage 3)")

@app.get("/")
def root():
    return {"message": "Milo API running...", "stage": "Stage 3 - API"}

@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    """Predict objects in uploaded image using YOLO"""
    contents = await file.read()
    detections = detect_objects(contents)
    return {"filename": file.filename, "detections": detections}

@app.post("/predict/text")
async def predict_text(prompt: str = Form(...)):
    """Analyze text using BitNet-style model"""
    analysis = analyze_text(prompt)
    return analysis

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
