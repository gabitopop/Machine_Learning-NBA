import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, KFold
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, AdaBoostRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, BayesianRidge
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    explained_variance_score, median_absolute_error
)
from sklearn.preprocessing import StandardScaler
import pickle
import json
import time

logger = logging.getLogger(__name__)


def split_data_regression(data: pd.DataFrame, parameters: dict) -> tuple:
    """Divide los datos en conjuntos de entrenamiento, validación y prueba para regresión.

    Args:
        data: Datos con características y variable objetivo.
        parameters: Parámetros definidos en parameters_regression.yml.
    
    Returns:
        Conjuntos de datos divididos (X_train, X_val, X_test, y_train, y_val, y_test).
    """
    logger.info("Iniciando división de datos para regresión...")
    
    # Configuración de división
    splitting_config = parameters["data_splitting"]
    target_column = parameters["target"]
    
    # Seleccionar características
    feature_columns = []
    if 'numeric_features' in parameters['features']:
        feature_columns.extend(parameters['features']['numeric_features'])
    if 'differential_features' in parameters['features']:
        feature_columns.extend(parameters['features']['differential_features'])
    if 'date_features' in parameters['features']:
        feature_columns.extend(parameters['features']['date_features'])
    if 'categorical_features' in parameters['features']:
        feature_columns.extend(parameters['features']['categorical_features'])
    
    # Agregar variables de season_type (One-Hot)
    season_columns = [col for col in data.columns if col.startswith('season_')]
    feature_columns.extend(season_columns)
    
    # Filtrar variables que existen en el dataset
    available_features = [col for col in feature_columns if col in data.columns]
    
    X = data[available_features]
    y = data[target_column]
    
    logger.info(f"Características seleccionadas: {len(available_features)}")
    logger.info(f"Variable objetivo: {target_column}")
    logger.info(f"Rango de valores objetivo: [{y.min():.2f}, {y.max():.2f}]")
    logger.info(f"Media de variable objetivo: {y.mean():.2f}")
    logger.info(f"Desviación estándar: {y.std():.2f}")
    
    # División sin estratificación (no es necesaria para regresión continua)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=splitting_config["test_size"],
        random_state=splitting_config["random_state"],
        shuffle=True
    )
    
    # División adicional para validación
    X_train_final, X_val, y_train_final, y_val = train_test_split(
        X_train, y_train,
        test_size=splitting_config["val_size"],
        random_state=splitting_config["random_state"],
        shuffle=True
    )
    
    logger.info(f"División completada:")
    logger.info(f"  Entrenamiento: {X_train_final.shape[0]:,} muestras")
    logger.info(f"  Validación: {X_val.shape[0]:,} muestras")
    logger.info(f"  Prueba: {X_test.shape[0]:,} muestras")
    
    return X_train_final, X_val, X_test, y_train_final, y_val, y_test


def train_ensemble_regressors(X_train: pd.DataFrame, y_train: pd.Series, parameters: dict) -> dict:
    """Entrena modelos de ensemble para regresión con GridSearch.
    
    Args:
        X_train: Datos de entrenamiento.
        y_train: Variable objetivo de entrenamiento.
        parameters: Parámetros del modelo.
    
    Returns:
        Diccionario con modelos entrenados.
    """
    logger.info("Entrenando modelos de ensemble para regresión con GridSearch...")
    
    models = {}
    cv = KFold(n_splits=parameters["cross_validation"]["n_splits"], shuffle=True, random_state=42)
    
    # Random Forest Regressor con GridSearch
    rf_params = {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    rf_grid = GridSearchCV(
        RandomForestRegressor(random_state=42),
        rf_params, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
    )
    rf_grid.fit(X_train, y_train)
    models['random_forest'] = rf_grid.best_estimator_
    logger.info(f"Random Forest - Mejores parámetros: {rf_grid.best_params_}")
    
    # Gradient Boosting Regressor con GridSearch
    gb_params = {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'subsample': [0.8, 0.9, 1.0]
    }
    gb_grid = GridSearchCV(
        GradientBoostingRegressor(random_state=42),
        gb_params, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
    )
    gb_grid.fit(X_train, y_train)
    models['gradient_boosting'] = gb_grid.best_estimator_
    logger.info(f"Gradient Boosting - Mejores parámetros: {gb_grid.best_params_}")
    
    # Extra Trees Regressor con GridSearch
    et_params = {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10]
    }
    et_grid = GridSearchCV(
        ExtraTreesRegressor(random_state=42),
        et_params, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
    )
    et_grid.fit(X_train, y_train)
    models['extra_trees'] = et_grid.best_estimator_
    logger.info(f"Extra Trees - Mejores parámetros: {et_grid.best_params_}")
    
    # AdaBoost Regressor con GridSearch
    ada_params = {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.1, 0.5, 1.0]
    }
    ada_grid = GridSearchCV(
        AdaBoostRegressor(random_state=42),
        ada_params, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
    )
    ada_grid.fit(X_train, y_train)
    models['ada_boost'] = ada_grid.best_estimator_
    logger.info(f"AdaBoost - Mejores parámetros: {ada_grid.best_params_}")
    
    return models


def train_linear_regressors(X_train: pd.DataFrame, y_train: pd.Series, parameters: dict) -> tuple:
    """Entrena modelos lineales para regresión con GridSearch.
    
    Args:
        X_train: Datos de entrenamiento.
        y_train: Variable objetivo de entrenamiento.
        parameters: Parámetros del modelo.
    
    Returns:
        Tupla con (diccionario de modelos, scaler).
    """
    logger.info("Entrenando modelos lineales para regresión con GridSearch...")
    
    models = {}
    cv = KFold(n_splits=parameters["cross_validation"]["n_splits"], shuffle=True, random_state=42)
    
    # Escalar datos para modelos lineales
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Linear Regression
    models['linear_regression'] = LinearRegression()
    models['linear_regression'].fit(X_train_scaled, y_train)
    logger.info("Linear Regression entrenado")
    
    # Ridge Regression con GridSearch
    ridge_params = {
        'alpha': [0.001, 0.01, 0.1, 1, 10, 100]
    }
    ridge_grid = GridSearchCV(
        Ridge(random_state=42),
        ridge_params, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
    )
    ridge_grid.fit(X_train_scaled, y_train)
    models['ridge'] = ridge_grid.best_estimator_
    logger.info(f"Ridge Regression - Mejores parámetros: {ridge_grid.best_params_}")
    
    # Lasso Regression con GridSearch
    lasso_params = {
        'alpha': [0.001, 0.01, 0.1, 1, 10, 100]
    }
    lasso_grid = GridSearchCV(
        Lasso(random_state=42, max_iter=1000),
        lasso_params, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
    )
    lasso_grid.fit(X_train_scaled, y_train)
    models['lasso'] = lasso_grid.best_estimator_
    logger.info(f"Lasso Regression - Mejores parámetros: {lasso_grid.best_params_}")
    
    # ElasticNet con GridSearch
    elastic_params = {
        'alpha': [0.001, 0.01, 0.1, 1, 10],
        'l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
    }
    elastic_grid = GridSearchCV(
        ElasticNet(random_state=42, max_iter=1000),
        elastic_params, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
    )
    elastic_grid.fit(X_train_scaled, y_train)
    models['elastic_net'] = elastic_grid.best_estimator_
    logger.info(f"ElasticNet - Mejores parámetros: {elastic_grid.best_params_}")
    
    # Bayesian Ridge
    models['bayesian_ridge'] = BayesianRidge()
    models['bayesian_ridge'].fit(X_train_scaled, y_train)
    logger.info("Bayesian Ridge entrenado")
    
    return models, scaler


def train_other_regressors(X_train: pd.DataFrame, y_train: pd.Series, parameters: dict) -> dict:
    """Entrena otros modelos de regresión con GridSearch.
    
    Args:
        X_train: Datos de entrenamiento.
        y_train: Variable objetivo de entrenamiento.
        parameters: Parámetros del modelo.
    
    Returns:
        Diccionario con modelos entrenados.
    """
    logger.info("Entrenando otros modelos de regresión con GridSearch...")
    
    models = {}
    cv = KFold(n_splits=parameters["cross_validation"]["n_splits"], shuffle=True, random_state=42)
    
    # SVR con GridSearch
    svr_params = {
        'C': [0.1, 1, 10, 100],
        'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
        'kernel': ['rbf', 'linear']
    }
    svr_grid = GridSearchCV(
        SVR(),
        svr_params, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
    )
    svr_grid.fit(X_train, y_train)
    models['svr'] = svr_grid.best_estimator_
    logger.info(f"SVR - Mejores parámetros: {svr_grid.best_params_}")
    
    # K-Nearest Neighbors Regressor con GridSearch
    knn_params = {
        'n_neighbors': [3, 5, 7, 9, 11],
        'weights': ['uniform', 'distance'],
        'metric': ['euclidean', 'manhattan']
    }
    knn_grid = GridSearchCV(
        KNeighborsRegressor(),
        knn_params, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
    )
    knn_grid.fit(X_train, y_train)
    models['knn'] = knn_grid.best_estimator_
    logger.info(f"KNN Regressor - Mejores parámetros: {knn_grid.best_params_}")
    
    # Decision Tree Regressor con GridSearch
    dt_params = {
        'max_depth': [3, 5, 7, 10, None],
        'min_samples_split': [2, 5, 10, 20],
        'min_samples_leaf': [1, 2, 4, 8]
    }
    dt_grid = GridSearchCV(
        DecisionTreeRegressor(random_state=42),
        dt_params, cv=cv, scoring='neg_mean_squared_error', n_jobs=-1
    )
    dt_grid.fit(X_train, y_train)
    models['decision_tree'] = dt_grid.best_estimator_
    logger.info(f"Decision Tree Regressor - Mejores parámetros: {dt_grid.best_params_}")
    
    return models


def create_regression_comparison_table(all_models: dict, scaler: StandardScaler, 
                                     X_val: pd.DataFrame, y_val: pd.Series) -> pd.DataFrame:
    """Crea tabla comparativa de todos los modelos de regresión.
    
    Args:
        all_models: Diccionario con todos los modelos entrenados.
        scaler: Scaler usado para modelos lineales.
        X_val: Datos de validación.
        y_val: Variable objetivo de validación.
    
    Returns:
        DataFrame con métricas comparativas.
    """
    logger.info("Creando tabla comparativa de modelos de regresión...")
    
    results = []
    
    # Determinar qué modelos necesitan escalado
    linear_models = ['linear_regression', 'ridge', 'lasso', 'elastic_net', 'bayesian_ridge']
    
    for name, model in all_models.items():
        start_time = time.time()
        
        # Preparar datos según el tipo de modelo
        if name in linear_models:
            X_val_prepared = scaler.transform(X_val)
        else:
            X_val_prepared = X_val
        
        # Predicciones
        y_pred = model.predict(X_val_prepared)
        
        # Métricas de regresión
        mse = mean_squared_error(y_val, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_val, y_pred)
        r2 = r2_score(y_val, y_pred)
        evs = explained_variance_score(y_val, y_pred)
        medae = median_absolute_error(y_val, y_pred)
        
        # Métricas adicionales
        mean_error = np.mean(y_pred - y_val)
        
        training_time = time.time() - start_time
        
        # Validación cruzada en conjunto de validación
        if name in linear_models:
            cv_scores = cross_val_score(model, X_val_prepared, y_val, cv=5, scoring='neg_mean_squared_error')
        else:
            cv_scores = cross_val_score(model, X_val, y_val, cv=5, scoring='neg_mean_squared_error')
        
        results.append({
            'Model': name,
            'RMSE': rmse,
            'MAE': mae,
            'R² Score': r2,
            'Explained Variance': evs,
            'Median AE': medae,
            'Mean Error': mean_error,
            'CV_MSE_Mean': -cv_scores.mean(),
            'CV_MSE_Std': cv_scores.std(),
            'Training_Time': training_time
        })
    
    # Crear DataFrame y ordenar por R² Score
    comparison_df = pd.DataFrame(results)
    comparison_df = comparison_df.sort_values('R² Score', ascending=False)
    comparison_df['Rank'] = range(1, len(comparison_df) + 1)
    
    logger.info("Tabla comparativa creada:")
    logger.info(f"\n{comparison_df.to_string(index=False)}")
    
    return comparison_df


def select_best_regressor(models: dict, scaler: StandardScaler, 
                         X_val: pd.DataFrame, y_val: pd.Series) -> tuple:
    """Selecciona el mejor modelo de regresión basado en el conjunto de validación.

    Args:
        models: Diccionario con modelos entrenados.
        scaler: Scaler usado para modelos lineales.
        X_val: Datos de validación.
        y_val: Variable objetivo de validación.

    Returns:
        Tupla con (mejor_modelo, nombre_del_modelo, métricas, scaler).
    """
    logger.info("Seleccionando mejor modelo de regresión...")
    
    best_model = None
    best_name = None
    best_score = float('-inf')
    best_metrics = None
    
    linear_models = ['linear_regression', 'ridge', 'lasso', 'elastic_net', 'bayesian_ridge']
    
    for name, model in models.items():
        # Preparar datos según el tipo de modelo
        if name in linear_models:
            X_val_prepared = scaler.transform(X_val)
        else:
            X_val_prepared = X_val
        
        # Evaluar en validación
        y_pred = model.predict(X_val_prepared)
        
        # Calcular R² Score (métrica principal)
        score = r2_score(y_val, y_pred)
        
        metrics = {
            'r2_score': score,
            'rmse': np.sqrt(mean_squared_error(y_val, y_pred)),
            'mae': mean_absolute_error(y_val, y_pred),
            'explained_variance': explained_variance_score(y_val, y_pred),
            'median_absolute_error': median_absolute_error(y_val, y_pred),
        }
        
        logger.info(f"  {name}: R² = {score:.4f}, RMSE = {metrics['rmse']:.2f}, MAE = {metrics['mae']:.2f}")
        
        if score > best_score:
            best_score = score
            best_model = model
            best_name = name
            best_metrics = metrics
    
    logger.info(f"Mejor modelo seleccionado: {best_name} (R²: {best_score:.4f})")
    
    # Guardar el nombre del modelo como string
    model_name_str = str(best_name)
    
    # Retornar el scaler solo si el mejor modelo es lineal
    if best_name in linear_models:
        return best_model, model_name_str, best_metrics, scaler
    else:
        return best_model, model_name_str, best_metrics, None


def evaluate_regressor(model, scaler, X_test: pd.DataFrame, y_test: pd.Series, 
                      parameters: dict) -> dict:
    """Evalúa el rendimiento del modelo de regresión.

    Args:
        model: Modelo entrenado.
        scaler: Scaler usado para modelos lineales (puede ser None).
        X_test: Datos de prueba.
        y_test: Variable objetivo de prueba.
        parameters: Parámetros de evaluación.

    Returns:
        Diccionario con métricas de evaluación.
    """
    logger.info("Evaluando modelo de regresión...")
    
    # Determinar si el modelo necesita escalado
    linear_models = ['linear_regression', 'ridge', 'lasso', 'elastic_net', 'bayesian_ridge']
    model_name = parameters.get('model_name', 'unknown')
    
    if scaler is not None and model_name in linear_models:
        X_test_prepared = scaler.transform(X_test)
    else:
        X_test_prepared = X_test
    
    # Predicciones
    y_pred = model.predict(X_test_prepared)
    
    # Métricas principales
    metrics = {
        'r2_score': r2_score(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'mae': mean_absolute_error(y_test, y_pred),
        'explained_variance': explained_variance_score(y_test, y_pred),
        'median_absolute_error': median_absolute_error(y_test, y_pred),
        'mean_squared_error': mean_squared_error(y_test, y_pred),
    }
    
    # Métricas adicionales
    residuals = y_test - y_pred
    metrics['mean_residual'] = residuals.mean()
    metrics['std_residual'] = residuals.std()
    metrics['mean_absolute_percentage_error'] = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-8))) * 100
    
    # Log de métricas
    logger.info("Métricas de evaluación:")
    for metric, value in metrics.items():
        if metric not in ['residuals']:
            logger.info(f"  {metric}: {value:.4f}")
    
    return metrics

