# Milo AI Prediction Model - Stage 1

**Student:** Mohamed Ali Khalifa Alketbi  
**ID:** K22056537  
**Repository:** https://github.com/5CCSACCA/coursework-M-alk.git

## Overview

Stage 1 implements two AI models with default parameters that work together to detect food items and analyze their health impact.

## Models

- **YOLO (YOLOv11n)**: Detects objects in images
- **BitNet (1.58-bit LLM)**: Analyzes text and answers questions

## How to Run

```bash
bash start_bitnet_server.sh

source venv/bin/activate
python tests/test_stage1.py
```

## Example Output

### YOLO Detection
Input: Image of fruits

```json
{
  "detections": [
    {"label": "apple", "confidence": 0.712},
    {"label": "orange", "confidence": 0.63},
    {"label": "banana", "confidence": 0.536}
  ],
  "total_objects": 21
}
```

### BitNet Analysis
Question: "Are banana, apple, orange healthy or unhealthy foods?"

Answer: "Bananas, apples, and oranges are all considered healthy foods."

**Performance:**
- YOLO: ~60-80ms
- BitNet: ~3-4s
