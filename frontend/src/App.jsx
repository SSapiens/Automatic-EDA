import React, { useState } from 'react'
import axios from 'axios'
import './index.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [results, setResults] = useState([])
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setLoading(true)
    setResults([]) // Clear previous
    try {
      const res = await axios.post(`${API_BASE}/upload`, formData)
      console.log("Resultados recibidos:", res.data.results)
      setResults(res.data.results || [])
      if (!res.data.results || res.data.results.length === 0) {
        alert("No se detectaron columnas categoricas en este archivo.")
      } else {
        alert("Analisis completado con exito")
      }
    } catch (err) {
      console.error(err)
      alert("Error al procesar el archivo")
    } finally {
      setLoading(false)
    }
  }

  const handleAsk = async () => {
    if (!question) return
    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/ask?question=${encodeURIComponent(question)}`)
      setAnswer(res.data.answer)
    } catch (err) {
      alert("Error al consultar al RAG")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>Analizador EDA Experto</h1>
      <div style={{ marginBottom: '2rem' }}>
        <p>Sube un CSV para que la ontologia lo clasifique y el RAG te asesore.</p>
        <input type="file" accept=".csv" onChange={handleFileUpload} disabled={loading} />
      </div>

      {loading && <div className="loader">Procesando datos con la Ontologia...</div>}

      <div className="card-grid">
        {results && results.length > 0 ? (
          results.map((res, i) => (
            <div key={i} className="card">
              <h3>{res.column}</h3>
              <p><strong>Cardinalidad:</strong> {res.cardinality}</p>
              <p><strong>Clasificacion:</strong></p>
              <div style={{ minHeight: '30px' }}>
                {res.profiles && res.profiles.length > 0 ? (
                  res.profiles.map(p => <span key={p} className="badge">{p}</span>)
                ) : (
                  <span style={{ fontSize: '0.8rem', color: '#999' }}>Sin clasificacion especifica</span>
                )}
              </div>
              <p><strong>Recomendaciones:</strong></p>
              <p style={{ fontSize: '0.9rem', color: '#555' }}>
                {res.recommendations && res.recommendations.length > 0 
                  ? res.recommendations.join(', ') 
                  : "No se encontraron recomendaciones para este perfil."}
              </p>
            </div>
          ))
        ) : (
          !loading && <p style={{ color: '#999' }}>Aun no hay datos analizados. Sube un archivo CSV.</p>
        )}
      </div>

      {results && results.length > 0 && (
        <div className="chat-box">
          <h2>Consultar al Asesor RAG (Ollama)</h2>
          <textarea 
            rows="3" 
            placeholder="Ej: ¿Por que la columna Ciudad tiene cardinalidad alta y que implica?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button onClick={handleAsk} disabled={loading}>Enviar Pregunta</button>
          
          {answer && (
            <div className="answer-pane">
              <strong>Respuesta del Experto:</strong>
              <p>{answer}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
