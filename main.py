from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.config import get_settings
from src.api.routes import feedback_router


# Obtener configuración
settings = get_settings()

# Crear app FastAPI
app = FastAPI(
    title="LLM Feedback Service",
    description="Servicio de generación de feedback personalizado usando LLM para Vocalis",
    version=settings.SERVICE_VERSION,
    debug=settings.DEBUG
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(feedback_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "running",
        "docs": "/docs"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Evento de inicio"""
    print(f"🚀 {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    print(f"   Listening on {settings.HOST}:{settings.PORT}")
    print(f"   Debug: {settings.DEBUG}")
    print(f"   Docs: http://{settings.HOST}:{settings.PORT}/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre"""
    print(f"👋 Shutting down {settings.SERVICE_NAME}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )