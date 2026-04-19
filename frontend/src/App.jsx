import { useState, useRef, useEffect } from 'react';
import { SendHorizonal, Bot, User, FileText, Sparkles, GraduationCap } from 'lucide-react';
import './index.css';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef(null);

  const SUGGESTIONS = [
    "What is the last date to apply for B.Tech?",
    "What are the eligibility criteria for MBA?",
    "How much is the hostel fee?",
    "What scholarships are available?"
  ];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async (text) => {
    if (!text.trim()) return;
    
    const queryMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, queryMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text, top_k: 5 })
      });
      if (!res.ok) throw new Error("Failed to fetch");
      const data = await res.json();
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.answer, 
        sources: data.sources,
        mode: data.mode
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection failed. Ensure backend runs at localhost:8000.', isError: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center p-4 sm:p-8">
      {/* Background decorations */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary/20 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-pulse hidden md:block"></div>
      <div className="absolute top-40 right-10 w-72 h-72 bg-cta/20 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-pulse hidden md:block" style={{ animationDelay: '2s' }}></div>

      {/* Main Chat Container */}
      <main className="glass-panel w-full max-w-4xl flex flex-col h-[90vh] relative z-10 overflow-hidden flex-1">
        
        {/* Header */}
        <header className="px-6 py-5 border-b border-white/20 bg-white/40 backdrop-blur-md flex items-center gap-4 shrink-0">
          <div className="bg-primary text-white p-3 rounded-2xl shadow-lg">
            <GraduationCap size={28} />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-cta font-heading leading-tight">
              Admissions Assistant
            </h1>
            <p className="text-sm text-text/70 flex items-center gap-1 font-body">
              <Sparkles size={14} className="text-cta" /> Ask about courses, criteria & deadlines!
            </p>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scroll-smooth">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-8 animate-in fade-in duration-700">
              <div className="w-24 h-24 bg-white/60 backdrop-blur-xl rounded-full flex items-center justify-center shadow-xl border border-white/40 mb-4">
                <Bot size={48} className="text-primary" />
              </div>
              <h2 className="text-3xl font-heading text-text max-w-md">How can I help you with your college journey today?</h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl mt-8">
                {SUGGESTIONS.map(q => (
                  <button 
                    key={q} 
                    className="glass-panel py-3 px-4 text-left text-sm text-text hover:bg-white/80 hover:-translate-y-1 hover:shadow-lg transition-all duration-300 border border-white/50"
                    onClick={() => handleSend(q)}
                  >
                    <span className="text-primary mr-2 font-bold">•</span>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-4 duration-300 opacity-100`}>
              <div className={`max-w-[85%] sm:max-w-[75%] rounded-3xl p-5 shadow-sm border ${
                msg.role === 'user' 
                  ? 'bg-primary text-white border-primary/20 rounded-br-sm' 
                  : 'bg-white/70 backdrop-blur-md border-white/50 rounded-bl-sm text-text'
              }`}>
                <div className="flex items-center gap-2 mb-2 opacity-80 text-xs font-semibold uppercase tracking-wider">
                  {msg.role === 'user' ? (
                    <><User size={14}/> <span>You</span></>
                  ) : (
                    <><Bot size={14}/> <span>{msg.mode ? `Chatbot (${msg.mode})` : 'AI Guide'}</span></>
                  )}
                </div>
                
                <div 
                  className={`prose prose-sm max-w-none font-body text-[15px] leading-relaxed ${msg.role === 'user' ? 'text-white/95' : 'text-text/90'}`}
                  dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, '<br/>') }} 
                />

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-2 pt-3 border-t border-black/5">
                    {msg.sources.map(src => (
                      <span key={src} className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-black/5 text-xs text-text/80 font-medium">
                        <FileText size={12} className="text-cta"/> {src}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white/70 backdrop-blur-md border border-white/50 rounded-3xl rounded-bl-sm p-5 shadow-sm">
                 <div className="flex space-x-2 items-center h-6">
                   <div className="w-2.5 h-2.5 bg-primary/60 rounded-full animate-bounce"></div>
                   <div className="w-2.5 h-2.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                   <div className="w-2.5 h-2.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                 </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} className="h-4" />
        </div>

        {/* Input Area */}
        <div className="p-4 sm:p-6 bg-white/40 backdrop-blur-lg border-t border-white/30 shrink-0">
          <div className="relative flex items-center group">
            <input 
              className="w-full bg-white/60 border border-white/60 focus:border-primary/50 focus:bg-white/90 focus:ring-4 focus:ring-primary/10 rounded-full py-4 pl-6 pr-16 text-text placeholder-text/50 font-body outline-none transition-all duration-300 shadow-inner"
              placeholder="Type your question here..." 
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend(input)}
              disabled={isLoading}
            />
            <button 
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2.5 glass-button disabled:opacity-50 disabled:hover:bg-primary/90 disabled:cursor-not-allowed group-focus-within:bg-primary"
              onClick={() => handleSend(input)} 
              disabled={isLoading || !input.trim()}
            >
               <SendHorizonal size={20} className="ml-0.5" />
            </button>
          </div>
          <div className="text-center mt-3 text-xs text-text/50 font-body">
            AI can make mistakes. Verify important deadlines on the official portal.
          </div>
        </div>

      </main>
    </div>
  );
}
