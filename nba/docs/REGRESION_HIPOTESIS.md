# Hipótesis de Regresión - NBA

## 🎯 Objetivo

Este documento describe la hipótesis de regresión implementada para predecir el **diferencial de puntos** en partidos de la NBA.

## 📊 Hipótesis Principal

**Hipótesis:** Es posible predecir el diferencial de puntos (pts_diff) en partidos de la NBA utilizando estadísticas históricas de equipos y partidos.

### Variable Objetivo

- **Nombre:** `pts_diff`
- **Definición:** Diferencial de puntos = `pts_home - pts_away`
- **Tipo:** Variable continua (regresión)
- **Interpretación:**
  - Valores positivos: El equipo local gana por ese margen
  - Valores negativos: El equipo visitante gana por ese margen
  - Valor 0: Empate teórico (raro en NBA)

### ¿Por qué esta hipótesis?

1. **Información más rica que clasificación:** A diferencia de predecir solo ganador/perdedor, el diferencial proporciona información sobre la **magnitud** de la victoria/derrota.

2. **Utilidad práctica:**
   - Análisis de competitividad de partidos
   - Estrategias de apuestas deportivas (spreads)
   - Evaluación de rendimiento de equipos
   - Identificación de partidos reñidos vs. partidos dominantes

3. **Variables disponibles:** El dataset NBA contiene estadísticas detalladas que pueden correlacionarse con el diferencial de puntos:
   - Estadísticas ofensivas (FG%, 3P%, FT%, puntos)
   - Estadísticas defensivas (rebotes, bloqueos, robos)
   - Eficiencia y control del juego (asistencias, turnovers)

## 🔬 Metodología

### Modelos de Regresión Implementados

El pipeline incluye múltiples algoritmos de regresión:

1. **Ensemble Methods:**
   - Random Forest Regressor
   - Gradient Boosting Regressor
   - Extra Trees Regressor
   - AdaBoost Regressor

2. **Modelos Lineales:**
   - Linear Regression
   - Ridge Regression
   - Lasso Regression
   - ElasticNet Regression
   - Bayesian Ridge Regression

3. **Otros Modelos:**
   - Support Vector Regressor (SVR)
   - K-Nearest Neighbors Regressor (KNN)
   - Decision Tree Regressor

### Selección del Mejor Modelo

El mejor modelo se selecciona basándose en:
- **Métrica principal:** R² Score (coeficiente de determinación)
- **Métricas adicionales:**
  - RMSE (Root Mean Squared Error)
  - MAE (Mean Absolute Error)
  - Explained Variance
  - Median Absolute Error

### Features Utilizadas

1. **Variables Numéricas:**
   - Puntos, porcentajes de tiros (FG%, 3P%, FT%)
   - Rebotes (ofensivos, defensivos, totales)
   - Asistencias, robos, bloqueos
   - Turnovers, faltas personales
   - Plus/Minus

2. **Variables Diferenciales:**
   - Diferencia en porcentaje de tiros
   - Diferencia en rebotes, asistencias
   - Diferencia en eficiencia ofensiva

3. **Variables Temporales:**
   - Año, mes, día de la semana
   - Indicadores de fin de semana, playoffs

4. **Variables Categóricas:**
   - Equipos (codificados)
   - Tipo de temporada (Regular, Playoffs, etc.)

## 📈 Resultados Esperados

### Métricas de Éxito

- **R² Score > 0.6:** Modelo explica más del 60% de la varianza
- **RMSE < 12 puntos:** Error promedio razonable para diferencial de puntos
- **MAE < 8 puntos:** Error absoluto promedio manejable

### Interpretación de Resultados

- Un R² de 0.7 significa que el modelo explica el 70% de la variabilidad en el diferencial de puntos
- Un RMSE de 10 significa que, en promedio, las predicciones tienen un error de ±10 puntos

## 🚀 Uso del Pipeline

### Ejecutar Localmente

```bash
# Pipeline completo de regresión
kedro run --pipeline full_regression_pipeline

# Solo entrenamiento de modelos
kedro run --pipeline regression

# Solo reportes
kedro run --pipeline regression_reporting
```

### Ejecutar con Docker

```bash
docker-compose up nba-ml
```

Luego ejecutar:
```bash
docker exec -it nba-ml-pipeline kedro run --pipeline full_regression_pipeline
```

### Ejecutar con Airflow

El DAG `nba_regression_pipeline` se ejecuta automáticamente según la programación configurada.

Acceder a Airflow UI: `http://localhost:8080`
- Usuario: `admin`
- Contraseña: `admin`

## 📁 Estructura de Archivos Generados

```
data/
├── 05_model_input/
│   ├── X_train_reg.csv          # Características de entrenamiento
│   ├── X_val_reg.csv            # Características de validación
│   ├── X_test_reg.csv           # Características de prueba
│   ├── y_train_reg.csv          # Variable objetivo entrenamiento
│   ├── y_val_reg.csv            # Variable objetivo validación
│   ├── y_test_reg.csv           # Variable objetivo prueba
│   └── regression_scaler.pkl    # Normalizador
├── 06_models/
│   ├── nba_regressor.pkl        # Mejor modelo entrenado
│   ├── ensemble_regressors.pkl  # Modelos ensemble
│   ├── linear_regressors.pkl    # Modelos lineales
│   └── other_regressors.pkl     # Otros modelos
├── 07_model_output/
│   ├── regression_metrics.json           # Métricas de evaluación
│   ├── regression_comparison_table.csv   # Comparación de modelos
│   └── best_regressor_metrics.json       # Métricas del mejor modelo
└── 08_reporting/
    ├── regression_target_distribution_plot.png  # Distribución de pts_diff
    ├── predicted_vs_actual_plot.png            # Predicciones vs reales
    ├── residuals_plot.png                      # Análisis de residuos
    └── regression_report.txt                   # Reporte completo
```

## 🔍 Validación de la Hipótesis

### Análisis de Residuos

El pipeline incluye análisis de residuos para validar:
- **Normalidad:** Los residuos deben seguir una distribución normal
- **Homocedasticidad:** Varianza constante de residuos
- **Independencia:** Residuos no correlacionados

### Visualizaciones

1. **Distribución de la Variable Objetivo:** Histograma de pts_diff
2. **Predicciones vs Valores Reales:** Scatter plot con línea perfecta
3. **Análisis de Residuos:** Residuos vs predicciones y distribución

## 💡 Próximos Pasos y Mejoras

1. **Feature Engineering:**
   - Incorporar estadísticas de jugadores clave
   - Estadísticas de últimos N partidos
   - Head-to-head históricos entre equipos

2. **Modelos Avanzados:**
   - Neural Networks
   - XGBoost
   - LightGBM

3. **Validación Externa:**
   - Validar predicciones con datos de temporadas futuras
   - Comparar con modelos de referencia

## 📚 Referencias

- Dataset NBA: Histórico de partidos desde 1946 hasta 2023
- Kedro Framework: Framework de MLOps utilizado
- Scikit-learn: Librería de machine learning

---

**Última actualización:** 2024
**Autor:** NBA ML Team


