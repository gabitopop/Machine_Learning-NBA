#!/usr/bin/env python
"""
Script de prueba local para verificar pipelines sin necesidad de Kedro CLI
"""

import sys
import os
import traceback

# Agregar el directorio src al path
# El script está en testing/, así que subimos un nivel para llegar a la raíz del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Subir un nivel desde testing/
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# Cambiar al directorio del proyecto
os.chdir(project_root)

def test_pipeline_structure():
    """Prueba la estructura de los pipelines"""
    print("=" * 70)
    print("PRUEBA 1: ESTRUCTURA DE PIPELINES")
    print("=" * 70)
    
    try:
        from nba.pipelines.regression.pipeline import create_pipeline as create_regression_pipeline
        from nba.pipelines.regression_reporting.pipeline import create_pipeline as create_regression_reporting_pipeline
        from nba.pipelines.data_processing.pipeline import create_pipeline as create_data_processing_pipeline
        
        # Pipeline de regresión
        regression_pipeline = create_regression_pipeline()
        print(f"\n[OK] Pipeline de Regresion:")
        print(f"   - Nodos: {len(regression_pipeline.nodes)}")
        for node in regression_pipeline.nodes:
            print(f"     * {node.name}")
        
        # Pipeline de reportes de regresión
        regression_reporting_pipeline = create_regression_reporting_pipeline()
        print(f"\n[OK] Pipeline de Reportes de Regresion:")
        print(f"   - Nodos: {len(regression_reporting_pipeline.nodes)}")
        for node in regression_reporting_pipeline.nodes:
            print(f"     * {node.name}")
        
        # Pipeline de procesamiento de datos
        data_processing_pipeline = create_data_processing_pipeline()
        print(f"\n[OK] Pipeline de Procesamiento de Datos:")
        print(f"   - Nodos: {len(data_processing_pipeline.nodes)}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al crear pipelines: {e}")
        traceback.print_exc()
        return False


def test_regression_nodes():
    """Prueba que las funciones de nodos estén disponibles"""
    print("\n" + "=" * 70)
    print("PRUEBA 2: FUNCIONES DE NODOS DE REGRESION")
    print("=" * 70)
    
    try:
        from nba.pipelines.regression.nodes import (
            split_data_regression,
            train_ensemble_regressors,
            train_linear_regressors,
            train_other_regressors,
            create_regression_comparison_table,
            select_best_regressor,
            evaluate_regressor
        )
        
        functions = [
            ('split_data_regression', split_data_regression),
            ('train_ensemble_regressors', train_ensemble_regressors),
            ('train_linear_regressors', train_linear_regressors),
            ('train_other_regressors', train_other_regressors),
            ('create_regression_comparison_table', create_regression_comparison_table),
            ('select_best_regressor', select_best_regressor),
            ('evaluate_regressor', evaluate_regressor)
        ]
        
        for func_name, func in functions:
            if func and callable(func):
                print(f"   [OK] {func_name}: Disponible")
            else:
                print(f"   [ERROR] {func_name}: NO DISPONIBLE")
                return False
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al importar funciones: {e}")
        traceback.print_exc()
        return False


def test_catalog_config():
    """Prueba la configuración del catálogo"""
    print("\n" + "=" * 70)
    print("PRUEBA 3: CONFIGURACION DEL CATALOGO")
    print("=" * 70)
    
    try:
        from kedro.config import OmegaConfigLoader
        
        conf_path = os.path.join(project_root, 'conf')
        config_loader = OmegaConfigLoader(conf_source=conf_path)
        
        catalog = config_loader["catalog"]
        
        # Verificar entradas clave de regresión
        regression_entries = [
            'X_train_reg',
            'X_val_reg', 
            'X_test_reg',
            'y_train_reg',
            'y_val_reg',
            'y_test_reg',
            'nba_regressor',
            'regression_metrics',
            'regression_comparison_table'
        ]
        
        print("\nEntradas del catalogo de regresion:")
        all_found = True
        for entry in regression_entries:
            if entry in catalog:
                print(f"   [OK] {entry}")
            else:
                print(f"   [WARN] {entry}: No encontrado")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"\n[ERROR] Error al verificar catalogo: {e}")
        traceback.print_exc()
        return False


def test_parameters_config():
    """Prueba la configuración de parámetros"""
    print("\n" + "=" * 70)
    print("PRUEBA 4: CONFIGURACION DE PARAMETROS")
    print("=" * 70)
    
    try:
        from kedro.config import OmegaConfigLoader
        
        conf_path = os.path.join(project_root, 'conf')
        config_loader = OmegaConfigLoader(conf_source=conf_path)
        
        # Parámetros de regresión - intentar con diferentes nombres
        regression_params = None
        param_names = ["parameters_regression", "regression", "params:regression"]
        
        for param_name in param_names:
            try:
                regression_params = config_loader[param_name]
                print(f"   [OK] Parametros encontrados como: {param_name}")
                break
            except KeyError:
                continue
        
        if regression_params is None:
            # Intentar leer directamente el archivo
            import yaml
            param_file = os.path.join(conf_path, 'base', 'parameters_regression.yml')
            if os.path.exists(param_file):
                with open(param_file, 'r') as f:
                    regression_params = yaml.safe_load(f)
                print(f"   [OK] Parametros cargados directamente del archivo")
            else:
                print(f"   [ERROR] Archivo parameters_regression.yml no encontrado")
                return False
        
        print("\nParametros de regresion:")
        if 'target' in regression_params:
            print(f"   [OK] Variable objetivo: {regression_params['target']}")
        else:
            print(f"   [ERROR] Variable objetivo no encontrada")
            return False
        
        if 'models' in regression_params:
            models = regression_params['models']
            print(f"   [OK] Modelos configurados: {len(models)}")
            for model_name in models.keys():
                print(f"     * {model_name}")
        else:
            print(f"   [ERROR] Modelos no encontrados")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al verificar parametros: {e}")
        traceback.print_exc()
        return False


def test_data_directories():
    """Prueba que los directorios de datos existan"""
    print("\n" + "=" * 70)
    print("PRUEBA 5: DIRECTORIOS DE DATOS")
    print("=" * 70)
    
    required_dirs = [
        'data/01_raw',
        'data/02_intermediate',
        'data/03_primary',
        'data/04_feature',
        'data/05_model_input',
        'data/06_models',
        'data/07_model_output',
        'data/08_reporting'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = os.path.join(project_root, dir_path)
        if os.path.exists(full_path):
            print(f"   [OK] {dir_path}")
        else:
            print(f"   [WARN] {dir_path}: No existe (se creara automaticamente)")
            all_exist = False
    
    return True  # No crítico - se pueden crear


def test_pipeline_registry():
    """Prueba el registro de pipelines"""
    print("\n" + "=" * 70)
    print("PRUEBA 6: REGISTRO DE PIPELINES")
    print("=" * 70)
    
    try:
        from nba.pipeline_registry import register_pipelines
        
        pipelines = register_pipelines()
        
        expected_pipelines = [
            'data_processing',
            'data_science',
            'regression',
            'regression_reporting',
            'full_regression_pipeline',
            'full_pipeline'
        ]
        
        print(f"\nPipelines registrados: {list(pipelines.keys())}")
        
        all_found = True
        for pipeline_name in expected_pipelines:
            if pipeline_name in pipelines:
                node_count = len(pipelines[pipeline_name].nodes)
                print(f"   [OK] {pipeline_name}: {node_count} nodos")
            else:
                print(f"   [ERROR] {pipeline_name}: NO ENCONTRADO")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"\n[ERROR] Error en registro de pipelines: {e}")
        traceback.print_exc()
        return False


def test_airflow_dag():
    """Prueba el DAG de Airflow"""
    print("\n" + "=" * 70)
    print("PRUEBA 7: DAG DE AIRFLOW")
    print("=" * 70)
    
    dag_path = os.path.join(project_root, 'airflow', 'dags', 'nba_regression_pipeline.py')
    
    if not os.path.exists(dag_path):
        print(f"   [ERROR] DAG no encontrado en {dag_path}")
        return False
    
    try:
        with open(dag_path, 'r', encoding='utf-8') as f:
            dag_code = f.read()
        
        # Compilar para verificar sintaxis
        compile(dag_code, dag_path, 'exec')
        print("   [OK] Sintaxis del DAG correcta")
        
        # Verificar elementos clave
        checks = [
            ('DAG(', 'Definicion de DAG'),
            ('regression_pipeline', 'Tarea de regresion'),
            ('data_processing_pipeline', 'Tarea de procesamiento'),
            ('regression_reporting_pipeline', 'Tarea de reportes')
        ]
        
        for keyword, description in checks:
            if keyword in dag_code:
                print(f"   [OK] {description}: Encontrado")
            else:
                print(f"   [WARN] {description}: No encontrado")
        
        return True
        
    except SyntaxError as e:
        print(f"   [ERROR] Error de sintaxis: {e}")
        return False
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        traceback.print_exc()
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "=" * 70)
    print("PRUEBAS LOCALES - PIPELINES NBA")
    print("=" * 70)
    print(f"\nDirectorio del proyecto: {project_root}")
    print(f"Directorio de codigo fuente: {src_path}")
    
    tests = [
        ("Estructura de Pipelines", test_pipeline_structure),
        ("Funciones de Nodos", test_regression_nodes),
        ("Configuracion del Catalogo", test_catalog_config),
        ("Configuracion de Parametros", test_parameters_config),
        ("Directorios de Datos", test_data_directories),
        ("Registro de Pipelines", test_pipeline_registry),
        ("DAG de Airflow", test_airflow_dag),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] Error inesperado en {test_name}: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK] PASO" if result else "[ERROR] FALLO"
        print(f"   {status}: {test_name}")
    
    print(f"\nPruebas exitosas: {passed}/{total}")
    
    if passed == total:
        print("\n[TODO OK] Todos los tests pasaron exitosamente!")
        print("\nSIGUIENTE PASO:")
        print("   Para ejecutar el pipeline completo, usa:")
        print("   kedro run --pipeline full_regression_pipeline")
        return 0
    else:
        print(f"\n[WARN] {total - passed} test(s) fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(main())

