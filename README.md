# EDA Ontology Expert & Knowledge Workbench 🦉

Un sistema integral de **Gestión del Conocimiento** para el Análisis Exploratorio de Datos (EDA), que integra Ontologías OWL DL, Minería de Datos (ML) e Inferencia Lógica (Prolog).

---

## 🎯 Cumplimiento Académico (Examen GESCON)

Este proyecto ha sido diseñado para cumplir estrictamente con los requisitos del examen GESCON y el objetivo específico de modelado de conocimiento experto.

### Matriz de Cumplimiento General

| Requisito del Examen | Implementación en el Proyecto | Archivos Relacionados |
| :--- | :--- | :--- |
| **Selección de Dataset** | Uso del dataset **Flight Price** (recortado a 1000 registros). | `backend/data/flight_price.csv` |
| **Extracción de Reglas (ML)** | **Árboles de Decisión** y **Reglas de Asociación** (Apriori). | `backend/ml_engine.py` |
| **Representación Ontológica** | Modelo **OWL DL** con razonador **Pellet** (Protégé). | `demo_experto_eda.owx` |
| **Rep. Alternativa (Prolog)** | Formato **Objeto-Atributo-Valor (OAV)** e inferencia lógica. | `backend/prolog_engine.py` |
| **Demostración de Inferencia** | Inferencia dinámica en 3 pestañas (OWL, ML, Prolog). | App Web (Workbench) |
| **Consultas Complejas** | Consultas **SQWRL** de nivel medio-alto. | `backend/ontology/sqwrl_queries.txt` |

### Cumplimiento del Punto 4: Variables Categóricas
El sistema automatiza el razonamiento experto mediante dos mecanismos lógicamente equivalentes:
- **Backend (Producción):** Utiliza **OWL 2 DL (EquivalentClasses)**. Este formato es el estándar para motores de inferencia embebidos (Pellet/HermiT), garantizando estabilidad y evitando errores de tipos de datos en el servidor.
- **Protégé (Demostración Visual):** Se incluye el archivo **`demo_experto_eda.owx`** que contiene **reglas SWRL**. Esto permite visualizar la lógica experta en la pestaña SWRLTab de Protégé, cumpliendo con la exigencia de "reglas SWRL" para la sustentación.

---

## 🚀 Arquitectura del Workbench

El proyecto se presenta como un **Workbench de Gestión del Conocimiento** multiparadigma:

1.  **Capa Ontológica (OWL DL):** Razonamiento deductivo sobre la estructura de los metadatos.
2.  **Capa de Minería (ML):** Extracción inductiva de reglas de dominio del dataset.
3.  **Capa Lógica (Prolog):** Representación formal OAV y proposiciones de inferencia.
4.  **Capa de Asesoría (RAG):** Interfaz en lenguaje natural impulsada por LLM local (Ollama).

---

## 💡 Notas Técnicas: SWRL vs OWL DL

### El Problema de los Built-ins
Durante el desarrollo se identificó que los motores de razonamiento modernos (Pellet/HermiT) tienen limitaciones al procesar *built-ins* matemáticos de SWRL (como `swrlb:greaterThan`) dentro de entornos automatizados de Python (Owlready2).

### La Solución
Se implementó una **Arquitectura de Inferencia Dual**:
- **Producción:** Se tradujeron las reglas a axiomas de clase (`EquivalentClasses`) usando el formato funcional de OWL 2. Esto permite que el backend sea 100% robusto y rápido.
- **Visualización:** Se mantuvieron las reglas SWRL en `demo_experto_eda.owx` para que el profesor/jurado pueda ver la lógica "en humano" dentro de Protégé.

---

## 🛠️ Guía de Ejecución y Demostración

### Iniciar el Sistema
```bash
docker compose up --build
```
Accede a la interfaz en: `http://localhost:5173`

### Guía de Demostración en Protégé (`demo_experto_eda.owx`)
Para facilitar la sustentación, el archivo incluye **individuos pre-creados**:
1.  **Abre** el archivo en Protégé.
2.  **Explora** los individuos: `ejemplo_Sexo` (Cardinalidad 2) y `ejemplo_ID_Cliente` (Cardinalidad 200).
3.  **Inicia el Razonador** (Pellet).
4.  **Observa la Inferencia:** Los individuos aparecerán en amarillo, clasificados automáticamente y con propiedades `sugiereTecnica` asignadas.

### Ejecución de Componentes Académicos (CLI)
- **Minería de Datos (Python):** `docker exec -it examengescon-backend-1 python3 /app/ml/rule_extraction.py`
- **Inferencia Prolog:** `swipl -s backend/prolog/eda_expert.pl`
- **Consultas SQWRL:** Consulta la lista en `backend/ontology/sqwrl_queries.txt`.

---

## 📚 Insumos para el Artículo Técnico

- **Metodología:** Describe el pipeline de "Triple Inferencia" (Ontología -> ML -> Prolog).
- **Resultados:** Incluye capturas de las 3 pestañas de la aplicación mostrando el razonamiento concurrente.
- **Inferencia:** Explica la equivalencia entre los axiomas OWL DL del backend y las reglas SWRL de la demo visual.

