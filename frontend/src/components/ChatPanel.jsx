import { useState, useRef, useEffect } from 'react'

const SAMPLE_QUESTIONS = [
  "What caused the Pump-101 vibration issue and how was it fixed?",
  "Are there any open compliance gaps right now?",
  "What is the lubrication interval for centrifugal pumps and who approves changes to it?",
  "Summarize everything related to Compressor-7.",
]

export default function ChatPanel({ apiBase }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (question) => {
    const q = question || input
    if (!q.trim() || loading) return
    setMessages((m) => [...m, { role: 'user', text: q }])
    setInput('')
    setLoading(true)
    try {
      const res = await fetch(`${apiBase}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      })
      const data = await res.json()
      setMessages((m) => [...m, { role: 'assistant', text: data.answer, sources: data.sources }])
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', text: 'Error reaching backend. Is it running?', sources: [] }])
    }
    setLoading(false)
  }

  return (
    <div className="panel chat-panel">
      <div className="card chat-card">
        <h2>Expert Knowledge Copilot</h2>
        <p className="muted">Ask any question across all ingested documents. Answers are grounded with source citations.</p>

        {messages.length === 0 && (
          <div className="sample-questions">
            {SAMPLE_QUESTIONS.map((q) => (
              <button key={q} className="chip" onClick={() => send(q)}>{q}</button>
            ))}
          </div>
        )}

        <div className="chat-window">
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>
              <div className="bubble-text">{m.text}</div>
              {m.sources && m.sources.length > 0 && (
                <div className="sources">
                  {m.sources.map((s, j) => (
                    <span key={j} className="source-tag">
                      {s.doc_name} · p.{s.page_number} · {Math.round(s.relevance_score * 100)}% match
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="bubble assistant"><div className="bubble-text muted">Thinking…</div></div>}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input-row">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Ask about equipment, compliance, maintenance history…"
          />
          <button className="primary" onClick={() => send()} disabled={loading}>Ask</button>
        </div>
      </div>
    </div>
  )
}
