# Setup del constructor
FROM python:3.12-alpine AS builder
WORKDIR /app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-compile --no-cache-dir --user -r requirements.txt

# Setup del runner
FROM python:3.12-alpine
WORKDIR /app
COPY --from=builder /root/.local /root/.local

# Copia los archivos necesarios
COPY cogs cogs
COPY lib lib
COPY views views
COPY *.json .
COPY main.py .

# Carga las dependencias en PATH
ENV PATH=/root/.local/bin:$PATH

# Ejecuta el bot
CMD ["python3", "main.py"]
