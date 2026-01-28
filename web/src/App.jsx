import { useState, useEffect } from 'react'

export default function App() {
    const [status, setStatus] = useState('offline')
    const [logs, setLogs] = useState([])

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

    const execute = async (type, params = {}) => {
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

    return (
        <div className="dashboard">
            <header className="header">
                <h1>OCTOPUS</h1>
                <div className="status-badge">
                    <div className={`status-dot ${status === 'ready' ? 'online' : 'offline'}`}></div>
                    {status.toUpperCase()}
                </div>
            </header>

            <main className="grid">
                <section className="card">
                    <h2>Quick Actions</h2>
                    <div className="controls">
                        <button className="btn" onClick={() => execute('mouse.move', { x: 500, y: 500 })}>
                            <span className="btn-icon">🎯</span>
                            Center Mouse
                        </button>
                        <button className="btn" onClick={() => execute('mouse.click', { button: 'left' })}>
                            <span className="btn-icon">🖱️</span>
                            Left Click
                        </button>
                        <button className="btn" onClick={() => execute('system.screen_size')}>
                            <span className="btn-icon">📏</span>
                            Screen Info
                        </button>
                        <button className="btn" onClick={() => execute('system.info')}>
                            <span className="btn-icon">⚙️</span>
                            System Info
                        </button>
                    </div>
                </section>

                <section className="card">
                    <h2>Execution Logs</h2>
                    <div className="log-container">
                        {logs.map((log, i) => (
                            <div key={i} className="log-entry">
                                {log}
                            </div>
                        ))}
                    </div>
                </section>
            </main>
        </div>
    )
}
