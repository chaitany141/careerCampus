import { useState, useRef, useEffect } from 'react'

function App() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: "Hello! I'm CareerCompass, your AI career advisor. How can I help you with your professional journey today?" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'ai', content: data.reply }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: "I'm sorry, I'm having trouble connecting to the server right now. Please ensure the backend is running and the API key is set." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Simple Markdown parser for basic formatting like bold and lists
  const renderMessageContent = (content) => {
    const paragraphs = content.split('\n').filter(p => p.trim());
    return paragraphs.map((p, idx) => {
      let formattedP = p.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      if (p.startsWith('* ') || p.startsWith('- ')) {
        return <li key={idx} dangerouslySetInnerHTML={{__html: formattedP.substring(2)}} />
      }
      return <p key={idx} dangerouslySetInnerHTML={{__html: formattedP}} />
    });
  }

  return (
    <div className="chat-container">
      <header className="chat-header">
        <div className="header-icon">
          🧭
        </div>
        <div className="header-title">
          <h1>CareerCompass</h1>
          <p>Your AI Career Advisor</p>
        </div>
      </header>
      
      <main className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="bubble">
              {renderMessageContent(msg.content)}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message ai">
            <div className="typing">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      <form onSubmit={handleSubmit} className="chat-input-area">
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask for career advice, resume tips, or interview prep..."
            className="chat-input"
            disabled={isLoading}
          />
          <button type="submit" className="send-btn" disabled={isLoading || !input.trim()}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </form>
    </div>
  )
}

export default App
