import requests
import os

BITNET_URL = os.getenv("BITNET_URL", "http://localhost:8080/completion")

def _truncate_at_sentence(text: str) -> str:
    for end in ['.', '!', '?']:
        idx = text.rfind(end)
        if idx > len(text) // 2:
            return text[:idx + 1].strip()
    return text.strip()

def analyze_text(prompt: str):
    try:
        full_prompt = f"Answer the question briefly.\nQ: {prompt}\nA:"
        
        response = requests.post(
            BITNET_URL,
            json={
                "prompt": full_prompt,
                "n_predict": 50,
                "temperature": 0.7,
                "stop": ["\n\n", "Q:", "\nQ"]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            output = response.json().get("content", "").strip()
            output = _truncate_at_sentence(output)
            return {"input": prompt, "output": output, "model": "bitnet"}
        else:
            return {"input": prompt, "output": f"HTTP {response.status_code}", "model": "fallback"}
            
    except requests.exceptions.Timeout:
        return {"input": prompt, "output": "Request timeout", "model": "fallback"}
    except requests.exceptions.ConnectionError:
        return {"input": prompt, "output": "BitNet server not running", "model": "fallback"}
    except Exception as e:
        return {"input": prompt, "output": f"Error: {str(e)}", "model": "fallback"}

