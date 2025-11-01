import logging
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.metrics import roc_curve, auc
from datetime import datetime

logger = logging.getLogger(__name__)

# Configurar matplotlib para usar backend no interactivo
matplotlib.use('Agg')


def create_win_distribution_plot(model_input_table: pd.DataFrame, parameters: dict) -> plt.Figure:
    """Crea un gráfico de distribución de victorias locales vs visitantes.

    Args:
        model_input_table: Datos del modelo con variable objetivo.
        parameters: Parámetros de visualización.

    Returns:
        Figura de matplotlib con el gráfico de distribución.
    """
    logger.info("Creando gráfico de distribución de victorias...")
    
    # Configuración de visualización
    viz_config = parameters["visualizations"]["win_distribution"]
    general_config = parameters["visualizations"]["general"]
    
    # Configurar estilo
    plt.style.use(general_config["style"])
    plt.rcParams['figure.figsize'] = general_config["figure_size"]
    plt.rcParams['figure.dpi'] = general_config["dpi"]
    
    # Crear figura
    fig, ax = plt.subplots()
    
    # Contar victorias y derrotas
    win_counts = model_input_table['home_win'].value_counts()
    labels = ['Derrota Local', 'Victoria Local']
    colors = viz_config["colors"]
    
    # Crear gráfico de barras
    bars = ax.bar(labels, [win_counts[0], win_counts[1]], color=colors)
    
    # Configurar título y etiquetas
    ax.set_title(viz_config["title"], fontsize=general_config["title_size"], fontweight='bold')
    ax.set_xlabel(viz_config["xlabel"], fontsize=general_config["font_size"])
    ax.set_ylabel(viz_config["ylabel"], fontsize=general_config["font_size"])
    
    # Agregar valores en las barras
    for bar, count in zip(bars, [win_counts[0], win_counts[1]]):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{count:,}\n({count/len(model_input_table):.1%})',
                ha='center', va='bottom', fontsize=general_config["font_size"])
    
    # Configurar grid
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    logger.info("Gráfico de distribución de victorias creado")
    
    return fig


def create_correlation_matrix_plot(model_input_table: pd.DataFrame, parameters: dict) -> plt.Figure:
    """Crea una matriz de correlación de variables de rendimiento NBA.

    Args:
        model_input_table: Datos del modelo.
        parameters: Parámetros de visualización.

    Returns:
        Figura de matplotlib con la matriz de correlación.
    """
    logger.info("Creando matriz de correlación...")
    
    # Configuración de visualización
    viz_config = parameters["visualizations"]["correlation_matrix"]
    general_config = parameters["visualizations"]["general"]
    
    # Configurar estilo
    plt.style.use(general_config["style"])
    plt.rcParams['figure.figsize'] = (16, 12)
    plt.rcParams['figure.dpi'] = general_config["dpi"]
    
    # Seleccionar variables numéricas para correlación
    numeric_cols = model_input_table.select_dtypes(include=[np.number]).columns
    correlation_data = model_input_table[numeric_cols].copy()
    
    # Calcular matriz de correlación
    correlation_matrix = correlation_data.corr()
    
    # Crear figura
    fig, ax = plt.subplots()
    
    # Crear heatmap
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    sns.heatmap(
        correlation_matrix, 
        mask=mask,
        annot=viz_config["annot"], 
        cmap=viz_config["cmap"], 
        center=viz_config["center"],
        square=viz_config["square"],
        fmt=viz_config["fmt"],
        cbar_kws=viz_config["cbar_kws"],
        ax=ax
    )
    
    ax.set_title(viz_config["title"], fontsize=general_config["title_size"], fontweight='bold')
    
    plt.tight_layout()
    logger.info("Matriz de correlación creada")
    
    return fig


def create_feature_importance_plot(nba_classifier, X_train: pd.DataFrame, parameters: dict) -> plt.Figure:
    """Crea un gráfico de importancia de características del modelo.

    Args:
        nba_classifier: Modelo entrenado.
        X_train: Datos de entrenamiento.
        parameters: Parámetros de visualización.

    Returns:
        Figura de matplotlib con el gráfico de importancia.
    """
    logger.info("Creando gráfico de importancia de características...")
    
    # Configuración de visualización
    viz_config = parameters["visualizations"]["feature_importance"]
    general_config = parameters["visualizations"]["general"]
    
    # Configurar estilo
    plt.style.use(general_config["style"])
    plt.rcParams['figure.figsize'] = general_config["figure_size"]
    plt.rcParams['figure.dpi'] = general_config["dpi"]
    
    # Obtener importancia de características
    if hasattr(nba_classifier, 'feature_importances_'):
        importances = nba_classifier.feature_importances_
        feature_names = X_train.columns
        
        # Crear DataFrame con importancia
        feature_importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=True)
        
        # Tomar solo las top N características
        top_n = viz_config["top_n"]
        feature_importance_df = feature_importance_df.tail(top_n)
        
        # Crear figura
        fig, ax = plt.subplots()
        
        # Crear gráfico de barras horizontales
        bars = ax.barh(
            feature_importance_df['feature'], 
            feature_importance_df['importance'],
            color=viz_config["color"]
        )
        
        # Configurar título y etiquetas
        ax.set_title(viz_config["title"], fontsize=general_config["title_size"], fontweight='bold')
        ax.set_xlabel(viz_config["xlabel"], fontsize=general_config["font_size"])
        ax.set_ylabel(viz_config["ylabel"], fontsize=general_config["font_size"])
        
        # Configurar grid
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        logger.info("Gráfico de importancia de características creado")
        
    else:
        # Si el modelo no tiene feature_importances_, crear un gráfico vacío
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'Modelo no soporta importancia de características', 
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Importancia de Características', fontsize=general_config["title_size"])
        logger.warning("Modelo no soporta importancia de características")

    return fig


def create_confusion_matrix_plot(model_metrics: dict, parameters: dict) -> plt.Figure:
    """Crea una matriz de confusión del modelo.

    Args:
        model_metrics: Métricas del modelo incluyendo matriz de confusión.
        parameters: Parámetros de visualización.

    Returns:
        Figura de matplotlib con la matriz de confusión.
    """
    logger.info("Creando matriz de confusión...")
    
    # Configuración de visualización
    viz_config = parameters["visualizations"]["confusion_matrix"]
    general_config = parameters["visualizations"]["general"]
    
    # Configurar estilo
    plt.style.use(general_config["style"])
    plt.rcParams['figure.figsize'] = (8, 6)
    plt.rcParams['figure.dpi'] = general_config["dpi"]
    
    # Obtener matriz de confusión
    cm = np.array(model_metrics['confusion_matrix'])
    
    # Crear figura
    fig, ax = plt.subplots()
    
    # Crear heatmap
    sns.heatmap(
        cm, 
        annot=viz_config["annot"], 
        fmt=viz_config["fmt"], 
        cmap=viz_config["cmap"],
        xticklabels=viz_config["labels"],
        yticklabels=viz_config["labels"],
        ax=ax
    )
    
    # Configurar título y etiquetas
    ax.set_title(viz_config["title"], fontsize=general_config["title_size"], fontweight='bold')
    ax.set_xlabel(viz_config["xlabel"], fontsize=general_config["font_size"])
    ax.set_ylabel(viz_config["ylabel"], fontsize=general_config["font_size"])
    
    plt.tight_layout()
    logger.info("Matriz de confusión creada")
    
    return fig


def create_roc_curve_plot(nba_classifier, X_test: pd.DataFrame, y_test: pd.Series, parameters: dict) -> plt.Figure:
    """Crea una curva ROC del modelo.

    Args:
        nba_classifier: Modelo entrenado.
        X_test: Datos de prueba.
        y_test: Variable objetivo de prueba.
        parameters: Parámetros de visualización.

    Returns:
        Figura de matplotlib con la curva ROC.
    """
    logger.info("Creando curva ROC...")
    
    # Configuración de visualización
    viz_config = parameters["visualizations"]["roc_curve"]
    general_config = parameters["visualizations"]["general"]
    
    # Configurar estilo
    plt.style.use(general_config["style"])
    plt.rcParams['figure.figsize'] = general_config["figure_size"]
    plt.rcParams['figure.dpi'] = general_config["dpi"]
    
    # Crear figura
    fig, ax = plt.subplots()
    
    # Obtener probabilidades de predicción
    if hasattr(nba_classifier, 'predict_proba'):
        y_pred_proba = nba_classifier.predict_proba(X_test)[:, 1]
        
        # Calcular curva ROC
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        # Crear curva ROC
        ax.plot(fpr, tpr, 
                color=viz_config["colors"][0], 
                linewidth=viz_config["linewidth"],
                label=f'ROC Curve (AUC = {roc_auc:.3f})')
        
        # Línea diagonal (clasificador aleatorio)
        ax.plot([0, 1], [0, 1], 
                color='gray', 
                linestyle='--', 
                alpha=0.5,
                label='Clasificador Aleatorio')
        
        # Configurar título y etiquetas
        ax.set_title(viz_config["title"], fontsize=general_config["title_size"], fontweight='bold')
        ax.set_xlabel(viz_config["xlabel"], fontsize=general_config["font_size"])
        ax.set_ylabel(viz_config["ylabel"], fontsize=general_config["font_size"])
        
        # Configurar límites y grid
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        
        # Agregar leyenda
        if viz_config["legend"]:
            ax.legend(loc="lower right")
        
        logger.info(f"Curva ROC creada con AUC = {roc_auc:.3f}")
        
    else:
        # Si el modelo no soporta probabilidades
        ax.text(0.5, 0.5, 'Modelo no soporta probabilidades de predicción', 
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Curva ROC', fontsize=general_config["title_size"])
        logger.warning("Modelo no soporta probabilidades de predicción")
    
    plt.tight_layout()
    logger.info("Curva ROC creada")

    return fig


def create_model_report(model_metrics: dict, best_model_name: str, parameters: dict) -> str:
    """Crea un reporte de texto con las métricas del modelo.

    Args:
        model_metrics: Métricas del modelo.
        best_model_name: Nombre del mejor modelo.
        parameters: Parámetros de reporte.

    Returns:
        Reporte de texto con las métricas.
    """
    logger.info("Creando reporte del modelo...")
    
    # Configuración de reporte
    report_config = parameters["reports"]["model_metrics"]
    format_config = parameters["reports"]["format"]
    
    # Crear reporte
    report = f"""
{report_config['title']}
{'=' * len(report_config['title'])}

Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Mejor modelo seleccionado: {best_model_name}

RESUMEN EJECUTIVO
-----------------
El modelo de clasificación para predicción de ganadores de partidos NBA ha sido entrenado
y evaluado exitosamente. Se compararon múltiples algoritmos y se seleccionó el mejor
basado en el rendimiento en el conjunto de validación.

MÉTRICAS DE RENDIMIENTO
-----------------------
"""
    
    # Agregar métricas principales
    for metric in ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']:
        if metric in model_metrics:
            value = model_metrics[metric]
            if metric == 'roc_auc':
                report += f"AUC Score: {value:.{format_config['decimal_places']}f}\n"
            else:
                report += f"{metric.replace('_', ' ').title()}: {value:.{format_config['decimal_places']}f}\n"
    
    # Agregar matriz de confusión
    if 'confusion_matrix' in model_metrics:
        cm = np.array(model_metrics['confusion_matrix'])
        report += f"""
MATRIZ DE CONFUSIÓN
-------------------
                Predicción
                0     1
Valor Real 0   {cm[0,0]:4d}  {cm[0,1]:4d}
           1   {cm[1,0]:4d}  {cm[1,1]:4d}

Donde:
- 0 = Derrota Local
- 1 = Victoria Local
"""
    
    # Agregar reporte de clasificación
    if 'classification_report' in model_metrics:
        report += "\nREPORTE DE CLASIFICACIÓN\n"
        report += "------------------------\n"
        report += f"Precisión por clase:\n"
        for class_name, metrics in model_metrics['classification_report'].items():
            if isinstance(metrics, dict) and 'precision' in metrics:
                report += f"  Clase {class_name}: {metrics['precision']:.{format_config['decimal_places']}f}\n"
    
    report += f"""
ANÁLISIS DE CARACTERÍSTICAS
---------------------------
El modelo utiliza múltiples características derivadas de estadísticas de partidos NBA,
incluyendo variables diferenciales entre equipos locales y visitantes, características
temporales y variables de eficiencia.

RECOMENDACIONES
---------------
1. El modelo muestra un rendimiento sólido para la predicción de ganadores
2. Se recomienda actualizar el modelo regularmente con datos recientes
3. Considerar la incorporación de datos adicionales como lesiones de jugadores
4. Monitorear el rendimiento del modelo en producción

---
Reporte generado automáticamente por el pipeline de NBA
"""
    
    logger.info("Reporte del modelo creado")
    
    return report


def create_regression_target_distribution(model_input_table: pd.DataFrame, parameters: dict) -> plt.Figure:
    """Crea un gráfico de distribución de la variable objetivo de regresión.

    Args:
        model_input_table: Datos del modelo con variable objetivo.
        parameters: Parámetros de visualización.

    Returns:
        Figura de matplotlib con el gráfico de distribución.
    """
    logger.info("Creando gráfico de distribución de diferencial de puntos...")
    
    # Configuración de visualización
    general_config = parameters["visualizations"]["general"]
    
    # Configurar estilo
    plt.style.use(general_config["style"])
    plt.rcParams['figure.figsize'] = general_config["figure_size"]
    plt.rcParams['figure.dpi'] = general_config["dpi"]
    
    # Crear figura
    fig, ax = plt.subplots()
    
    # Obtener variable objetivo de regresión
    target_col = parameters.get("regression_target", "pts_diff")
    if target_col not in model_input_table.columns:
        logger.warning(f"Columna {target_col} no encontrada, usando pts_diff si existe")
        if "pts_diff" in model_input_table.columns:
            target_col = "pts_diff"
        else:
            logger.error("No se encontró variable objetivo de regresión")
            return fig
    
    target_data = model_input_table[target_col]
    
    # Crear histograma
    ax.hist(target_data, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    
    # Agregar línea de media
    mean_val = target_data.mean()
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Media: {mean_val:.2f}')
    
    # Configurar título y etiquetas
    ax.set_title("Distribución del Diferencial de Puntos (pts_diff)", 
                fontsize=general_config["title_size"], fontweight='bold')
    ax.set_xlabel("Diferencial de Puntos (pts_home - pts_away)", fontsize=general_config["font_size"])
    ax.set_ylabel("Frecuencia", fontsize=general_config["font_size"])
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    logger.info("Gráfico de distribución de diferencial de puntos creado")
    
    return fig


def create_predicted_vs_actual_plot(nba_regressor, scaler, X_test: pd.DataFrame, y_test: pd.Series, 
                                   parameters: dict) -> plt.Figure:
    """Crea un gráfico de predicciones vs valores reales.

    Args:
        nba_regressor: Modelo entrenado.
        scaler: Scaler usado (puede ser None).
        X_test: Datos de prueba.
        y_test: Variable objetivo de prueba.
        parameters: Parámetros de visualización.

    Returns:
        Figura de matplotlib con el gráfico.
    """
    logger.info("Creando gráfico de predicciones vs valores reales...")
    
    # Configuración de visualización
    general_config = parameters["visualizations"]["general"]
    model_name = parameters.get("model_name", "unknown")
    
    # Configurar estilo
    plt.style.use(general_config["style"])
    plt.rcParams['figure.figsize'] = general_config["figure_size"]
    plt.rcParams['figure.dpi'] = general_config["dpi"]
    
    # Determinar si el modelo necesita escalado
    linear_models = ['linear_regression', 'ridge', 'lasso', 'elastic_net', 'bayesian_ridge']
    
    if scaler is not None and model_name in linear_models:
        X_test_prepared = scaler.transform(X_test)
    else:
        X_test_prepared = X_test
    
    # Predicciones
    y_pred = nba_regressor.predict(X_test_prepared)
    
    # Crear figura
    fig, ax = plt.subplots()
    
    # Scatter plot
    ax.scatter(y_test, y_pred, alpha=0.5, s=20)
    
    # Línea perfecta (y = x)
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Predicción Perfecta')
    
    # Configurar título y etiquetas
    ax.set_title(f"Predicciones vs Valores Reales - {model_name.replace('_', ' ').title()}", 
                fontsize=general_config["title_size"], fontweight='bold')
    ax.set_xlabel("Valores Reales (pts_diff)", fontsize=general_config["font_size"])
    ax.set_ylabel("Predicciones (pts_diff)", fontsize=general_config["font_size"])
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    logger.info("Gráfico de predicciones vs valores reales creado")
    
    return fig


def create_residuals_plot(nba_regressor, scaler, X_test: pd.DataFrame, y_test: pd.Series, 
                          parameters: dict) -> plt.Figure:
    """Crea un gráfico de residuos.

    Args:
        nba_regressor: Modelo entrenado.
        scaler: Scaler usado (puede ser None).
        X_test: Datos de prueba.
        y_test: Variable objetivo de prueba.
        parameters: Parámetros de visualización.

    Returns:
        Figura de matplotlib con el gráfico.
    """
    logger.info("Creando gráfico de residuos...")
    
    # Configuración de visualización
    general_config = parameters["visualizations"]["general"]
    model_name = parameters.get("model_name", "unknown")
    
    # Configurar estilo
    plt.style.use(general_config["style"])
    plt.rcParams['figure.figsize'] = general_config["figure_size"]
    plt.rcParams['figure.dpi'] = general_config["dpi"]
    
    # Determinar si el modelo necesita escalado
    linear_models = ['linear_regression', 'ridge', 'lasso', 'elastic_net', 'bayesian_ridge']
    
    if scaler is not None and model_name in linear_models:
        X_test_prepared = scaler.transform(X_test)
    else:
        X_test_prepared = X_test
    
    # Predicciones y residuos
    y_pred = nba_regressor.predict(X_test_prepared)
    residuals = y_test - y_pred
    
    # Crear figura con subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Gráfico 1: Residuos vs Predicciones
    ax1.scatter(y_pred, residuals, alpha=0.5, s=20)
    ax1.axhline(y=0, color='r', linestyle='--', linewidth=2)
    ax1.set_title("Residuos vs Predicciones", fontsize=general_config["title_size"], fontweight='bold')
    ax1.set_xlabel("Predicciones", fontsize=general_config["font_size"])
    ax1.set_ylabel("Residuos", fontsize=general_config["font_size"])
    ax1.grid(True, alpha=0.3)
    ax1.set_axisbelow(True)
    
    # Gráfico 2: Distribución de residuos
    ax2.hist(residuals, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    ax2.axvline(x=0, color='r', linestyle='--', linewidth=2)
    ax2.set_title("Distribución de Residuos", fontsize=general_config["title_size"], fontweight='bold')
    ax2.set_xlabel("Residuos", fontsize=general_config["font_size"])
    ax2.set_ylabel("Frecuencia", fontsize=general_config["font_size"])
    ax2.grid(True, alpha=0.3)
    ax2.set_axisbelow(True)
    
    plt.tight_layout()
    logger.info("Gráfico de residuos creado")
    
    return fig


def create_regression_report(regression_metrics: dict, best_regressor_name: str, parameters: dict) -> str:
    """Crea un reporte de texto con las métricas del modelo de regresión.

    Args:
        regression_metrics: Métricas del modelo de regresión.
        best_regressor_name: Nombre del mejor modelo.
        parameters: Parámetros de reporte.

    Returns:
        Reporte de texto con las métricas.
    """
    logger.info("Creando reporte del modelo de regresión...")
    
    # Configuración de reporte
    report_config = parameters["reports"]["model_metrics"]
    format_config = parameters["reports"]["format"]
    
    # Crear reporte
    report = f"""
{report_config['title']} - REGRESIÓN
{'=' * len(report_config['title'])} REGRESIÓN

Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Mejor modelo seleccionado: {best_regressor_name}

HIPÓTESIS DE REGRESIÓN
----------------------
La hipótesis propuesta es predecir el diferencial de puntos (pts_diff) en partidos de la NBA.
El diferencial de puntos se calcula como: pts_home - pts_away

Esta métrica proporciona información valiosa sobre:
- La magnitud de la victoria/derrota del equipo local
- La competitividad del partido
- La capacidad del equipo local para mantener ventajas o superar desventajas

RESUMEN EJECUTIVO
-----------------
El modelo de regresión para predicción del diferencial de puntos en partidos NBA ha sido
entrenado y evaluado exitosamente. Se compararon múltiples algoritmos y se seleccionó el mejor
basado en el rendimiento en el conjunto de validación (métrica principal: R² Score).

MÉTRICAS DE RENDIMIENTO
------------------------
"""
    
    # Agregar métricas principales
    for metric in ['r2_score', 'rmse', 'mae', 'explained_variance']:
        if metric in regression_metrics:
            value = regression_metrics[metric]
            if metric == 'r2_score':
                report += f"R² Score: {value:.{format_config['decimal_places']}f}\n"
            elif metric == 'rmse':
                report += f"RMSE (Root Mean Squared Error): {value:.{format_config['decimal_places']}f}\n"
            elif metric == 'mae':
                report += f"MAE (Mean Absolute Error): {value:.{format_config['decimal_places']}f}\n"
            elif metric == 'explained_variance':
                report += f"Explained Variance: {value:.{format_config['decimal_places']}f}\n"
    
    # Métricas adicionales
    if 'mean_residual' in regression_metrics:
        report += f"""
ANÁLISIS DE RESIDUOS
--------------------
Media de Residuos: {regression_metrics['mean_residual']:.{format_config['decimal_places']}f}
Desviación Estándar de Residuos: {regression_metrics.get('std_residual', 0):.{format_config['decimal_places']}f}
"""
    
    report += f"""
INTERPRETACIÓN DE RESULTADOS
-----------------------------
"""
    
    r2 = regression_metrics.get('r2_score', 0)
    if r2 > 0.8:
        report += "El modelo muestra un excelente ajuste (R² > 0.8), explicando más del 80% de la varianza.\n"
    elif r2 > 0.6:
        report += "El modelo muestra un buen ajuste (R² > 0.6), explicando más del 60% de la varianza.\n"
    elif r2 > 0.4:
        report += "El modelo muestra un ajuste moderado (R² > 0.4), explicando más del 40% de la varianza.\n"
    else:
        report += "El modelo muestra un ajuste limitado. Se recomienda revisar características y parámetros.\n"
    
    report += f"""
ANÁLISIS DE CARACTERÍSTICAS
---------------------------
El modelo utiliza múltiples características derivadas de estadísticas de partidos NBA,
incluyendo variables diferenciales entre equipos locales y visitantes, características
temporales y variables de eficiencia para predecir el diferencial de puntos.

RECOMENDACIONES
---------------
1. El modelo está listo para predicciones del diferencial de puntos
2. Se recomienda actualizar el modelo regularmente con datos recientes
3. Considerar la incorporación de datos adicionales como lesiones de jugadores clave
4. Monitorear el rendimiento del modelo en producción
5. Validar predicciones con expertos en NBA para mejorar el modelo

---
Reporte generado automáticamente por el pipeline de regresión NBA
"""
    
    logger.info("Reporte del modelo de regresión creado")
    
    return report
