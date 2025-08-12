from typing import Optional
from pydantic import BaseModel, Field


class PromptLayout(BaseModel):
    """Controls the layout of a response line."""
    padding: int = Field(default=0, ge=0)
    margin: int = Field(default=0, ge=0)
    width: Optional[int] = Field(default=None, gt=0)
    
    def apply_to_text(self, text: str) -> str:
        """Apply layout settings to text."""
        result = text
        
        # Apply padding
        if self.padding > 0:
            result = " " * self.padding + result + " " * self.padding
            
        # Apply margin
        if self.margin > 0:
            result = " " * self.margin + result + " " * self.margin
            
        # Apply width by truncating or padding
        if self.width is not None:
            if len(result) > self.width:
                result = result[:self.width-3] + "..."
            else:
                result = result.ljust(self.width)
                
        return result
