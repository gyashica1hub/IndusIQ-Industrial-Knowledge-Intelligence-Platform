import { useState, useEffect, useRef } from 'react'

export default function UploadPanel({ apiBase, onDocCountChange }) {
  const [files, setFiles] = useState([])
  const [results, setResults] = useState([])
  const [uploading, setUploading] = useState(false)
  const [docs, setDocs] = useState([])
  const fileInput = useRef(null)

  const refreshDocs = async () => {
    const res = await fetch(`${apiBase}/documents`)
    const data = await res.json()
    setDocs(data.documents || [])
    onDocCountChange((data.documents || []).length)
  }

  useEffect(() => { refreshDocs() }, [])

  const handleUpload = async () => {
    if (!files.length) return
    setUploading(true)
    const newResults = []
    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)
      try {
        const res = await fetch(`${apiBase}/upload`, { method: 'POST', body: formData })
        const data = await res.json()
        newResults.push({ file: file.name, ...data })
      } catch (err) {
        newResults.push({ file: file.name, status: 'error', error: String(err) })
      }
    }
    setResults(newResults)
    setUploading(false)
    setFiles([])
    if (fileInput.current) fileInput.current.value = ''
    refreshDocs()
  }

  return (
    <div className="panel">
      <div className="card">
        <h2>Ingest Documents</h2>
        <p className="muted">
          Upload PDFs — maintenance logs, inspection reports, SOPs, P&amp;IDs. Each document is
          chunked, embedded, and scanned for entities (equipment, personnel, regulations) which
          feed the knowledge graph.
        </p>
        <input
          ref={fileInput}
          type="file"
          accept="application/pdf"
          multiple
          onChange={(e) => setFiles(Array.from(e.target.files))}
        />
        <button className="primary" disabled={!files.length || uploading} onClick={handleUpload}>
          {uploading ? 'Processing…' : `Upload & Process ${files.length ? `(${files.length})` : ''}`}
        </button>
      </div>

      {results.length > 0 && (
        <div className="card">
          <h3>Processing Results</h3>
          {results.map((r, i) => (
            <div key={i} className="result-row">
              <strong>{r.file}</strong>
              {r.status === 'success' ? (
                <div className="muted small">
                  {r.chunks_indexed} chunks indexed across {r.pages_processed} pages.
                  {' '}Entities found — Equipment: {r.entities_found?.equipment?.join(', ') || 'none'};
                  {' '}Regulations: {r.entities_found?.regulations?.join(', ') || 'none'}
                </div>
              ) : (
                <div className="error small">Failed: {r.error || r.detail}</div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h3>Indexed Documents ({docs.length})</h3>
        {docs.length === 0 && <p className="muted small">No documents indexed yet.</p>}
        <ul className="doc-list">
          {docs.map((d) => <li key={d}>{d}</li>)}
        </ul>
      </div>
    </div>
  )
}
