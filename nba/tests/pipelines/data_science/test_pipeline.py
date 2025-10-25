import logging
import pandas as pd
import pytest
import numpy as np
from kedro.io import DataCatalog
from kedro.runner import SequentialRunner
from nba.pipelines.data_science import create_pipeline as create_ds_pipeline
from nba.pipelines.data_science.nodes import split_data, train_random_forest, evaluate_model
from sklearn.ensemble import RandomForestClassifier


@pytest.fixture
def dummy_nba_data():
    """Datos de prueba para el proyecto NBA."""
    np.random.seed(42)
    n_samples = 100
    
    return pd.DataFrame({
        # Variables numéricas
        'pts_home': np.random.normal(110, 15, n_samples),
        'pts_away': np.random.normal(108, 15, n_samples),
        'fg_pct_home': np.random.uniform(0.4, 0.6, n_samples),
        'fg_pct_away': np.random.uniform(0.4, 0.6, n_samples),
        'reb_home': np.random.normal(45, 8, n_samples),
        'reb_away': np.random.normal(44, 8, n_samples),
        'ast_home': np.random.normal(25, 6, n_samples),
        'ast_away': np.random.normal(24, 6, n_samples),
        
        # Variables diferenciales
        'pts_diff': np.random.normal(2, 20, n_samples),
        'fg_pct_diff': np.random.normal(0, 0.1, n_samples),
        'reb_diff': np.random.normal(1, 10, n_samples),
        'ast_diff': np.random.normal(1, 8, n_samples),
        
        # Variables de fecha
        'year': np.random.randint(2015, 2023, n_samples),
        'month': np.random.randint(1, 13, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'is_weekend': np.random.randint(0, 2, n_samples),
        'is_playoff_season': np.random.randint(0, 2, n_samples),
        
        # Variables categóricas codificadas
        'team_home_encoded': np.random.randint(0, 30, n_samples),
        'team_away_encoded': np.random.randint(0, 30, n_samples),
        'season_Regular Season': np.random.randint(0, 2, n_samples),
        'season_Playoffs': np.random.randint(0, 2, n_samples),
        
        # Variable objetivo
        'home_win': np.random.randint(0, 2, n_samples)
    })


@pytest.fixture
def dummy_nba_parameters():
    """Parámetros de prueba para el proyecto NBA."""
    return {
        "data_splitting": {
            "test_size": 0.2,
            "val_size": 0.2,
            "random_state": 42,
            "stratify": True
        },
        "target": "home_win",
        "features": {
            "numeric_features": [
                'pts_home', 'pts_away', 'fg_pct_home', 'fg_pct_away',
                'reb_home', 'reb_away', 'ast_home', 'ast_away'
            ],
            "differential_features": [
                'pts_diff', 'fg_pct_diff', 'reb_diff', 'ast_diff'
            ],
            "date_features": [
                'year', 'month', 'day_of_week', 'is_weekend', 'is_playoff_season'
            ],
            "categorical_features": [
                'team_home_encoded', 'team_away_encoded',
                'season_Regular Season', 'season_Playoffs'
            ]
        },
        "models": {
            "random_forest": {
                "n_estimators": 10,  # Reducido para tests
                "max_depth": 5,
                "min_samples_split": 2,
                "min_samples_leaf": 1,
                "random_state": 42,
                "n_jobs": 1
            }
        },
        "cross_validation": {
            "n_splits": 3,  # Reducido para tests
            "shuffle": True,
            "random_state": 42,
            "scoring": "roc_auc"
        }
    }


def test_split_data(dummy_nba_data, dummy_nba_parameters):
    """Test de la función split_data."""
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(
        dummy_nba_data, dummy_nba_parameters
    )
    
    # Verificar que se devuelven 6 conjuntos
    assert len([X_train, X_val, X_test, y_train, y_val, y_test]) == 6
    
    # Verificar dimensiones
    assert X_train.shape[1] > 0  # Debe tener características
    assert X_val.shape[1] > 0
    assert X_test.shape[1] > 0
    assert len(y_train) > 0
    assert len(y_val) > 0
    assert len(y_test) > 0
    
    # Verificar que no hay overlap
    assert len(set(X_train.index) & set(X_val.index)) == 0
    assert len(set(X_train.index) & set(X_test.index)) == 0
    assert len(set(X_val.index) & set(X_test.index)) == 0


def test_split_data_missing_target(dummy_nba_data, dummy_nba_parameters):
    """Test de split_data con variable objetivo faltante."""
    dummy_data_missing_target = dummy_nba_data.drop(columns="home_win")
    
    with pytest.raises(KeyError) as e_info:
        split_data(dummy_data_missing_target, dummy_nba_parameters)
    
    assert "home_win" in str(e_info.value)


def test_train_random_forest(dummy_nba_data, dummy_nba_parameters):
    """Test de la función train_random_forest."""
    # Preparar datos
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(
        dummy_nba_data, dummy_nba_parameters
    )
    
    # Entrenar modelo
    model = train_random_forest(X_train, y_train, dummy_nba_parameters)
    
    # Verificar que es un RandomForestClassifier
    assert isinstance(model, RandomForestClassifier)
    
    # Verificar que está entrenado
    assert hasattr(model, 'feature_importances_')
    assert len(model.feature_importances_) == X_train.shape[1]


def test_evaluate_model(dummy_nba_data, dummy_nba_parameters):
    """Test de la función evaluate_model."""
    # Preparar datos
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(
        dummy_nba_data, dummy_nba_parameters
    )
    
    # Entrenar modelo
    model = train_random_forest(X_train, y_train, dummy_nba_parameters)
    
    # Evaluar modelo
    metrics = evaluate_model(model, X_test, y_test, dummy_nba_parameters)
    
    # Verificar métricas
    assert 'accuracy' in metrics
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'f1_score' in metrics
    assert 'roc_auc' in metrics
    assert 'confusion_matrix' in metrics
    assert 'classification_report' in metrics
    
    # Verificar que las métricas están en el rango correcto
    assert 0 <= metrics['accuracy'] <= 1
    assert 0 <= metrics['precision'] <= 1
    assert 0 <= metrics['recall'] <= 1
    assert 0 <= metrics['f1_score'] <= 1
    assert 0 <= metrics['roc_auc'] <= 1


def test_data_science_pipeline(caplog, dummy_nba_data, dummy_nba_parameters):
    """Test del pipeline completo de data science."""
    # Crear pipeline solo con split_data para test rápido
    pipeline = (
        create_ds_pipeline()
        .from_nodes("split_data_node")
        .to_nodes("split_data_node")
    )
    
    catalog = DataCatalog()
    catalog["model_input_table"] = dummy_nba_data
    catalog["params:data_science"] = dummy_nba_parameters
    
    caplog.set_level(logging.INFO, logger="kedro")
    successful_run_msg = "Pipeline execution completed successfully"
    
    SequentialRunner().run(pipeline, catalog)
    
    assert successful_run_msg in caplog.text


def test_data_science_pipeline_with_training(caplog, dummy_nba_data, dummy_nba_parameters):
    """Test del pipeline completo incluyendo entrenamiento."""
    # Crear pipeline con entrenamiento
    pipeline = (
        create_ds_pipeline()
        .from_nodes("split_data_node")
        .to_nodes("train_random_forest_node")
    )
    
    catalog = DataCatalog()
    catalog["model_input_table"] = dummy_nba_data
    catalog["params:data_science"] = dummy_nba_parameters
    
    caplog.set_level(logging.INFO, logger="kedro")
    successful_run_msg = "Pipeline execution completed successfully"
    
    SequentialRunner().run(pipeline, catalog)
    
    assert successful_run_msg in caplog.text
