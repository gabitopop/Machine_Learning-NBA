import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier, AdaBoostClassifier, BaggingClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier, SGDClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler
import pickle
import json
import time

logger = logging.getLogger(__name__)


def split_data(data: pd.DataFrame, parameters: dict) -> tuple:
    """Divide los datos en conjuntos de entrenamiento, validación y prueba.

    Args:
        data: Datos con características y variable objetivo.
        parameters: Parámetros definidos en parameters_data_science.yml.
    
    Returns:
        Conjuntos de datos divididos (X_train, X_val, X_test, y_train, y_val, y_test).
    """
    logger.info("Iniciando división de datos...")
    
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
    
    # División estratificada
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=splitting_config["test_size"],
        random_state=splitting_config["random_state"],
        stratify=y if splitting_config["stratify"] else None,
        shuffle=True
    )
    
    # División adicional para validación
    X_train_final, X_val, y_train_final, y_val = train_test_split(
        X_train, y_train,
        test_size=splitting_config["val_size"],
        random_state=splitting_config["random_state"],
        stratify=y_train if splitting_config["stratify"] else None,
        shuffle=True
    )
    
    logger.info(f"División completada:")
    logger.info(f"  Entrenamiento: {X_train_final.shape[0]:,} muestras")
    logger.info(f"  Validación: {X_val.shape[0]:,} muestras")
    logger.info(f"  Prueba: {X_test.shape[0]:,} muestras")
    
    # Verificar estratificación
    train_class_dist = y_train_final.value_counts(normalize=True)
    val_class_dist = y_val.value_counts(normalize=True)
    test_class_dist = y_test.value_counts(normalize=True)
    
    logger.info(f"Distribución de clases:")
    logger.info(f"  Entrenamiento: {train_class_dist[1]:.1%} victorias locales")
    logger.info(f"  Validación: {val_class_dist[1]:.1%} victorias locales")
    logger.info(f"  Prueba: {test_class_dist[1]:.1%} victorias locales")
    
    return X_train_final, X_val, X_test, y_train_final, y_val, y_test


def train_random_forest(X_train: pd.DataFrame, y_train: pd.Series, parameters: dict) -> RandomForestClassifier:
    """Entrena un modelo de Random Forest.

    Args:
        X_train: Datos de entrenamiento.
        y_train: Variable objetivo de entrenamiento.
        parameters: Parámetros del modelo.

    Returns:
        Modelo entrenado de Random Forest.
    """
    logger.info("Entrenando modelo Random Forest...")
    
    model_params = parameters["models"]["random_forest"]
    model = RandomForestClassifier(**model_params)
    
    # Validación cruzada
    cv_scores = cross_val_score(
        model, X_train, y_train, 
        cv=parameters["cross_validation"]["n_splits"],
        scoring=parameters["cross_validation"]["scoring"]
    )
    
    # Entrenar modelo final
    model.fit(X_train, y_train)
    
    logger.info(f"Random Forest entrenado:")
    logger.info(f"  CV Score (AUC): {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    logger.info(f"  Características importantes: {len(model.feature_importances_)}")
    
    return model


def train_gradient_boosting(X_train: pd.DataFrame, y_train: pd.Series, parameters: dict) -> GradientBoostingClassifier:
    """Entrena un modelo de Gradient Boosting.

    Args:
        X_train: Datos de entrenamiento.
        y_train: Variable objetivo de entrenamiento.
        parameters: Parámetros del modelo.

    Returns:
        Modelo entrenado de Gradient Boosting.
    """
    logger.info("Entrenando modelo Gradient Boosting...")
    
    model_params = parameters["models"]["gradient_boosting"]
    model = GradientBoostingClassifier(**model_params)
    
    # Validación cruzada
    cv_scores = cross_val_score(
        model, X_train, y_train, 
        cv=parameters["cross_validation"]["n_splits"],
        scoring=parameters["cross_validation"]["scoring"]
    )
    
    # Entrenar modelo final
    model.fit(X_train, y_train)
    
    logger.info(f"Gradient Boosting entrenado:")
    logger.info(f"  CV Score (AUC): {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    logger.info(f"  Características importantes: {len(model.feature_importances_)}")
    
    return model


def train_logistic_regression(X_train: pd.DataFrame, y_train: pd.Series, parameters: dict) -> LogisticRegression:
    """Entrena un modelo de Regresión Logística.

    Args:
        X_train: Datos de entrenamiento.
        y_train: Variable objetivo de entrenamiento.
        parameters: Parámetros del modelo.

    Returns:
        Modelo entrenado de Regresión Logística.
    """
    logger.info("Entrenando modelo Regresión Logística...")
    
    model_params = parameters["models"]["logistic_regression"]
    model = LogisticRegression(**model_params)
    
    # Validación cruzada
    cv_scores = cross_val_score(
        model, X_train, y_train, 
        cv=parameters["cross_validation"]["n_splits"],
        scoring=parameters["cross_validation"]["scoring"]
    )
    
    # Entrenar modelo final
    model.fit(X_train, y_train)
    
    logger.info(f"Regresión Logística entrenada:")
    logger.info(f"  CV Score (AUC): {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    return model


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series, parameters: dict) -> dict:
    """Evalúa el rendimiento del modelo.

    Args:
        model: Modelo entrenado.
        X_test: Datos de prueba.
        y_test: Variable objetivo de prueba.
        parameters: Parámetros de evaluación.

    Returns:
        Diccionario con métricas de evaluación.
    """
    logger.info("Evaluando modelo...")
    
    # Predicciones
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
    
    # Métricas principales
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred),
    }
    
    # AUC si el modelo soporta probabilidades
    if y_pred_proba is not None:
        metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba)
    
    # Matriz de confusión
    cm = confusion_matrix(y_test, y_pred)
    metrics['confusion_matrix'] = cm.tolist()
    
    # Reporte de clasificación
    report = classification_report(y_test, y_pred, output_dict=True)
    metrics['classification_report'] = report
    
    # Log de métricas
    logger.info("Métricas de evaluación:")
    for metric, value in metrics.items():
        if metric not in ['confusion_matrix', 'classification_report']:
            logger.info(f"  {metric}: {value:.3f}")
    
    return metrics


def train_ensemble_models(X_train: pd.DataFrame, y_train: pd.Series, parameters: dict) -> dict:
    """Entrena modelos de ensemble con GridSearch.
    
    Args:
        X_train: Datos de entrenamiento.
        y_train: Variable objetivo de entrenamiento.
        parameters: Parámetros del modelo.
    
    Returns:
        Diccionario con modelos entrenados.
    """
    logger.info("Entrenando modelos de ensemble con GridSearch...")
    
    models = {}
    cv = StratifiedKFold(n_splits=parameters["cross_validation"]["n_splits"], shuffle=True, random_state=42)
    
    # Random Forest con GridSearch
    rf_params = {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    rf_grid = GridSearchCV(
        RandomForestClassifier(random_state=42),
        rf_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    rf_grid.fit(X_train, y_train)
    models['random_forest'] = rf_grid.best_estimator_
    logger.info(f"Random Forest - Mejores parámetros: {rf_grid.best_params_}")
    
    # Gradient Boosting con GridSearch
    gb_params = {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'subsample': [0.8, 0.9, 1.0]
    }
    gb_grid = GridSearchCV(
        GradientBoostingClassifier(random_state=42),
        gb_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    gb_grid.fit(X_train, y_train)
    models['gradient_boosting'] = gb_grid.best_estimator_
    logger.info(f"Gradient Boosting - Mejores parámetros: {gb_grid.best_params_}")
    
    # Extra Trees con GridSearch
    et_params = {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5, 10]
    }
    et_grid = GridSearchCV(
        ExtraTreesClassifier(random_state=42),
        et_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    et_grid.fit(X_train, y_train)
    models['extra_trees'] = et_grid.best_estimator_
    logger.info(f"Extra Trees - Mejores parámetros: {et_grid.best_params_}")
    
    # AdaBoost con GridSearch
    ada_params = {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.1, 0.5, 1.0]
    }
    ada_grid = GridSearchCV(
        AdaBoostClassifier(random_state=42),
        ada_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    ada_grid.fit(X_train, y_train)
    models['ada_boost'] = ada_grid.best_estimator_
    logger.info(f"AdaBoost - Mejores parámetros: {ada_grid.best_params_}")
    
    # Bagging con GridSearch
    bag_params = {
        'n_estimators': [10, 50, 100],
        'max_samples': [0.5, 0.8, 1.0],
        'max_features': [0.5, 0.8, 1.0]
    }
    bag_grid = GridSearchCV(
        BaggingClassifier(random_state=42),
        bag_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    bag_grid.fit(X_train, y_train)
    models['bagging'] = bag_grid.best_estimator_
    logger.info(f"Bagging - Mejores parámetros: {bag_grid.best_params_}")
    
    return models


def train_linear_models(X_train: pd.DataFrame, y_train: pd.Series, parameters: dict) -> dict:
    """Entrena modelos lineales con GridSearch.
    
    Args:
        X_train: Datos de entrenamiento.
        y_train: Variable objetivo de entrenamiento.
        parameters: Parámetros del modelo.
    
    Returns:
        Diccionario con modelos entrenados.
    """
    logger.info("Entrenando modelos lineales con GridSearch...")
    
    models = {}
    cv = StratifiedKFold(n_splits=parameters["cross_validation"]["n_splits"], shuffle=True, random_state=42)
    
    # Escalar datos para modelos lineales
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Logistic Regression con GridSearch
    lr_params = {
        'C': [0.001, 0.01, 0.1, 1, 10, 100],
        'penalty': ['l1', 'l2'],
        'solver': ['liblinear', 'saga']
    }
    lr_grid = GridSearchCV(
        LogisticRegression(random_state=42, max_iter=1000),
        lr_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    lr_grid.fit(X_train_scaled, y_train)
    models['logistic_regression'] = lr_grid.best_estimator_
    logger.info(f"Logistic Regression - Mejores parámetros: {lr_grid.best_params_}")
    
    # Ridge Classifier con GridSearch
    ridge_params = {
        'alpha': [0.001, 0.01, 0.1, 1, 10, 100]
    }
    ridge_grid = GridSearchCV(
        RidgeClassifier(random_state=42),
        ridge_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    ridge_grid.fit(X_train_scaled, y_train)
    models['ridge_classifier'] = ridge_grid.best_estimator_
    logger.info(f"Ridge Classifier - Mejores parámetros: {ridge_grid.best_params_}")
    
    # SGD Classifier con GridSearch
    sgd_params = {
        'alpha': [0.0001, 0.001, 0.01, 0.1],
        'loss': ['hinge', 'log', 'modified_huber'],
        'penalty': ['l1', 'l2', 'elasticnet']
    }
    sgd_grid = GridSearchCV(
        SGDClassifier(random_state=42, max_iter=1000),
        sgd_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    sgd_grid.fit(X_train_scaled, y_train)
    models['sgd_classifier'] = sgd_grid.best_estimator_
    logger.info(f"SGD Classifier - Mejores parámetros: {sgd_grid.best_params_}")
    
    return models, scaler


def train_other_models(X_train: pd.DataFrame, y_train: pd.Series, parameters: dict) -> dict:
    """Entrena otros modelos con GridSearch.
    
    Args:
        X_train: Datos de entrenamiento.
        y_train: Variable objetivo de entrenamiento.
        parameters: Parámetros del modelo.
    
    Returns:
        Diccionario con modelos entrenados.
    """
    logger.info("Entrenando otros modelos con GridSearch...")
    
    models = {}
    cv = StratifiedKFold(n_splits=parameters["cross_validation"]["n_splits"], shuffle=True, random_state=42)
    
    # SVM con GridSearch
    svm_params = {
        'C': [0.1, 1, 10, 100],
        'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
        'kernel': ['rbf', 'linear']
    }
    svm_grid = GridSearchCV(
        SVC(random_state=42, probability=True),
        svm_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    svm_grid.fit(X_train, y_train)
    models['svm'] = svm_grid.best_estimator_
    logger.info(f"SVM - Mejores parámetros: {svm_grid.best_params_}")
    
    # K-Nearest Neighbors con GridSearch
    knn_params = {
        'n_neighbors': [3, 5, 7, 9, 11],
        'weights': ['uniform', 'distance'],
        'metric': ['euclidean', 'manhattan']
    }
    knn_grid = GridSearchCV(
        KNeighborsClassifier(),
        knn_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    knn_grid.fit(X_train, y_train)
    models['knn'] = knn_grid.best_estimator_
    logger.info(f"KNN - Mejores parámetros: {knn_grid.best_params_}")
    
    # Naive Bayes (sin GridSearch, parámetros por defecto)
    models['naive_bayes'] = GaussianNB()
    models['naive_bayes'].fit(X_train, y_train)
    logger.info("Naive Bayes entrenado con parámetros por defecto")
    
    # Decision Tree con GridSearch
    dt_params = {
        'max_depth': [3, 5, 7, 10, None],
        'min_samples_split': [2, 5, 10, 20],
        'min_samples_leaf': [1, 2, 4, 8]
    }
    dt_grid = GridSearchCV(
        DecisionTreeClassifier(random_state=42),
        dt_params, cv=cv, scoring='roc_auc', n_jobs=-1
    )
    dt_grid.fit(X_train, y_train)
    models['decision_tree'] = dt_grid.best_estimator_
    logger.info(f"Decision Tree - Mejores parámetros: {dt_grid.best_params_}")
    
    return models


def create_model_comparison_table(all_models: dict, X_val: pd.DataFrame, y_val: pd.Series) -> pd.DataFrame:
    """Crea tabla comparativa de todos los modelos.
    
    Args:
        all_models: Diccionario con todos los modelos entrenados.
        X_val: Datos de validación.
        y_val: Variable objetivo de validación.
    
    Returns:
        DataFrame con métricas comparativas.
    """
    logger.info("Creando tabla comparativa de modelos...")
    
    results = []
    
    for name, model in all_models.items():
        start_time = time.time()
        
        # Predicciones
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1] if hasattr(model, 'predict_proba') else None
        
        # Métricas
        accuracy = accuracy_score(y_val, y_pred)
        precision = precision_score(y_val, y_pred)
        recall = recall_score(y_val, y_pred)
        f1 = f1_score(y_val, y_pred)
        roc_auc = roc_auc_score(y_val, y_pred_proba) if y_pred_proba is not None else 0.0
        
        training_time = time.time() - start_time
        
        # Validación cruzada
        cv_scores = cross_val_score(model, X_val, y_val, cv=5, scoring='roc_auc')
        
        results.append({
            'Model': name,
            'Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1,
            'ROC-AUC': roc_auc,
            'CV_Score_Mean': cv_scores.mean(),
            'CV_Score_Std': cv_scores.std(),
            'Training_Time': training_time
        })
    
    # Crear DataFrame y ordenar por ROC-AUC
    comparison_df = pd.DataFrame(results)
    comparison_df = comparison_df.sort_values('ROC-AUC', ascending=False)
    comparison_df['Rank'] = range(1, len(comparison_df) + 1)
    
    logger.info("Tabla comparativa creada:")
    logger.info(f"\n{comparison_df.to_string(index=False)}")
    
    return comparison_df


def select_best_model(models: dict, X_val: pd.DataFrame, y_val: pd.Series) -> tuple:
    """Selecciona el mejor modelo basado en el conjunto de validación.

    Args:
        models: Diccionario con modelos entrenados.
        X_val: Datos de validación.
        y_val: Variable objetivo de validación.

    Returns:
        Tupla con (mejor_modelo, nombre_del_modelo, métricas).
    """
    logger.info("Seleccionando mejor modelo...")
    
    best_model = None
    best_name = None
    best_score = 0
    best_metrics = None
    
    for name, model in models.items():
        # Evaluar en validación
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1] if hasattr(model, 'predict_proba') else None
        
        # Calcular AUC
        if y_pred_proba is not None:
            score = roc_auc_score(y_val, y_pred_proba)
        else:
            score = accuracy_score(y_val, y_pred)
        
        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'precision': precision_score(y_val, y_pred),
            'recall': recall_score(y_val, y_pred),
            'f1_score': f1_score(y_val, y_pred),
        }
        
        if y_pred_proba is not None:
            metrics['roc_auc'] = score
        
        logger.info(f"  {name}: AUC = {score:.3f}, Accuracy = {metrics['accuracy']:.3f}")
        
        if score > best_score:
            best_score = score
            best_model = model
            best_name = name
            best_metrics = metrics
    
    logger.info(f"Mejor modelo seleccionado: {best_name} (AUC: {best_score:.3f})")
    
    return best_model, best_name, best_metrics
