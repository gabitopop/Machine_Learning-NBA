"""Project pipelines para el proyecto NBA."""

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline


def register_pipelines() -> dict[str, Pipeline]:
    """Registra los pipelines del proyecto NBA.

    Este proyecto incluye varios pipelines:
    1. data_processing: Limpieza y preparación de datos NBA
    2. data_science: Entrenamiento y evaluación de modelos de clasificación
    3. regression: Entrenamiento y evaluación de modelos de regresión
    4. reporting: Generación de visualizaciones y reportes (clasificación)
    5. regression_reporting: Generación de visualizaciones y reportes (regresión)

    Returns:
        Un mapeo de nombres de pipelines a objetos ``Pipeline``.
    """
    pipelines = find_pipelines()
    
    # Pipeline completo (todos los pipelines combinados)
    pipelines["__default__"] = sum(pipelines.values())
    
    # Pipeline solo de procesamiento de datos
    pipelines["data_processing"] = pipelines["data_processing"]
    
    # Pipeline solo de ciencia de datos (clasificación)
    pipelines["data_science"] = pipelines["data_science"]
    
    # Pipeline solo de reportes (clasificación)
    pipelines["reporting"] = pipelines["reporting"]
    
    # Pipeline de regresión
    pipelines["regression"] = pipelines["regression"]
    
    # Pipeline de reportes de regresión
    pipelines["regression_reporting"] = pipelines["regression_reporting"]
    
    # Pipeline de ML completo (procesamiento + ciencia de datos)
    pipelines["ml_pipeline"] = pipelines["data_processing"] + pipelines["data_science"]
    
    # Pipeline de regresión completo (procesamiento + regresión)
    pipelines["regression_pipeline"] = pipelines["data_processing"] + pipelines["regression"]
    
    # Pipeline completo de regresión con reportes
    pipelines["full_regression_pipeline"] = (
        pipelines["data_processing"] + 
        pipelines["regression"] + 
        pipelines["regression_reporting"]
    )
    
    # Pipeline completo con reportes (clasificación)
    pipelines["full_pipeline"] = (
        pipelines["data_processing"] + 
        pipelines["data_science"] + 
        pipelines["reporting"]
    )
    
    return pipelines
