from kedro.pipeline import Node, Pipeline

from .nodes import clean_nba_data, create_features, create_model_input_table


def create_pipeline(**kwargs) -> Pipeline:
    """Crea el pipeline de procesamiento de datos para el proyecto NBA.
    
    Este pipeline procesa los datos raw de partidos de la NBA a través de:
    1. Limpieza de datos (valores nulos, outliers, inconsistencias)
    2. Creación de características (feature engineering)
    3. Preparación de la tabla de entrada para el modelo
    
    Returns:
        Pipeline de procesamiento de datos NBA.
    """
    return Pipeline(
        [
            Node(
                func=clean_nba_data,
                inputs=["game", "params:data_processing"],
                outputs="games_cleaned",
                name="clean_nba_data_node",
                tags=["data_cleaning", "nba"],
            ),
            Node(
                func=create_features,
                inputs=["games_cleaned", "params:data_processing"],
                outputs="games_features",
                name="create_features_node",
                tags=["feature_engineering", "nba"],
            ),
            Node(
                func=create_model_input_table,
                inputs=["games_features", "params:data_science"],
                outputs="model_input_table",
                name="create_model_input_table_node",
                tags=["model_preparation", "nba"],
            ),
        ]
    )
