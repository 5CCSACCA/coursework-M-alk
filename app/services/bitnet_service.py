from transformers import pipeline
import os

# Initialize sentiment analysis pipeline (lightweight model for 4 CPU/16GB constraint)
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_text(prompt: str):
    """
    Analyze text using a lightweight transformer model for nutrition recommendations.
    Uses sentiment analysis to understand meal descriptions and provide recommendations.
    """
    try:
        # Analyze sentiment of the meal description
        sentiment_result = sentiment_analyzer(prompt)
        sentiment = sentiment_result[0]['label']
        confidence = sentiment_result[0]['score']
        
        # Generate nutrition-focused recommendations based on sentiment
        if sentiment == "POSITIVE":
            recommendation = "Great choice! Continue with balanced meals including proteins, vegetables, and whole grains."
        else:
            recommendation = "Consider adding more nutritious options like fresh vegetables, lean proteins, or whole grains to your meal."
        
        # Extract key food items mentioned
        food_keywords = ["chicken", "rice", "salad", "vegetables", "fruit", "meat", "fish", "pasta", "bread", "soup"]
        mentioned_foods = [food for food in food_keywords if food.lower() in prompt.lower()]
        
        summary = f"Meal analysis: {sentiment.lower()} sentiment (confidence: {confidence:.2f})"
        if mentioned_foods:
            summary += f". Detected foods: {', '.join(mentioned_foods)}"
        
        return {
            "summary": summary,
            "recommendation": recommendation,
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "detected_foods": mentioned_foods
        }
        
    except Exception as e:
        # Fallback to simple analysis if model fails
        return {
            "summary": f"Text analysis: {prompt[:50]}...",
            "recommendation": "Eat balanced meals with proteins and vitamins.",
            "sentiment": "NEUTRAL",
            "confidence": 0.5,
            "detected_foods": [],
            "error": str(e)
        }