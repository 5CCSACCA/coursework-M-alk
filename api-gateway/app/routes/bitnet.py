import logging
from fastapi import APIRouter, HTTPException, status
from ..models import CompletionRequest, CompletionResponse
from ..services import BitNetClient
from ..utils import clean_response, is_low_quality_response

router = APIRouter()
logger = logging.getLogger(__name__)

bitnet_client = BitNetClient()


@router.post("/completion", response_model=CompletionResponse, status_code=200)
async def completion(request: CompletionRequest):
    try:
        if not bitnet_client.is_healthy():
            raise HTTPException(status_code=503, detail="BitNet service unavailable")
        
        result = bitnet_client.generate(
            prompt=request.prompt,
            n_predict=request.n_predict,
            temperature=request.temperature,
            stop=request.stop
        )
        
        content = result.get("content", "") or result.get("text", "") or result.get("generated_text", "")
        
        if not content:
            raise HTTPException(status_code=502, detail="Empty response from model")
        
        content = clean_response(content, prompt=request.prompt)
        
        if is_low_quality_response(content):
            raise HTTPException(status_code=502, detail="Low quality response generated")
        
        tokens = result.get("tokens_predicted", len(content.split()))
        if not isinstance(tokens, int):
            tokens = len(content.split())
        
        response_data = CompletionResponse(
            content=content,
            stop=result.get("stop", True),
            generated_text=content,
            tokens_predicted=tokens
        )
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"BitNet completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

