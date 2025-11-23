"""
Analysis Context Domain Model
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AnalysisContext:
    """
    Contexto completo para generar feedback personalizado.
    
    Contiene toda la información necesaria para que el LLM
    genere un feedback apropiado y específico.
    """
    
    # Identificadores
    attempt_id: str
    user_id: str
    exercise_id: str
    
    # Scores del ML Service
    pronunciation_score: float  # 0-100
    fluency_score: float  # 0-100
    rhythm_score: float  # 0-100
    overall_score: float  # 0-100
    
    # Información del ejercicio
    exercise_type: str  # "fonema" | "ritmo" | "entonacion"
    exercise_content: str  # "palabras con /r/"
    difficulty_level: int  # 1-5
    reference_text: str  # Texto que debía pronunciar
    
    # Información del usuario
    user_age: Optional[int] = None
    attempt_number: int = 1
    
    # Progresión (del sistema de niveles)
    passed: bool = False  # True si overall_score >= 70
    stars_earned: int = 0  # 0-3 estrellas
    unlocked_next: bool = False
    
    # Contexto adicional (opcional)
    weak_areas: List[str] = field(default_factory=list)
    strong_areas: List[str] = field(default_factory=list)
    previous_best_score: Optional[float] = None
    
    def __post_init__(self):
        """Validaciones post-inicialización"""
        # Validar scores
        if not (0 <= self.pronunciation_score <= 100):
            raise ValueError("pronunciation_score debe estar entre 0 y 100")
        if not (0 <= self.fluency_score <= 100):
            raise ValueError("fluency_score debe estar entre 0 y 100")
        if not (0 <= self.rhythm_score <= 100):
            raise ValueError("rhythm_score debe estar entre 0 y 100")
        if not (0 <= self.overall_score <= 100):
            raise ValueError("overall_score debe estar entre 0 y 100")
        
        # Validar difficulty_level
        if not (1 <= self.difficulty_level <= 5):
            raise ValueError("difficulty_level debe estar entre 1 y 5")
        
        # Validar exercise_type
        valid_types = ["fonema", "ritmo", "entonacion"]
        if self.exercise_type not in valid_types:
            raise ValueError(f"exercise_type debe ser uno de: {valid_types}")
        
        # Validar stars
        if not (0 <= self.stars_earned <= 3):
            raise ValueError("stars_earned debe estar entre 0 y 3")
    
    def get_score_category(self) -> str:
        """
        Retorna la categoría del score general.
        
        Returns:
            str: "excellent" | "great" | "good" | "needs_practice" | "try_again"
        """
        if self.overall_score >= 90:
            return "excellent"
        elif self.overall_score >= 80:
            return "great"
        elif self.overall_score >= 70:
            return "good"
        elif self.overall_score >= 50:
            return "needs_practice"
        else:
            return "try_again"
    
    def get_weakest_aspect(self) -> str:
        """
        Identifica el aspecto más débil.
        
        Returns:
            str: "pronunciation" | "fluency" | "rhythm"
        """
        scores = {
            "pronunciation": self.pronunciation_score,
            "fluency": self.fluency_score,
            "rhythm": self.rhythm_score
        }
        return min(scores, key=scores.get)
    
    def get_strongest_aspect(self) -> str:
        """
        Identifica el aspecto más fuerte.
        
        Returns:
            str: "pronunciation" | "fluency" | "rhythm"
        """
        scores = {
            "pronunciation": self.pronunciation_score,
            "fluency": self.fluency_score,
            "rhythm": self.rhythm_score
        }
        return max(scores, key=scores.get)
    
    def has_improved(self) -> bool:
        """
        Verifica si mejoró respecto al intento anterior.
        
        Returns:
            bool: True si mejoró
        """
        if self.previous_best_score is None:
            return False
        return self.overall_score > self.previous_best_score