# 🧪 Carpeta de Testing y Verificación

Esta carpeta contiene todos los archivos relacionados con pruebas, verificaciones y documentación de testing del proyecto NBA Machine Learning.

## 📁 Estructura

```
testing/
├── README.md                          # Este archivo
├── test_pipelines.py                  # Script de prueba general de pipelines
├── test_pipelines_local.py            # Script de prueba local (sin Kedro CLI)
├── test_docker_airflow.sh             # Script de prueba para Docker y Airflow
├── TEST_RESULTS.md                    # Resultados de pruebas generales
├── RESULTADOS_PRUEBAS_LOCALES.md      # Resultados de pruebas locales ejecutadas
├── VERIFICACION_COMPLETA.md           # Documentación completa de verificación
└── VERIFICACION_REQUISITOS.md         # Verificación de requisitos de la rúbrica
```

## 📋 Archivos Incluidos

### Scripts de Prueba

1. **`test_pipelines.py`**
   - Prueba general de pipelines
   - Verifica estructura, funciones, catálogo, parámetros
   - Verifica DAG de Airflow

2. **`test_pipelines_local.py`**
   - Prueba local sin necesidad de Kedro CLI instalado
   - Funciona directamente con Python
   - Ideal para verificación rápida de estructura

3. **`test_docker_airflow.sh`**
   - Script bash para verificar configuración de Docker y Airflow
   - Verifica docker-compose.yml, Dockerfile, y DAGs
   - Ejecutar en Linux/Mac: `bash testing/test_docker_airflow.sh`

### Documentación de Resultados

4. **`TEST_RESULTS.md`**
   - Resultados detallados de todas las pruebas
   - Estado de componentes
   - Checklist final

5. **`RESULTADOS_PRUEBAS_LOCALES.md`**
   - Resultados específicos de pruebas locales ejecutadas
   - Estadísticas y detalles de cada prueba
   - Conclusión y próximos pasos

### Documentación de Verificación

6. **`VERIFICACION_COMPLETA.md`**
   - Guía completa de verificación de pipelines
   - Instrucciones de prueba con Docker y Airflow
   - Problemas conocidos y soluciones

7. **`VERIFICACION_REQUISITOS.md`**
   - Verificación de cumplimiento de requisitos de la rúbrica
   - Estado de implementación de cada requisito

## 🚀 Uso

### Ejecutar Pruebas Locales

```bash
cd nba
python testing/test_pipelines_local.py
```

### Ejecutar Pruebas Generales

```bash
cd nba
python testing/test_pipelines.py
```

### Verificar Docker y Airflow (Linux/Mac)

```bash
cd nba
bash testing/test_docker_airflow.sh
```

### Ver Resultados

Consultar los archivos `.md` para ver los resultados detallados de las pruebas.

## 📊 Estado Actual

- ✅ **6/7 pruebas locales exitosas**
- ✅ Pipelines correctamente estructurados
- ✅ Configuración verificada
- ✅ DAGs de Airflow con sintaxis correcta
- ⚠️ 1 prueba con problema conocido (no afecta funcionalidad)

## 🔗 Referencias

- [README Principal](../README.md) - Documentación general del proyecto
- [REGRESION_README.md](../REGRESION_README.md) - Documentación del pipeline de regresión
- [Documentación CRISP-DM](../notebooks/PROYECTO_COMPLETO_CRISP_DM.ipynb) - Notebook completo del proyecto

---

**Última actualización:** 2024

