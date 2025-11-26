from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class CompletionRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    n_predict: int = Field(default=50, ge=1, le=2048)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stop: Optional[List[str]] = Field(default=None)
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()


class CompletionResponse(BaseModel):
    content: str
    stop: bool = True
    generated_text: str
    tokens_predicted: int = Field(..., ge=0)

