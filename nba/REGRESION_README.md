# 🏀 Pipeline de Regresión NBA - Guía de Uso

## 📋 Descripción

Este pipeline de regresión predice el **diferencial de puntos** (`pts_diff`) en partidos de la NBA utilizando múltiples algoritmos de machine learning.

### Hipótesis

**Predecir el diferencial de puntos (pts_diff = pts_home - pts_away) en partidos NBA** basándose en estadísticas históricas de equipos y partidos.

## 🚀 Inicio Rápido

### 1. Ejecutar Pipeline Localmente

```bash
# Pipeline completo (procesamiento + regresión + reportes)
kedro run --pipeline full_regression_pipeline

# Solo entrenamiento de modelos de regresión
kedro run --pipeline regression

# Solo reportes de regresión
kedro run --pipeline regression_reporting
```

### 2. Ejecutar con Docker

```bash
# Construir e iniciar contenedores
cd nba
docker-compose up -d nba-ml

# Ejecutar pipeline de regresión
docker exec -it nba-ml-pipeline kedro run --pipeline full_regression_pipeline
```

### 3. Ejecutar con Airflow

El DAG `nba_regression_pipeline` está configurado y se ejecutará automáticamente.

```bash
# Iniciar servicios Docker (incluye Airflow)
docker-compose up -d nba-airflow

# Acceder a Airflow UI
# URL: http://localhost:8080
# Usuario: admin
# Contraseña: admin
```

## 📊 Modelos Implementados

### Ensemble Methods
- Random Forest Regressor
- Gradient Boosting Regressor
- Extra Trees Regressor
- AdaBoost Regressor

### Modelos Lineales
- Linear Regression
- Ridge Regression
- Lasso Regression
- ElasticNet Regression
- Bayesian Ridge Regression

### Otros Modelos
- Support Vector Regressor (SVR)
- K-Nearest Neighbors Regressor (KNN)
- Decision Tree Regressor

## 📈 Métricas de Evaluación

- **R² Score**: Coeficiente de determinación (métrica principal)
- **RMSE**: Root Mean Squared Error
- **MAE**: Mean Absolute Error
- **Explained Variance**: Varianza explicada
- **Median Absolute Error**: Error absoluto mediano

## 📁 Estructura de Archivos

### Datos de Entrenamiento
```
data/05_model_input/
├── X_train_reg.csv
├── X_val_reg.csv
├── X_test_reg.csv
├── y_train_reg.csv
├── y_val_reg.csv
└── y_test_reg.csv
```

### Modelos Entrenados
```
data/06_models/
├── nba_regressor.pkl              # Mejor modelo
├── ensemble_regressors.pkl
├── linear_regressors.pkl
└── other_regressors.pkl
```

### Resultados
```
data/07_model_output/
├── regression_metrics.json
├── regression_comparison_table.csv
└── best_regressor_metrics.json
```

### Reportes y Visualizaciones
```
data/08_reporting/
├── regression_target_distribution_plot.png
├── predicted_vs_actual_plot.png
├── residuals_plot.png
└── regression_report.txt
```

## ⚙️ Configuración

### Parámetros de Regresión
Editar: `conf/base/parameters_regression.yml`

- Variables objetivo y features
- Parámetros de división de datos
- Configuración de modelos
- Métricas de evaluación

### Catálogo de Datasets
Editar: `conf/base/catalog.yml`

Contiene todas las definiciones de datasets utilizados por el pipeline.

## 🔍 Visualizaciones Generadas

1. **Distribución de Variable Objetivo**: Histograma de pts_diff
2. **Predicciones vs Valores Reales**: Scatter plot con línea perfecta
3. **Análisis de Residuos**: Gráficos de residuos vs predicciones y distribución

## 📝 Ejemplo de Uso del Modelo

```python
import pickle
import pandas as pd

# Cargar modelo
with open('data/06_models/nba_regressor.pkl', 'rb') as f:
    model = pickle.load(f)

# Cargar scaler si es necesario
with open('data/05_model_input/final_regression_scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# Preparar datos de ejemplo
features = [...]  # Características del partido

# Hacer predicción
if scaler is not None:
    features_scaled = scaler.transform([features])
    prediction = model.predict(features_scaled)[0]
else:
    prediction = model.predict([features])[0]

print(f"Diferencial de puntos predicho: {prediction:.2f}")
```

## 🐛 Solución de Problemas

### Error: "Module not found"
Asegúrate de tener todas las dependencias instaladas:
```bash
pip install -r requirements.txt
```

### Error: "Dataset not found"
Verifica que los datos estén en `data/01_raw/game.csv`

### Error en Airflow
Verifica que los paths en el DAG coincidan con la estructura del contenedor.

## 📚 Documentación Adicional

- [Hipótesis de Regresión](./docs/REGRESION_HIPOTESIS.md): Documentación detallada de la hipótesis
- [README Principal](./README.md): Documentación general del proyecto

## 🔗 Pipelines Relacionados

- **Clasificación**: `kedro run --pipeline full_pipeline`
- **Solo Regresión**: `kedro run --pipeline regression_pipeline`
- **Regresión Completa**: `kedro run --pipeline full_regression_pipeline`

---

**Última actualización:** 2024
**Autor:** NBA ML Team


