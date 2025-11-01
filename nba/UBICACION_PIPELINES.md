# 📍 Ubicación de los Pipelines - NBA Machine Learning

## 🔍 Resumen
Este proyecto implementa **únicamente clasificación**, NO tiene pipelines de regresión.

## 🎯 Pipeline de Clasificación

### 📂 Ubicación Principal
```
Machine_Learning-NBA-main/nba/src/nba/pipelines/data_science/
├── pipeline.py    → Define el flujo del pipeline
└── nodes.py       → Contiene todas las funciones de entrenamiento
```

### 🧠 Modelos de Clasificación Implementados

#### 1️⃣ **Modelos Ensemble** (líneas 244-331 en `nodes.py`)
- ✅ Random Forest
- ✅ Gradient Boosting
- ✅ Extra Trees
- ✅ AdaBoost
- ✅ Bagging

#### 2️⃣ **Modelos Lineales** (líneas 334-394 en `nodes.py`)
- ✅ Logistic Regression
- ✅ Ridge Classifier
- ✅ SGD Classifier

#### 3️⃣ **Otros Modelos** (líneas 397-460 en `nodes.py`)
- ✅ SVM (Support Vector Machine)
- ✅ K-Nearest Neighbors (KNN)
- ✅ Naive Bayes
- ✅ Decision Tree

### 📊 Variable Objetivo
- **Variable**: `home_win` (binaria: 0 o 1)
- **Problema**: Clasificación binaria para predecir si el equipo local ganará
- **Configuración**: En `conf/base/parameters_data_science.yml` (línea 71)

### 🔄 Flujo del Pipeline (pipeline.py)

```
1. split_data               → Divide datos en train/val/test
2. train_ensemble_models    → Entrena modelos ensemble
3. train_linear_models      → Entrena modelos lineales
4. train_other_models       → Entrena otros modelos
5. create_model_comparison  → Compara todos los modelos
6. select_best_model        → Selecciona el mejor
7. evaluate_model           → Evalúa el modelo final
```

### ⚙️ Funciones Clave en `nodes.py`

| Función | Líneas | Descripción |
|---------|--------|-------------|
| `split_data` | 23-96 | Divide datos estratificados |
| `train_ensemble_models` | 244-331 | Entrena RF, GB, ET, AdaBoost, Bagging |
| `train_linear_models` | 334-394 | Entrena modelos lineales con escalado |
| `train_other_models` | 397-460 | Entrena SVM, KNN, Naive Bayes, DT |
| `create_model_comparison_table` | 463-517 | Crea tabla comparativa |
| `select_best_model` | 520-569 | Selecciona mejor modelo por AUC |

## 🚀 Cómo Ejecutar

### Ver el Pipeline Completo
```bash
kedro run --pipeline data_science
```

### Ver Node Específico
```bash
# Ver entrenamiento de ensemble
kedro run --node train_ensemble_models_node

# Ver entrenamiento de modelos lineales
kedro run --node train_linear_models_node

# Ver evaluación final
kedro run --node evaluate_model_node
```

## 📝 Configuración
- **Archivo**: `conf/base/parameters_data_science.yml`
- **Métricas**: Accuracy, Precision, Recall, F1-Score, ROC-AUC
- **Validación**: Cross-validation con StratifiedKFold (5 splits)

## ⚠️ Nota Importante
Este proyecto es **SOLO CLASIFICACIÓN BINARIA**. 
No hay pipeline de regresión en el código actual.
Para implementar regresión, necesitarías crear nuevas funciones en `nodes.py`.






