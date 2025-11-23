# 🚀 Quick Start - Despliegue en AWS EC2

Guía rápida para desplegar el LLM Feedback Service en AWS en menos de 10 minutos.

## Paso 1: Conectarse a tu instancia EC2

```bash
ssh -i tu-clave.pem ubuntu@tu-ip-ec2
```

## Paso 2: Instalar Git (si no está instalado)

```bash
sudo apt-get update
sudo apt-get install -y git
```

## Paso 3: Clonar el repositorio

```bash
cd /tmp
git clone <URL_DEL_REPOSITORIO> llm-service-temp
cd llm-service-temp
```

## Paso 4: Ejecutar instalación automática

```bash
chmod +x setup_aws.sh
./setup_aws.sh
```

Cuando te pida la URL del repositorio, ingresa la URL completa de tu repo.

## Paso 5: Configurar API Key

```bash
cd /opt/llm-service
nano .env
```

Busca esta línea:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

Reemplaza `your_google_api_key_here` con tu API Key real de Google Gemini.

**Obtén tu API Key aquí**: https://makersuite.google.com/app/apikey

Guarda: `Ctrl+O`, `Enter`, `Ctrl+X`

## Paso 6: Configurar y arrancar el servicio

```bash
# Ajustar usuario si no es 'ubuntu'
sudo nano llm-service.service  # Cambiar User y Group si es necesario

# Instalar servicio
sudo cp llm-service.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable llm-service
sudo systemctl start llm-service
```

## Paso 7: Verificar que funciona

```bash
# Ver estado
sudo systemctl status llm-service

# Ver logs
sudo journalctl -u llm-service -f

# Probar API
curl http://localhost:8003/
```

## ✅ ¡Listo!

Tu servicio está corriendo en: `http://tu-ip-ec2:8003`

**Documentación interactiva**: `http://tu-ip-ec2:8003/docs`

---

## 📝 Comandos Útiles

```bash
# Reiniciar servicio
sudo systemctl restart llm-service

# Ver logs en tiempo real
sudo journalctl -u llm-service -f

# Actualizar código
cd /opt/llm-service && ./deploy.sh
```

---

## 🔒 Security Group AWS

Asegúrate de abrir estos puertos:
- **22** (SSH)
- **80** (HTTP) - si usas Nginx
- **8003** (API) - si quieres acceso directo

---

## ❓ Problemas Comunes

### El servicio no arranca
```bash
sudo journalctl -u llm-service -n 50
```

Revisa que `GOOGLE_API_KEY` esté configurado correctamente en `/opt/llm-service/.env`

### Puerto 8003 bloqueado
Verifica el Security Group en la consola de AWS.

---

Para configuración avanzada (Nginx, HTTPS, dominios), consulta **DEPLOYMENT.md**.

