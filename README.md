# ✉️ Mensajero
Bot para cubrir todas vuestras necesidades de-sastrosas.


## Funciones
- Sistema de economía simple y robusto
- Sistema de tienda
- GAMBLING
- Hecho por un perrito estúpido.

## ¿Cómo instalarlo?
Si quieres encargarte del hosting del bot, puedes usar [Docker](https://www.docker.com):
1. Clona el repositorio de GitHub:

```bash
git clone
cd estanteria-bot
```


### Con Docker Compose
Esta es la forma preferente para instalar el bot:

2. Añade el siguiente fragmento de código a tu archivo `docker-compose.yml`:
```yaml
services:
  estanteria-bot:
    build: .
    container_name: estanteria-bot
    restart: unless-stopped
    volumes:
      - /home/misper/estanteria-bot-data:/app/data
    environment:
      - TOKEN = # (añade aquí la token de tu bot)
```
3. Ejecuta el siguiente comando:
```bash
docker compose up -d
```

### Con Docker (terminal de comandos)
2. Construye la imagen de Docker:
```bash
sudo docker build -t estanteria-bot:latest .
```

3. Instala el bot a través del siguiente comando:
```bash
sudo docker run -d \
  --name estanteria-bot \
  -e TOKEN= `Insertar token de tu bot` \
  --restart unless-stopped \
  estanteria-bot:latest
```


Si prefieres ahorrarte todo el proceso de preparar el hosting, puedes invitar al bot a través de este link:
<br>
[![Añadir a servidor](https://badgen.net/badge/icon/A%C3%B1adir%20a%20servidor?icon=discord&label&color=5865f2)](https://discord.com/oauth2/authorize?client_id=1384229875921191024)


[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)