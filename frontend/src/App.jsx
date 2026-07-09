import { useState } from 'react'
import UploadPanel from './components/UploadPanel.jsx'
import ChatPanel from './components/ChatPanel.jsx'
import GraphView from './components/GraphView.jsx'

const API_BASE = '/api'

export default function App() {
  const [tab, setTab] = useState('chat')
  const [docCount, setDocCount] = useState(0)

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <div className="logo-mark">IK</div>
          <div>
            <h1>Industrial Knowledge Intelligence</h1>
            <p className="subtitle">Unified Asset &amp; Operations Brain — Prototype</p>
          </div>
        </div>
        <div className="doc-badge">{docCount} document{docCount !== 1 ? 's' : ''} indexed</div>
      </header>

      <nav className="tabs">
        <button className={tab === 'chat' ? 'active' : ''} onClick={() => setTab('chat')}>
          Expert Copilot
        </button>
        <button className={tab === 'upload' ? 'active' : ''} onClick={() => setTab('upload')}>
          Ingest Documents
        </button>
        <button className={tab === 'graph' ? 'active' : ''} onClick={() => setTab('graph')}>
          Knowledge Graph
        </button>
      </nav>

      <main className="main">
        {tab === 'upload' && <UploadPanel apiBase={API_BASE} onDocCountChange={setDocCount} />}
        {tab === 'chat' && <ChatPanel apiBase={API_BASE} />}
        {tab === 'graph' && <GraphView apiBase={API_BASE} />}
      </main>
    </div>
  )
}
