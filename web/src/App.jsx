import { useState, useEffect, useRef } from 'react'

export default function App() {
    const [status, setStatus] = useState('online')
    const [logs, setLogs] = useState([])
    const [prompt, setPrompt] = useState('')
    const [isProcessing, setIsProcessing] = useState(false)
    const [showConfig, setShowConfig] = useState(false)
    const [showGuide, setShowGuide] = useState(false)
    const [guideContent, setGuideContent] = useState('')
    const logsEndRef = useRef(null)

    // LLM Config State
    const [llmConfig, setLlmConfig] = useState({
        provider: 'gemini',
        api_key: '',
        model: 'gemini-1.5-flash',
        base_url: ''
    })

    useEffect(() => {
        // Initial fetch
        fetch('/api/logs').then(res => res.json()).then(data => setLogs(data.logs || []))
        fetch('/api/guide').then(res => res.json()).then(data => setGuideContent(data.content))

        const interval = setInterval(() => {
            fetch('/api/logs')
                .then(res => res.json())
                .then(data => setLogs(data.logs || []))
                .catch(() => { })
        }, 2000)

        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [logs])

    const addLocalLog = (msg, type = 'info') => {
        const time = new Date().toLocaleTimeString()
        setLogs(prev => [...prev, `${time} | ${type.toUpperCase()} | ${msg}`])
    }

    const executeAction = async (type, params = {}) => {
        const cmdStr = `agent run '{"type": "${type}", "params": ${JSON.stringify(params)}}'`
        addLocalLog(`Calling Terminal: ${cmdStr}`, 'system')

        try {
            const res = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, params })
            })
            const data = await res.json()
            if (data.status === 'ok') {
                addLocalLog(`Terminal Output: ${data.output.trim()}`, 'ok')
            }
        } catch (err) {
            addLocalLog(`Execution failed: ${err.message}`, 'error')
        }
    }

    const handleChat = async (e) => {
        e.preventDefault()
        if (!prompt.trim() || isProcessing) return

        setIsProcessing(true)
        addLocalLog(`Instruction: ${prompt}`, 'user')

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            })
            const data = await res.json()

            if (data.status === 'error') {
                addLocalLog(`AI Error: ${data.message}`, 'error')
            } else {
                addLocalLog(`AI Intent: ${data.intent}`, 'ai')
                data.results.forEach(r => {
                    if (r.status === 'ok') addLocalLog(`Action Success: ${r.output.trim()}`, 'ok')
                    else addLocalLog(`Action Error: ${r.message}`, 'error')
                })
            }
            setPrompt('')
        } catch (err) {
            addLocalLog(`Chat failed: ${err.message}`, 'error')
        } finally {
            setIsProcessing(false)
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
            addLocalLog(`LLM Platform configured: ${llmConfig.provider}`, 'system')
        } catch (err) {
            addLocalLog('Failed to save config', 'error')
        }
    }

    return (
        <div className="dashboard">
            <header className="header">
                <div className="brand">
                    <h1>OCTOPUS</h1>
                    <span className="version">Unified Engine v0.1</span>
                </div>
                <div className="header-actions">
                    <button className="btn-icon-only" onClick={() => setShowGuide(true)} title="Usage Guide">
                        ❓
                    </button>
                    <button className="btn-icon-only" onClick={() => setShowConfig(true)} title="Settings">
                        ⚙️
                    </button>
                    <div className="status-badge">
                        <div className="status-dot online"></div>
                        TERMINAL CONNECTED
                    </div>
                </div>
            </header>

            <main className="grid">
                <section className="card card-controls">
                    <div className="card-header">
                        <h2>Unified Control</h2>
                        <p className="subtitle">Logic Path Identical to PowerShell CLI</p>
                    </div>

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
                        <h3>Human-in-the-Loop AI Orchestration</h3>
                        <form onSubmit={handleChat} className="chat-form">
                            <input
                                type="text"
                                placeholder="Ex: 'List files in workspace'..."
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                disabled={isProcessing}
                            />
                            <button type="submit" disabled={isProcessing}>
                                {isProcessing ? 'Thinking...' : 'Execute CLI'}
                            </button>
                        </form>
                    </div>
                </section>

                <section className="card card-logs">
                    <h2>CLI Output Console</h2>
                    <div className="log-container">
                        {logs.length === 0 ? (
                            <div className="log-empty">Waiting for CLI interaction...</div>
                        ) : (
                            logs.map((log, i) => {
                                const isSystem = log.includes('| SYSTEM |') || log.includes('Calling Terminal')
                                const isError = log.includes('| ERROR |') || log.includes('Error')
                                const isOk = log.includes('| OK |') || log.includes('Action Success')
                                const isAi = log.includes('| AI |')

                                let className = "log-entry"
                                if (isSystem) className += " system"
                                if (isError) className += " error"
                                if (isOk) className += " ok"
                                if (isAi) className += " ai"

                                return (
                                    <div key={i} className={className}>
                                        {log}
                                    </div>
                                )
                            })
                        )}
                        <div ref={logsEndRef} />
                    </div>
                </section>
            </main>

            {/* Configuration Modal */}
            {showConfig && (
                <div className="modal-overlay">
                    <div className="modal card">
                        <h2>LLM Platform Engine</h2>
                        <p className="modal-subtitle">Configure cloud or local LLM providers</p>

                        <div className="form-group">
                            <label>Provider Type</label>
                            <select
                                value={llmConfig.provider}
                                onChange={(e) => setLlmConfig({ ...llmConfig, provider: e.target.value })}
                            >
                                <option value="gemini">Google Gemini</option>
                                <option value="openai">OpenAI Cloud</option>
                                <option value="local">Local LLM (Ollama/LM Studio)</option>
                                <option value="custom">Custom Provider</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>API Key / Secret</label>
                            <input
                                type="password"
                                placeholder={llmConfig.provider === 'local' ? 'Optional for local' : 'sk-...'}
                                value={llmConfig.api_key}
                                onChange={(e) => setLlmConfig({ ...llmConfig, api_key: e.target.value })}
                            />
                        </div>

                        <div className="form-group">
                            <label>Model Identifier</label>
                            <input
                                type="text"
                                placeholder="e.g. gpt-4o, llama3, gemini-1.5-pro"
                                value={llmConfig.model}
                                onChange={(e) => setLlmConfig({ ...llmConfig, model: e.target.value })}
                            />
                        </div>

                        <div className="form-group">
                            <label>Base URL (API Endpoint)</label>
                            <input
                                type="text"
                                placeholder={llmConfig.provider === 'local' ? 'http://localhost:11434/v1' : 'Leave empty for default'}
                                value={llmConfig.base_url}
                                onChange={(e) => setLlmConfig({ ...llmConfig, base_url: e.target.value })}
                            />
                        </div>

                        <div className="modal-actions">
                            <button className="btn secondary" onClick={() => setShowConfig(false)}>Cancel</button>
                            <button className="btn primary" onClick={saveConfig}>Apply & Unify</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Guide Modal */}
            {showGuide && (
                <div className="modal-overlay">
                    <div className="modal card guide-modal">
                        <div className="guide-content">
                            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{guideContent}</pre>
                        </div>
                        <div className="modal-actions">
                            <button className="btn primary" onClick={() => setShowGuide(false)}>I Understand</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
