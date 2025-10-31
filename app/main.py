from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from app.services.yolo_service import detect_objects
from app.services.bitnet_service import analyze_text
from app.services.firebase_service import save_analysis, get_analysis, get_all_analyses, update_analysis, delete_analysis, get_analyses_by_type
from app.services.database import init_db, save_entry, get_history
from app.services.queue import publish
import uvicorn

# FastAPI app
app = FastAPI(title="Milo – AI Nutrition Analyzer")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Milo API running...", "stage": "Production Ready"}

@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    contents = await file.read()
    detections = detect_objects(contents)  # YOLO detection
    
    save_entry("image", file.filename, detections)

    result = save_analysis("image", file.filename, detections)
    firebase_id = result.get("id") if result and "id" in result else None
    # send event for async post-processing
    publish({
        "type": "image",
        "filename": file.filename,
        "data": detections,
        "firebase_id": firebase_id
    })
    
    return {"filename": file.filename, "detections": detections, "firebase_id": firebase_id}





@app.post("/predict/text")
async def predict_text(prompt: str = Form(...)):
    analysis = analyze_text(prompt)  # BitNet analysis
    
    save_entry("text", "prompt_input", analysis, prompt)

    result = save_analysis("text", "prompt_input", analysis, prompt)
    firebase_id = result.get("id") if result and "id" in result else None
    # send event for async post-processing
    publish({
        "type": "text",
        "filename": "prompt_input",
        "data": analysis,
        "prompt": prompt,
        "firebase_id": firebase_id
    })
    
    return {**analysis, "firebase_id": firebase_id}


@app.get("/history")
def history():
    return {"history": get_history()}

@app.get("/analyses")
def get_all():
    return get_all_analyses()

@app.get("/analyses/{analysis_id}")
def get_specific(analysis_id: str):
    result = get_analysis(analysis_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.put("/analyses/{analysis_id}")
def update_specific(analysis_id: str, update_data: dict):
    result = update_analysis(analysis_id, update_data)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.delete("/analyses/{analysis_id}")
def delete_specific(analysis_id: str):
    result = delete_analysis(analysis_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/analyses/type/{analysis_type}")
def get_by_type(analysis_type: str):
    if analysis_type not in ["image", "text"]:
        raise HTTPException(status_code=400, detail="Analysis type must be 'image' or 'text'")
    return get_analyses_by_type(analysis_type)

@app.get("/stats")
def stats():
    # monitoring endpoint using Firebase 
    all_analyses = get_all_analyses()
    return {
        "total_analyses": len(all_analyses.get("analyses", []))
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
