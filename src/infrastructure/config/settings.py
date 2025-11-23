"""
Service Configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración del LLM Feedback Service.
    
    Lee variables de entorno y provee valores por defecto.
    """
    
    # Service Info
    SERVICE_NAME: str = "llm-feedback-service"
    SERVICE_VERSION: str = "1.0.0"
    
    # API Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    DEBUG: bool = False
    
    GOOGLE_API_KEY: Optional[str] = None
    
    # LLM Settings
    LLM_MAX_TOKENS: int = 1024
    LLM_TEMPERATURE: float = 0.7
    LLM_TIMEOUT_SECONDS: int = 10
    
    # CORS
    CORS_ORIGINS: str = "*"  # En producción usar dominios específicos
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins_list(self) -> list:
        """Convierte CORS_ORIGINS string a lista"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Singleton de settings
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Obtiene la instancia singleton de Settings.
    
    Returns:
        Settings: Configuración del servicio
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings