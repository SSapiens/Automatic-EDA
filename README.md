# Knowledge Management Workbench - EDA Numérico Experto

Este proyecto es una plataforma integral de **Gestión del Conocimiento** diseñada para automatizar el Análisis Exploratorio de Datos (EDA) de variables numéricas. Combina minería de datos, ontologías y lógica formal para actuar como un "Consultor Estadístico Experto".

---

## 🏗️ Arquitectura del Sistema y Flujo de Datos

El sistema utiliza una arquitectura desacoplada donde el conocimiento fluye a través de múltiples motores de razonamiento:

1.  **Capa de Presentación (React + Vite)**: Interfaz premium para la carga de datasets y visualización de perfiles inferidos.
2.  **Capa de Orquestación (FastAPI)**:
    *   **OntologyEngine**: Realiza el perfilamiento estadístico y la inferencia ontológica.
    *   **PrologEngine**: Traduce métricas a hechos Objeto-Atributo-Valor (OAV) para validación lógica.
    *   **MLEngine**: Extrae reglas de asociación y dependencias mediante Árboles de Decisión.
    *   **RAGEngine**: Procesa consultas en lenguaje natural fundamentándose en los resultados de los motores anteriores.
3.  **Capa de Inferencia**:
    *   **OWL 2 DL**: Clasificación semántica de variables.
    *   **SWI-Prolog**: Razonamiento sobre la calidad y coherencia del dato.
    *   **Llama 3.2 (Ollama)**: Generación de lenguaje natural fundamentado.

---

## 🔬 Justificación Técnica: Arquitectura de Inferencia Dual

Durante el desarrollo se identificó un reto técnico crítico:

### El Problema de los Built-ins
Los motores de razonamiento que se integran fácilmente con Python (como `Owlready2` usando Pellet) suelen tener limitaciones o bajo rendimiento al procesar **built-ins matemáticos complejos de SWRL** (como `swrlb:greaterThan`) en tiempo de ejecución de API.

### La Solución: Inferencia Dual
Se implementó un enfoque híbrido para garantizar robustez y fines académicos:
*   **Inferencia de Producción (Backend)**: Se tradujeron las reglas de negocio a **Axiomas de Clase (EquivalentClasses)** usando el formato funcional de OWL 2. Esto permite que el backend clasifique las columnas (ej: *ColumnaAsimetrica*) de forma instantánea y 100% robusta dentro de la aplicación.
*   **Inferencia de Visualización (Protégé)**: Se mantuvieron y documentaron las reglas **SWRL** en la ontología para que el profesor/jurado pueda auditar la lógica en un formato "humano" y demostrar inferencias complejas y consultas SQWRL dentro de la herramienta estándar de la industria.

### 🔗 Tabla de Correspondencia de Reglas (Trazabilidad)

Para garantizar la integridad, cada regla de la demo tiene un "gemelo" funcional en el Backend:

| ID Regla | Lógica Experta (Umbral) | Sugerencia / Acción | Implementación en Backend | Regla en Demo (Protégé) |
| :--- | :--- | :--- | :--- | :--- |
| **R1** | Asimetría $> 1.0$ | Histograma Logarítmico | `prolog/eda_expert.pl` (regla `es_sesgada`) | `S1` (SWRL) |
| **R2** | $\|Asimetría\| < 0.5$ | Histograma Estándar | `ontology_engine.py` (clase `ColumnaNormal`) | `S2` (SWRL) |
| **R3** | Ratio Outliers $> 0.05$ | Diagrama de Caja | `prolog/eda_expert.pl` (regla `tiene_outliers`) | `S3` (SWRL) |
| **R4** | Correlación $> 0.7$ | Gráfico de Dispersión | `ml_engine.py` (Cálculo de Pearson) | `S4` (SWRL) |

---

## 📖 Documentación de la API (REST)

El backend expone los siguientes servicios:

*   `POST /upload`: Recibe un archivo CSV y lo almacena temporalmente para su procesamiento.
*   `POST /analyze`: Dispara el pipeline multiparadigma. Retorna:
    *   Métricas estadísticas (Asimetría, Outliers, Correlación).
    *   Clasificaciones inferidas por la Ontología.
    *   Validaciones lógicas de Prolog.
    *   Reglas extraídas por ML.
*   `POST /ask`: Recibe una pregunta en lenguaje natural y retorna una respuesta del RAG fundamentada en los metadatos y la ontología.

---

## ✅ Cumplimiento de Requerimientos (GESCON)

| Requerimiento | Implementación en este Proyecto | Archivo / Componente Clave |
| :--- | :--- | :--- |
| **Dataset Seleccionado** | **Seattle Weather**: Variables numéricas reales. | `backend/data/` |
| **Extracción de Reglas** | **Árboles de Decisión** para dependencias numéricas. | `backend/ml_engine.py` |
| **Representación OWL** | Ontología con perfiles estadísticos y jerarquía de técnicas. | `backend/demo_experto_eda_v3_numericas.owx` |
| **Consultas SQWRL** | 3 consultas de alta complejidad (Agregación `avg`, Alertas). | `SQWRL Query Tab` (Protégé) |
| **Representación OAV** | Hechos dinámicos procesados por motor Prolog. | `backend/prolog_engine.py` |
| **RAG Fundamentado** | IA que explica el EDA basándose en el grafo de conocimiento. | `backend/rag_engine.py` |

---

## 🦉 Guía de la Demo en Protégé

1.  Abrir `backend/demo_experto_eda_v3_numericas.owx`.
2.  **Configuración**: `Reasoner -> Pellet` -> `Start Reasoner`.
3.  **SWRL**: Las reglas S1-S4 demuestran la lógica de recomendación visual.
4.  **SQWRL**: Ejecutar `Q1_Identificar_Predictores_Ideales` para ver la potencia del filtrado semántico.

---

### 📊 Resultados Esperados de las Consultas (Demo)

Al ejecutar las consultas SQWRL en Protégé sobre el dataset de Seattle, estos son los resultados que el sistema debe arrojar:

| Consulta | Lo que "piensa" el motor | Resultado Esperado |
| :--- | :--- | :--- |
| **Q1 (Predictores)** | Busca variables normales con alta correlación. | Identifica a `temp_max` y `temp_min` (Corr: 0.88). |
| **Q2 (Calidad)** | Busca sesgo extremo ($>2$) y muchos outliers ($>10\%$). | Identifica a `precipitation` como variable de riesgo crítico. |
| **Q3 (Agregación)** | Calcula el promedio de dependencia del dataset. | Retorna un valor único (aprox. `0.70`) como métrica de cohesión del dataset. |

---

## 🛠️ Guía de Ejecución

### Requisitos Previos
*   Docker y Docker Compose.
*   Ollama instalado (opcional para RAG local).

### Pasos
1.  Clonar el repositorio.
2.  Ejecutar el entorno:
    ```bash
    docker compose up --build
    ```
3.  Acceder a la interfaz: `http://localhost:5173`.
4.  Subir el archivo `seattle-weather.csv` (incluido en samples) y presionar **"Iniciar Análisis Multiparadigma"**.

---
**Desarrollado para el Examen GESCON - Punto 3: Variables Numéricas**
