from kedro.pipeline import Node, Pipeline

from nba.pipelines.reporting.nodes import (
    create_regression_target_distribution,
    create_predicted_vs_actual_plot,
    create_residuals_plot,
    create_regression_report,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Crea el pipeline de reportes de regresión para el proyecto NBA.
    
    Este pipeline genera visualizaciones y reportes del modelo de regresión
    para predecir el diferencial de puntos en partidos NBA.
    
    Returns:
        Pipeline de reportes de regresión NBA.
    """
    return Pipeline(
        [
            Node(
                func=create_regression_target_distribution,
                inputs=["model_input_table", "params:regression"],
                outputs="regression_target_distribution_plot",
                name="create_regression_target_distribution_node",
                tags=["visualization", "regression", "nba"],
            ),
            Node(
                func=lambda name, params: {**params, "model_name": name},
                inputs=["best_regressor_name", "params:reporting"],
                outputs="regression_reporting_params",
                name="prepare_regression_reporting_params_node",
                tags=["preparation", "regression", "nba"],
            ),
            Node(
                func=create_predicted_vs_actual_plot,
                inputs=["nba_regressor", "final_regression_scaler", "X_test_reg", "y_test_reg", "regression_reporting_params"],
                outputs="predicted_vs_actual_plot",
                name="create_predicted_vs_actual_plot_node",
                tags=["visualization", "regression", "nba"],
            ),
            Node(
                func=create_residuals_plot,
                inputs=["nba_regressor", "final_regression_scaler", "X_test_reg", "y_test_reg", "regression_reporting_params"],
                outputs="residuals_plot",
                name="create_residuals_plot_node",
                tags=["visualization", "regression", "nba"],
            ),
            Node(
                func=create_regression_report,
                inputs=["regression_metrics", "best_regressor_name", "params:reporting"],
                outputs="regression_report",
                name="create_regression_report_node",
                tags=["reporting", "regression", "nba"],
            ),
        ]
    )

