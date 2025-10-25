import logging
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)


def clean_nba_data(games: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    """Limpia los datos de partidos de la NBA.

    Args:
        games: Datos raw de partidos de la NBA.
        parameters: Parámetros de limpieza definidos en parameters_data_processing.yml.
    
    Returns:
        Datos limpios de partidos.
    """
    logger.info("Iniciando limpieza de datos NBA...")
    df_clean = games.copy()
    
    # 1. Análisis de valores nulos
    null_analysis = pd.DataFrame({
        'Valores_Nulos': df_clean.isnull().sum(),
        'Porcentaje_Nulos': (df_clean.isnull().sum() / len(df_clean)) * 100
    }).sort_values('Porcentaje_Nulos', ascending=False)
    
    null_columns = null_analysis[null_analysis['Valores_Nulos'] > 0]
    logger.info(f"Columnas con valores nulos: {len(null_columns)}")
    
    # 2. Imputación de valores nulos
    imputation_strategy = parameters["data_cleaning"]["imputation_strategy"]
    
    # Variables numéricas: imputación con mediana
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_clean[col].isnull().any():
            median_value = df_clean[col].median()
            df_clean[col].fillna(median_value, inplace=True)
            logger.info(f"Imputado {col} con mediana: {median_value:.2f}")
    
    # Variables categóricas: imputación con moda
    categorical_cols = df_clean.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df_clean[col].isnull().any():
            mode_value = df_clean[col].mode().iloc[0] if not df_clean[col].mode().empty else 'Unknown'
            df_clean[col].fillna(mode_value, inplace=True)
            logger.info(f"Imputado {col} con moda: {mode_value}")
    
    # 3. Tratamiento de outliers
    outlier_config = parameters["data_cleaning"]["outlier_detection"]
    exclude_cols = parameters["data_cleaning"]["exclude_from_outlier_analysis"]
    
    def detect_and_cap_outliers(data, column, multiplier=1.5):
        """Detecta y capa outliers usando el método IQR."""
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outliers_before = ((data[column] < lower_bound) | (data[column] > upper_bound)).sum()
        data[column] = np.clip(data[column], lower_bound, upper_bound)
        outliers_after = ((data[column] < lower_bound) | (data[column] > upper_bound)).sum()
        
        return outliers_before, outliers_after
    
    outliers_treated = 0
    for col in numeric_cols:
        if col not in exclude_cols and col in df_clean.columns:
            outliers_before, outliers_after = detect_and_cap_outliers(
                df_clean, col, outlier_config["multiplier"]
            )
            if outliers_before > 0:
                outliers_treated += outliers_before
                logger.info(f"Outliers tratados en {col}: {outliers_before}")
    
    # 4. Corrección de inconsistencias
    # Convertir fechas
    df_clean['game_date'] = pd.to_datetime(df_clean['game_date'])
    
    # Corregir porcentajes (convertir de 0-100 a 0-1 si es necesario)
    percentage_cols = [col for col in df_clean.columns if 'pct' in col.lower()]
    for col in percentage_cols:
        if col in df_clean.columns and df_clean[col].max() > 1:
            df_clean[col] = df_clean[col] / 100
            logger.info(f"Convertido {col} de escala 0-100 a 0-1")
    
    # Corregir valores negativos en estadísticas que no deberían tenerlos
    positive_cols = ['pts_home', 'pts_away', 'reb_home', 'reb_away', 'ast_home', 'ast_away']
    for col in positive_cols:
        if col in df_clean.columns:
            negative_count = (df_clean[col] < 0).sum()
            if negative_count > 0:
                df_clean[col] = np.maximum(df_clean[col], 0)
                logger.info(f"Corregidos {negative_count} valores negativos en {col}")
    
    # Verificar que no queden valores nulos
    remaining_nulls = df_clean.isnull().sum().sum()
    logger.info(f"Valores nulos restantes: {remaining_nulls}")
    logger.info(f"Total de outliers tratados: {outliers_treated}")
    logger.info(f"Dataset limpio: {df_clean.shape}")
    
    return df_clean


def create_features(games_cleaned: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    """Crea características (features) para el modelo de NBA.

    Args:
        games_cleaned: Datos limpios de partidos.
        parameters: Parámetros de transformación definidos en parameters_data_processing.yml.
    
    Returns:
        Datos con características creadas.
    """
    logger.info("Iniciando creación de características...")
    df_features = games_cleaned.copy()
    
    # 1. Variables de fecha
    date_features = parameters["data_transformation"]["date_features"]
    df_features['year'] = df_features['game_date'].dt.year
    df_features['month'] = df_features['game_date'].dt.month
    df_features['day'] = df_features['game_date'].dt.day
    df_features['day_of_week'] = df_features['game_date'].dt.dayofweek
    df_features['day_of_year'] = df_features['game_date'].dt.dayofyear
    df_features['week_of_year'] = df_features['game_date'].dt.isocalendar().week
    df_features['is_weekend'] = (df_features['day_of_week'] >= 5).astype(int)
    df_features['is_playoff_season'] = (df_features['month'].isin([4, 5, 6])).astype(int)
    
    logger.info("Variables de fecha creadas")
    
    # 2. Variable objetivo binaria
    df_features['home_win'] = (df_features['wl_home'] == 'W').astype(int)
    logger.info("Variable objetivo binaria creada: home_win")
    
    # 3. Codificación de variables categóricas
    categorical_encoding = parameters["data_transformation"]["categorical_encoding"]
    
    # One-Hot Encoding para season_type
    if 'season_type' in categorical_encoding.get('one_hot', []):
        season_type_dummies = pd.get_dummies(df_features['season_type'], prefix='season')
        df_features = pd.concat([df_features, season_type_dummies], axis=1)
        logger.info(f"season_type codificado con One-Hot: {list(season_type_dummies.columns)}")
    
    # Label Encoding para equipos
    if 'team_abbreviation_home' in categorical_encoding.get('label', []):
        le_home = LabelEncoder()
        df_features['team_home_encoded'] = le_home.fit_transform(df_features['team_abbreviation_home'])
        logger.info(f"Equipos locales codificados: {df_features['team_home_encoded'].nunique()} equipos únicos")
    
    if 'team_abbreviation_away' in categorical_encoding.get('label', []):
        le_away = LabelEncoder()
        df_features['team_away_encoded'] = le_away.fit_transform(df_features['team_abbreviation_away'])
        logger.info(f"Equipos visitantes codificados: {df_features['team_away_encoded'].nunique()} equipos únicos")
    
    # 4. Variables diferenciales
    differential_features = parameters["data_transformation"]["differential_features"]
    
    if 'pts_diff' in differential_features:
        df_features['pts_diff'] = df_features['pts_home'] - df_features['pts_away']
    if 'fg_pct_diff' in differential_features:
        df_features['fg_pct_diff'] = df_features['fg_pct_home'] - df_features['fg_pct_away']
    if 'reb_diff' in differential_features:
        df_features['reb_diff'] = df_features['reb_home'] - df_features['reb_away']
    if 'ast_diff' in differential_features:
        df_features['ast_diff'] = df_features['ast_home'] - df_features['ast_away']
    if 'stl_diff' in differential_features:
        df_features['stl_diff'] = df_features['stl_home'] - df_features['stl_away']
    if 'blk_diff' in differential_features:
        df_features['blk_diff'] = df_features['blk_home'] - df_features['blk_away']
    if 'tov_diff' in differential_features:
        df_features['tov_diff'] = df_features['tov_home'] - df_features['tov_away']
    
    logger.info("Variables diferenciales creadas")
    
    # 5. Variables de eficiencia
    df_features['home_efficiency'] = df_features['pts_home'] / (df_features['fga_home'] + 0.001)
    df_features['away_efficiency'] = df_features['pts_away'] / (df_features['fga_away'] + 0.001)
    df_features['efficiency_diff'] = df_features['home_efficiency'] - df_features['away_efficiency']
    
    logger.info("Variables de eficiencia creadas")
    
    # 6. Escalado de variables numéricas
    scaling_config = parameters["data_transformation"]["scaling"]
    features_to_scale = scaling_config["features_to_scale"]
    
    # Filtrar variables que existen en el dataset
    available_features = [col for col in features_to_scale if col in df_features.columns]
    
    if scaling_config["method"] == "standard":
        scaler = StandardScaler()
        df_features[available_features] = scaler.fit_transform(df_features[available_features])
        logger.info(f"StandardScaler aplicado a {len(available_features)} variables")
        logger.info(f"Media de variables escaladas: {df_features[available_features].mean().mean():.6f}")
        logger.info(f"Desviación estándar: {df_features[available_features].std().mean():.6f}")
    
    # 7. Verificación final
    inf_count = np.isinf(df_features.select_dtypes(include=[np.number])).sum().sum()
    nan_count = df_features.isnull().sum().sum()
    
    if inf_count > 0:
        logger.warning(f"Corrigiendo {inf_count} valores infinitos...")
        df_features = df_features.replace([np.inf, -np.inf], np.nan)
        df_features = df_features.fillna(0)
    
    logger.info(f"Dataset con características: {df_features.shape}")
    logger.info(f"Valores infinitos: {inf_count}")
    logger.info(f"Valores nulos: {nan_count}")
    
    return df_features


def create_model_input_table(games_features: pd.DataFrame, parameters: dict) -> pd.DataFrame:
    """Crea la tabla de entrada para el modelo de NBA.

    Args:
        games_features: Datos con características creadas.
        parameters: Parámetros de ciencia de datos definidos en parameters_data_science.yml.
    
    Returns:
        Tabla de entrada para el modelo.
    """
    logger.info("Creando tabla de entrada para el modelo...")
    
    # Seleccionar variables predictoras
    feature_columns = []
    
    # Variables numéricas
    if 'numeric_features' in parameters['features']:
        feature_columns.extend(parameters['features']['numeric_features'])
    
    # Variables diferenciales
    if 'differential_features' in parameters['features']:
        feature_columns.extend(parameters['features']['differential_features'])
    
    # Variables de fecha
    if 'date_features' in parameters['features']:
        feature_columns.extend(parameters['features']['date_features'])
    
    # Variables categóricas
    if 'categorical_features' in parameters['features']:
        feature_columns.extend(parameters['features']['categorical_features'])
    
    # Filtrar variables que existen en el dataset
    available_features = [col for col in feature_columns if col in games_features.columns]
    
    # Agregar variables de season_type (One-Hot)
    season_columns = [col for col in games_features.columns if col.startswith('season_')]
    available_features.extend(season_columns)
    
    # Crear dataset final
    target_column = parameters['target']
    model_data = games_features[available_features + [target_column]].copy()
    
    logger.info(f"Tabla de entrada creada: {model_data.shape}")
    logger.info(f"Variables predictoras: {len(available_features)}")
    logger.info(f"Variable objetivo: {target_column}")
    
    # Verificar distribución de la variable objetivo
    target_distribution = model_data[target_column].value_counts()
    logger.info(f"Distribución de clases:")
    logger.info(f"  Clase 0 (Derrota Local): {target_distribution[0]:,} ({target_distribution[0]/len(model_data):.1%})")
    logger.info(f"  Clase 1 (Victoria Local): {target_distribution[1]:,} ({target_distribution[1]/len(model_data):.1%})")
    
    return model_data
