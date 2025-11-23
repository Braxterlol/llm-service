#!/bin/bash

# Script de despliegue para LLM Feedback Service
# Este script actualiza el código y reinicia el servicio

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVICE_NAME="llm-service"
SERVICE_DIR="/opt/llm-service"

echo -e "${BLUE}=========================================="
echo "LLM Feedback Service - Despliegue"
echo "==========================================${NC}"

# Verificar que existe el directorio
if [ ! -d "$SERVICE_DIR" ]; then
    echo -e "${RED}Error: Directorio $SERVICE_DIR no existe${NC}"
    echo "Ejecuta primero setup_aws.sh"
    exit 1
fi

cd $SERVICE_DIR

echo -e "${YELLOW}[1/6] Verificando estado del servicio...${NC}"
if systemctl is-active --quiet $SERVICE_NAME; then
    SERVICE_WAS_RUNNING=true
    echo -e "${GREEN}Servicio está corriendo${NC}"
else
    SERVICE_WAS_RUNNING=false
    echo -e "${YELLOW}Servicio no está corriendo${NC}"
fi

echo -e "${YELLOW}[2/6] Actualizando código desde repositorio...${NC}"
git fetch origin
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Branch actual: $CURRENT_BRANCH"

# Guardar cambios locales si existen
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}Hay cambios locales, creando stash...${NC}"
    git stash
fi

git pull origin $CURRENT_BRANCH

echo -e "${YELLOW}[3/6] Activando entorno virtual...${NC}"
source venv/bin/activate

echo -e "${YELLOW}[4/6] Actualizando dependencias...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}[5/6] Verificando configuración...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}Error: Archivo .env no existe${NC}"
    echo "Copia .env.example a .env y configura las variables necesarias"
    exit 1
fi

# Verificar que GOOGLE_API_KEY está configurado
if ! grep -q "GOOGLE_API_KEY=your_google_api_key_here" .env; then
    echo -e "${GREEN}GOOGLE_API_KEY configurado${NC}"
else
    echo -e "${RED}Error: GOOGLE_API_KEY no está configurado en .env${NC}"
    exit 1
fi

echo -e "${YELLOW}[6/6] Reiniciando servicio...${NC}"
if [ "$SERVICE_WAS_RUNNING" = true ]; then
    sudo systemctl restart $SERVICE_NAME
    echo -e "${GREEN}Servicio reiniciado${NC}"
else
    echo "¿Deseas iniciar el servicio? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        sudo systemctl start $SERVICE_NAME
        echo -e "${GREEN}Servicio iniciado${NC}"
    fi
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Despliegue completado"
echo "==========================================${NC}"
echo ""

# Mostrar estado del servicio
echo "Estado del servicio:"
sudo systemctl status $SERVICE_NAME --no-pager

echo ""
echo "Comandos útiles:"
echo "  Ver logs:        sudo journalctl -u $SERVICE_NAME -f"
echo "  Detener:         sudo systemctl stop $SERVICE_NAME"
echo "  Iniciar:         sudo systemctl start $SERVICE_NAME"
echo "  Reiniciar:       sudo systemctl restart $SERVICE_NAME"
echo "  Ver estado:      sudo systemctl status $SERVICE_NAME"

