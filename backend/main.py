from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import io
from ontology_engine import OntologyEngine
from ml_engine import MLEngine
from prolog_engine import PrologEngine

app = FastAPI(title="EDA Knowledge Workbench API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ONTOLOGY_PATH = os.getenv("ONTOLOGY_PATH", "demo_experto_eda_v3_numericas.owx")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2")

engine = OntologyEngine(ONTOLOGY_PATH)

# Store temporary dataframes in memory (for demo purposes)
# In production, use Redis or a temp file
temp_storage = {}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # Save to temp storage (use filename as key)
        file_id = file.filename
        temp_storage[file_id] = df
        
        return {
            "filename": file.filename,
            "columns": df.columns.tolist(),
            "sample": df.head(5).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze")
async def analyze_full(filename: str = Form(...), target_column: str = Form(...)):
    if filename not in temp_storage:
        raise HTTPException(status_code=404, detail="File not found. Please upload again.")
    
    df = temp_storage[filename]
    
    try:
        # 1. Ontology Analysis (Structural Knowledge)
        ontology_results = engine.analyze_csv(df)
        
        # 2. ML Rule Extraction (Domain Knowledge)
        ml_results = MLEngine.extract_rules(df, target_column)
        
        # 3. Prolog Inference (Alternative Formal Logic)
        prolog_results = PrologEngine.infer(ontology_results)
        
        return {
            "ontology": ontology_results,
            "ml": ml_results,
            "prolog": prolog_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_rag(question: str = Form(...), context: str = Form(...)):
    # Re-using the RAG logic
    import requests
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer based on EDA knowledge and the context provided:"
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False}
        )
        return response.json()
    except Exception as e:
        return {"response": f"Error connecting to Ollama: {str(e)}"}
