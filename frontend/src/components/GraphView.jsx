import { useEffect, useState, useCallback } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

const COLORS = {
  document: '#4f9dde',
  equipment: '#e8a03c',
  personnel: '#6fcf97',
  regulations: '#eb5757',
  process_parameters: '#bb86fc',
}

export default function GraphView({ apiBase }) {
  const [data, setData] = useState({ nodes: [], links: [] })
  const [loading, setLoading] = useState(true)

  const loadGraph = useCallback(async () => {
    setLoading(true)
    const res = await fetch(`${apiBase}/graph`)
    const graph = await res.json()
    setData({
      nodes: graph.nodes.map((n) => ({ ...n, val: n.type === 'document' ? 8 : 4 })),
      links: graph.links,
    })
    setLoading(false)
  }, [apiBase])

  useEffect(() => { loadGraph() }, [loadGraph])

  return (
    <div className="panel">
      <div className="card">
        <h2>Knowledge Graph</h2>
        <p className="muted">
          Documents (blue) linked to extracted entities — equipment (orange), personnel (green),
          regulations (red), process parameters (purple). Nodes shared across documents reveal
          cross-document relationships, e.g. a piece of equipment mentioned in both a maintenance
          log and an inspection report.
        </p>
        <div className="legend">
          {Object.entries(COLORS).map(([k, c]) => (
            <span key={k} className="legend-item"><span className="dot" style={{ background: c }} />{k}</span>
          ))}
        </div>
        <button className="secondary" onClick={loadGraph}>Refresh Graph</button>

        <div className="graph-container">
          {loading && <p className="muted">Loading graph…</p>}
          {!loading && data.nodes.length === 0 && (
            <p className="muted">No graph data yet — ingest documents first.</p>
          )}
          {!loading && data.nodes.length > 0 && (
            <ForceGraph2D
              graphData={data}
              nodeLabel={(n) => `${n.label} (${n.type})`}
              nodeColor={(n) => COLORS[n.type] || '#999'}
              nodeVal={(n) => n.val}
              linkColor={() => 'rgba(255,255,255,0.15)'}
              width={800}
              height={520}
              backgroundColor="#0f1117"
            />
          )}
        </div>
      </div>
    </div>
  )
}
