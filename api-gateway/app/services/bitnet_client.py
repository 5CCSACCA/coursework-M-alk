import os
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class BitNetClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or os.getenv("BITNET_URL", "http://bitnet:8080")).replace("/completion", "")
        self.mock_mode = os.getenv("BITNET_MOCK", "0") == "1"
    
    def is_healthy(self) -> bool:
        if self.mock_mode:
            return True
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate(self, prompt: str, n_predict: int = 50, temperature: float = 0.7, stop: Optional[list] = None) -> Dict[str, Any]:
        if self.mock_mode:
            return {
                "content": f"Test response: {prompt[:120]}",
                "stop": True,
                "generated_text": f"Test response: {prompt[:120]}",
                "tokens_predicted": len(prompt.split()) + 6
            }
        
        request_data = {
            "prompt": prompt,
            "n_predict": n_predict,
            "temperature": temperature,
        }
        if stop:
            request_data["stop"] = stop
        
        response = requests.post(
            f"{self.base_url}/completion",
            json=request_data,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"BitNet error: {response.text}")
        
        return response.json()

