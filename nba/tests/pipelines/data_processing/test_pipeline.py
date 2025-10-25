import logging
import pandas as pd
import pytest
import numpy as np
from kedro.io import DataCatalog
from kedro.runner import SequentialRunner
from nba.pipelines.data_processing import create_pipeline as create_dp_pipeline
from nba.pipelines.data_processing.nodes import clean_nba_data, create_features, create_model_input_table


@pytest.fixture
def dummy_games_data():
    """Datos de prueba para partidos de NBA."""
    np.random.seed(42)
    n_samples = 100
    
    return pd.DataFrame({
        # Variables básicas
        'game_id': range(1, n_samples + 1),
        'game_date': pd.date_range('2020-01-01', periods=n_samples, freq='D'),
        'season_id': np.random.randint(2015, 2023, n_samples),
        'season_type': np.random.choice(['Regular Season', 'Playoffs'], n_samples),
        
        # Estadísticas locales
        'pts_home': np.random.normal(110, 15, n_samples),
        'fg_pct_home': np.random.uniform(0.4, 0.6, n_samples),
        'fg3_pct_home': np.random.uniform(0.3, 0.4, n_samples),
        'ft_pct_home': np.random.uniform(0.7, 0.9, n_samples),
        'reb_home': np.random.normal(45, 8, n_samples),
        'oreb_home': np.random.normal(12, 3, n_samples),
        'dreb_home': np.random.normal(33, 6, n_samples),
        'ast_home': np.random.normal(25, 6, n_samples),
        'stl_home': np.random.normal(8, 2, n_samples),
        'blk_home': np.random.normal(5, 2, n_samples),
        'tov_home': np.random.normal(15, 3, n_samples),
        'pf_home': np.random.normal(22, 4, n_samples),
        'plus_minus_home': np.random.normal(2, 20, n_samples),
        'fga_home': np.random.normal(85, 10, n_samples),
        
        # Estadísticas visitantes
        'pts_away': np.random.normal(108, 15, n_samples),
        'fg_pct_away': np.random.uniform(0.4, 0.6, n_samples),
        'fg3_pct_away': np.random.uniform(0.3, 0.4, n_samples),
        'ft_pct_away': np.random.uniform(0.7, 0.9, n_samples),
        'reb_away': np.random.normal(44, 8, n_samples),
        'oreb_away': np.random.normal(11, 3, n_samples),
        'dreb_away': np.random.normal(33, 6, n_samples),
        'ast_away': np.random.normal(24, 6, n_samples),
        'stl_away': np.random.normal(8, 2, n_samples),
        'blk_away': np.random.normal(5, 2, n_samples),
        'tov_away': np.random.normal(15, 3, n_samples),
        'pf_away': np.random.normal(23, 4, n_samples),
        'plus_minus_away': np.random.normal(-2, 20, n_samples),
        'fga_away': np.random.normal(84, 10, n_samples),
        
        # Variables categóricas
        'team_abbreviation_home': np.random.choice(['LAL', 'GSW', 'BOS', 'MIA', 'PHX'], n_samples),
        'team_abbreviation_away': np.random.choice(['LAL', 'GSW', 'BOS', 'MIA', 'PHX'], n_samples),
        'wl_home': np.random.choice(['W', 'L'], n_samples),
        'wl_away': np.random.choice(['W', 'L'], n_samples),
    })


@pytest.fixture
def dummy_data_processing_parameters():
    """Parámetros de prueba para procesamiento de datos."""
    return {
        "data_cleaning": {
            "imputation_strategy": {
                "numeric": "median",
                "categorical": "mode"
            },
            "outlier_detection": {
                "method": "iqr",
                "multiplier": 1.5,
                "treatment": "cap"
            },
            "exclude_from_outlier_analysis": [
                "game_id", "season_id", "team_id_home", "team_id_away", "game_date"
            ]
        },
        "data_transformation": {
            "date_features": [
                "year", "month", "day", "day_of_week", "day_of_year", 
                "week_of_year", "is_weekend", "is_playoff_season"
            ],
            "categorical_encoding": {
                "one_hot": ["season_type"],
                "label": ["team_abbreviation_home", "team_abbreviation_away"]
            },
            "differential_features": [
                "pts_diff", "fg_pct_diff", "reb_diff", "ast_diff", 
                "stl_diff", "blk_diff", "tov_diff", "efficiency_diff"
            ],
            "scaling": {
                "method": "standard",
                "features_to_scale": [
                    "pts_home", "pts_away", "fg_pct_home", "fg_pct_away",
                    "reb_home", "reb_away", "ast_home", "ast_away"
                ]
            }
        }
    }


@pytest.fixture
def dummy_data_science_parameters():
    """Parámetros de prueba para ciencia de datos."""
    return {
        "target": "home_win",
        "features": {
            "numeric_features": [
                "pts_home", "pts_away", "fg_pct_home", "fg_pct_away",
                "reb_home", "reb_away", "ast_home", "ast_away"
            ],
            "differential_features": [
                "pts_diff", "fg_pct_diff", "reb_diff", "ast_diff"
            ],
            "date_features": [
                "year", "month", "day_of_week", "is_weekend", "is_playoff_season"
            ],
            "categorical_features": [
                "team_home_encoded", "team_away_encoded"
            ]
        }
    }


def test_clean_nba_data(dummy_games_data, dummy_data_processing_parameters):
    """Test de la función clean_nba_data."""
    # Agregar algunos valores nulos para probar la limpieza
    data_with_nulls = dummy_games_data.copy()
    data_with_nulls.loc[0:5, 'pts_home'] = np.nan
    data_with_nulls.loc[10:15, 'wl_home'] = np.nan
    
    # Limpiar datos
    cleaned_data = clean_nba_data(data_with_nulls, dummy_data_processing_parameters)
    
    # Verificar que no hay valores nulos
    assert cleaned_data.isnull().sum().sum() == 0
    
    # Verificar que se mantiene la forma básica
    assert cleaned_data.shape[0] == dummy_games_data.shape[0]
    assert cleaned_data.shape[1] >= dummy_games_data.shape[1]
    
    # Verificar que las fechas se convirtieron correctamente
    assert pd.api.types.is_datetime64_any_dtype(cleaned_data['game_date'])


def test_create_features(dummy_games_data, dummy_data_processing_parameters):
    """Test de la función create_features."""
    # Primero limpiar los datos
    cleaned_data = clean_nba_data(dummy_games_data, dummy_data_processing_parameters)
    
    # Crear características
    features_data = create_features(cleaned_data, dummy_data_processing_parameters)
    
    # Verificar que se crearon nuevas columnas
    assert features_data.shape[1] > cleaned_data.shape[1]
    
    # Verificar variables de fecha
    expected_date_features = dummy_data_processing_parameters["data_transformation"]["date_features"]
    for feature in expected_date_features:
        assert feature in features_data.columns
    
    # Verificar variable objetivo
    assert 'home_win' in features_data.columns
    assert features_data['home_win'].dtype in [np.int64, np.int32, bool]
    
    # Verificar variables diferenciales
    expected_diff_features = dummy_data_processing_parameters["data_transformation"]["differential_features"]
    for feature in expected_diff_features:
        if feature != "efficiency_diff":  # efficiency_diff se crea internamente
            assert feature in features_data.columns
    
    # Verificar codificación de equipos
    assert 'team_home_encoded' in features_data.columns
    assert 'team_away_encoded' in features_data.columns


def test_create_model_input_table(dummy_games_data, dummy_data_processing_parameters, dummy_data_science_parameters):
    """Test de la función create_model_input_table."""
    # Procesar datos completos
    cleaned_data = clean_nba_data(dummy_games_data, dummy_data_processing_parameters)
    features_data = create_features(cleaned_data, dummy_data_processing_parameters)
    
    # Crear tabla de entrada del modelo
    model_data = create_model_input_table(features_data, dummy_data_science_parameters)
    
    # Verificar que tiene la variable objetivo
    assert dummy_data_science_parameters["target"] in model_data.columns
    
    # Verificar que tiene características
    assert model_data.shape[1] > 1  # Más que solo la variable objetivo
    
    # Verificar que no hay valores nulos
    assert model_data.isnull().sum().sum() == 0
    
    # Verificar distribución de la variable objetivo
    target_dist = model_data[dummy_data_science_parameters["target"]].value_counts()
    assert len(target_dist) == 2  # Debe tener 2 clases


def test_data_processing_pipeline(caplog, dummy_games_data, dummy_data_processing_parameters, dummy_data_science_parameters):
    """Test del pipeline completo de procesamiento de datos."""
    # Crear pipeline
    pipeline = create_dp_pipeline()
    
    catalog = DataCatalog()
    catalog["game"] = dummy_games_data
    catalog["params:data_processing"] = dummy_data_processing_parameters
    catalog["params:data_science"] = dummy_data_science_parameters
    
    caplog.set_level(logging.INFO, logger="kedro")
    successful_run_msg = "Pipeline execution completed successfully"
    
    SequentialRunner().run(pipeline, catalog)
    
    assert successful_run_msg in caplog.text


def test_clean_nba_data_with_outliers(dummy_games_data, dummy_data_processing_parameters):
    """Test de limpieza con outliers extremos."""
    # Crear datos con outliers extremos
    data_with_outliers = dummy_games_data.copy()
    data_with_outliers.loc[0, 'pts_home'] = 300  # Outlier extremo
    data_with_outliers.loc[1, 'pts_away'] = 50   # Outlier extremo
    
    # Limpiar datos
    cleaned_data = clean_nba_data(data_with_outliers, dummy_data_processing_parameters)
    
    # Verificar que los outliers fueron tratados
    assert cleaned_data['pts_home'].max() < 300
    assert cleaned_data['pts_away'].min() > 50
    
    # Verificar que no hay valores nulos
    assert cleaned_data.isnull().sum().sum() == 0


def test_create_features_with_missing_columns(dummy_games_data, dummy_data_processing_parameters):
    """Test de creación de características con columnas faltantes."""
    # Remover algunas columnas para probar robustez
    data_missing_cols = dummy_games_data.drop(columns=['fg3_pct_home', 'fg3_pct_away'])
    
    # Limpiar datos
    cleaned_data = clean_nba_data(data_missing_cols, dummy_data_processing_parameters)
    
    # Crear características (debe manejar columnas faltantes)
    features_data = create_features(cleaned_data, dummy_data_processing_parameters)
    
    # Verificar que se crearon características básicas
    assert 'home_win' in features_data.columns
    assert 'year' in features_data.columns
    assert 'month' in features_data.columns
