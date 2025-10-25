"""Project pipelines para el proyecto NBA."""

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline


def register_pipelines() -> dict[str, Pipeline]:
    """Registra los pipelines del proyecto NBA.

    Este proyecto incluye tres pipelines principales:
    1. data_processing: Limpieza y preparación de datos NBA
    2. data_science: Entrenamiento y evaluación de modelos de ML
    3. reporting: Generación de visualizaciones y reportes

    Returns:
        Un mapeo de nombres de pipelines a objetos ``Pipeline``.
    """
    pipelines = find_pipelines()
    
    # Pipeline completo (todos los pipelines combinados)
    pipelines["__default__"] = sum(pipelines.values())
    
    # Pipeline solo de procesamiento de datos
    pipelines["data_processing"] = pipelines["data_processing"]
    
    # Pipeline solo de ciencia de datos
    pipelines["data_science"] = pipelines["data_science"]
    
    # Pipeline solo de reportes
    pipelines["reporting"] = pipelines["reporting"]
    
    # Pipeline de ML completo (procesamiento + ciencia de datos)
    pipelines["ml_pipeline"] = pipelines["data_processing"] + pipelines["data_science"]
    
    # Pipeline completo con reportes
    pipelines["full_pipeline"] = sum(pipelines.values())
    
    return pipelines
