import requests
import os

BITNET_URL = os.getenv("BITNET_URL", "http://localhost:8080/completion")

def analyze_text(prompt: str):
    try:
        full_prompt = f"Answer the question briefly.\nQ: {prompt}\nA:"
        
        response = requests.post(
            BITNET_URL,
            json={
                "prompt": full_prompt,
                "n_predict": 50,
                "temperature": 0.7,
                "stop": ["\n\n", "Q:"]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            output = response.json().get("content", "").strip()
            return {"input": prompt, "output": output, "model": "bitnet"}
        else:
            return {"input": prompt, "output": f"HTTP {response.status_code}", "model": "fallback"}
            
    except requests.exceptions.Timeout:
        return {"input": prompt, "output": "Request timeout", "model": "fallback"}
    except requests.exceptions.ConnectionError:
        return {"input": prompt, "output": "BitNet server not running", "model": "fallback"}
    except Exception as e:
        return {"input": prompt, "output": f"Error: {str(e)}", "model": "fallback"}

