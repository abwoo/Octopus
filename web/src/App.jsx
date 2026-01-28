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
    Link2,
    Languages
} from 'lucide-react'

// Hardcoded fallback content for the guide to ensure it ALWAYS shows up
const EMBEDDED_GUIDE = {
    zh: `# Octopus 操作指南 (v0.4)
欢迎使用 Octopus。这是一个由 AI 驱动的 Windows 自动化执行引擎。

## 1. 核心功能
- **AI 模式**: 直接输入指令，AI 会自动寻找对应的本地技能执行。
- **PS 模式**: 输入 \`!\` 开头的指令，直接透传到 PowerShell 执行。
- **多语言支持**: 顶部切换中英文界面。

## 2. 快捷指令
- \`!ls\`: 列出当前目录。
- \`!Get-Process\`: 查看系统进程。
- \`!ipconfig\`: 查看网络信息。

## 3. 模型配置
支持 OpenAI, DeepSeek, Gemini, Claude, 以及任何通用 API 端点。`,
    en: `# Octopus Operation Guide (v0.4)
Welcome to Octopus, an AI-powered automation engine for Windows.

## 1. Core Features
- **AI Mode**: Type instructions, AI will generate actions.
- **PS Mode**: Use \`!\` prefix to execute raw PowerShell commands.
- **Language**: Toggle between ZH/EN in the top bar.

## 2. Shortcuts
- \`!ls\`: List directory.
- \`!Get-Process\`: View system processes.
- \`!ipconfig\`: Check network status.

## 3. Configuration
Supports OpenAI, DeepSeek, Gemini, Claude, and any universal API endpoints.`
}

const TRANSLATIONS = {
    zh: {
        dashboard: "混合仪表盘",
        config: "API 配置",
        guide: "操作指南",
        utilities: "实用工具",
        console: "原始控制台",
        ready: "内核 v0.4 已就绪",
        commandInterface: "自动化中心",
        bridgeDesc: "管理您的 AI 驱动系统动作",
        quickActions: "快捷动作",
        triggerDesc: "即时 PowerShell 触发器",
        terminalTitle: "octopus-kernel-bash",
        waiting: "等待内核流...",
        thinking: "思考中...",
        enterBtn: "发送",
        placeholder: "告诉 Octopus 做什么，或者使用 ! 执行 PowerShell...",
        psPlaceholder: "正在运行 PowerShell 命令...",
        apply: "更新内核配置",
        provider: "模型供应商",
        apiKey: "API 密钥 / Secret",
        modelId: "模型 ID",
        baseUrl: "自定义 Base URL (可选)",
        refresh: "刷新文档",
        running: "实时同步中"
    },
    en: {
        dashboard: "Hybrid Dashboard",
        config: "API Configuration",
        guide: "Instruction Guide",
        utilities: "Utilities",
        console: "Raw Console",
        ready: "KERNEL v0.4 READY",
        commandInterface: "Automation Hub",
        bridgeDesc: "Manage your AI-powered actions",
        quickActions: "Quick Actions",
        triggerDesc: "Instant PowerShell Triggers",
        terminalTitle: "octopus-kernel-bash",
        waiting: "Waiting for stream...",
        thinking: "Thinking...",
        enterBtn: "ENTER",
        placeholder: "Tell Octopus what to do, or use ! for PowerShell",
        psPlaceholder: "Running PowerShell command...",
        apply: "Apply Changes",
        provider: "Provider",
        apiKey: "API Key / Secret",
        modelId: "Model ID",
        baseUrl: "Custom Base URL (Optional)",
        refresh: "Refresh",
        running: "Syncing Active"
    }
}

export default function App() {
    const [lang, setLang] = useState('zh')
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
    const t = TRANSLATIONS[lang]

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
        fetch('/api/guide')
            .then(res => res.json())
            .then(data => {
                if (data.content && !data.content.includes("not found")) {
                    setGuideContent(data.content)
                } else {
                    setGuideContent(EMBEDDED_GUIDE[lang])
                }
            })
            .catch(() => setGuideContent(EMBEDDED_GUIDE[lang]))
    }

    const handleCommand = async (e) => {
        e.preventDefault()
        if (!prompt.trim() || isProcessing) return
        setIsProcessing(true)
        const cmd = prompt.trim()

        if (cmd.startsWith('!')) {
            const rawCmd = cmd.substring(1)
            addLocalLog(`Executing: ${rawCmd}`, 'terminal')
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
            addLocalLog(`Instruction: ${cmd}`, 'user')
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

    const addLocalLog = (msg, type = 'info') => {
        const time = new Date().toLocaleTimeString()
        setLogs(prev => [...prev, `${time} | ${type.toUpperCase()} | ${msg}`])
    }

    const executeAction = async (type, params = {}) => {
        addLocalLog(`Action: ${type}`, 'system')
        try {
            const res = await fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, params })
            })
            const data = await res.json()
            if (data.output) addLocalLog(data.output, 'ok')
        } catch (err) {
            addLocalLog(`Failed: ${err.message}`, 'error')
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
            <aside className="sidebar">
                <div className="brand">
                    <div className="logo-box"><Box color="#6366f1" size={28} /></div>
                    <h1>OCTOPUS</h1>
                </div>
                <nav className="nav">
                    <NavItem id="dashboard" icon={Monitor} label={t.dashboard} />
                    <NavItem id="config" icon={Settings} label={t.config} />
                    <NavItem id="guide" icon={BookOpen} label={t.guide} />
                    <div className="nav-section-title">{t.utilities}</div>
                    <NavItem id="terminal" icon={Terminal} label={t.console} />
                </nav>
                <div className="sidebar-footer">
                    <div className="status-badge">
                        <div className="status-dot online"></div>
                        {t.ready}
                    </div>
                </div>
            </aside>

            <main className="main-content">
                <header className="top-bar">
                    <div className="page-title">
                        <h2>{activeTab === 'dashboard' ? t.commandInterface : activeTab === 'config' ? t.config : t.guide}</h2>
                        <p>{activeTab === 'dashboard' ? t.bridgeDesc : t.running}</p>
                    </div>
                    <div className="top-actions">
                        <button className="lang-toggle" onClick={() => {
                            const newLang = lang === 'zh' ? 'en' : 'zh'
                            setLang(newLang)
                            // Update guide content if it was showing embedded version
                            if (guideContent === EMBEDDED_GUIDE.zh || guideContent === EMBEDDED_GUIDE.en) {
                                setGuideContent(EMBEDDED_GUIDE[newLang])
                            }
                        }}>
                            <Languages size={18} />
                            <span>{lang === 'zh' ? 'EN' : '中文'}</span>
                        </button>
                        <div className="activity-indicator">
                            <Activity size={16} color="var(--success)" />
                            <span>{t.running}</span>
                        </div>
                    </div>
                </header>

                <section className="view-container">
                    <AnimatePresence mode="wait">
                        {activeTab === 'dashboard' && (
                            <motion.div key="dash" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                                <div className="grid">
                                    <div className="glass-card">
                                        <h3>{t.quickActions}</h3>
                                        <p className="subtitle">{t.triggerDesc}</p>
                                        <div className="action-grid">
                                            <div className="action-btn" onClick={() => executeAction('system.screen_size')}><Monitor /><span>Screen</span></div>
                                            <div className="action-btn" onClick={() => executeAction('system.info')}><Cpu /><span>Sys Info</span></div>
                                            <div className="action-btn" onClick={() => window.open('https://github.com', '_blank')}><Globe /><span>Browser</span></div>
                                            <div className="action-btn" onClick={() => executeAction('file.read', { path: 'workspace/logs.txt' })}><Folder /><span>Workspace</span></div>
                                        </div>
                                    </div>
                                    <div className="terminal-card">
                                        <div className="terminal-header">
                                            <div className="dot red"></div><div className="dot yellow"></div><div className="dot green"></div>
                                            <span className="term-title">{t.terminalTitle}</span>
                                        </div>
                                        <div className="log-scroller">
                                            {logs.length === 0 ? <div className="log-empty">{t.waiting}</div> :
                                                logs.map((log, i) => (
                                                    <div key={i} className={`log-line ${log.toLowerCase().includes('error') ? 'error' : log.toLowerCase().includes('ai') ? 'ai' : ''}`}>
                                                        <span className="log-msg">{log}</span>
                                                    </div>
                                                ))}
                                            <div ref={logsEndRef} />
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {activeTab === 'config' && (
                            <motion.div key="cfg" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card" style={{ maxWidth: '800px', margin: '0 auto' }}>
                                <div className="config-header">
                                    <div className="icon-badge"><Settings color="var(--accent)" size={32} /></div>
                                    <div>
                                        <h3>{t.config}</h3>
                                        <p className="subtitle">Diversify your LLM adapters (DeepSeek ready)</p>
                                    </div>
                                </div>
                                <div className="config-grid">
                                    <div className="form-group">
                                        <label>{t.provider}</label>
                                        <select value={llmConfig.provider} onChange={(e) => setLlmConfig({ ...llmConfig, provider: e.target.value })}>
                                            <option value="deepseek">DeepSeek (R1/V3)</option>
                                            <option value="openai">OpenAI (GPT-4o/o1)</option>
                                            <option value="gemini">Google Gemini (1.5)</option>
                                            <option value="anthropic">Anthropic (Claude 3.5)</option>
                                            <option value="http">Universal HTTP</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>{t.apiKey}</label>
                                        <input type="password" placeholder="Key..." value={llmConfig.api_key} onChange={(e) => setLlmConfig({ ...llmConfig, api_key: e.target.value })} />
                                    </div>
                                </div>
                                <div className="config-grid">
                                    <div className="form-group">
                                        <label>{t.modelId}</label>
                                        <input type="text" placeholder="e.g. deepseek-chat" value={llmConfig.model} onChange={(e) => setLlmConfig({ ...llmConfig, model: e.target.value })} />
                                    </div>
                                    <div className="form-group">
                                        <label>{t.baseUrl}</label>
                                        <input type="text" placeholder="https://api.deepseek.com/v1" value={llmConfig.base_url} onChange={(e) => setLlmConfig({ ...llmConfig, base_url: e.target.value })} />
                                    </div>
                                </div>
                                <button className="enter-btn" style={{ width: '100%', padding: '1.25rem' }} onClick={() => {
                                    fetch('/api/config', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(llmConfig) })
                                    addLocalLog(`Kernel update: ${llmConfig.provider}`, 'system')
                                }}>
                                    {t.apply}
                                </button>
                            </motion.div>
                        )}

                        {activeTab === 'guide' && (
                            <motion.div key="gui" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card doc-viewer">
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem' }}>
                                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}><BookOpen color="var(--accent)" /><h3>{t.guide}</h3></div>
                                    <button onClick={fetchGuide} className="action-btn" style={{ padding: '0.5rem 1rem' }}>{t.refresh}</button>
                                </div>
                                <div className="guide-content-wrapper terminal-style" style={{ padding: '1.5rem', background: '#000', borderRadius: '16px', border: '1px solid #222' }}>
                                    <pre style={{ whiteSpace: 'pre-wrap', color: '#fff', fontSize: '0.95rem' }}>{guideContent}</pre>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </section>

                <footer className="command-bar">
                    <form onSubmit={handleCommand} className="input-box">
                        <span style={{ color: 'var(--accent)', fontWeight: 900 }}>{prompt.startsWith('!') ? '>' : 'AI'}</span>
                        <input
                            type="text"
                            placeholder={prompt.startsWith('!') ? t.psPlaceholder : t.placeholder}
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            disabled={isProcessing}
                        />
                        <button type="submit" className="enter-btn" disabled={isProcessing || !prompt.trim()}>
                            {isProcessing ? t.thinking : <Send size={18} />}
                        </button>
                    </form>
                </footer>
            </main>

            <style dangerouslySetInnerHTML={{
                __html: `
        .nav-section-title { margin: 2rem 0 1rem; padding-left: 1rem; font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase; fontWeight: 800; }
        .lang-toggle { background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border); color: #fff; padding: 0.5rem 1rem; border-radius: 99px; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s; }
        .lang-toggle:hover { background: var(--accent); border-color: transparent; }
        .config-header { display: flex; gap: 2rem; align-items: center; margin-bottom: 3rem; }
        .icon-badge { width: 64px; height: 64px; border-radius: 16px; background: rgba(99, 102, 241, 0.1); display: flex; align-items: center; justify-content: center; }
        .term-title { font-size: 0.7rem; color: var(--text-dim); margin-left: 1rem; }
        .nav-glow { position: absolute; left: 0; width: 4px; height: 20px; background: var(--accent); border-radius: 0 4px 4px 0; box-shadow: 0 0 15px var(--accent-glow); }
        .logo-box { width: 42px; height: 42px; background: rgba(99, 102, 241, 0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: inset 0 0 0 1px rgba(99, 102, 241, 0.2); }
      `}} />
        </div>
    )
}
