from kedro.pipeline import Node, Pipeline

from .nodes import (
    create_win_distribution_plot,
    create_correlation_matrix_plot,
    create_feature_importance_plot,
    create_confusion_matrix_plot,
    create_roc_curve_plot,
    create_model_report,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Crea el pipeline de reportes para el proyecto NBA.
    
    Este pipeline genera visualizaciones y reportes del modelo de predicción
    de ganadores de partidos NBA, incluyendo gráficos de distribución,
    correlaciones, importancia de características y métricas de evaluación.
    
    Returns:
        Pipeline de reportes NBA.
    """
    return Pipeline(
        [
            Node(
                func=create_win_distribution_plot,
                inputs=["model_input_table", "params:reporting"],
                outputs="win_distribution_plot",
                name="create_win_distribution_plot_node",
                tags=["visualization", "nba"],
            ),
            Node(
                func=create_correlation_matrix_plot,
                inputs=["model_input_table", "params:reporting"],
                outputs="correlation_matrix_plot",
                name="create_correlation_matrix_plot_node",
                tags=["visualization", "nba"],
            ),
            Node(
                func=create_feature_importance_plot,
                inputs=["nba_classifier", "X_train", "params:reporting"],
                outputs="feature_importance_plot",
                name="create_feature_importance_plot_node",
                tags=["visualization", "nba"],
            ),
            Node(
                func=create_confusion_matrix_plot,
                inputs=["model_metrics", "params:reporting"],
                outputs="confusion_matrix_plot",
                name="create_confusion_matrix_plot_node",
                tags=["visualization", "nba"],
            ),
            Node(
                func=create_roc_curve_plot,
                inputs=["nba_classifier", "X_test", "y_test", "params:reporting"],
                outputs="roc_curve_plot",
                name="create_roc_curve_plot_node",
                tags=["visualization", "nba"],
            ),
            Node(
                func=create_model_report,
                inputs=["model_metrics", "best_model_name", "params:reporting"],
                outputs="model_report",
                name="create_model_report_node",
                tags=["reporting", "nba"],
            ),
        ]
    )
