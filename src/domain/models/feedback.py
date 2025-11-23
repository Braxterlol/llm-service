"""
Feedback Domain Model
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Feedback:
    """
    Modelo de feedback generado por LLM.
    
    Representa el feedback personalizado que se le da al niño
    después de completar un ejercicio de habla.
    """
    
    # Mensaje principal motivacional
    main_message: str
    
    # Fortalezas detectadas (lo que hizo bien)
    strengths: List[str]
    
    # Áreas a mejorar
    areas_to_improve: List[str]
    
    # Tip específico y accionable
    specific_tip: str
    
    # Mensaje de celebración (si pasó el ejercicio)
    celebration: Optional[str] = None
    
    # Mensaje de ánimo final
    encouragement: str = ""
    
    # Tono del feedback
    tone: str = "encouraging"  # positive | encouraging | motivational
    
    # Metadata
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    model_used: str = "gemini-1.5-flash"
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para serialización"""
        return {
            "main_message": self.main_message,
            "strengths": self.strengths,
            "areas_to_improve": self.areas_to_improve,
            "specific_tip": self.specific_tip,
            "celebration": self.celebration,
            "encouragement": self.encouragement,
            "tone": self.tone,
            "generated_at": self.generated_at,
            "model_used": self.model_used
        }