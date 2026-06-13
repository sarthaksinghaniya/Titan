"""
Input Validation & Sanitization for TITAN
==========================================
Prevents prompt injection attacks and validates user input.
"""
from typing import Optional
import re
from pydantic import BaseModel, validator, Field


class ProblemInputRequest(BaseModel):
    """Validated problem submission request."""
    
    problem: str = Field(
        ..., 
        min_length=20,
        max_length=5000,
        description="The governance problem to analyze"
    )
    context: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional context or constraints"
    )

    @validator('problem')
    def validate_problem(cls, v: str) -> str:
        """Sanitize and validate problem text."""
        # Strip whitespace
        v = v.strip()
        
        # Check length again
        if len(v) < 20 or len(v) > 5000:
            raise ValueError("Problem must be between 20 and 5000 characters")
        
        # Remove suspicious characters that could indicate injection
        suspicious_patterns = [
            r'<script',  # Script tags
            r'javascript:',  # JS protocol
            r'on\w+\s*=',  # Event handlers
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Problem contains potentially unsafe content")
        
        # Normalize whitespace (collapse multiple spaces)
        v = re.sub(r'\s+', ' ', v)
        
        return v

    @validator('context')
    def validate_context(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize and validate context text."""
        if v is None:
            return v
        
        v = v.strip()
        
        if not v:
            return None
        
        if len(v) > 2000:
            raise ValueError("Context must not exceed 2000 characters")
        
        # Same injection checks as problem
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'on\w+\s*=',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Context contains potentially unsafe content")
        
        v = re.sub(r'\s+', ' ', v)
        
        return v


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """
    General-purpose text sanitization.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        ValueError: If text is unsafe or too long
    """
    text = text.strip()
    
    if not text:
        raise ValueError("Text cannot be empty")
    
    if len(text) > max_length:
        raise ValueError(f"Text exceeds maximum length of {max_length}")
    
    # Remove control characters (except newline, tab)
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text
