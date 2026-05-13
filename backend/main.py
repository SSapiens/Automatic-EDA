from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import requests
import io
from ontology_engine import OntologyEngine

app = FastAPI(title="EDA Ontology Expert API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ONTOLOGY_PATH = os.getenv("ONTOLOGY_PATH", "/app/ontology.owx")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2")

# Initialize Engine
engine = OntologyEngine(ONTOLOGY_PATH)

# Global store for current analysis (simplified for demo)
current_analysis = []

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    global current_analysis
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    
    try:
        current_analysis = engine.analyze_csv(df)
        return {"message": "File processed", "results": current_analysis}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_rag(question: str):
    if not current_analysis:
        raise HTTPException(status_code=400, detail="No data analyzed yet. Upload a CSV first.")
    
    # Build Context from Ontology Inferences
    context = engine.get_knowledge_context(current_analysis)
    
    prompt = f"""Eres un experto en Analisis Exploratorio de Datos (EDA). 
Basate UNICAMENTE en el contexto de la ontologia proporcionado para responder la pregunta del usuario. 
Si la informacion no esta en el contexto, usa tu conocimiento general pero indica que es una sugerencia externa.

CONTEXTO DE LA ONTOLOGIA:
{context}

PREGUNTA DEL USUARIO:
{question}

RESPUESTA EXPERTA:"""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        return {"answer": response.json().get("response")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Ollama: {str(e)}")

@app.get("/status")
def get_status():
    return {"status": "online", "ontology_loaded": engine.onto is not None}
