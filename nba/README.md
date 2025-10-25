# 🏀 NBA Game Winner Prediction

[![Powered by Kedro](https://img.shields.io/badge/powered_by-kedro-ffc900?logo=kedro)](https://kedro.org)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📋 Descripción del Proyecto

Este proyecto utiliza **Kedro** para desarrollar un sistema de machine learning que predice el ganador de partidos de la NBA. El proyecto analiza más de 65,000 partidos históricos desde 1946 hasta 2023, utilizando estadísticas detalladas de equipos, jugadores y métricas de rendimiento.

### 🎯 Objetivo Principal
Desarrollar un modelo de clasificación binaria que prediga con alta precisión qué equipo ganará un partido de la NBA siendo local, basándose en estadísticas históricas y características del juego.

### 🧠 Tipo de Problema
- **Clasificación Binaria**: Victoria local (1) vs Derrota local (0)
- **Variable Objetivo**: `home_win` (derivada de `wl_home`)
- **Algoritmos**: Random Forest, Gradient Boosting, Regresión Logística

## 🏗️ Arquitectura del Proyecto

### 📁 Estructura de Pipelines

El proyecto está organizado en tres pipelines principales:

1. **`data_processing`**: Limpieza y preparación de datos
   - Limpieza de valores nulos y outliers
   - Feature engineering (variables diferenciales, temporales)
   - Codificación de variables categóricas
   - Normalización y escalado

2. **`data_science`**: Entrenamiento y evaluación de modelos
   - División estratificada de datos
   - Entrenamiento de múltiples algoritmos
   - Selección del mejor modelo
   - Evaluación con métricas robustas

3. **`reporting`**: Visualizaciones y reportes
   - Gráficos de distribución y correlaciones
   - Matrices de confusión y curvas ROC
   - Reportes de métricas y recomendaciones

### 📊 Datasets Principales

- **`game.csv`**: Dataset principal con 65,698 partidos y 55 variables
- **`other_stats.csv`**: Estadísticas adicionales de partidos
- **`team.csv`**, **`player.csv`**: Información de equipos y jugadores
- **`model_input_table`**: Dataset final procesado para modelado

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- pip o conda

### Instalación de Dependencias

```bash
# Clonar el repositorio
git clone <repository-url>
cd nba

# Instalar dependencias
pip install -r requirements.txt
```

### Estructura de Datos
Coloca los archivos CSV de la NBA en el directorio `data/01_raw/`:
- `game.csv`
- `other_stats.csv`
- `team.csv`
- `player.csv`
- `game_info.csv`
- Y otros archivos de datos NBA

## 🏃‍♂️ Ejecución del Proyecto

### Ejecutar Pipeline Completo
```bash
kedro run
```

### Ejecutar Pipelines Específicos
```bash
# Solo procesamiento de datos
kedro run --pipeline data_processing

# Solo entrenamiento de modelos
kedro run --pipeline data_science

# Solo reportes
kedro run --pipeline reporting

# Pipeline de ML completo (procesamiento + ciencia de datos)
kedro run --pipeline ml_pipeline
```

### Ejecutar con Tags
```bash
# Solo nodos de limpieza de datos
kedro run --tag data_cleaning

# Solo nodos de entrenamiento
kedro run --tag model_training

# Solo visualizaciones
kedro run --tag visualization
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/pipelines/data_processing/
pytest tests/pipelines/data_science/

# Con cobertura
pytest --cov=src/nba
```

### Tests Incluidos
- Tests unitarios para funciones de procesamiento de datos
- Tests de pipelines de machine learning
- Tests de validación de datos
- Tests de métricas de evaluación

## 📊 Análisis Exploratorio y Notebooks

### Notebooks Incluidos
El proyecto incluye notebooks detallados en `notebooks/`:

- **`Fase_1.ipynb`**: Comprensión del negocio y objetivos
- **`Fase_2.ipynb`**: Análisis exploratorio de datos (EDA)
- **`Fase_3.ipynb`**: Preparación y feature engineering
- **`Untitled.ipynb`**: Análisis adicionales y limpieza

### Trabajar con Jupyter

```bash
# Iniciar Jupyter Notebook
kedro jupyter notebook

# Iniciar JupyterLab
kedro jupyter lab

# Iniciar IPython
kedro ipython
```

> **Nota**: Los notebooks tienen acceso a `catalog`, `context`, `pipelines` y `session` de Kedro.

## 📈 Resultados y Métricas

### Métricas de Rendimiento Esperadas
- **Accuracy**: > 60% (superior al rendimiento aleatorio del 50%)
- **AUC Score**: > 0.65
- **Precision/Recall**: Balanceados para ambas clases
- **F1-Score**: > 0.60

### Características Más Importantes
1. **Plus/Minus**: Diferencia de puntos durante el partido
2. **Porcentaje de Tiros de Campo**: Eficiencia ofensiva
3. **Puntos Totales**: Capacidad ofensiva
4. **Rebotes**: Control del balón
5. **Asistencias**: Juego en equipo

## 🔧 Configuración Avanzada

### Parámetros del Proyecto
Los parámetros están organizados en:
- `conf/base/parameters.yml`: Configuración global
- `conf/base/parameters_data_processing.yml`: Procesamiento de datos
- `conf/base/parameters_data_science.yml`: Ciencia de datos
- `conf/base/parameters_reporting.yml`: Reportes y visualizaciones

### Personalización
Puedes modificar los parámetros en `conf/local/` para personalizar:
- Tamaños de conjuntos de entrenamiento/prueba
- Hiperparámetros de modelos
- Configuraciones de visualización
- Umbrales de evaluación

## 📚 Documentación Adicional

### Enlaces Útiles
- [Documentación de Kedro](https://docs.kedro.org)
- [Scikit-learn](https://scikit-learn.org/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)

### Estructura del Proyecto
```
nba/
├── conf/           # Configuraciones
├── data/           # Datos (raw, intermediate, primary, etc.)
├── docs/           # Documentación
├── notebooks/      # Jupyter notebooks
├── src/nba/        # Código fuente
│   ├── pipelines/  # Pipelines de Kedro
│   └── settings.py # Configuraciones
└── tests/          # Tests unitarios
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [Kedro](https://kedro.org) por el framework de MLOps
- [NBA](https://www.nba.com) por los datos históricos
- [Scikit-learn](https://scikit-learn.org/) por las herramientas de ML
