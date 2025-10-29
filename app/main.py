from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header, Depends
from app.services.yolo_service import detect_objects
from app.services.bitnet_service import analyze_text
from app.services.firebase_service import save_analysis, get_analysis, get_all_analyses, update_analysis, delete_analysis, get_analyses_by_type
from app.services.database import init_db, save_entry, get_history
from app.services.queue import publish
from app.services.auth_service import get_bearer_token, verify_id_token
import uvicorn

# FastAPI app
app = FastAPI(title="Milo – AI Nutrition Analyzer (Stage 5)")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Milo API running...", "stage": "Stage 5: Firebase Integration"}


def get_current_user(authorization: str = Header(None)):
    # Firebase auth via ID token
    token = get_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    user = verify_id_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
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
async def predict_text(prompt: str = Form(...), user: dict = Depends(get_current_user)):
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


@app.get("/me")
def me(user: dict = Depends(get_current_user)):
    # simple current-user endpoint
    return {"user": user}


    

@app.get("/history")
def history(user: dict = Depends(get_current_user)):
    """Return local SQLite history of past requests (Stage 4)"""
    return {"history": get_history()}

@app.get("/analyses")
def get_all(user: dict = Depends(get_current_user)):
    """Get all analyses from Firebase"""
    return get_all_analyses()

@app.get("/analyses/{analysis_id}")
def get_specific(analysis_id: str, user: dict = Depends(get_current_user)):
    """Get specific analysis by ID"""
    result = get_analysis(analysis_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.put("/analyses/{analysis_id}")
def update_specific(analysis_id: str, update_data: dict, user: dict = Depends(get_current_user)):
    """Update analysis in Firebase"""
    result = update_analysis(analysis_id, update_data)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.delete("/analyses/{analysis_id}")
def delete_specific(analysis_id: str, user: dict = Depends(get_current_user)):
    """Delete analysis from Firebase"""
    result = delete_analysis(analysis_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/analyses/type/{analysis_type}")
def get_by_type(analysis_type: str, user: dict = Depends(get_current_user)):
    """Get analyses filtered by type (image or text)"""
    if analysis_type not in ["image", "text"]:
        raise HTTPException(status_code=400, detail="Analysis type must be 'image' or 'text'")
    return get_analyses_by_type(analysis_type)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
