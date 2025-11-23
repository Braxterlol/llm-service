"""
Google Gemini API Client
"""

import os
import asyncio
from typing import Optional
import google.generativeai as genai


class GeminiClient:
    """
    Cliente para interactuar con la API de Google Gemini.
    
    Maneja la comunicación con el modelo Gemini para generar
    feedback personalizado.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el cliente.
        
        Args:
            api_key: API key de Google (opcional, usa env var si no se provee)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY no encontrada. "
                "Configúrala en .env o pásala al constructor."
            )
        
        # Configurar Gemini
        genai.configure(api_key=self.api_key)
        
        # Probar modelos en orden de preferencia
        # Usar modelos estables con mejores límites de cuota
        model_names_to_try = [
            "models/gemini-2.5-pro",             # Pro - mejor cuota
            "models/gemini-pro-latest",          # Pro latest
            "models/gemini-2.5-flash-lite",      # Flash lite
            "models/gemini-flash-lite-latest",   # Flash lite latest
            "models/gemini-2.0-flash",           # Flash 2.0
        ]
        
        self.model = None
        self.model_name = None
        
        for model_name in model_names_to_try:
            try:
                self.model = genai.GenerativeModel(model_name)
                self.model_name = model_name
                print(f"✅ Usando modelo Gemini: {model_name}")
                break
            except Exception as e:
                continue
        
        if not self.model:
            raise ValueError(
                "No se pudo inicializar ningún modelo de Gemini. "
                "Ejecuta 'python list_gemini_models.py' para ver modelos disponibles."
            )
        
        # Configuración de generación
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
    
    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Genera una completion usando Gemini.
        
        Args:
            system_prompt: System prompt con instrucciones
            user_prompt: User prompt con el contexto específico
            temperature: Nivel de creatividad (0-1)
            max_tokens: Máximo de tokens (usa default si no se especifica)
        
        Returns:
            str: Respuesta generada por Gemini
        
        Raises:
            Exception: Si hay error en la API
        """
        try:
            # Combinar system y user prompt (Gemini no tiene system prompt separado)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Actualizar config si se especifican parámetros
            config = self.generation_config.copy()
            config["temperature"] = temperature
            if max_tokens:
                config["max_output_tokens"] = max_tokens
            
            # Ejecutar en thread pool para no bloquear
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._sync_generate(full_prompt, config)
            )
            return response
            
        except Exception as e:
            print(f"❌ Error en Gemini API: {e}")
            raise
    
    def _sync_generate(self, prompt: str, config: dict) -> str:
        """
        Genera completion de forma síncrona con retry limitado.
        
        Args:
            prompt: Prompt completo
            config: Configuración de generación
        
        Returns:
            str: Texto de la respuesta
        """
        import time
        
        # Configuración de safety para ser menos restrictivo
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        
        # Solo 2 intentos para respetar rate limit (2 req/min)
        max_attempts = 2
        
        for attempt in range(max_attempts):
            try:
                # Variar el prompt en el segundo intento
                current_prompt = prompt
                if attempt > 0:
                    # Esperar 2 segundos antes del reintento
                    time.sleep(2)
                    # Agregar variación simple
                    current_prompt = f"Generate original feedback:\n\n{prompt}"
                
                response = self.model.generate_content(
                    current_prompt,
                    generation_config=config,
                    safety_settings=safety_settings
                )
                
                # Intentar obtener el texto
                try:
                    if response.text:
                        return response.text
                except ValueError as e:
                    # Si falla, verificar por qué
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        finish_reason = candidate.finish_reason
                        
                        # Si es finish_reason 2 (RECITATION) y es el primer intento
                        if finish_reason == 2 and attempt == 0:
                            print(f"⚠️ Recitation detectado, reintentando con variación...")
                            continue
                        
                        # Registrar el error
                        if hasattr(response, 'prompt_feedback'):
                            print(f"⚠️ Prompt bloqueado: {response.prompt_feedback}")
                        
                        print(f"⚠️ Finish reason: {finish_reason}")
                        print(f"⚠️ Safety ratings: {candidate.safety_ratings}")
                        
                        # Intentar obtener contenido parcial
                        if hasattr(candidate, 'content') and candidate.content.parts:
                            partial_text = ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                            if partial_text:
                                return partial_text
                    
                    # Si es el segundo intento, lanzar error
                    if attempt == 1:
                        raise ValueError(f"Gemini no retornó contenido. Finish reason: {finish_reason}")
                    
            except Exception as e:
                if attempt == 0:
                    print(f"⚠️ Primer intento falló: {e}, reintentando...")
                    continue
                raise
        
        raise ValueError("No se pudo generar respuesta")
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con la API.
        
        Returns:
            bool: True si la conexión funciona
        """
        try:
            response = self.model.generate_content(
                "Hello, respond with 'OK'",
                generation_config={"max_output_tokens": 10}
            )
            return bool(response.text)
        except Exception as e:
            print(f"❌ Test de conexión falló: {e}")
            return False