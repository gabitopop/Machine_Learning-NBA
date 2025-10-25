from kedro.pipeline import Node, Pipeline

from .nodes import (
    split_data, 
    train_random_forest, 
    train_gradient_boosting, 
    train_logistic_regression,
    train_ensemble_models,
    train_linear_models,
    train_other_models,
    create_model_comparison_table,
    evaluate_model,
    select_best_model
)


def create_pipeline(**kwargs) -> Pipeline:
    """Crea el pipeline de ciencia de datos para el proyecto NBA.
    
    Este pipeline entrena múltiples modelos de clasificación para predecir
    ganadores de partidos de la NBA y selecciona el mejor modelo.
    
    Returns:
        Pipeline de ciencia de datos NBA.
    """
    return Pipeline(
        [
            Node(
                func=split_data,
                inputs=["model_input_table", "params:data_science"],
                outputs=["X_train", "X_val", "X_test", "y_train", "y_val", "y_test"],
                name="split_data_node",
                tags=["data_splitting", "nba"],
            ),
            # Modelos Ensemble con GridSearch
            Node(
                func=train_ensemble_models,
                inputs=["X_train", "y_train", "params:data_science"],
                outputs="ensemble_models",
                name="train_ensemble_models_node",
                tags=["model_training", "ensemble", "nba"],
            ),
            # Modelos Lineales con GridSearch
            Node(
                func=train_linear_models,
                inputs=["X_train", "y_train", "params:data_science"],
                outputs=["linear_models", "scaler"],
                name="train_linear_models_node",
                tags=["model_training", "linear", "nba"],
            ),
            # Otros Modelos con GridSearch
            Node(
                func=train_other_models,
                inputs=["X_train", "y_train", "params:data_science"],
                outputs="other_models",
                name="train_other_models_node",
                tags=["model_training", "other", "nba"],
            ),
            # Crear tabla comparativa
            Node(
                func=create_model_comparison_table,
                inputs=["ensemble_models", "linear_models", "other_models", "X_val", "y_val"],
                outputs="model_comparison_table",
                name="create_model_comparison_table_node",
                tags=["model_comparison", "nba"],
            ),
            # Seleccionar mejor modelo
            Node(
                func=select_best_model,
                inputs=["ensemble_models", "linear_models", "other_models", "X_val", "y_val"],
                outputs=["nba_classifier", "best_model_name", "best_model_metrics"],
                name="select_best_model_node",
                tags=["model_selection", "nba"],
            ),
            # Evaluar modelo final
            Node(
                func=evaluate_model,
                inputs=["nba_classifier", "X_test", "y_test", "params:data_science"],
                outputs="model_metrics",
                name="evaluate_model_node",
                tags=["model_evaluation", "nba"],
            ),
        ]
    )
