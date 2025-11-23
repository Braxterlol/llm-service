"""
Prompt Templates para Feedback Generation
"""

from src.domain.models.analysis_context import AnalysisContext


# System Prompt - Instrucciones para GPT-4
SYSTEM_PROMPT = """Eres un asistente de terapia de habla para personas de 19 a 55 años.
Genera feedback motivador y específico sobre ejercicios de pronunciación.

Responde SOLO con un objeto JSON válido en este formato:
{
  "main_message": "mensaje motivacional breve",
  "strengths": ["fortaleza 1", "fortaleza 2"],
  "areas_to_improve": ["área a mejorar"],
  "specific_tip": "tip práctico y fácil de seguir",
  "celebration": "mensaje si pasó el ejercicio, o null si no pasó",
  "encouragement": "mensaje final de ánimo"
}

Reglas:
- Empieza siempre con algo positivo
- Sé específico (menciona pronunciación, fluidez o ritmo)
- Usa lenguaje simple y no técnico.
- Da UN tip concreto y accionable
- Si score >= 70: celebra el logro
- NO uses términos técnicos"""


def build_user_prompt(context: AnalysisContext) -> str:
    """
    Construye el user prompt con el contexto del análisis.
    
    Args:
        context: Contexto del análisis
    
    Returns:
        str: User prompt completo
    """
    
    prompt = f"""Ejercicio: {context.exercise_content}
Tipo: {_translate_exercise_type(context.exercise_type)}
Texto de referencia: "{context.reference_text}"

Scores obtenidos:
- Pronunciación: {context.pronunciation_score:.0f}/100
- Fluidez: {context.fluency_score:.0f}/100
- Ritmo: {context.rhythm_score:.0f}/100
- Score general: {context.overall_score:.0f}/100

Resultado: {'✅ PASÓ (necesitaba 70+)' if context.passed else '❌ No pasó (necesita 70+)'}
{'🎉 Desbloqueó el siguiente nivel' if context.unlocked_next else ''}

Genera feedback motivador en JSON."""
    
    return prompt.strip()


def _analyze_scores(context: AnalysisContext) -> str:
    """
    Analiza los scores y genera descripción para el LLM.
    
    Args:
        context: Contexto del análisis
    
    Returns:
        str: Análisis de scores
    """
    lines = ["ANÁLISIS DE SCORES:"]
    
    # Pronunciación
    if context.pronunciation_score >= 85:
        lines.append("- ✅ Pronunciación EXCELENTE - Muy claro y preciso")
    elif context.pronunciation_score >= 75:
        lines.append("- ✅ Pronunciación BUENA - Claro con algunos detalles a pulir")
    elif context.pronunciation_score >= 65:
        lines.append("- ⚠️ Pronunciación REGULAR - Necesita practicar claridad")
    elif context.pronunciation_score >= 50:
        lines.append("- ⚠️ Pronunciación BAJA - Requiere más práctica en sonidos específicos")
    else:
        lines.append("- ❌ Pronunciación MUY BAJA - Enfócate en pronunciar cada sonido despacio")
    
    # Fluidez
    if context.fluency_score >= 85:
        lines.append("- ✅ Fluidez EXCELENTE - Habla muy natural y continua")
    elif context.fluency_score >= 75:
        lines.append("- ✅ Fluidez BUENA - Habla bastante seguido con pocas pausas")
    elif context.fluency_score >= 65:
        lines.append("- ⚠️ Fluidez REGULAR - Hay algunas pausas o cortes")
    elif context.fluency_score >= 50:
        lines.append("- ⚠️ Fluidez BAJA - Muchas pausas, necesita practicar continuidad")
    else:
        lines.append("- ❌ Fluidez MUY BAJA - Habla muy cortado, practica decirlo de corrido")
    
    # Ritmo
    if context.rhythm_score >= 85:
        lines.append("- ✅ Ritmo EXCELENTE - Muy natural y con buena cadencia")
    elif context.rhythm_score >= 75:
        lines.append("- ✅ Ritmo BUENO - Natural con algunos detalles menores")
    elif context.rhythm_score >= 65:
        lines.append("- ⚠️ Ritmo REGULAR - Necesita trabajar la velocidad o musicalidad")
    elif context.rhythm_score >= 50:
        lines.append("- ⚠️ Ritmo BAJO - Muy lento o muy rápido, busca el punto medio")
    else:
        lines.append("- ❌ Ritmo MUY BAJO - Practica la velocidad y el tono")
    
    return "\n".join(lines)


def _build_progression_info(context: AnalysisContext) -> str:
    """
    Construye información de progresión.
    
    Args:
        context: Contexto del análisis
    
    Returns:
        str: Info de progresión
    """
    lines = ["PROGRESIÓN:"]
    
    if context.passed:
        lines.append(f"- ✅ ¡PASÓ EL EJERCICIO! (necesitaba 70+)")
        lines.append(f"- Estrellas ganadas: {context.stars_earned} ⭐")
        if context.unlocked_next:
            lines.append("- 🎉 ¡Desbloqueó el siguiente nivel!")
    else:
        lines.append(f"- ❌ No pasó todavía (necesita 70+, obtuvo {context.overall_score:.1f})")
        lines.append(f"- Estrellas: {context.stars_earned} ⭐")
        lines.append("- Intenta de nuevo para desbloquear el siguiente")
    
    return "\n".join(lines)


def _translate_exercise_type(exercise_type: str) -> str:
    """Traduce el tipo de ejercicio a texto legible"""
    translations = {
        "fonema": "Práctica de sonidos (fonemas)",
        "ritmo": "Práctica de ritmo y velocidad",
        "entonacion": "Práctica de entonación"
    }
    return translations.get(exercise_type, exercise_type)


def _translate_aspect(aspect: str) -> str:
    """Traduce el aspecto a español"""
    translations = {
        "pronunciation": "Pronunciación",
        "fluency": "Fluidez",
        "rhythm": "Ritmo"
    }
    return translations.get(aspect, aspect)