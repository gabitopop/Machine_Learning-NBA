"""
DAG de Airflow para el pipeline de Machine Learning de NBA
Ejecuta ambos pipelines (data_processing + data_science) y consolida resultados
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
    'nba_ml_pipeline',
    default_args=default_args,
    description='Pipeline completo de ML para predicción de partidos NBA',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['nba', 'ml', 'kedro', 'dvc'],
)

# Tareas del DAG

# 1. Verificar disponibilidad de datos
check_data_availability = FileSensor(
    task_id='check_data_availability',
    filepath='/opt/airflow/data/01_raw/game.csv',
    poke_interval=30,
    timeout=300,
    mode='poke',
    dag=dag,
)

# 2. Pipeline de procesamiento de datos
data_processing_pipeline = BashOperator(
    task_id='data_processing_pipeline',
    bash_command='''
    export PYTHONPATH=/opt/airflow/src:$PYTHONPATH
    cd /opt/airflow
    kedro run --pipeline data_processing
    ''',
    dag=dag,
)

# 3. Pipeline de ciencia de datos
data_science_pipeline = BashOperator(
    task_id='data_science_pipeline',
    bash_command='''
    export PYTHONPATH=/opt/airflow/src:$PYTHONPATH
    cd /opt/airflow
    kedro run --pipeline data_science
    ''',
    dag=dag,
)

# 4. Pipeline de reportes
reporting_pipeline = BashOperator(
    task_id='reporting_pipeline',
    bash_command='''
    export PYTHONPATH=/opt/airflow/src:$PYTHONPATH
    cd /opt/airflow
    kedro run --pipeline reporting
    ''',
    dag=dag,
)

# 5. Función para consolidar resultados
def consolidate_results(**context):
    """Consolida métricas y resultados de todos los pipelines"""
    
    # Leer métricas de cada pipeline
    metrics = {}
    
    # Métricas de procesamiento de datos
    try:
        with open('/opt/airflow/data/metrics/data_processing.json', 'r') as f:
            metrics['data_processing'] = json.load(f)
    except FileNotFoundError:
        metrics['data_processing'] = {'error': 'Archivo no encontrado'}
    
    # Métricas de ciencia de datos
    try:
        with open('/opt/airflow/data/metrics/data_science.json', 'r') as f:
            metrics['data_science'] = json.load(f)
    except FileNotFoundError:
        metrics['data_science'] = {'error': 'Archivo no encontrado'}
    
    # Métricas de reportes (si existe)
    try:
        with open('/opt/airflow/data/metrics/reporting.json', 'r') as f:
            metrics['reporting'] = json.load(f)
    except FileNotFoundError:
        metrics['reporting'] = {'error': 'Archivo no encontrado'}
    
    # Crear reporte consolidado
    consolidated_report = {
        'timestamp': datetime.now().isoformat(),
        'pipeline_status': 'completed',
        'metrics': metrics,
        'artifacts': {
            'models': '/opt/airflow/data/06_models/',
            'reports': '/opt/airflow/data/08_reporting/',
            'plots': '/opt/airflow/data/plots/'
        }
    }
    
    # Guardar reporte consolidado
    os.makedirs('/opt/airflow/data/metrics', exist_ok=True)
    with open('/opt/airflow/data/metrics/consolidated_report.json', 'w') as f:
        json.dump(consolidated_report, f, indent=2)
    
    print("✅ Reporte consolidado generado exitosamente")
    return consolidated_report

# 6. Tarea para consolidar resultados
consolidate_results_task = PythonOperator(
    task_id='consolidate_results',
    python_callable=consolidate_results,
    dag=dag,
)

# 7. Tarea de notificación de finalización
notify_completion = BashOperator(
    task_id='notify_completion',
    bash_command='''
    echo "🏀 Pipeline NBA ML completado exitosamente!"
    echo "📊 Métricas disponibles en: /opt/airflow/data/metrics/"
    echo "📈 Reportes disponibles en: /opt/airflow/data/08_reporting/"
    echo "🎯 Modelos disponibles en: /opt/airflow/data/06_models/"
    ''',
    dag=dag,
)

# Definir dependencias entre tareas
check_data_availability >> data_processing_pipeline
data_processing_pipeline >> data_science_pipeline
data_science_pipeline >> reporting_pipeline
reporting_pipeline >> consolidate_results_task
consolidate_results_task >> notify_completion

