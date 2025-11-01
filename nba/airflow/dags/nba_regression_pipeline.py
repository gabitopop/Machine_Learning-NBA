"""
DAG de Airflow para el pipeline de Regresión de NBA
Ejecuta el pipeline completo de regresión para predecir diferencial de puntos
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.dates import days_ago
import json
import os

# Configuración por defecto del DAG
default_args = {
    'owner': 'nba-ml-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definir el DAG
dag = DAG(
    'nba_regression_pipeline',
    default_args=default_args,
    description='Pipeline completo de Regresión para predicción de diferencial de puntos NBA',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['nba', 'regression', 'kedro', 'dvc'],
)

# Tareas del DAG

# 1. Verificar disponibilidad de datos
check_data_availability = FileSensor(
    task_id='check_data_availability',
    filepath='/opt/airflow/data/01_raw/game.csv',
    fs_conn_id='fs_default',
    poke_interval=30,
    timeout=300,
    dag=dag,
)

# 2. Pipeline de procesamiento de datos (necesario para regresión)
data_processing_pipeline = BashOperator(
    task_id='data_processing_pipeline',
    bash_command='''
    cd /opt/airflow
    kedro run --pipeline data_processing
    ''',
    dag=dag,
)

# 3. Pipeline de regresión
regression_pipeline = BashOperator(
    task_id='regression_pipeline',
    bash_command='''
    cd /opt/airflow
    kedro run --pipeline regression
    ''',
    dag=dag,
)

# 4. Pipeline de reportes de regresión
regression_reporting_pipeline = BashOperator(
    task_id='regression_reporting_pipeline',
    bash_command='''
    cd /opt/airflow
    kedro run --pipeline regression_reporting
    ''',
    dag=dag,
)

# 5. Función para consolidar resultados de regresión
def consolidate_regression_results(**context):
    """Consolida métricas y resultados del pipeline de regresión"""
    
    # Leer métricas de regresión
    metrics = {}
    
    # Métricas de regresión
    try:
        with open('/opt/airflow/data/07_model_output/regression_metrics.json', 'r') as f:
            metrics['regression'] = json.load(f)
    except FileNotFoundError:
        metrics['regression'] = {'error': 'Archivo no encontrado'}
    
    # Tabla comparativa
    try:
        import pandas as pd
        comparison_df = pd.read_csv('/opt/airflow/data/07_model_output/regression_comparison_table.csv')
        metrics['model_comparison'] = comparison_df.to_dict('records')
    except Exception as e:
        metrics['model_comparison'] = {'error': str(e)}
    
    # Crear reporte consolidado
    consolidated_report = {
        'timestamp': datetime.now().isoformat(),
        'pipeline_type': 'regression',
        'pipeline_status': 'completed',
        'hypothesis': 'Predecir el diferencial de puntos (pts_diff) en partidos NBA',
        'target_variable': 'pts_diff (pts_home - pts_away)',
        'metrics': metrics,
        'artifacts': {
            'models': '/opt/airflow/data/06_models/nba_regressor.pkl',
            'reports': '/opt/airflow/data/08_reporting/regression_report.txt',
            'plots': '/opt/airflow/data/08_reporting/',
            'comparison_table': '/opt/airflow/data/07_model_output/regression_comparison_table.csv'
        }
    }
    
    # Guardar reporte consolidado
    os.makedirs('/opt/airflow/data/metrics', exist_ok=True)
    with open('/opt/airflow/data/metrics/regression_consolidated_report.json', 'w') as f:
        json.dump(consolidated_report, f, indent=2)
    
    print("✅ Reporte consolidado de regresión generado exitosamente")
    print(f"📊 R² Score: {metrics.get('regression', {}).get('r2_score', 'N/A')}")
    print(f"📉 RMSE: {metrics.get('regression', {}).get('rmse', 'N/A')}")
    print(f"📏 MAE: {metrics.get('regression', {}).get('mae', 'N/A')}")
    return consolidated_report

# 6. Tarea para consolidar resultados
consolidate_results_task = PythonOperator(
    task_id='consolidate_regression_results',
    python_callable=consolidate_regression_results,
    dag=dag,
)

# 7. Tarea de notificación de finalización
notify_completion = BashOperator(
    task_id='notify_completion',
    bash_command='''
    echo "🏀 Pipeline NBA Regresión completado exitosamente!"
    echo "📊 Métricas disponibles en: /opt/airflow/data/metrics/regression_consolidated_report.json"
    echo "📈 Reportes disponibles en: /opt/airflow/data/08_reporting/regression_report.txt"
    echo "🎯 Modelo disponible en: /opt/airflow/data/06_models/nba_regressor.pkl"
    echo "📋 Hipótesis: Predecir diferencial de puntos (pts_diff) en partidos NBA"
    ''',
    dag=dag,
)

# Definir dependencias entre tareas
check_data_availability >> data_processing_pipeline
data_processing_pipeline >> regression_pipeline
regression_pipeline >> regression_reporting_pipeline
regression_reporting_pipeline >> consolidate_results_task
consolidate_results_task >> notify_completion

