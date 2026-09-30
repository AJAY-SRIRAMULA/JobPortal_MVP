import { useState } from 'react'; import api from '../services/api';
export default function AI() {
    const [q, setQ] = useState('');
    const [messages, setMessages] = useState([]);
    const ask = async () => {
        if (!q.trim()) return;
        const x = q; setQ(''); setMessages(m => [...m, { who: 'You', text: x }]);
        const r = await api.post('/ai/assistant/', { message: x });
        setMessages(m => [...m, { who: 'JobPortal AI', text: r.data.reply }])
    };
    return <div className="container py-4">
        <div className="page-card mx-auto" style={{ maxWidth: 850 }}>
            <h2 className="fw-bold">AI Career Assistant</h2>
            <p className="text-secondary">Rule-based career assistant with an optional AI API extension point.</p>
            <div className="chat-box mb-3">{messages.length ? messages.map((m, i) => <div className={`mb-3 ${m.who === 'You' ? 'text-end' : ''}`} key={i}><span className="badge text-bg-light">{m.who}</span><div className="mt-1">{m.text}</div></div>) : <div className="text-secondary">Ask: “What are my skill gaps?” or “How should I prepare for an interview?”</div>}</div>
            <div className="input-group">
                <input className="form-control" value={q} onChange={e => setQ(e.target.value)} onKeyDown={e => e.key === 'Enter' && ask()} placeholder="Ask about career, skills, resume or interviews" /><button className="btn btn-primary" onClick={ask}>Ask</button>
            </div>
        </div>
    </div>
}
