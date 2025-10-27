from fastapi import FastAPI, UploadFile, File, Form
from app.services.yolo_service import detect_objects
from app.services.bitnet_service import analyze_text
from app.services.database import init_db, save_entry, get_history
import uvicorn

app = FastAPI(title="Milo – AI Nutrition Analyzer (Stage 4)")

init_db()

@app.get("/")
def root():
    return {"message": "Milo API running...", "stage": "Stage 4 - API with Database"}


@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    contents = await file.read()
    detections = detect_objects(contents)
    save_entry("image", file.filename, detections)
    return {"filename": file.filename, "detections": detections}


@app.post("/predict/text")
async def predict_text(prompt: str = Form(...)):
    analysis = analyze_text(prompt)
    # ✅ Save the text input to database as "prompt"
    save_entry("text", "prompt_input", analysis, prompt)
    return analysis


@app.get("/history")
def history():
    return {"history": get_history()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
