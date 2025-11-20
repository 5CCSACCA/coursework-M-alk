import requests
import os

BITNET_URL = os.getenv("BITNET_URL", "http://localhost:8080/completion")

def analyze_text(prompt: str):
    try:
        full_prompt = f"Answer the following question directly and concisely.\n\nQuestion: {prompt}\n\nAnswer:"
        
        response = requests.post(
            BITNET_URL,
            json={
                "prompt": full_prompt,
                "n_predict": 15,
                "temperature": 0.7
            },
            timeout=60
        )
        if response.status_code == 200:
            output = response.json().get("content", "").strip()
            return {"input": prompt, "output": output, "model": "bitnet"}
        else:
            return {"input": prompt, "output": f"Server error", "model": "fallback"}
    except:
        return {"input": prompt, "output": "Model unavailable", "model": "fallback"}