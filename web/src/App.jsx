import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Terminal,
    Settings,
    BookOpen,
    Monitor,
    Cpu,
    Globe,
    Folder,
    Send,
    CheckCircle2,
    AlertCircle,
    Info,
    ChevronRight,
    Activity,
    Box,
    Key,
    Database,
    Link2
} from 'lucide-react'

export default function App() {
    const [activeTab, setActiveTab] = useState('dashboard')
    const [logs, setLogs] = useState([])
    const [prompt, setPrompt] = useState('')
    const [isProcessing, setIsProcessing] = useState(false)
    const [guideContent, setGuideContent] = useState('')
    const [llmConfig, setLlmConfig] = useState({
        provider: 'openai',
        api_key: '',
        model: '',
        base_url: ''
    })
    const logsEndRef = useRef(null)

    useEffect(() => {
        fetchLogs()
        fetchGuide()
        const interval = setInterval(fetchLogs, 2000)
        return () => clearInterval(interval)
    }, [])

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [logs])

    const fetchLogs = () => {
        fetch('/api/logs').then(res => res.json()).then(data => setLogs(data.logs || []))
    }

    const fetchGuide = () => {
        fetch('/api/guide').then(res => res.json()).then(data => setGuideContent(data.content))
    }

    const addLocalLog = (msg, type = 'info') => {
        const time = new Date().toLocaleTimeString()
        setLogs(prev => [...prev, `${time} | ${type.toUpperCase()} | ${msg}`])
    }

    const handleCommand = async (e) => {
        e.preventDefault()
        if (!prompt.trim() || isProcessing) return
        setIsProcessing(true)
        const cmd = prompt.trim()

        if (cmd.startsWith('!')) {
            const rawCmd = cmd.substring(1)
            addLocalLog(`Executing PowerShell: ${rawCmd}`, 'terminal')
            try {
                const res = await fetch('/api/terminal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cmd: rawCmd })
                })
                const data = await res.json()
                if (data.output) addLocalLog(data.output, 'ok')
                if (data.error) addLocalLog(data.error, 'error')
            } catch (err) {
                addLocalLog(`Terminal Error: ${err.message}`, 'error')
            }
        } else {
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

    const NavItem = ({ id, icon: Icon, label }) => (
        <div
            className={`nav-item ${activeTab === id ? 'active' : ''}`}
            onClick={() => setActiveTab(id)}
        >
            <Icon size={20} />
            <span>{label}</span>
            {activeTab === id && <motion.div layoutId="nav-glow" className="nav-glow" />}
        </div>
    )

    return (
        <div className="app-container">
            {/* Sidebar Navigation */}
            <aside className="sidebar">
                <div className="brand">
                    <div className="logo-box">
                        <Box color="#6366f1" size={28} />
                    </div>
                    <h1>OCTOPUS</h1>
                </div>
                <nav className="nav">
                    <NavItem id="dashboard" icon={Monitor} label="Hybrid Dashboard" />
                    <NavItem id="config" icon={Settings} label="API Configuration" />
                    <NavItem id="guide" icon={BookOpen} label="Instruction Guide" />
                    <div style={{ margin: '2rem 0 1rem', paddingLeft: '1rem', fontSize: '0.7rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 800 }}>Utilities</div>
                    <NavItem id="terminal" icon={Terminal} label="Raw Console" />
                </nav>
                <div className="sidebar-footer">
                    <div className="status-badge">
                        <div className="status-dot online"></div>
                        KERNEL v0.3 READY
                    </div>
                </div>
            </aside>

            {/* Main UI Area */}
            <main className="main-content">
                <header className="top-bar">
                    <div className="page-title">
                        <h2>{activeTab === 'dashboard' ? 'Automation Hub' : activeTab === 'config' ? 'Protocol Settings' : 'Knowledge Base'}</h2>
                        <p>{activeTab === 'dashboard' ? 'Manage your AI-powered system actions' : 'Diversify your LLM adapters & protocols'}</p>
                    </div>
                    <div className="top-actions">
                        <div className="activity-indicator">
                            <Activity size={16} color="var(--success)" />
                            <span>Real-time Sync Active</span>
                        </div>
                    </div>
                </header>

                <section className="view-container">
                    <AnimatePresence mode="wait">
                        {activeTab === 'dashboard' && (
                            <motion.div
                                key="dashboard"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="dashboard-view"
                            >
                                <div className="grid">
                                    <div className="glass-card">
                                        <h3>Quick Actions</h3>
                                        <p className="subtitle">Instant PowerShell Triggers</p>
                                        <div className="action-grid">
                                            <div className="action-btn" onClick={() => executeAction('system.screen_size')}>
                                                <Monitor />
                                                <span>Screen Size</span>
                                            </div>
                                            <div className="action-btn" onClick={() => executeAction('system.info')}>
                                                <Cpu />
                                                <span>Sys Info</span>
                                            </div>
                                            <div className="action-btn" onClick={() => window.open('https://github.com', '_blank')}>
                                                <Globe />
                                                <span>Browser</span>
                                            </div>
                                            <div className="action-btn" onClick={() => executeAction('file.read', { path: 'workspace/logs.txt' })}>
                                                <Folder />
                                                <span>Workspace</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="terminal-card">
                                        <div className="terminal-header">
                                            <div className="dot red"></div>
                                            <div className="dot yellow"></div>
                                            <div className="dot green"></div>
                                            <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginLeft: '1rem' }}>octopus-kernel-bash</span>
                                        </div>
                                        <div className="log-scroller">
                                            {logs.length === 0 ? (
                                                <div className="log-empty">Waiting for kernel stream...</div>
                                            ) : (
                                                logs.map((log, i) => {
                                                    const type = log.includes('| SYSTEM |') ? 'system' :
                                                        log.includes('| TERMINAL |') ? 'terminal' :
                                                            log.includes('| USER |') ? 'user' :
                                                                log.includes('| AI |') ? 'ai' :
                                                                    log.includes('| OK |') ? 'ok' :
                                                                        log.includes('| ERROR |') ? 'error' : ''
                                                    return (
                                                        <div key={i} className={`log-line ${type}`}>
                                                            <span className="log-time">{log.split('|')[0]}</span>
                                                            <span className="log-msg">{log.split('|').slice(2).join('|')}</span>
                                                        </div>
                                                    )
                                                })
                                            )}
                                            <div ref={logsEndRef} />
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {activeTab === 'config' && (
                            <motion.div
                                key="config"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="glass-card"
                                style={{ maxWidth: '800px', margin: '0 auto' }}
                            >
                                <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', marginBottom: '3rem' }}>
                                    <div style={{ width: '64px', height: '64px', borderRadius: '16px', background: 'rgba(99, 102, 241, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <Settings color="var(--accent)" size={32} />
                                    </div>
                                    <div>
                                        <h3 style={{ fontSize: '1.5rem', color: '#fff' }}>Protocol Configuration</h3>
                                        <p className="subtitle">Connect to any OpenAI, Gemini, or Custom endpoint</p>
                                    </div>
                                </div>

                                <div className="config-grid">
                                    <div className="form-group">
                                        <label><Box size={14} inline /> Model Provider</label>
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
                                        <label><Key size={14} inline /> API Key / Secret</label>
                                        <input
                                            type="password"
                                            placeholder="sk-..."
                                            value={llmConfig.api_key}
                                            onChange={(e) => setLlmConfig({ ...llmConfig, api_key: e.target.value })}
                                        />
                                    </div>
                                </div>

                                <div className="config-grid">
                                    <div className="form-group">
                                        <label><Database size={14} inline /> Model ID</label>
                                        <input
                                            type="text"
                                            placeholder="e.g. gpt-4o"
                                            value={llmConfig.model}
                                            onChange={(e) => setLlmConfig({ ...llmConfig, model: e.target.value })}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label><Link2 size={14} inline /> Custom Base URL (Optional)</label>
                                        <input
                                            type="text"
                                            placeholder="https://api.example.com/v1"
                                            value={llmConfig.base_url}
                                            onChange={(e) => setLlmConfig({ ...llmConfig, base_url: e.target.value })}
                                        />
                                    </div>
                                </div>

                                <button
                                    className="enter-btn"
                                    style={{ width: '100%', padding: '1.25rem', marginTop: '1rem' }}
                                    onClick={saveConfig}
                                >
                                    Apply Kernel Changes
                                </button>
                            </motion.div>
                        )}

                        {activeTab === 'guide' && (
                            <motion.div
                                key="guide"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="glass-card doc-viewer"
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                        <BookOpen color="var(--accent)" />
                                        <h3 style={{ margin: 0 }}>Omni-Guide</h3>
                                    </div>
                                    <button onClick={fetchGuide} className="action-btn" style={{ padding: '0.5rem 1rem', border: 'none' }}>
                                        <Activity size={12} /> Refresh
                                    </button>
                                </div>
                                <div className="guide-content-wrapper">
                                    {guideContent ? (
                                        <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'Inter', fontSize: '1rem' }}>{guideContent}</pre>
                                    ) : (
                                        <div className="loading">Retuning knowledge base...</div>
                                    )}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </section>

                {/* Floating Command Bar */}
                <footer className="command-bar">
                    <form onSubmit={handleCommand} className="input-box">
                        <span style={{ color: 'var(--accent)', fontWeight: 900 }}>{prompt.startsWith('!') ? '>' : 'AI'}</span>
                        <input
                            type="text"
                            placeholder={prompt.startsWith('!') ? 'Run PowerShell command...' : 'Tell Octopus what to do, or use ! for PowerShell'}
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            disabled={isProcessing}
                        />
                        <button type="submit" className="enter-btn" disabled={isProcessing || !prompt.trim()}>
                            {isProcessing ? 'Thinking...' : <Send size={18} />}
                        </button>
                    </form>
                </footer>
            </main>

            <style dangerouslySetInnerHTML={{
                __html: `
        .nav-glow {
          position: absolute;
          left: 0;
          width: 4px;
          height: 20px;
          background: var(--accent);
          border-radius: 0 4px 4px 0;
          box-shadow: 0 0 15px var(--accent-glow);
        }
        .logo-box {
          width: 42px;
          height: 42px;
          background: rgba(99, 102, 241, 0.1);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: inset 0 0 0 1px rgba(99, 102, 241, 0.2);
        }
        .activity-indicator {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(16, 185, 129, 0.05);
          padding: 0.5rem 1rem;
          border-radius: 99px;
          font-size: 0.75rem;
          color: var(--success);
          font-weight: 600;
          border: 1px solid rgba(16, 185, 129, 0.1);
        }
      `}} />
        </div>
    )
}
