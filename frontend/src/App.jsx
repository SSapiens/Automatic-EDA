import React, { useState } from 'react'
import axios from 'axios'
import './index.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [fileData, setFileData] = useState(null)
  const [targetCol, setTargetCol] = useState('')
  const [fullResults, setFullResults] = useState(null)
  const [activeTab, setActiveTab] = useState('ontology')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/upload`, formData)
      setFileData(res.data)
      setTargetCol(res.data.columns[res.data.columns.length - 1]) // Default to last
    } catch (err) {
      alert("Error al subir archivo")
    } finally {
      setLoading(false)
    }
  }

  const handleRunAnalysis = async () => {
    setLoading(true)
    const formData = new FormData()
    formData.append('filename', fileData.filename)
    formData.append('target_column', targetCol)
    try {
      const res = await axios.post(`${API_BASE}/analyze`, formData)
      setFullResults(res.data)
    } catch (err) {
      alert("Error en el analisis de conocimiento")
    } finally {
      setLoading(false)
    }
  }

  const handleAsk = async () => {
    if (!question) return
    setLoading(true)
    const formData = new FormData()
    formData.append('question', question)
    formData.append('context', JSON.stringify(fullResults?.ontology || {}))
    try {
      const res = await axios.post(`${API_BASE}/ask`, formData)
      setAnswer(res.data.response)
    } catch (err) {
      alert("Error en RAG")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header style={{ marginBottom: '3rem' }}>
        <h1>Workbench de Gestión del Conocimiento</h1>
        <p style={{ color: '#94a3b8' }}>Extracción, Representación y Razonamiento Multiparadigma para EDA</p>
      </header>

      {!fileData ? (
        <div className="glass" style={{ textAlign: 'center', padding: '4rem' }}>
          <h2>Empezar Análisis</h2>
          <p>Selecciona un dataset CSV para iniciar el flujo de conocimiento experto.</p>
          <input type="file" accept=".csv" onChange={handleFileUpload} />
        </div>
      ) : !fullResults ? (
        <div className="glass config-step">
          <h2>Configurar Inferencia</h2>
          <p>Dataset cargado: <strong>{fileData.filename}</strong></p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <label>Selecciona la etiqueta (Target) para ML:</label>
            <select value={targetCol} onChange={(e) => setTargetCol(e.target.value)}>
              {fileData.columns.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <button className="primary" onClick={handleRunAnalysis} disabled={loading}>
            {loading && <span className="loader"></span>}
            Ejecutar Suite de Conocimiento
          </button>
        </div>
      ) : (
        <>
          <div className="tab-nav">
            <button className={`tab-btn ${activeTab === 'ontology' ? 'active' : ''}`} onClick={() => setActiveTab('ontology')}>
              Ontología (OWL DL)
            </button>
            <button className={`tab-btn ${activeTab === 'ml' ? 'active' : ''}`} onClick={() => setActiveTab('ml')}>
              Reglas de Dominio (ML)
            </button>
            <button className={`tab-btn ${activeTab === 'prolog' ? 'active' : ''}`} onClick={() => setActiveTab('prolog')}>
              Lógica Formal (Prolog)
            </button>
          </div>

          <div className="glass">
            {activeTab === 'ontology' && (
              <div className="grid">
                {fullResults.ontology.map((res, i) => (
                  <div key={i} className="card glass" style={{ padding: '1rem' }}>
                    <h3 style={{ margin: '0 0 0.5rem 0', color: '#38bdf8' }}>{res.column}</h3>
                    <p style={{ fontSize: '0.9rem' }}><strong>Cardinalidad:</strong> {res.cardinality}</p>
                    <div>
                      {res.profiles.map(p => <span key={p} className="badge">{p}</span>)}
                    </div>
                    <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '1rem' }}>
                      <strong>Sugerencia:</strong> {res.recommendations.join(', ')}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'ml' && (
              <div>
                <h3>Árbol de Decisión (Extracción de Reglas)</h3>
                <pre>{fullResults.ml.tree}</pre>
                <h3 style={{ marginTop: '2rem' }}>Reglas de Asociación (Apriori)</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {fullResults.ml.association_rules.map((r, i) => (
                    <div key={i} className="badge" style={{ display: 'block', borderRadius: '0.5rem' }}>{r}</div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'prolog' && (
              <div>
                <h3>Hechos OAV Generados (Object-Attribute-Value)</h3>
                <pre>{fullResults.prolog.facts}</pre>
                <h3 style={{ marginTop: '2rem' }}>Resultado de Inferencia Lógica</h3>
                <pre>{fullResults.prolog.inferences}</pre>
              </div>
            )}
          </div>

          <div className="chat-box glass">
            <h2>Asistente RAG Fundamentado</h2>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8' }}>Este asesor utiliza los resultados de la Ontología y el ML para fundamentar sus respuestas.</p>
            <textarea 
              rows="3" 
              placeholder="¿Qué me sugieres para una columna con cardinalidad alta?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <button className="primary" onClick={handleAsk} disabled={loading}>
              {loading && <span className="loader"></span>}
              Consultar Experto
            </button>
            {answer && (
              <div style={{ marginTop: '1rem', padding: '1rem', background: '#020617', borderRadius: '0.5rem' }}>
                <p>{answer}</p>
              </div>
            )}
          </div>
          <button style={{ marginTop: '2rem', background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }} onClick={() => setFullResults(null)}>
            ← Analizar otro archivo
          </button>
        </>
      )}
    </div>
  )
}

export default App
