"""
Milo AI Unified API - Stage 3

FastAPI server exposing BitNet and YOLO models.
Author: Mohamed Alketbi
"""
import argparse
import json
import logging
import os
import re
import signal
import sys
import subprocess
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from services.yolo.yolo_service import detect_objects
    YOLO_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import YOLO service: {e}")
    YOLO_AVAILABLE = False

# Mock mode to keep deployment lightweight
BITNET_MOCK = os.getenv("BITNET_MOCK", "1") == "1"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompletionRequest(BaseModel):
    """BitNet text generation request"""
    prompt: str = Field(..., min_length=1, max_length=10000, description="Text prompt")
    n_predict: int = Field(default=50, ge=1, le=2048, description="Max tokens")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    stop: Optional[List[str]] = Field(default=None, description="Stop sequences")
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class CompletionResponse(BaseModel):
    """BitNet generation response"""
    content: str = Field(..., description="Generated text")
    stop: bool = Field(default=True, description="Stopped naturally")
    generated_text: str = Field(..., description="Generated text (alias)")
    tokens_predicted: int = Field(..., ge=0, description="Token count")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="BitNet ready")
    llama_server_running: bool = Field(default=False, description="llama-server status")
    yolo_available: bool = Field(default=False, description="YOLO status")


app = FastAPI(
    title="Milo AI Unified API",
    description="RESTful API for BitNet (Text) and YOLO (Vision) models",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llama_server_process: Optional[subprocess.Popen] = None
llama_server_port: int = 8080
model_path: Optional[str] = None


def start_llama_server(model_path: str, port: int = 8080, threads: int = 4, ctx_size: int = 1024):
    """Start llama-server binary as a subprocess."""
    global llama_server_process
    
    bitnet_dir = PROJECT_ROOT / "BitNet"
    llama_server_bin = bitnet_dir / "build" / "bin" / "llama-server"
    
    if not llama_server_bin.exists():
        possible_paths = [
             PROJECT_ROOT / "BitNet" / "build" / "bin" / "llama-server",
             Path("BitNet/build/bin/llama-server").absolute()
        ]
        for p in possible_paths:
            if p.exists():
                llama_server_bin = p
                bitnet_dir = p.parent.parent.parent
                break
    
    if not llama_server_bin.exists():
        raise FileNotFoundError(
            f"llama-server binary not found. Please build BitNet first."
        )
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    cmd = [
        str(llama_server_bin),
        "-m", model_path,
        "--port", str(port),
        "-t", str(threads),
        "-c", str(ctx_size),
        "--host", "127.0.0.1"
    ]
    
    logger.info(f"Starting llama-server: {' '.join(cmd)}")
    
    llama_server_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(bitnet_dir)
    )
    
    time.sleep(2)
    
    if llama_server_process.poll() is not None:
        stderr = llama_server_process.stderr.read().decode() if llama_server_process.stderr else ""
        raise RuntimeError(f"Failed to start llama-server: {stderr}")
    
    return llama_server_process


def stop_llama_server():
    """Stop llama-server process"""
    global llama_server_process
    if llama_server_process:
        llama_server_process.terminate()
        try:
            llama_server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            llama_server_process.kill()
        llama_server_process = None


def _is_low_quality_response(content: str) -> bool:
    """Filter out bad LLM outputs"""
    if not content or len(content.strip()) < 3:
        return True
    
    content_lower = content.lower()
    
    lines = content.split('\n')
    question_lines = sum(1 for line in lines if line.strip().endswith('?') and len(line.strip()) < 100)
    if question_lines >= 3 and len(lines) < 20:
        logger.warning("Detected question-spamming pattern")
        return True
    
    numbered_lines = sum(1 for line in lines if line.strip().startswith('- ') or 
                        (line.strip() and line.strip()[0].isdigit() and 
                         (line.strip().startswith('1') or line.strip().startswith('2'))))
    if numbered_lines > 5 and len(lines) < 15:
        return True
    
    if '|' in content and ('comment' in content_lower or 
                           any(char.isdigit() for char in content if '-' in content)):
        if content.count('|') >= 2 and ('comment' in content_lower or 
                                        any(part.strip().count('-') == 2 for part in content.split('|'))):
            return True
    
    return False


def _clean_response(content: str, prompt: str = "") -> str:
    """Clean up LLM output"""
    content = content.strip()
    
    a_marker_match = re.search(r'(?:^|\n)(?:A:|Answer:)\s*', content, re.IGNORECASE)
    if a_marker_match:
        content = content[a_marker_match.end():].strip()
    
    if prompt and len(prompt) > 5:
        prompt_clean = prompt.strip()
        if content.startswith(prompt_clean):
            content = content[len(prompt_clean):].strip()
        
        first_line = content.split('\n')[0]
        if first_line in prompt_clean or prompt_clean in first_line:
             pass

    content = re.sub(r'^\s*\|\s*\d{1,2}-\d{1,2}-\d{4}\s*\|\s*\d+\s*[Cc]omments?\s*', '', content)
    
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        line_stripped = line.strip()
        if line_stripped and not (
            line_stripped.startswith('- ') and len(line_stripped) < 10 or
            (line_stripped.count('|') >= 2 and 'comment' in line_stripped.lower()) or
            (line_stripped.isdigit() and len(line_stripped) < 3) or
            (len(line_stripped) < 5 and '?' in line_stripped)
        ):
            cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines).strip()
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r' {2,}', ' ', content)
    
    return content.strip()


@app.on_event("startup")
async def startup_event():
    """Start llama-server on FastAPI startup."""
    global model_path, llama_server_port
    
    if BITNET_MOCK:
        logger.info("BITNET_MOCK=1 set, skipping llama-server startup.")
        return
    
    # Check if llama-server is already running
    try:
        import requests
        response = requests.get(f"http://127.0.0.1:{llama_server_port}/health", timeout=2)
        if response.status_code == 200:
            logger.info(f"Using existing llama-server on port {llama_server_port}")
            return
    except:
        pass
    
    if model_path:
        logger.info(f"Starting llama-server with model: {model_path}")
        try:
            start_llama_server(
                model_path=model_path,
                port=llama_server_port,
                threads=4,
                ctx_size=1024
            )
            logger.info(f"llama-server started on port {llama_server_port}")
        except Exception as e:
            logger.error(f"Warning: Could not start llama-server: {e}")
    else:
        logger.info(f"Using existing llama-server on port {llama_server_port}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop llama-server on FastAPI shutdown."""
    if BITNET_MOCK:
        return
    logger.info("Stopping llama-server...")
    stop_llama_server()


@app.get("/", response_model=dict, status_code=status.HTTP_200_OK)
async def root():
    """API information endpoint."""
    return {
        "service": "Milo AI Unified API",
        "version": "1.0",
        "framework": "FastAPI",
        "endpoints": {
            "POST /bitnet/completion": "Generate text completion (BitNet)",
            "POST /yolo/detect": "Detect objects in image (YOLO)",
            "GET /health": "Check service health",
            "GET /docs": "Interactive API documentation"
        },
        "models": {
            "bitnet": "BitNet-b1.58-2B-4T",
            "yolo": "YOLOv11n"
        }
    }


@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """Health check"""
    global llama_server_process, llama_server_port
    
    bitnet_running = (llama_server_process is not None and llama_server_process.poll() is None)
    bitnet_healthy = False
    if BITNET_MOCK:
        bitnet_running = True
        bitnet_healthy = True
    else:
        try:
            import requests
            response = requests.get(f"http://127.0.0.1:{llama_server_port}/health", timeout=2)
            bitnet_healthy = response.status_code == 200
        except:
            bitnet_healthy = False
    
    return HealthResponse(
        status="ok" if (bitnet_running or bitnet_healthy or BITNET_MOCK) and YOLO_AVAILABLE else "degraded",
        model_loaded=(bitnet_running or bitnet_healthy or BITNET_MOCK),
        llama_server_running=(bitnet_running or bitnet_healthy or BITNET_MOCK),
        yolo_available=YOLO_AVAILABLE
    )


@app.post("/bitnet/completion", response_model=CompletionResponse, tags=["BitNet"])
async def completion(request: CompletionRequest):
    """BitNet text generation"""
    global llama_server_port

    if BITNET_MOCK:
        content = f"Mock response for: {request.prompt[:120]}"
        tokens = len(content.split())
        return CompletionResponse(
            content=content,
            stop=True,
            generated_text=content,
            tokens_predicted=tokens
        )
    
    try:
        import requests
        
        try:
            health = requests.get(f"http://127.0.0.1:{llama_server_port}/health", timeout=2)
            if health.status_code != 200:
                raise HTTPException(status_code=503, detail="BitNet model server unhealthy")
        except:
             raise HTTPException(status_code=503, detail="BitNet model server unavailable")

        llama_request = {
            "prompt": request.prompt,
            "n_predict": request.n_predict,
            "temperature": request.temperature,
        }
        if request.stop:
            llama_request["stop"] = request.stop
            
        try:
            response = requests.post(
                f"http://127.0.0.1:{llama_server_port}/completion",
                json=llama_request,
                timeout=120
            )
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Model server timed out")
            
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Model error: {response.text}")
            
        result = response.json()
        content = result.get("content", "") or result.get("text", "") or result.get("generated_text", "")
        
        if not content:
            raise HTTPException(status_code=502, detail="Empty response from model")
            
        content = _clean_response(content, prompt=request.prompt)
        
        if _is_low_quality_response(content):
             raise HTTPException(status_code=502, detail="Low quality response generated")
             
        tokens = result.get("tokens_predicted", len(content.split()))
        if not isinstance(tokens, int): tokens = len(content.split())
        
        return CompletionResponse(
            content=content,
            stop=result.get("stop", True),
            generated_text=content,
            tokens_predicted=tokens
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/yolo/detect", tags=["YOLO"])
async def detect_objects_endpoint(file: UploadFile = File(...)):
    """YOLO object detection"""
    if not YOLO_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YOLO service is not available"
        )
    
    try:
        contents = await file.read()
        result = detect_objects(contents)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        logger.error(f"YOLO error: {e}")
        raise HTTPException(status_code=500, detail=f"YOLO processing error: {str(e)}")


def main():
    """Start API server"""
    global model_path, llama_server_port
    
    parser = argparse.ArgumentParser(description='Milo AI Unified API Server')
    parser.add_argument("-m", "--model", type=str, required=True, help="BitNet model path")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    parser.add_argument("--llama-port", type=int, default=8080, help="llama-server port")
    
    args = parser.parse_args()
    
    model_path = os.path.abspath(args.model)
    llama_server_port = args.llama_port
    
    import uvicorn
    print(f"Starting Milo AI Unified API on http://{args.host}:{args.port}")
    print(f"BitNet Model: {model_path}")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
