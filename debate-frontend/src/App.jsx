import React, { useState, useEffect, useRef } from 'react'
import './App.css'

const App = () => {
  const [topic, setTopic] = useState('')
  const [personas, setPersonas] = useState({})
  const [selectedProPersona, setSelectedProPersona] = useState('')
  const [selectedConPersona, setSelectedConPersona] = useState('')
  const [rounds, setRounds] = useState('2')
  const [isRunning, setIsRunning] = useState(false)
  const [debateData, setDebateData] = useState([])
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [recentDebates, setRecentDebates] = useState(() => {
    const saved = localStorage.getItem('recentDebates')
    return saved ? JSON.parse(saved) : []
  })
  const eventSourceRef = useRef(null)
  const debateCompletedRef = useRef(false)

  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/personas`)
        if (response.ok) {
          const data = await response.json()
          setPersonas(data)
          if (Object.keys(data).length > 0) {
            const firstKey = Object.keys(data)[0]
            setSelectedProPersona(data[firstKey].pro)
            setSelectedConPersona(data[firstKey].con)
          }
        }
      } catch (error) {
        console.error('Failed to fetch personas:', error)
      }
    }
    fetchPersonas()
  }, [])

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const startDebate = () => {
    if (!topic.trim() || isRunning) return

    setIsRunning(true)
    setConnectionStatus('connecting')
    setDebateData([])

    const url = new URL(`${import.meta.env.VITE_API_URL}/api/debate`)
    url.searchParams.append('topic', topic)
    url.searchParams.append('rounds', rounds)

    eventSourceRef.current = new EventSource(url.toString())

    eventSourceRef.current.onopen = () => {
      setConnectionStatus('connected')
    }

    eventSourceRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setDebateData(prev => [...prev, data])
        
        if (data.type === 'done') {
          debateCompletedRef.current = true
          eventSourceRef.current?.close()
          setIsRunning(false)
          setConnectionStatus('completed')
          
          const newDebate = {
            topic,
            timestamp: new Date().toISOString(),
            rounds: parseInt(rounds),
            proPersona: selectedProPersona,
            conPersona: selectedConPersona
          }
          
          const updated = [newDebate, ...recentDebates].slice(0, 10)
          setRecentDebates(updated)
          localStorage.setItem('recentDebates', JSON.stringify(updated))
        }
      } catch (error) {
        console.error('Error parsing event:', error)
      }
    }

    eventSourceRef.current.onerror = () => {
      if (!debateCompletedRef.current) {
        setIsRunning(false)
        setConnectionStatus('error')
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }

  const downloadTranscript = () => {
    const transcriptLines = []
    debateData.forEach(item => {
      if (item.type === 'start') {
        transcriptLines.push('# Debate Started')
        transcriptLines.push(`**Topic:** ${item.topic}`)
        transcriptLines.push(`**Rounds:** ${item.rounds}`)
        transcriptLines.push(`**Pro:** ${item.pro_name}`)
        transcriptLines.push(`**Con:** ${item.con_name}`)
        transcriptLines.push('')
      } else if (item.type === 'round_start') {
        transcriptLines.push(`## Round ${item.round}`)
      } else if (item.type === 'argument') {
        transcriptLines.push(`**${item.name}** (${item.side}): ${item.text}`)
      } else if (item.type === 'verdict') {
        transcriptLines.push(`### Verdict`)
        transcriptLines.push(item.text)
      }
    })

    const markdown = transcriptLines.join('\n\n')
    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `debate-transcript-${Date.now()}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [])

  const hasStarted = debateData.some(item => item.type === 'start')
  
  const verdictItem = debateData.find(item => item.type === 'verdict')
  const argumentItems = debateData.filter(item => item.type === 'argument')
  const roundNumbers = [...new Set(argumentItems.map(item => item.round))].sort((a, b) => a - b)

  return (
    <div className="app">
      <header className="top-bar">
        <h1 className="headline">Debate Arena</h1>
        {isRunning && (
          <div className="live-indicator">
            <div className="live-dot" />
            <span>Live</span>
          </div>
        )}
      </header>

      <main className="main-content">
        <section className="control-panel">
          <div className="form-group">
            <label className="label-sm">TOPIC</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter debate topic..."
              className="input-field"
              disabled={isRunning}
            />
          </div>

          <div className="form-group">
            <label className="label-sm">PERSONAS</label>
            <select
              value={selectedProPersona}
              onChange={(e) => {
                const personaKey = Object.keys(personas).find(key => personas[key].pro === e.target.value)
                if (personaKey) {
                  setSelectedProPersona(personas[personaKey].pro)
                  setSelectedConPersona(personas[personaKey].con)
                }
              }}
              className="select-field"
              disabled={isRunning || Object.keys(personas).length === 0}
            >
              <option value="">Select Persona</option>
              {Object.entries(personas).map(([key, value]) => (
                <option key={key} value={value.pro}>{value.pro} vs {value.con}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="label-sm">ROUNDS</label>
            <select
              value={rounds}
              onChange={(e) => setRounds(e.target.value)}
              className="select-field"
              disabled={isRunning}
            >
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
            </select>
          </div>

          <button
            onClick={startDebate}
            disabled={isRunning || !topic.trim() || !selectedProPersona || !selectedConPersona}
            className="button button-primary"
          >
            Start Debate
          </button>
        </section>

        {connectionStatus && (
          <div className={`status-line ${connectionStatus}`}>
            Status: {connectionStatus}
          </div>
        )}

        <section className="debate-feed">
          {debateData.length > 0 && (
            <>
              {roundNumbers.map(round => (
                <div key={round} className="round-divider">
                  <span className="label-sm">ROUND {round}</span>
                </div>
              ))}

              {debateData.map((item, index) => {
                if (item.type === 'argument') {
                  const prev = debateData[index - 1]
                  const side = item.side
                  const borderColor = side === 'pro' ? 'var(--color-success)' : 'var(--color-error)'
                  
                  return (
                    <article key={index} className="argument-card" style={{ borderTopColor: borderColor }}>
                      <div className="argument-header">
                        <span className="side-tag" style={{ 
                          backgroundColor: side === 'pro' ? 'rgba(43, 224, 140, 0.1)' : 'rgba(255, 58, 92, 0.1)'
                        }}>
                          {side.toUpperCase()}
                        </span>
                        <span className="speaker-name">{item.name}</span>
                      </div>
                      <p className="argument-text">{item.text}</p>
                    </article>
                  )
                } else if (item.type === 'verdict') {
                  return (
                    <article key={index} className="verdict-card">
                      <div className="verdict-header">
                        <div className="info-icon" />
                        <span className="label-sm">JUDGE</span>
                      </div>
                      <p className="verdict-text">{item.text}</p>
                    </article>
                  )
                }
                return null
              })}
            </>
          )}
        </section>

        {verdictItem && (
          <section className="transcript-section">
            <button onClick={downloadTranscript} className="button button-secondary">
              Download transcript
            </button>
          </section>
        )}

        {recentDebates.length > 0 && (
          <section className="recent-debates">
            <h2 className="subtitle">Recent Debates</h2>
            <div className="debates-list">
              {recentDebates.map((debate, index) => (
                <div key={index} className="debate-row">
                  <span className="debate-topic">{debate.topic}</span>
                  <span className="debate-meta">
                    {debate.rounds} rounds • {debate.proPersona} vs {debate.conPersona} • {formatTimestamp(debate.timestamp)}
                  </span>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
