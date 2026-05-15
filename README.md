# EDA Ontology Expert 🦉

Un sistema de **Análisis Exploratorio de Datos (EDA)** basado en conocimiento experto, construido sobre una ontología OWL con razonamiento automático y un asistente RAG impulsado por LLM local (Ollama).

## Cumplimiento Académico (GESCON)

Este proyecto ha sido diseñado para cumplir con los requisitos del examen GESCON, integrando múltiples paradigmas de gestión del conocimiento.

### 🎯 Mapeo de Objetivos Académicos

| Requisito | Implementación | Archivos Relacionados |
|---|---|---|
| **Dataset Seleccionado** | `flight_price.csv` (recortado a 1000 registros) | `backend/data/flight_price.csv` |
| **Extracción de Reglas (ML)** | Árboles de Decisión y Reglas de Asociación (Apriori) | `backend/ml/rule_extraction.py` |
| **Representación Ontológica** | Modelo OWL DL con razonamiento automático (Pellet) | `demo_experto_eda.owx` |
| **Representación Alternativa** | Lógica en Prolog (OAV + Proposiciones) | `backend/prolog/eda_expert.pl` |
| **Consultas Complejas** | Consultas SQWRL de nivel medio-alto | `backend/ontology/sqwrl_queries.txt` |
| **Inferencia Demostrada** | Inferencia en OWL (Pellet) y en Prolog | Ver secciones de ejecución |

---

---

## ¿Qué hace?

Subes un archivo CSV con variables categóricas y el sistema:

1. **Analiza** cada columna: cardinalidad, distribución, ratio de nulos y categoría dominante.
2. **Razona** con una ontología OWL DL — el motor Pellet infiere automáticamente el perfil de cada columna (ej. `ColumnaBinaria`, `DistribucionDesbalanceada`, `AlertaNulosAltos`).
3. **Recomienda** técnicas de visualización específicas basadas en el perfil inferido (Gráfico de Torta, Treemap, Barras Horizontal, etc.).
4. **Asesora** mediante un chatbot RAG que contextualiza las respuestas con los resultados de la ontología usando un LLM local via Ollama.

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    USUARIO                               │
│   Sube CSV → Dashboard → Pregunta al RAG                │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTP
┌───────────────────▼─────────────────────────────────────┐
│               FRONTEND (React + Vite)                    │
│   Puerto 5173 — Tabla de perfiles + Chat RAG             │
└───────────────────┬─────────────────────────────────────┘
                    │ REST API
┌───────────────────▼─────────────────────────────────────┐
│               BACKEND (FastAPI + Python)                 │
│                                                          │
│   POST /upload ─► OntologyEngine.analyze_csv()          │
│         │                                               │
│         ▼                                               │
│   ┌─────────────────────────────────────────┐           │
│   │     ONTOLOGÍA OWL DL (.owx)             │           │
│   │                                          │           │
│   │  ColumnaCategorica                       │           │
│   │    ├─ ColumnaBinaria (card = 2)         │           │
│   │    ├─ CardinalidadBaja (3–14)           │           │
│   │    ├─ CardinalidadAlta (≥15)            │           │
│   │    ├─ DistribucionBalanceada (<50%)     │           │
│   │    ├─ DistribucionMuyDesbalanceada(≥80%)│           │
│   │    ├─ AlertaNulosAltos (>20% nulos)     │           │
│   │    └─ AlertaCategoriaDominante (≥80%)   │           │
│   └─────────────┬───────────────────────────┘           │
│                 │                                        │
│         ┌───────▼────────┐                              │
│         │  PELLET (Java) │  Motor de inferencia OWL DL  │
│         │  Razonamiento  │  Clasifica + asigna           │
│         │  automático    │  sugiereTecnica /             │
│         └───────┬────────┘  tieneRecomendacion           │
│                 │                                        │
│   POST /ask ──► RAG Context Builder                     │
│         │                                               │
└─────────┼───────────────────────────────────────────────┘
          │ HTTP localhost:11434
┌─────────▼──────────────────┐
│     OLLAMA (host)           │
│   Modelo: llama3.2          │
│   Responde preguntas EDA    │
└────────────────────────────┘
```

---

## Flujo detallado

### 1. Carga del CSV
El frontend envía el archivo a `POST /upload`. FastAPI lo parsea con pandas.

### 2. Análisis estadístico
Por cada columna categórica detectada, el motor calcula:
- `tieneCardinalidad` — número de valores únicos
- `tieneTotalRegistros` — número de filas
- `tieneRatioDominante` — frecuencia relativa de la categoría más común
- `tieneRatioNulos` — proporción de valores nulos

### 3. Razonamiento OWL DL (el núcleo del proyecto)
Cada columna se instancia como un individuo `ColumnaCategorica` en la ontología con sus propiedades de datos. Luego se ejecuta **Pellet**:

```
Pellet lee:  ind.tieneCardinalidad = 2
Pellet aplica: ColumnaBinaria ≡ ColumnaCategorica ∧ tieneCardinalidad value 2
Pellet concluye: ind rdf:type ColumnaBinaria
```

Las clasificaciones están definidas mediante `EquivalentClasses` en OWL DL:

| Clase OWL | Condición |
|---|---|
| `ColumnaBinaria` | `tieneCardinalidad value 2` |
| `ColumnaCardinalidadBaja` | `tieneCardinalidad some (int [3..14])` |
| `ColumnaCardinalidadAlta` | `tieneCardinalidad some (int [≥15])` |
| `DistribucionBalanceada` | `tieneRatioDominante some (double [<0.5])` |
| `DistribucionDesbalanceada` | `tieneRatioDominante some (double [≥0.5])` |
| `DistribucionMuyDesbalanceada` | `tieneRatioDominante some (double [≥0.8])` |
| `AlertaNulosAltos` | `tieneRatioNulos some (double [>0.2])` |
| `AlertaCategoriaDominante` | `tieneRatioDominante some (double [≥0.8])` |

Las recomendaciones se propagan vía herencia `SubClassOf`:
```
ColumnaBinaria SubClassOf sugiereTecnica value indTortaPastel
ColumnaCardinalidadAlta SubClassOf tieneRecomendacion value indAgruparMinoritarias
```

### 4. Respuesta y dashboard
El backend devuelve los perfiles y recomendaciones inferidas. El frontend los muestra en tarjetas por columna.

### 5. RAG con Ollama
El usuario escribe una pregunta. El backend construye un prompt con el contexto completo de la ontología (perfiles + recomendaciones) y lo envía a Ollama. El modelo responde fundamentado en ese contexto experto.

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Frontend | React 18 + Vite 4 |
| Backend API | FastAPI + Python 3.10 |
| Motor ontológico | Owlready2 0.46 + Pellet 2.3.1 |
| Ontología | OWL 2 DL (formato RDF/XML) |
| LLM local | Ollama (llama3.2) |
| Contenedores | Docker + Docker Compose |
| Java runtime | OpenJDK 17 (para Pellet) |

---

## Requisitos previos

- **Docker** y **Docker Compose** instalados
- **Ollama** instalado en el host con el modelo `llama3.2`:
  ```bash
  ollama pull llama3.2
  ollama serve   # o habilitado como systemd service
  ```

---

## Instalación y ejecución

```bash
# Clonar el repositorio
git clone <URL_DEL_REPO>
cd eda-ontology-expert

# Levantar los servicios
docker compose up --build

# Acceder
# Frontend: http://localhost:5173
# API docs: http://localhost:8000/docs
```

---

## Estructura del proyecto

```
.
├── docker-compose.yml                          # Orquestación de servicios
├── ontologia_variables_categoricas_corregida.owx  # Ontología OWL DL (fuente de conocimiento)
├── setup_ollama.sh                             # Script opcional para configurar Ollama como servicio
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                  # API FastAPI (endpoints /upload, /ask, /status)
│   └── ontology_engine.py       # Motor: análisis estadístico + razonamiento Pellet
│
└── frontend/
    ├── Dockerfile
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        └── App.jsx              # Dashboard: upload, perfiles, chat RAG
```

---

## API

### `POST /upload`
Sube un CSV y obtiene el análisis ontológico.

**Request:** `multipart/form-data` con campo `file`

**Response:**
```json
{
  "message": "File processed",
  "results": [
    {
      "column": "Sex",
      "cardinality": 2,
      "ratio_dominante": 0.52,
      "ratio_nulos": 0.0,
      "profiles": ["Columna Binaria (2 categorías)", "Distribución Desbalanceada"],
      "recommendations": ["Gráfico de Torta / Pastel", "Gráfico de Barras Horizontal"]
    }
  ]
}
```

### `POST /ask?question=...`
Envía una pregunta al asistente RAG.

**Response:**
```json
{ "answer": "Dado que Sex es una variable binaria..." }
```

### `GET /status`
Verifica que el backend y la ontología estén cargados.

---

## Notas técnicas

- **¿Por qué OWL DL en lugar de SWRL?**  
  Los motores embebidos en Owlready2 (HermiT y Pellet) no soportan operadores matemáticos de SWRL (`swrlb:greaterThanOrEqual`) sobre literales numéricos en modo de producción. La migración a `EquivalentClasses` con `ConstrainedDatatype` es el estándar OWL 2 para expresar este tipo de reglas y es plenamente soportada.

- **Network mode host para Ollama:**  
  El backend usa `network_mode: host` en Docker Compose para poder conectarse al servicio Ollama del host directamente en `localhost:11434` sin configuración adicional de red.

- **Owlready2 0.46 (pinned):**  
  Las versiones posteriores incluyen una versión de Pellet compilada para Java 25, incompatible con OpenJDK 17 (`UnsupportedClassVersionError`). La versión 0.46 es la última estable compatible con Java 17.

---

## ¿Por qué las tabs SWRL y SQWRL de Protégé están vacías?

Al abrir `ontologia_variables_categoricas_corregida.owx` en Protégé, las pestañas **SWRL** y **SQWRL** no muestran reglas. Esto es **intencional** — aquí la explicación completa.

### El diseño original usaba reglas SWRL

La ontología fue diseñada con reglas `DLSafeRule` (SWRL) para expresar el conocimiento experto:

```
# Regla SWRL original (visible en Protégé)
ColumnaCategorica(?c) ∧ tieneCardinalidad(?c, ?n) ∧ swrlb:equal(?n, 2)
  → ColumnaBinaria(?c)

ColumnaCategorica(?c) ∧ tieneRatioDominante(?c, ?r) ∧ swrlb:greaterThan(?r, 0.8)
  → NoInformativaParaSegmentacion(?c)
```

Estas reglas son válidas en Protégé y se verían en la tab SWRL. El problema es ejecutarlas en producción.

### El problema: SWRL built-ins no son soportados por los motores embebidos

| Motor | Comportamiento con `swrlb:greaterThanOrEqual` |
|---|---|
| **HermiT** (Owlready2) | `IllegalArgumentException: built-in atoms are not supported yet` |
| **Pellet** (vía N-Triples) | Los ignora — no infiere nada, resultado vacío |
| **Pellet** (RDF/XML directo) | `InconsistentOntologyError` por conflicto de datatypes |

Error real obtenido al intentarlo con HermiT:
```
Exception in thread "main" java.lang.IllegalArgumentException:
A SWRL rule uses a built-in atom, but built-in atoms are not supported yet.
  at org.semanticweb.HermiT.structural.OWLNormalization$RuleNormalizer.visit
```

### La solución: migración a OWL DL con EquivalentClasses

El conocimiento SWRL se migró a **axiomas OWL 2 DL** con `EquivalentClasses` y `ConstrainedDatatype`:

```
# Equivalente OWL DL — visible en Protégé tab "Classes"
ColumnaBinaria ≡ ColumnaCategorica ⊓ (tieneCardinalidad value 2)

DistribucionMuyDesbalanceada ≡ ColumnaCategorica ⊓
    (tieneRatioDominante some double[≥ 0.8])
```

Las recomendaciones (antes en la cabeza de las reglas SWRL) se expresan como `SubClassOf`:
```
# En lugar de: ColumnaBinaria(?c) → sugiereTecnica(?c, indTortaPastel)
ColumnaBinaria SubClassOf (sugiereTecnica value indTortaPastel)
```

### Comparativa SWRL vs OWL DL

| Aspecto | SWRL (original) | OWL DL (actual) |
|---|---|---|
| Visible en tab SWRL de Protégé | ✅ Sí | ❌ No (están en tab "Classes") |
| Ejecutable por HermiT embebido | ❌ Error en built-ins | ✅ Funciona |
| Ejecutable por Pellet embebido | ❌ Silencioso/inconsistente | ✅ Funciona |
| Estándar W3C | SWRL 1.0 (2004) | OWL 2 (2009, recomendado) |

> Las restricciones actuales **sí son visibles en Protégé** — en la pestaña **"Classes"**, seleccionando cualquier clase (ej. `ColumnaBinaria`), se ven los `EquivalentClasses` con las restricciones numéricas.

### Verificación: el razonador sí funciona

El log de Docker confirma que Pellet infiere correctamente desde los axiomas OWL DL:

```
* Owlready * Reparenting tmp_Sex:  {ColumnaCategorica} => {ColumnaBinaria, DistribucionDesbalanceada}
* Owlready * Reparenting tmp_BP:   {ColumnaCategorica} => {ColumnaCardinalidadBaja, DistribucionBalanceada}
* Owlready * Adding relation tmp_Drug tieneRecomendacion indAptoSegmentacion
```

`Reparenting` es el mensaje de Owlready2 indicando que el razonador **cambió la clasificación** de un individuo — el resultado es idéntico al que habrían producido las reglas SWRL, pero expresado en el lenguaje nativo de OWL 2 DL.

---

## Versión Visual (SWRL/SQWRL)

Para facilitar la navegación y comprensión del conocimiento experto en Protégé, se ha incluido un archivo adicional:

**`demo_experto_eda.owx`**

### Características:
- **Pestaña SWRL:** Contiene todas las reglas de negocio en formato `DLSafeRule` legibles por Protégé.
- **Pestaña SQWRL:** Permite realizar consultas sobre los perfiles e individuos.
- **Propósito:** Meramente **educativo y de visualización**.

### Nota Importante sobre Inferencia:
Aunque esta versión es más fácil de leer en Protégé, **no se utiliza en el pipeline de producción**. Como se explicó en las [Notas Técnicas](#notas-técnicas), los motores de razonamiento embebidos fallan al procesar los *built-ins* matemáticos de SWRL. 

Para el funcionamiento del sistema, se debe utilizar siempre la versión **`ontologia_variables_categoricas_corregida.owx`**, que utiliza axiomas OWL DL puros para garantizar una inferencia estable y rápida en el servidor.

---

## Cumplimiento de Objetivos (Examen GESCON)

Este proyecto cumple estrictamente con los requisitos del **Punto 4: Ontología de conocimiento para análisis exploratorio de variables categóricas**:

### 1. Modelado de Conocimiento Experto
Se han modelado las dimensiones clave del análisis de variables categóricas:
- **Metadatos Estadísticos:** Cardinalidad (número de categorías), ratio de categoría dominante, ratio de nulos y frecuencia de categorías.
- **Perfiles de Columna:** Definición de clases como `ColumnaBinaria`, `ColumnaCardinalidadBaja`, `ColumnaCardinalidadAlta`, `AlertaNulosAltos` y `AlertaCategoriaDominante`.
- **Técnicas de Análisis:** Recomendación de técnicas específicas como Barras (Horizontal/Vertical), Torta, Treemap y Frecuencia Acumulada.

### 2. Inferencia y Recomendaciones Automáticas
El sistema automatiza el razonamiento experto mediante dos mecanismos lógicamente equivalentes:
- **Backend (Producción):** Utiliza **OWL 2 DL (EquivalentClasses)**. Este formato es el estándar para motores de inferencia embebidos (Pellet/HermiT), garantizando estabilidad y evitando errores de tipos de datos en el servidor.
- **Protégé (Demostración Visual):** Se incluye el archivo **`demo_experto_eda.owx`** que contiene **reglas SWRL**. Esto permite visualizar la lógica experta en la pestaña SWRLTab de Protégé, cumpliendo con la exigencia de "reglas SWRL" para la sustentación.

### 3. Pipeline RAG Fundamentado
El chatbot RAG (Ollama) no responde genéricamente. Su prompt es construido dinámicamente con los **resultados del razonador de la ontología**, permitiéndole responder con precisión a preguntas como:
- *"¿Qué hago con una columna de 200 valores únicos?"* (Infiere Cardinalidad Alta -> Sugiere Treemap + Agrupar).
- *"¿Cuándo es útil una variable para segmentar?"* (Infiere AptoParaSegmentacion basado en ratio dominante y nulos).

---

## Guía de Demostración (demo_experto_eda.owx)

Para facilitar la sustentación, el archivo `demo_experto_eda.owx` incluye **individuos pre-creados**:

1.  **Abre** el archivo en Protégé.
2.  **Explora** los individuos en la pestaña "Individuals":
    -   `ejemplo_Sexo`: Verás que tiene `tieneCardinalidad = 2`.
    -   `ejemplo_ID_Cliente`: Verás que tiene `tieneCardinalidad = 200`.
3.  **Inicia el Razonador** (Pellet).
4.  **Observa la Inferencia:** Los individuos se clasificarán automáticamente (aparecerán en amarillo) y se les asignarán las propiedades `sugiereTecnica` y `tieneRecomendacion` según la lógica experta.


## Ejecución de Componentes Académicos

### 1. Minería de Datos (Python)
Para extraer las reglas del dataset de vuelos, ejecuta el script dentro del contenedor del backend:
```bash
docker exec -it examengescon-backend-1 python3 /app/ml/rule_extraction.py
```
Las reglas se guardarán en `backend/ml/reglas_extraidas.txt`.

### 2. Inferencia Lógica (Prolog)
Para demostrar las inferencias en Prolog, utiliza SWI-Prolog con el archivo de conocimiento:
```bash
swipl -s backend/prolog/eda_expert.pl
# Ejemplo de consulta:
# ?- sugiere_tecnica(airline, T).
```

### 3. Consultas SQWRL (Protégé)
Las consultas SQWRL están documentadas en `backend/ontology/sqwrl_queries.txt`. Puedes copiarlas y pegarlas en la pestaña **SQWRLTab** de Protégé mientras tienes abierta la ontología `demo_experto_eda.owx`.

---
