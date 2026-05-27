import React, { useState } from 'react';
import InteractionForm from '../components/InteractionForm';
import ChatInterface from '../components/ChatInterface';
import InteractionTable from '../components/InteractionTable';
import './LogInteraction.css';

/**
 * Log Interaction page with two tabs:
 * 1. Structured Form
 * 2. Conversational Chat (AI-powered)
 * Also displays the interaction table below.
 */
function LogInteraction() {
  const [activeTab, setActiveTab] = useState('form');

  return (
    <div className="log-page">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Log Interaction</h1>
          <p className="page-subtitle">Record HCP interactions via form or AI chat</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-container">
        <div className="tabs-header">
          <button
            className={`tab-btn ${activeTab === 'form' ? 'active' : ''}`}
            onClick={() => setActiveTab('form')}
          >
            📝 Structured Form
          </button>
          <button
            className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            💬 AI Chat
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'form' ? (
            <div className="tab-panel">
              <InteractionForm />
            </div>
          ) : (
            <div className="tab-panel">
              <ChatInterface />
            </div>
          )}
        </div>
      </div>

      {/* Interaction Table */}
      <div className="table-section">
        <h2 className="section-title">All Interactions</h2>
        <InteractionTable />
      </div>
    </div>
  );
}

export default LogInteraction;
