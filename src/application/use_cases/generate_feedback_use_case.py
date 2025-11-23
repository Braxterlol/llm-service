"""
Generate Feedback Use Case
"""

import json
from typing import Optional
from src.domain.models import Feedback, AnalysisContext
from src.infrastructure.llm import SYSTEM_PROMPT, build_user_prompt


class GenerateFeedbackUseCase:
    """
    Use case para generar feedback personalizado usando LLM.
    
    Este es el caso de uso principal del servicio.
    Orquesta la generación de feedback usando un cliente LLM (Gemini, Claude, etc).
    """
    
    def __init__(self, llm_client):
        """
        Inicializa el use case.
        
        Args:
            llm_client: Cliente LLM (GeminiClient, ClaudeClient, etc)
        """
        self.llm_client = llm_client
    
    async def execute(self, context: AnalysisContext) -> Feedback:
        """
        Genera feedback personalizado para un intento.
        
        Args:
            context: Contexto del análisis con scores y metadata
        
        Returns:
            Feedback: Feedback generado por el LLM
        
        Raises:
            Exception: Si hay error en la generación
        """
        print(f"🎯 Generando feedback para attempt_id: {context.attempt_id}")
        print(f"   Scores: P={context.pronunciation_score:.1f}, "
              f"F={context.fluency_score:.1f}, R={context.rhythm_score:.1f}, "
              f"Overall={context.overall_score:.1f}")
        
        # USAR FALLBACK POR DEFECTO (más confiable y rápido)
        print(f"📝 Usando feedback algorítmico inteligente")
        feedback = self._generate_fallback_feedback(context)
        print(f"✨ Feedback generado exitosamente")
        return feedback
        
    #     # CÓDIGO PARA USAR LLM (GEMINI/OPENAI) - Descomenta para activar:
    #     """
    #     try:
    #         # 1. Construir prompts
    #         user_prompt = build_user_prompt(context)
            
    #         print(f"📝 Llamando a LLM API...")
            
    #         # 2. Llamar al LLM
    #         response = await self.llm_client.generate_completion(
    #             system_prompt=SYSTEM_PROMPT,
    #             user_prompt=user_prompt,
    #             temperature=0.7
    #         )
            
    #         print(f"✅ Respuesta recibida del LLM")
            
    #         # 3. Parsear respuesta JSON
    #         feedback_data = self._parse_llm_response(response)
            
    #         # 4. Determinar tono basado en score
    #         tone = self._determine_tone(context.overall_score)
            
    #         # 5. Crear modelo Feedback
    #         feedback = Feedback(
    #             main_message=feedback_data["main_message"],
    #             strengths=feedback_data["strengths"],
    #             areas_to_improve=feedback_data["areas_to_improve"],
    #             specific_tip=feedback_data["specific_tip"],
    #             celebration=feedback_data.get("celebration"),
    #             encouragement=feedback_data["encouragement"],
    #             tone=tone,
    #             model_used=getattr(self.llm_client, 'model_name', 'gemini-1.5-flash')
    #         )
            
    #         print(f"✨ Feedback generado exitosamente")
    #         return feedback
            
    #     except Exception as e:
    #         print(f"❌ Error generando feedback: {e}")
    #         print(f"⚠️ Usando feedback de fallback")
            
    #         # Fallback a feedback genérico
    #         return self._generate_fallback_feedback(context)
    
    # def _parse_llm_response(self, response: str) -> dict:
    #     """
    #     Parsea la respuesta del LLM (JSON de GPT-4/Gemini).
        
    #     Args:
    #         response: Respuesta raw del LLM
        
    #     Returns:
    #         dict: Datos del feedback parseados
        
    #     Raises:
    #         ValueError: Si no se puede parsear
    #     """
    #     try:
    #         # Limpiar respuesta
    #         response_clean = response.strip()
            
    #         # Remover markdown code blocks
    #         if "```json" in response_clean:
    #             # Extraer contenido entre ```json y ```
    #             start = response_clean.find("```json") + 7
    #             end = response_clean.find("```", start)
    #             response_clean = response_clean[start:end].strip()
    #         elif "```" in response_clean:
    #             # Remover ``` al inicio y final
    #             response_clean = response_clean.replace("```", "").strip()
            
    #         # Si empieza con {, buscar el JSON completo
    #         if response_clean.startswith("{"):
    #             # Encontrar el cierre del JSON
    #             brace_count = 0
    #             json_end = 0
    #             for i, char in enumerate(response_clean):
    #                 if char == '{':
    #                     brace_count += 1
    #                 elif char == '}':
    #                     brace_count -= 1
    #                     if brace_count == 0:
    #                         json_end = i + 1
    #                         break
                
    #             if json_end > 0:
    #                 response_clean = response_clean[:json_end]
            
    #         # Parsear JSON
    #         data = json.loads(response_clean)
            
    #         # Validar campos requeridos
    #         required = ["main_message", "strengths", "areas_to_improve", "specific_tip", "encouragement"]
    #         for key in required:
    #             if key not in data:
    #                 raise ValueError(f"Falta campo: {key}")
            
    #         return data
            
    #     except json.JSONDecodeError as e:
    #         print(f"⚠️ Error parseando JSON: {e}")
    #         print(f"Response limpio intentado: {response_clean[:300]}...")
            
    #         # Último intento: buscar manualmente el JSON
    #         try:
    #             start_idx = response.find('{')
    #             if start_idx >= 0:
    #                 # Contar llaves para encontrar el cierre
    #                 brace_count = 0
    #                 for i in range(start_idx, len(response)):
    #                     if response[i] == '{':
    #                         brace_count += 1
    #                     elif response[i] == '}':
    #                         brace_count -= 1
    #                         if brace_count == 0:
    #                             json_str = response[start_idx:i+1]
    #                             return json.loads(json_str)
    #         except:
    #             pass
            
    #         raise ValueError(f"Respuesta no es JSON válido: {e}")
    
    # def _determine_tone(self, overall_score: float) -> str:
    #     """
    #     Determina el tono apropiado basado en el score.
        
    #     Args:
    #         overall_score: Score general (0-100)
        
    #     Returns:
    #         str: Tono del feedback
    #     """
    #     if overall_score >= 80:
    #         return "positive"
    #     elif overall_score >= 60:
    #         return "encouraging"
    #     else:
    #         return "motivational"
    
    def _generate_fallback_feedback(self, context: AnalysisContext) -> Feedback:
        """
        Genera feedback genérico de fallback si Claude falla.
        
        Args:
            context: Contexto del análisis
        
        Returns:
            Feedback: Feedback genérico pero apropiado
        """
        
        # Determinar si pasó
        if context.passed:
            # Feedback positivo
            main_message = "¡Muy bien! Completaste el ejercicio."
            
            strengths = ["Hiciste un buen esfuerzo"]
            if context.overall_score >= 80:
                strengths.append("Tu pronunciación estuvo muy clara")
            
            areas_to_improve = []
            if context.overall_score < 90:
                areas_to_improve.append("Puedes seguir mejorando con más práctica")
            
            specific_tip = "Sigue practicando todos los días para mejorar aún más."
            
            celebration = None
            if context.unlocked_next:
                celebration = "¡Desbloqueaste el siguiente nivel! 🎉"
            
            encouragement = "¡Sigue así! Vas por muy buen camino."
            tone = "positive"
            
        else:
            # Feedback motivacional
            main_message = "¡Buen intento! Sigamos practicando."
            
            strengths = ["Lo importante es que lo intentaste"]
            
            # Identificar área más débil
            weakest = context.get_weakest_aspect()
            areas_to_improve = []
            
            if weakest == "pronunciation":
                areas_to_improve.append("Necesitas trabajar la claridad al pronunciar")
                specific_tip = "Intenta pronunciar cada sonido más despacio y claro."
            elif weakest == "fluency":
                areas_to_improve.append("Necesitas hablar más seguido, sin pausas largas")
                specific_tip = "Practica diciendo la frase completa de un solo golpe."
            else:  # rhythm
                areas_to_improve.append("Necesitas trabajar el ritmo y la velocidad")
                specific_tip = "Intenta hablar ni muy rápido ni muy lento, busca un punto medio."
            
            celebration = None
            encouragement = "¡No te rindas! Cada intento te acerca más a lograrlo."
            tone = "motivational"
        
        return Feedback(
            main_message=main_message,
            strengths=strengths,
            areas_to_improve=areas_to_improve,
            specific_tip=specific_tip,
            celebration=celebration,
            encouragement=encouragement,
            tone=tone
        )