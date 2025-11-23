"""
Feedback API Routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from src.domain.models import AnalysisContext
from src.application.use_cases import GenerateFeedbackUseCase
from src.api.dependencies import get_generate_feedback_use_case


router = APIRouter(prefix="/feedback", tags=["Feedback"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class GenerateFeedbackRequest(BaseModel):
    """Request para generar feedback"""
    
    # Identificadores
    attempt_id: str = Field(..., description="ID del intento")
    user_id: str = Field(..., description="ID del usuario")
    exercise_id: str = Field(..., description="ID del ejercicio")
    
    # Scores del ML Service
    pronunciation_score: float = Field(..., ge=0, le=100, description="Score de pronunciación")
    fluency_score: float = Field(..., ge=0, le=100, description="Score de fluidez")
    rhythm_score: float = Field(..., ge=0, le=100, description="Score de ritmo")
    overall_score: float = Field(..., ge=0, le=100, description="Score general")
    
    # Información del ejercicio
    exercise_type: str = Field(..., description="Tipo: fonema, ritmo, entonacion")
    exercise_content: str = Field(..., description="Descripción del contenido")
    difficulty_level: int = Field(..., ge=1, le=5, description="Nivel de dificultad")
    reference_text: str = Field(..., description="Texto de referencia")
    
    # Información del usuario (opcional)
    user_age: Optional[int] = Field(None, ge=3, le=18, description="Edad del usuario")
    attempt_number: int = Field(1, ge=1, description="Número de intento")
    
    # Progresión
    passed: bool = Field(..., description="Si pasó el ejercicio (>= 70)")
    stars_earned: int = Field(..., ge=0, le=3, description="Estrellas ganadas")
    unlocked_next: bool = Field(..., description="Si desbloqueó siguiente nivel")
    
    # Contexto adicional (opcional)
    previous_best_score: Optional[float] = Field(None, ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "exercise_id": "fonema_r_suave_1",
                "pronunciation_score": 85.5,
                "fluency_score": 78.2,
                "rhythm_score": 92.0,
                "overall_score": 85.2,
                "exercise_type": "fonema",
                "exercise_content": "palabras con /r/ suave",
                "difficulty_level": 2,
                "reference_text": "raro, caro, pera, coro",
                "user_age": 7,
                "attempt_number": 3,
                "passed": True,
                "stars_earned": 2,
                "unlocked_next": True,
                "previous_best_score": 78.0
            }
        }


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class FeedbackResponse(BaseModel):
    """Response con el feedback generado"""
    
    main_message: str = Field(..., description="Mensaje principal motivacional")
    strengths: List[str] = Field(..., description="Fortalezas detectadas")
    areas_to_improve: List[str] = Field(..., description="Áreas a mejorar")
    specific_tip: str = Field(..., description="Tip específico y accionable")
    celebration: Optional[str] = Field(None, description="Mensaje de celebración")
    encouragement: str = Field(..., description="Mensaje de ánimo")
    tone: str = Field(..., description="Tono del feedback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "main_message": "¡Excelente trabajo! Tu pronunciación está mejorando mucho.",
                "strengths": [
                    "Tu ritmo fue muy natural, ¡casi perfecto!",
                    "La pronunciación de la /r/ suave estuvo muy bien"
                ],
                "areas_to_improve": [
                    "Intenta hablar un poquito más fluido, sin pausas largas"
                ],
                "specific_tip": "Practica diciendo la palabra completa de un solo golpe, sin detenerte en medio.",
                "celebration": "¡Desbloqueaste el siguiente nivel! 🎉",
                "encouragement": "¡Sigue así! Vas por muy buen camino.",
                "tone": "positive"
            }
        }


class HealthResponse(BaseModel):
    """Response del health check"""
    
    status: str
    service: str
    version: str
    azure_openai_api_connected: bool


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/generate", response_model=FeedbackResponse)
async def generate_feedback(
    request: GenerateFeedbackRequest
):
    """
    Genera feedback personalizado para un intento de ejercicio.
    
    Este es el endpoint principal del servicio. Recibe los scores
    del ML Service y genera feedback motivador y específico para el niño.
    
    Args:
        request: Datos del intento y scores
    
    Returns:
        FeedbackResponse: Feedback generado
    
    Raises:
        HTTPException: Si hay error en la generación
    """
    try:
        # Obtener use case
        use_case = get_generate_feedback_use_case()
        
        # Crear contexto de análisis
        context = AnalysisContext(
            attempt_id=request.attempt_id,
            user_id=request.user_id,
            exercise_id=request.exercise_id,
            pronunciation_score=request.pronunciation_score,
            fluency_score=request.fluency_score,
            rhythm_score=request.rhythm_score,
            overall_score=request.overall_score,
            exercise_type=request.exercise_type,
            exercise_content=request.exercise_content,
            difficulty_level=request.difficulty_level,
            reference_text=request.reference_text,
            user_age=request.user_age,
            attempt_number=request.attempt_number,
            passed=request.passed,
            stars_earned=request.stars_earned,
            unlocked_next=request.unlocked_next,
            previous_best_score=request.previous_best_score
        )
        
        # Generar feedback
        feedback = await use_case.execute(context)
        
        # Retornar response
        return FeedbackResponse(
            main_message=feedback.main_message,
            strengths=feedback.strengths,
            areas_to_improve=feedback.areas_to_improve,
            specific_tip=feedback.specific_tip,
            celebration=feedback.celebration,
            encouragement=feedback.encouragement,
            tone=feedback.tone
        )
        
    except ValueError as e:
        # Error de validación
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Error interno
        print(f"❌ Error en endpoint /feedback/generate: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando feedback: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check del servicio.
    
    Verifica que el servicio esté funcionando y que la
    conexión con OpenAI API esté disponible.
    
    Returns:
        HealthResponse: Estado del servicio
    """
    from src.infrastructure.config import get_settings
    from src.api.dependencies import get_azure_openai_client
    
    settings = get_settings()
    
    # Test conexión con OpenAI
    llm_connected = False
    try:
        azure_openai_client = get_azure_openai_client()
        llm_connected = azure_openai_client.test_connection()
    except Exception as e:
        print(f"⚠️ Health check - Azure OpenAI API no disponible: {e}")
    
    return HealthResponse(
        status="healthy" if llm_connected else "degraded",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        azure_openai_api_connected=llm_connected
    )