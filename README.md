# EDA Ontology Expert & Knowledge Workbench 🦉

Un sistema integral de **Gestión del Conocimiento** para el Análisis Exploratorio de Datos (EDA), que integra Ontologías OWL DL, Minería de Datos (ML) e Inferencia Lógica (Prolog).

---

## 🎯 Cumplimiento Académico (Examen GESCON)

Este proyecto ha sido diseñado para cumplir estrictamente con los requisitos del examen GESCON y el objetivo específico de modelado de conocimiento experto.

### 1. Objetivo Específico: Perfilado de Variables Categóricas
El sistema cumple con el **Punto 4** de la guía:
- **Modelo Experto:** Ontología que modela cardinalidad, distribución, categorías dominantes y nulos.
- **Clases de Perfil:** `ColumnaBinaria`, `CardinalidadAlta`, `DistribucionDesbalanceada`, etc.
- **Recomendaciones:** Sugerencias automáticas de técnicas (Barras, Torta, Treemap) e instrucciones de limpieza (Agrupar minoritarias).
- **RAG Pipeline:** Asistente que fundamenta respuestas sobre EDA categórico basándose en la literatura y la inferencia de la ontología.

### 2. Matriz de Cumplimiento General

| Requisito del Examen | Implementación en el Proyecto | Archivos Relacionados |
| :--- | :--- | :--- |
| **Selección de Dataset** | Uso del dataset **Flight Price** (recortado a 1000 registros). | `backend/data/flight_price.csv` |
| **Extracción de Reglas** | **Árboles de Decisión** y **Reglas de Asociación** (Apriori). | `backend/ml_engine.py` |
| **Representación Ontológica** | Modelo **OWL DL** con razonador **Pellet** (Protégé). | `demo_experto_eda.owx` |
| **Rep. Alternativa (Prolog)** | Formato **Objeto-Atributo-Valor (OAV)** e inferencia lógica. | `backend/prolog_engine.py` |
| **Demostración de Inferencia** | Inferencia dinámica en 3 pestañas (OWL, ML, Prolog). | App Web (Workbench) |
| **Consultas Complejas** | Consultas **SQWRL** de nivel medio-alto. | `backend/ontology/sqwrl_queries.txt` |

---

## 🚀 Arquitectura del Workbench

El proyecto se presenta como un **Workbench de Gestión del Conocimiento** multiparadigma:

1.  **Capa Ontológica (OWL DL):** Razonamiento deductivo sobre la estructura de los metadatos.
2.  **Capa de Minería (ML):** Extracción inductiva de reglas de dominio del dataset.
3.  **Capa Lógica (Prolog):** Representación formal OAV y proposiciones de inferencia.
4.  **Capa de Asesoría (RAG):** Interfaz en lenguaje natural impulsada por LLM local (Ollama).

---

## 🛠️ Guía de Ejecución

### Requisitos Previos
- Docker y Docker Compose.
- Ollama instalado en el host (opcional para el chatbot).

### Iniciar el Sistema
```bash
docker compose up --build
```
Accede a la interfaz en: `http://localhost:5173`

### Componentes de Soporte (Para el Artículo)
- **Reglas ML Extraídas:** `backend/ml/reglas_extraidas.txt`
- **Lógica Prolog:** `backend/prolog/eda_expert.pl`
- **Consultas SQWRL:** `backend/ontology/sqwrl_queries.txt`

---

## 📚 Secciones para el Artículo Técnico

- **Metodología:** Describe el pipeline de "Triple Inferencia" (Ontología -> ML -> Prolog).
- **Resultados:** Incluye capturas de las 3 pestañas de la aplicación mostrando el razonamiento concurrente sobre el dataset `flight_price`.
- **Inferencia:** Explica cómo el modelo clasifica automáticamente individuos en Protégé usando Pellet y cómo se traduce a hechos OAV en Prolog.

