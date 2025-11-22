# Milo AI Prediction Model - Stage 1

**Student:** Mohamed Ali Khalifa Alketbi  
**ID:** K22056537  
**Repository:** https://github.com/5CCSACCA/coursework-M-alk.git

## Overview

Detects food items in images using YOLO, then analyzes their health impact using BitNet.

## Models

- **YOLO (YOLOv11n)**: Object detection
- **BitNet (Microsoft)**: 1.58-bit LLM (2B params)

## Architecture

Microservices approach:
- YOLO runs locally
- BitNet runs as separate server
- Communication via HTTP

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start BitNet Server

```bash
./start_bitnet_server.sh
```

First run downloads model (~1.2GB) and sets up BitNet repo.

### 3. Run Test

In new terminal:

```bash
source venv/bin/activate
python tests/test_stage1.py
```

## Example Output

```
=== YOLO Detection ===
Detected: 21 objects (apples, oranges, bananas)
{
  "detections": [
    {
      "label": "apple",
      "confidence": 0.712
    },
    {
      "label": "orange",
      "confidence": 0.63
    },
    {
      "label": "banana",
      "confidence": 0.272
    },
  ],
  "total_objects": 21
}

Time: ~60ms

=== BitNet Analysis ===
Question: Are apple, banana, orange healthy or unhealthy foods?
Answer: All three fruits are generally considered healthy foods...
Time: ~7s
```
