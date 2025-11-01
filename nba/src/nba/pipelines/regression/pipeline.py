from kedro.pipeline import Node, Pipeline

from .nodes import (
    split_data_regression,
    train_ensemble_regressors,
    train_linear_regressors,
    train_other_regressors,
    create_regression_comparison_table,
    evaluate_regressor,
    select_best_regressor
)


def create_pipeline(**kwargs) -> Pipeline:
    """Crea el pipeline de regresión para el proyecto NBA.
    
    Este pipeline entrena múltiples modelos de regresión para predecir
    el diferencial de puntos en partidos de la NBA y selecciona el mejor modelo.
    
    Returns:
        Pipeline de regresión NBA.
    """
    return Pipeline(
        [
            Node(
                func=split_data_regression,
                inputs=["model_input_table", "params:regression"],
                outputs=["X_train_reg", "X_val_reg", "X_test_reg", "y_train_reg", "y_val_reg", "y_test_reg"],
                name="split_data_regression_node",
                tags=["data_splitting", "regression", "nba"],
            ),
            # Modelos Ensemble con GridSearch
            Node(
                func=train_ensemble_regressors,
                inputs=["X_train_reg", "y_train_reg", "params:regression"],
                outputs="ensemble_regressors",
                name="train_ensemble_regressors_node",
                tags=["model_training", "ensemble", "regression", "nba"],
            ),
            # Modelos Lineales con GridSearch
            Node(
                func=train_linear_regressors,
                inputs=["X_train_reg", "y_train_reg", "params:regression"],
                outputs=["linear_regressors", "regression_scaler"],
                name="train_linear_regressors_node",
                tags=["model_training", "linear", "regression", "nba"],
            ),
            # Otros Modelos con GridSearch
            Node(
                func=train_other_regressors,
                inputs=["X_train_reg", "y_train_reg", "params:regression"],
                outputs="other_regressors",
                name="train_other_regressors_node",
                tags=["model_training", "other", "regression", "nba"],
            ),
            # Combinar todos los modelos
            Node(
                func=lambda ensemble, linear, other: {**ensemble, **linear, **other},
                inputs=["ensemble_regressors", "linear_regressors", "other_regressors"],
                outputs="all_regressors",
                name="combine_regressors_node",
                tags=["model_combination", "regression", "nba"],
            ),
            # Crear tabla comparativa
            Node(
                func=create_regression_comparison_table,
                inputs=["all_regressors", "regression_scaler", "X_val_reg", "y_val_reg"],
                outputs="regression_comparison_table",
                name="create_regression_comparison_table_node",
                tags=["model_comparison", "regression", "nba"],
            ),
            # Seleccionar mejor modelo
            Node(
                func=select_best_regressor,
                inputs=["all_regressors", "regression_scaler", "X_val_reg", "y_val_reg"],
                outputs=["nba_regressor", "best_regressor_name", "best_regressor_metrics", "final_regression_scaler"],
                name="select_best_regressor_node",
                tags=["model_selection", "regression", "nba"],
            ),
            # Preparar parámetros con nombre del modelo para evaluación
            Node(
                func=lambda name, params: {**params, "model_name": name},
                inputs=["best_regressor_name", "params:regression"],
                outputs="regression_params_with_model",
                name="prepare_regression_params_node",
                tags=["preparation", "regression", "nba"],
            ),
            # Evaluar modelo final
            Node(
                func=evaluate_regressor,
                inputs=["nba_regressor", "final_regression_scaler", "X_test_reg", "y_test_reg", "regression_params_with_model"],
                outputs="regression_metrics",
                name="evaluate_regressor_node",
                tags=["model_evaluation", "regression", "nba"],
            ),
        ]
    )

