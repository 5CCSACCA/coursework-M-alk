from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

# BitNet model name
model_name = "microsoft/BitNet-b1.58-2B-4T"
tokenizer = None
model = None

def load_bitnet():
    """Load BitNet model"""
    global tokenizer, model
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        print(f"Loaded BitNet model: {model_name}")
        return True
    except Exception as e:
        print(f"Failed to load BitNet: {e}")
        return False

def analyze_text(prompt: str):
    """Run BitNet analysis on text"""
    global tokenizer, model
    
    if model is None:
        if not load_bitnet():
            return fallback_analysis(prompt)
    
    try:
        # Create nutrition-focused prompt
        system_prompt = "You are a nutrition expert. Analyze this meal description and provide health recommendations:"
        full_prompt = f"{system_prompt}\n\n{prompt}\n\nAnalysis:"
        
        # Tokenize input
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=512)
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_new_tokens=100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Extract analysis from response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        analysis_text = response.split("Analysis:")[-1].strip()
        
        return parse_bitnet_response(analysis_text, prompt)
        
    except Exception as e:
        print(f"BitNet inference failed: {e}")
        return fallback_analysis(prompt)

def parse_bitnet_response(response: str, original_prompt: str):
    """Parse BitNet response"""
    sentiment = "NEUTRAL"
    if any(word in response.lower() for word in ["good", "healthy", "great", "excellent", "nutritious"]):
        sentiment = "POSITIVE"
    elif any(word in response.lower() for word in ["bad", "unhealthy", "poor", "avoid", "unhealthy"]):
        sentiment = "NEGATIVE"
    
    food_keywords = ["chicken", "rice", "salad", "vegetables", "fruit", "meat", "fish", "pasta", "bread", "soup", "apple", "banana", "broccoli", "carrot"]
    mentioned_foods = [food for food in food_keywords if food.lower() in original_prompt.lower()]
    
    summary = f"BitNet analysis: {response[:100]}..."
    if mentioned_foods:
        summary += f" Detected foods: {', '.join(mentioned_foods)}"
    
    return {
        "summary": summary,
        "recommendation": response,
        "sentiment": sentiment,
        "confidence": 0.95,
        "detected_foods": mentioned_foods,
        "model": "BitNet-b1.58-2B-4T"
    }

def fallback_analysis(prompt: str):
    """Fallback analysis"""
    return {
        "summary": f"Basic analysis: {prompt[:50]}...",
        "recommendation": "Eat balanced meals with proteins and vitamins.",
        "sentiment": "NEUTRAL",
        "confidence": 0.5,
        "detected_foods": [],
        "model": "fallback"
    }