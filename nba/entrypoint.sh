#!/bin/bash

# Script de entrada para el contenedor NBA
echo "🏀 Iniciando NBA Machine Learning Pipeline"
echo "=========================================="

# Verificar que los datos estén disponibles
if [ ! -f "data/01_raw/game.csv" ]; then
    echo "❌ Error: Archivo game.csv no encontrado en data/01_raw/"
    echo "Por favor, coloca los archivos de datos NBA en el directorio data/01_raw/"
    exit 1
fi

# Inicializar DVC si no está inicializado
if [ ! -d ".dvc" ]; then
    echo "🔧 Inicializando DVC..."
    dvc init --no-scm
fi

# Ejecutar pipeline completo
echo "🚀 Ejecutando pipeline completo..."
kedro run

# Generar reporte final
echo "📊 Generando reporte final..."
kedro run --pipeline reporting

# Mostrar métricas
echo "📈 Métricas del modelo:"
if [ -f "metrics/data_science.json" ]; then
    cat metrics/data_science.json
fi

echo "✅ Pipeline completado exitosamente!"
echo "📁 Resultados disponibles en:"
echo "   - Modelos: data/06_models/"
echo "   - Reportes: data/08_reporting/"
echo "   - Métricas: metrics/"
echo "   - Gráficos: plots/"

