# Usar Python 3.9 como imagen base
FROM python:3.9-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV KEDRO_CONFIG_FILE=conf/local/parameters.yml

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY requirements.txt pyproject.toml ./
COPY conf/ ./conf/
COPY src/ ./src/

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar DVC
RUN pip install dvc[s3]

# Crear directorios necesarios
RUN mkdir -p data/01_raw data/02_intermediate data/03_primary data/04_feature \
    data/05_model_input data/06_models data/07_model_output data/08_reporting \
    metrics plots logs

# Copiar el resto del código
COPY . .

# Hacer el script ejecutable
RUN chmod +x entrypoint.sh

# Exponer puerto para Jupyter (opcional)
EXPOSE 8888

# Comando por defecto
CMD ["./entrypoint.sh"]

