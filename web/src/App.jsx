import { useState, useEffect } from 'react'

export default function App() {
    const [status, setStatus] = useState('offline')
    const [logs, setLogs] = useState([])
    const [prompt, setPrompt] = useState('')
    const [isSyncing, setIsSyncing] = useState(false)
    const [showConfig, setShowConfig] = useState(false)

    // LLM Config State
    const [llmConfig, setLlmConfig] = useState({
        provider: 'gemini',
        api_key: '',
        model: 'gemini-1.5-flash'
    })

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await fetch('/api/status')
                const data = await res.json()
                setStatus(data.status)
            } catch (err) {
                setStatus('offline')
            }
        }

        const fetchLogs = async () => {
            try {
                const res = await fetch('/api/logs')
                const data = await res.json()
                setLogs(data.logs)
            } catch (err) { }
        }

        const interval = setInterval(() => {
            fetchStatus()
            fetchLogs()
        }, 1000)

        return () => clearInterval(interval)
    }, [])

    const executeAction = async (type, params = {}) => {
        try {
            await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, params })
            })
        } catch (err) {
            console.error(err)
        }
    }

    const handleChat = async (e) => {
        e.preventDefault()
        if (!prompt.trim() || isSyncing) return

        setIsSyncing(true)
        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            })
            const data = await res.json()
            if (data.status === 'error') {
                alert(`LLM Error: ${data.message}`)
            }
            setPrompt('')
        } catch (err) {
            alert('Failed to send prompt to Octopus')
        } finally {
            setIsSyncing(false)
        }
    }

    const saveConfig = async () => {
        try {
            await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(llmConfig)
            })
            setShowConfig(false)
        } catch (err) {
            alert('Failed to save configuration')
        }
    }

    return (
        <div className="dashboard">
            <header className="header">
                <div className="brand">
                    <h1>OCTOPUS</h1>
                    <span className="version">v0.1 Premium</span>
                </div>
                <div className="header-actions">
                    <button className="btn-icon-only" onClick={() => setShowConfig(true)} title="Settings">
                        ⚙️
                    </button>
                    <div className="status-badge">
                        <div className={`status-dot ${status === 'ready' ? 'online' : 'offline'}`}></div>
                        {status.toUpperCase()}
                    </div>
                </div>
            </header>

            <main className="grid">
                <section className="card card-controls">
                    <h2>Quick Actions</h2>
                    <div className="controls">
                        <button className="btn" onClick={() => executeAction('mouse.move', { x: 500, y: 500 })}>
                            <span className="btn-icon">🎯</span>
                            Center Mouse
                        </button>
                        <button className="btn" onClick={() => executeAction('mouse.click', { button: 'left' })}>
                            <span className="btn-icon">🖱️</span>
                            Left Click
                        </button>
                        <button className="btn" onClick={() => executeAction('system.screen_size')}>
                            <span className="btn-icon">📏</span>
                            Screen Info
                        </button>
                        <button className="btn" onClick={() => executeAction('system.info')}>
                            <span className="btn-icon">⚙️</span>
                            System Info
                        </button>
                    </div>

                    <div className="chat-area">
                        <h3>Natural Language Instruction</h3>
                        <form onSubmit={handleChat} className="chat-form">
                            <input
                                type="text"
                                placeholder="Ex: 'Create a new folder named work on desktop'..."
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                disabled={isSyncing}
                            />
                            <button type="submit" disabled={isSyncing}>
                                {isSyncing ? '...' : 'Send'}
                            </button>
                        </form>
                    </div>
                </section>

                <section className="card card-logs">
                    <h2>Execution Logs</h2>
                    <div className="log-container">
                        {logs.length === 0 ? (
                            <div className="log-empty">No actions recorded yet...</div>
                        ) : (
                            logs.map((log, i) => (
                                <div key={i} className="log-entry">
                                    {log}
                                </div>
                            ))
                        )}
                    </div>
                </section>
            </main>

            {showConfig && (
                <div className="modal-overlay">
                    <div className="modal card">
                        <h2>Platform Configuration</h2>
                        <div className="form-group">
                            <label>Provider</label>
                            <select
                                value={llmConfig.provider}
                                onChange={(e) => setLlmConfig({ ...llmConfig, provider: e.target.value })}
                            >
                                <option value="gemini">Google Gemini</option>
                                <option value="openai">OpenAI</option>
                                <option value="mock">Mock Tester</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>API Key</label>
                            <input
                                type="password"
                                placeholder="Paste your key here..."
                                value={llmConfig.api_key}
                                onChange={(e) => setLlmConfig({ ...llmConfig, api_key: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label>Model Name</label>
                            <input
                                type="text"
                                placeholder="e.g. gemini-1.5-pro"
                                value={llmConfig.model}
                                onChange={(e) => setLlmConfig({ ...llmConfig, model: e.target.value })}
                            />
                        </div>
                        <div className="modal-actions">
                            <button className="btn secondary" onClick={() => setShowConfig(false)}>Cancel</button>
                            <button className="btn primary" onClick={saveConfig}>Save Changes</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
