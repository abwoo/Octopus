import { useState, useEffect, useRef } from 'react'

export default function App() {
    const [logs, setLogs] = useState([])
    const [prompt, setPrompt] = useState('')
    const [isProcessing, setIsProcessing] = useState(false)
    const [showConfig, setShowConfig] = useState(false)
    const [showGuide, setShowGuide] = useState(false)
    const [guideContent, setGuideContent] = useState('')
    const logsEndRef = useRef(null)

    // LLM Config State
    const [llmConfig, setLlmConfig] = useState({
        provider: 'openai',
        api_key: '',
        model: '',
        base_url: ''
    })

    useEffect(() => {
        fetchLogs()
        fetchGuide()
        const interval = setInterval(fetchLogs, 2000)
        return () => clearInterval(interval)
    }, [])

    const fetchLogs = () => {
        fetch('/api/logs').then(res => res.json()).then(data => setLogs(data.logs || []))
    }

    const fetchGuide = () => {
        fetch('/api/guide').then(res => res.json()).then(data => setGuideContent(data.content))
    }

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [logs])

    const addLocalLog = (msg, type = 'info') => {
        const time = new Date().toLocaleTimeString()
        setLogs(prev => [...prev, `${time} | ${type.toUpperCase()} | ${msg}`])
    }

    const handleCommand = async (e) => {
        e.preventDefault()
        if (!prompt.trim() || isProcessing) return

        setIsProcessing(true)
        const cmd = prompt.trim()

        // If it starts with '!', treat as raw PowerShell, else treat as AI instruction
        if (cmd.startsWith('!')) {
            const rawCmd = cmd.substring(1)
            addLocalLog(`Executing PowerShell: ${rawCmd}`, 'system')
            try {
                const res = await fetch('/api/terminal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cmd: rawCmd })
                })
                const data = await res.json()
                if (data.output) addLocalLog(data.output, 'terminal')
                if (data.error) addLocalLog(data.error, 'error')
            } catch (err) {
                addLocalLog(`Terminal Error: ${err.message}`, 'error')
            }
        } else {
            // AI Chat Mode
            addLocalLog(`AI Instruction: ${cmd}`, 'user')
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: cmd })
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
            } catch (err) {
                addLocalLog(`Chat failed: ${err.message}`, 'error')
            }
        }

        setPrompt('')
        setIsProcessing(false)
    }

    const saveConfig = async () => {
        try {
            await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(llmConfig)
            })
            setShowConfig(false)
            addLocalLog(`Protocol configured: ${llmConfig.provider}`, 'system')
        } catch (err) {
            addLocalLog('Failed to save config', 'error')
        }
    }

    const executeAction = async (type, params = {}) => {
        addLocalLog(`Sending Action: ${type}`, 'system')
        try {
            const res = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, params })
            })
            const data = await res.json()
            if (data.output) addLocalLog(data.output, 'ok')
            else if (data.message) addLocalLog(data.message, 'error')
        } catch (err) {
            addLocalLog(`Execution failed: ${err.message}`, 'error')
        }
    }

    return (
        <div className="dashboard">
            <header className="header">
                <div className="brand">
                    <h1>OCTOPUS</h1>
                    <span className="version">Hybrid Engine v0.2</span>
                </div>
                <div className="header-actions">
                    <button className="btn-icon-only" onClick={() => { fetchGuide(); setShowGuide(true); }} title="Guide">❓</button>
                    <button className="btn-icon-only" onClick={() => setShowConfig(true)} title="Settings">⚙️</button>
                    <div className="status-badge">
                        <div className="status-dot online"></div>
                        KERNEL READY
                    </div>
                </div>
            </header>

            <main className="grid">
                <section className="card card-controls">
                    <div className="card-header">
                        <h2>Command Interface</h2>
                        <p className="subtitle">Universal PowerShell & AI Bridge</p>
                    </div>

                    <div className="controls">
                        <button className="btn" onClick={() => executeAction('system.screen_size')}>
                            <span className="btn-icon">📏</span> Screen Size
                        </button>
                        <button className="btn" onClick={() => executeAction('system.info')}>
                            <span className="btn-icon">⚙️</span> System Info
                        </button>
                        <button className="btn" onClick={() => window.open('https://github.com', '_blank')}>
                            <span className="btn-icon">🌐</span> Open Browser
                        </button>
                        <button className="btn" onClick={() => executeAction('file.read', { path: 'workspace/logs.txt' })}>
                            <span className="btn-icon">📂</span> Read Workspace
                        </button>
                    </div>

                    <div className="chat-area">
                        <h3>Terminal Interaction</h3>
                        <p className="hint">Tip: Use <code>!</code> to run raw PowerShell (e.g. <code>!ls</code>)</p>
                        <form onSubmit={handleCommand} className="chat-form">
                            <input
                                type="text"
                                placeholder="Ask AI or type !powershell_command..."
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                disabled={isProcessing}
                            />
                            <button type="submit" disabled={isProcessing}>
                                {isProcessing ? 'Proc...' : 'ENTER'}
                            </button>
                        </form>
                    </div>
                </section>

                <section className="card card-logs">
                    <h2>Octopus Core Engine Logs</h2>
                    <div className="log-container">
                        {logs.map((log, i) => {
                            const type = log.includes('| SYSTEM |') ? 'system' :
                                log.includes('| TERMINAL |') ? 'terminal' :
                                    log.includes('| USER |') ? 'user' :
                                        log.includes('| AI |') ? 'ai' :
                                            log.includes('| OK |') ? 'ok' :
                                                log.includes('| ERROR |') ? 'error' : ''
                            return (
                                <div key={i} className={`log-entry ${type}`}>
                                    {log}
                                </div>
                            )
                        })}
                        <div ref={logsEndRef} />
                    </div>
                </section>
            </main>

            {showConfig && (
                <div className="modal-overlay">
                    <div className="modal card">
                        <h2>Module Config</h2>
                        <p className="modal-subtitle">Diversify Model Protocols & Endpoints</p>

                        <div className="form-group">
                            <label>Protocol / Provider</label>
                            <select
                                value={llmConfig.provider}
                                onChange={(e) => setLlmConfig({ ...llmConfig, provider: e.target.value })}
                            >
                                <option value="openai">OpenAI (GPT-4o/o1)</option>
                                <option value="gemini">Google Gemini (1.5 Pro)</option>
                                <option value="anthropic">Anthropic (Claude 3.5)</option>
                                <option value="local">Local (Ollama/LM Studio)</option>
                                <option value="http">Universal HTTP (Custom)</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Secret Key</label>
                            <input
                                type="password"
                                placeholder="API Key..."
                                value={llmConfig.api_key}
                                onChange={(e) => setLlmConfig({ ...llmConfig, api_key: e.target.value })}
                            />
                        </div>

                        <div className="form-group">
                            <label>Model ID</label>
                            <input
                                type="text"
                                placeholder="gpt-4o, claude-3-5-sonnet..."
                                value={llmConfig.model}
                                onChange={(e) => setLlmConfig({ ...llmConfig, model: e.target.value })}
                            />
                        </div>

                        <div className="form-group">
                            <label>Custom Endpoint (Base URL)</label>
                            <input
                                type="text"
                                placeholder="https://api.example.com/v1"
                                value={llmConfig.base_url}
                                onChange={(e) => setLlmConfig({ ...llmConfig, base_url: e.target.value })}
                            />
                        </div>

                        <div className="modal-actions">
                            <button className="btn secondary" onClick={() => setShowConfig(false)}>Close</button>
                            <button className="btn primary" onClick={saveConfig}>Update Kernel</button>
                        </div>
                    </div>
                </div>
            )}

            {showGuide && (
                <div className="modal-overlay">
                    <div className="modal card guide-modal expanded">
                        <h2>Operation Manual</h2>
                        <div className="guide-content terminal-style">
                            {guideContent ? (
                                <pre>{guideContent}</pre>
                            ) : (
                                <div className="loading">Loading manual from core docs...</div>
                            )}
                        </div>
                        <div className="modal-actions">
                            <button className="btn primary" onClick={() => setShowGuide(false)}>Close Manual</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
