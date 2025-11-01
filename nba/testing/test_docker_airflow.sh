#!/bin/bash
# Script de prueba para Docker y Airflow

echo "=========================================="
echo "PRUEBAS DE DOCKER Y AIRFLOW"
echo "=========================================="
echo ""

# Verificar que docker-compose.yml existe
echo "TEST 1: Verificando docker-compose.yml"
if [ -f "docker-compose.yml" ]; then
    echo "  [OK] docker-compose.yml encontrado"
    
    # Verificar sintaxis básica
    if docker-compose config > /dev/null 2>&1; then
        echo "  [OK] Sintaxis de docker-compose.yml correcta"
    else
        echo "  [WARN] Error al validar docker-compose.yml (puede requerir Docker instalado)"
    fi
else
    echo "  [ERROR] docker-compose.yml no encontrado"
fi

echo ""

# Verificar Dockerfile
echo "TEST 2: Verificando Dockerfile"
if [ -f "Dockerfile" ]; then
    echo "  [OK] Dockerfile encontrado"
    
    # Verificar que tenga elementos clave
    if grep -q "FROM python" Dockerfile; then
        echo "  [OK] Dockerfile tiene imagen base de Python"
    fi
    
    if grep -q "requirements.txt" Dockerfile; then
        echo "  [OK] Dockerfile incluye requirements.txt"
    fi
else
    echo "  [ERROR] Dockerfile no encontrado"
fi

echo ""

# Verificar DAGs de Airflow
echo "TEST 3: Verificando DAGs de Airflow"
if [ -f "airflow/dags/nba_regression_pipeline.py" ]; then
    echo "  [OK] DAG de regresion encontrado"
    
    # Verificar sintaxis Python
    if python -m py_compile airflow/dags/nba_regression_pipeline.py 2>/dev/null; then
        echo "  [OK] Sintaxis Python del DAG correcta"
    else
        echo "  [WARN] Error al compilar DAG (puede requerir dependencias)"
    fi
else
    echo "  [ERROR] DAG de regresion no encontrado"
fi

if [ -f "airflow/dags/nba_ml_pipeline.py" ]; then
    echo "  [OK] DAG de clasificacion encontrado"
else
    echo "  [WARN] DAG de clasificacion no encontrado (opcional)"
fi

echo ""

# Verificar estructura de directorios
echo "TEST 4: Verificando estructura de directorios"
directories=(
    "src/nba/pipelines/regression"
    "src/nba/pipelines/regression_reporting"
    "src/nba/pipelines/data_science"
    "conf/base"
    "airflow/dags"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "  [OK] Directorio $dir existe"
    else
        echo "  [ERROR] Directorio $dir no existe"
    fi
done

echo ""
echo "=========================================="
echo "RESUMEN"
echo "=========================================="
echo "Si todos los tests muestran [OK], la configuracion esta lista"
echo "para usar con Docker y Airflow."

