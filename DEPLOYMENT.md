# Guía de Despliegue en AWS EC2

Esta guía te ayudará a desplegar el **LLM Feedback Service** en una instancia de AWS EC2.

## 📋 Requisitos Previos

### 1. Instancia EC2
- **Sistema Operativo**: Ubuntu 22.04 LTS o superior
- **Tipo de instancia recomendado**: t3.small o superior (mínimo 2GB RAM)
- **Almacenamiento**: Mínimo 20GB
- **Security Group**: Debe permitir:
  - Puerto 22 (SSH)
  - Puerto 80 (HTTP)
  - Puerto 443 (HTTPS) - opcional
  - Puerto 8003 (API) - si quieres acceso directo sin Nginx

### 2. Credenciales
- Clave SSH (.pem) para acceder a la instancia
- Google API Key para Gemini (obtener en [Google AI Studio](https://makersuite.google.com/app/apikey))

---

## 🚀 Proceso de Despliegue

### Paso 1: Conectarse a la Instancia EC2

```bash
ssh -i tu-clave.pem ubuntu@tu-ip-publica
```

### Paso 2: Clonar el Repositorio

```bash
cd /tmp
git clone <URL_DE_TU_REPOSITORIO> llm-service-temp
cd llm-service-temp
```

### Paso 3: Ejecutar Script de Instalación

```bash
chmod +x setup_aws.sh
./setup_aws.sh
```

Este script:
- ✅ Actualiza el sistema
- ✅ Instala Python 3.12 y dependencias
- ✅ Crea el directorio `/opt/llm-service`
- ✅ Configura el entorno virtual
- ✅ Instala las dependencias de Python
- ✅ Crea el archivo `.env` desde `.env.example`

### Paso 4: Configurar Variables de Entorno

```bash
cd /opt/llm-service
nano .env
```

**Variables críticas a configurar:**

```env
# OBLIGATORIO: Tu API Key de Google Gemini
GOOGLE_API_KEY=AIzaSy...

# Configuración del servidor
HOST=0.0.0.0
PORT=8003
DEBUG=False

# CORS - En producción, especifica tus dominios
CORS_ORIGINS=https://tu-dominio.com,https://app.tu-dominio.com

# Logging
LOG_LEVEL=INFO
```

Guarda con `Ctrl+O`, `Enter` y sal con `Ctrl+X`.

### Paso 5: Probar el Servicio Manualmente

Antes de configurar como servicio, prueba que funcione:

```bash
cd /opt/llm-service
source venv/bin/activate
python main.py
```

Deberías ver:
```
🚀 llm-feedback-service v1.0.0
   Listening on 0.0.0.0:8003
   Debug: False
   Docs: http://0.0.0.0:8003/docs
```

Prueba desde otra terminal:
```bash
curl http://localhost:8003/
```

Si funciona, presiona `Ctrl+C` para detener.

### Paso 6: Configurar como Servicio Systemd

```bash
# Ajustar el usuario en el archivo de servicio si no usas 'ubuntu'
sudo nano /opt/llm-service/llm-service.service
# Cambia User=ubuntu y Group=ubuntu si tu usuario es diferente

# Copiar archivo de servicio
sudo cp /opt/llm-service/llm-service.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable llm-service

# Iniciar el servicio
sudo systemctl start llm-service

# Verificar estado
sudo systemctl status llm-service
```

### Paso 7: Verificar que Funciona

```bash
# Ver logs en tiempo real
sudo journalctl -u llm-service -f

# Probar el endpoint
curl http://localhost:8003/
```

---

## 🔒 Configuración de Nginx (Opcional pero Recomendado)

Nginx actúa como proxy inverso y permite configurar HTTPS fácilmente.

### 1. Configurar Nginx

```bash
# Editar el archivo de configuración con tu dominio
sudo nano /opt/llm-service/nginx-llm-service.conf
# Cambia 'your-domain.com' por tu dominio real

# Copiar configuración
sudo cp /opt/llm-service/nginx-llm-service.conf /etc/nginx/sites-available/llm-service

# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/llm-service /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 2. Configurar DNS

En tu proveedor de DNS (Route 53, Cloudflare, etc.):
- Crea un registro A apuntando a la IP pública de tu instancia EC2

### 3. Obtener Certificado SSL (HTTPS)

```bash
# Instalar Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtener certificado (reemplaza con tu email y dominio)
sudo certbot --nginx -d tu-dominio.com

# El certificado se renovará automáticamente
```

Ahora descomentar la sección HTTPS en `/etc/nginx/sites-available/llm-service`:

```bash
sudo nano /etc/nginx/sites-available/llm-service
# Descomentar las secciones marcadas con "# Configuración HTTPS"
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔄 Actualizaciones y Despliegues

Para actualizar el código:

```bash
cd /opt/llm-service
./deploy.sh
```

Este script:
- ✅ Actualiza el código desde Git
- ✅ Instala nuevas dependencias
- ✅ Reinicia el servicio automáticamente

---

## 📊 Comandos Útiles

### Gestión del Servicio
```bash
# Ver estado
sudo systemctl status llm-service

# Iniciar
sudo systemctl start llm-service

# Detener
sudo systemctl stop llm-service

# Reiniciar
sudo systemctl restart llm-service

# Ver logs en tiempo real
sudo journalctl -u llm-service -f

# Ver últimos 100 logs
sudo journalctl -u llm-service -n 100
```

### Nginx
```bash
# Ver estado
sudo systemctl status nginx

# Reiniciar
sudo systemctl restart nginx

# Ver logs de acceso
sudo tail -f /var/log/nginx/llm-service-access.log

# Ver logs de errores
sudo tail -f /var/log/nginx/llm-service-error.log
```

### Monitoreo
```bash
# Ver uso de recursos
htop

# Ver procesos Python
ps aux | grep python

# Ver uso de puerto
sudo netstat -tlnp | grep 8003
```

---

## 🧪 Pruebas del API

### 1. Health Check
```bash
curl http://tu-dominio.com/
```

### 2. Documentación Interactiva
Abre en tu navegador:
```
http://tu-dominio.com/docs
```

### 3. Generar Feedback
```bash
curl -X POST http://tu-dominio.com/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "analysisContext": {
      "sessionId": "test-123",
      "timestamp": "2024-11-23T10:00:00Z",
      "metrics": {
        "fluency": 85.5,
        "pronunciation": 78.3,
        "vocabulary": 90.0
      }
    }
  }'
```

---

## 🔐 Security Group de AWS

Asegúrate de que tu Security Group tenga estas reglas:

| Tipo | Puerto | Origen | Descripción |
|------|--------|--------|-------------|
| SSH | 22 | Tu IP / 0.0.0.0/0 | Acceso SSH |
| HTTP | 80 | 0.0.0.0/0 | Tráfico HTTP |
| HTTPS | 443 | 0.0.0.0/0 | Tráfico HTTPS |
| Custom TCP | 8003 | 0.0.0.0/0 | API directo (opcional) |

**Recomendación de seguridad**: Restringe el puerto 22 (SSH) solo a tu IP.

---

## ⚠️ Troubleshooting

### El servicio no inicia
```bash
# Ver logs detallados
sudo journalctl -u llm-service -n 50 --no-pager

# Verificar permisos
ls -la /opt/llm-service/

# Verificar variables de entorno
cat /opt/llm-service/.env
```

### Error: GOOGLE_API_KEY no válido
```bash
# Editar .env y verificar la API Key
nano /opt/llm-service/.env

# Reiniciar servicio
sudo systemctl restart llm-service
```

### Nginx muestra 502 Bad Gateway
```bash
# Verificar que el servicio esté corriendo
sudo systemctl status llm-service

# Verificar que el puerto 8003 esté escuchando
sudo netstat -tlnp | grep 8003

# Ver logs de Nginx
sudo tail -f /var/log/nginx/llm-service-error.log
```

### Puerto 8003 ya en uso
```bash
# Ver qué proceso está usando el puerto
sudo lsof -i :8003

# Matar el proceso si es necesario
sudo kill -9 <PID>

# Reiniciar servicio
sudo systemctl restart llm-service
```

---

## 📈 Monitoreo y Mantenimiento

### Logs
Los logs del servicio se guardan en systemd journal:
```bash
sudo journalctl -u llm-service -f
```

### Rotación de Logs
Los logs de Nginx rotan automáticamente. Para systemd:
```bash
sudo nano /etc/systemd/journald.conf
# Configurar SystemMaxUse=1G
sudo systemctl restart systemd-journald
```

### Backups
Respalda regularmente:
```bash
# Variables de entorno
sudo cp /opt/llm-service/.env /opt/llm-service/.env.backup

# Configuraciones
sudo tar -czf llm-service-backup.tar.gz /opt/llm-service/.env /etc/nginx/sites-available/llm-service
```

---

## 🎯 Checklist de Despliegue

- [ ] Instancia EC2 creada y accesible por SSH
- [ ] Security Group configurado correctamente
- [ ] Script `setup_aws.sh` ejecutado exitosamente
- [ ] Archivo `.env` configurado con GOOGLE_API_KEY válido
- [ ] Servicio probado manualmente y funcionando
- [ ] Servicio systemd configurado y habilitado
- [ ] DNS configurado (si aplica)
- [ ] Nginx instalado y configurado (opcional)
- [ ] Certificado SSL obtenido (opcional)
- [ ] API funcionando y respondiendo correctamente
- [ ] Documentación accesible en `/docs`

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa los logs: `sudo journalctl -u llm-service -f`
2. Verifica la configuración: `cat /opt/llm-service/.env`
3. Consulta la documentación de la API: `http://tu-dominio.com/docs`

---

## 📚 Recursos Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Google Gemini API](https://ai.google.dev/docs)

