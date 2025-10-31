from fastapi.testclient import TestClient
from app.main import app
import io
from PIL import Image

client = TestClient(app)


def test_predict_text(monkeypatch):
    # stub model to skip heavy load
    def fake_analyze_text(prompt: str):
        return {
            "summary": f"stub: {prompt}",
            "recommendation": "ok",
            "sentiment": "NEUTRAL",
            "confidence": 0.9,
            "detected_foods": [],
            "model": "test",
        }
    
    import app.main as main_module
    monkeypatch.setattr(main_module, "analyze_text", fake_analyze_text)
    
    resp = client.post("/predict/text", data={"prompt": "salad"})
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "recommendation" in data


def test_predict_image(monkeypatch):
    # stub detector
    def fake_detect_objects(_):
        return {
            "detections": [{"label": "salad", "confidence": 0.99, "is_food": True, "health_status": "healthy"}],
            "food_items": ["salad"],
            "non_food_items": [],
            "nutrition_summary": "ok",
            "total_foods": 1,
            "total_objects": 1,
        }
    
    import app.main as main_module
    monkeypatch.setattr(main_module, "detect_objects", fake_detect_objects)
    
    # tiny fake image
    img = Image.new("RGB", (2, 2))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    
    resp = client.post("/predict/image", files={"file": ("test.jpg", buf, "image/jpeg")})
    assert resp.status_code == 200
    data = resp.json()
    assert "filename" in data
    assert "detections" in data


