#!/bin/bash

# Script de configuración para instancia AWS EC2
# Este script instala todas las dependencias necesarias para el servicio LLM

set -e

echo "=========================================="
echo "LLM Feedback Service - AWS Setup"
echo "=========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que se ejecuta como usuario no root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}No ejecutar este script como root${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/7] Actualizando sistema...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo -e "${YELLOW}[2/7] Instalando Python 3.12 y dependencias...${NC}"
sudo apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    git \
    nginx \
    curl \
    wget

# Verificar instalación de Python
if ! command -v python3.12 &> /dev/null; then
    echo -e "${RED}Python 3.12 no se instaló correctamente${NC}"
    exit 1
fi

echo -e "${GREEN}Python $(python3.12 --version) instalado correctamente${NC}"

echo -e "${YELLOW}[3/7] Configurando directorio del servicio...${NC}"
SERVICE_DIR="/opt/llm-service"
sudo mkdir -p $SERVICE_DIR
sudo chown $USER:$USER $SERVICE_DIR

echo -e "${YELLOW}[4/7] Clonando repositorio...${NC}"
# Si el directorio ya existe y tiene contenido, hacer backup
if [ -d "$SERVICE_DIR/.git" ]; then
    echo "Directorio ya existe, actualizando..."
    cd $SERVICE_DIR
    git pull
else
    echo "Ingrese la URL del repositorio Git:"
    read REPO_URL
    git clone $REPO_URL $SERVICE_DIR
    cd $SERVICE_DIR
fi

echo -e "${YELLOW}[5/7] Creando entorno virtual...${NC}"
python3.12 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}[6/7] Instalando dependencias de Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}[7/7] Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Archivo .env creado. DEBES EDITARLO con tus credenciales:${NC}"
    echo "   nano .env"
    echo ""
    echo "   Específicamente, configura:"
    echo "   - GOOGLE_API_KEY: Tu API key de Google Gemini"
    echo "   - CORS_ORIGINS: Dominios permitidos en producción"
else
    echo -e "${GREEN}.env ya existe${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Instalación completada"
echo "==========================================${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Editar archivo de configuración:"
echo "   cd $SERVICE_DIR"
echo "   nano .env"
echo ""
echo "2. Probar el servicio manualmente:"
echo "   cd $SERVICE_DIR"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. Configurar como servicio systemd:"
echo "   sudo cp llm-service.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable llm-service"
echo "   sudo systemctl start llm-service"
echo ""
echo "4. Configurar Nginx (opcional, para HTTPS):"
echo "   sudo cp nginx-llm-service.conf /etc/nginx/sites-available/llm-service"
echo "   sudo ln -s /etc/nginx/sites-available/llm-service /etc/nginx/sites-enabled/"
echo "   sudo nginx -t"
echo "   sudo systemctl restart nginx"
echo ""

