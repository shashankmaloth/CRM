import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendChatMessage, addUserMessage, clearChat } from '../store/slices/chatSlice';
import { fetchAllInteractions } from '../store/slices/interactionsSlice';
import './ChatInterface.css';

/**
 * Conversational chat interface for AI-powered interaction logging.
 * Renders messages, handles input, and displays extracted data cards.
 */
function ChatInterface() {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((state) => state.chat);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput('');
    dispatch(addUserMessage(text));

    try {
      await dispatch(sendChatMessage(text)).unwrap();
      // Refresh interactions list after successful log
      dispatch(fetchAllInteractions());
    } catch (err) {
      // Error handled in slice
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    dispatch(clearChat());
  };

  const examplePrompts = [
    "Met Dr. Rao at Apollo Hospital. Discussed Januvia for diabetes. Very interested.",
    "Called Dr. Mehta about Rosuvastatin. He wants more clinical data.",
    "Show me history for Dr. Priya Rao",
    "Suggest next actions for Dr. Sunita Sharma",
  ];

  return (
    <div className="chat-container">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-header-info">
          <div className="ai-avatar">🤖</div>
          <div>
            <p className="chat-title">AI CRM Assistant</p>
            <p className="chat-subtitle">Powered by LangGraph + Groq gemma2-9b-it</p>
          </div>
        </div>
        <button className="btn-clear" onClick={handleClear} title="Clear chat">
          🗑️ Clear
        </button>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-bubble typing">
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Example prompts */}
      {messages.length <= 1 && (
        <div className="example-prompts">
          <p className="prompts-label">Try these examples:</p>
          <div className="prompts-grid">
            {examplePrompts.map((prompt, i) => (
              <button
                key={i}
                className="prompt-chip"
                onClick={() => setInput(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="chat-input-area">
        <textarea
          ref={inputRef}
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe your HCP interaction... (Press Enter to send)"
          rows="2"
          disabled={loading}
        />
        <button
          className="btn-send"
          onClick={handleSend}
          disabled={!input.trim() || loading}
        >
          {loading ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
}

/**
 * Individual message bubble component.
 * Renders user and assistant messages with extracted data cards.
 */
function MessageBubble({ message }) {
  const [showSteps, setShowSteps] = useState(false);
  const isAssistant = message.role === 'assistant';

  // Format markdown-like content
  const formatContent = (content) => {
    return content
      .split('\n')
      .map((line, i) => {
        // Bold text
        line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Italic
        line = line.replace(/\*(.*?)\*/g, '<em>$1</em>');
        return <p key={i} dangerouslySetInnerHTML={{ __html: line || '&nbsp;' }} />;
      });
  };

  return (
    <div className={`message ${message.role} ${message.isError ? 'error' : ''}`}>
      {isAssistant && <div className="message-avatar">🤖</div>}

      <div className="message-content">
        <div className="message-bubble">
          {formatContent(message.content)}
        </div>

        {/* Extracted Data Card */}
        {message.extractedData && (
          <div className="extracted-card">
            <p className="card-title">📋 Extracted Data</p>
            <div className="card-grid">
              {Object.entries(message.extractedData)
                .filter(([k, v]) => v && !['id', 'created_at', 'updated_at'].includes(k))
                .map(([key, value]) => (
                  <div key={key} className="card-item">
                    <span className="card-key">{key.replace(/_/g, ' ')}</span>
                    <span className="card-value">{String(value)}</span>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Suggested Actions */}
        {message.suggestedActions && message.suggestedActions.length > 0 && (
          <div className="suggestions-card">
            <p className="card-title">💡 Suggested Actions</p>
            <ul className="suggestions-list">
              {message.suggestedActions.map((action, i) => (
                <li key={i}>{action}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Agent Steps (collapsible) */}
        {message.agentSteps && message.agentSteps.length > 0 && (
          <div className="agent-steps">
            <button
              className="steps-toggle"
              onClick={() => setShowSteps(!showSteps)}
            >
              {showSteps ? '▼' : '▶'} Agent Steps ({message.agentSteps.length})
            </button>
            {showSteps && (
              <div className="steps-list">
                {message.agentSteps.map((step, i) => (
                  <div key={i} className="step-item">
                    <span className="step-num">{i + 1}</span>
                    <span className="step-node">{step.node}</span>
                    {step.intent && <span className="step-detail">→ {step.intent}</span>}
                    {step.result && <span className="step-result">{step.result}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <span className="message-time">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>

      {!isAssistant && <div className="message-avatar user-avatar">👤</div>}
    </div>
  );
}

export default ChatInterface;
