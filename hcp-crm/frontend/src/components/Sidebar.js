import React from 'react';
import './Sidebar.css';

/**
 * Sidebar navigation component.
 * Fixed left panel with app branding and nav links.
 */
function Sidebar({ activePage, onNavigate }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'log', label: 'Log Interaction', icon: '✏️' },
  ];

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="brand-icon">💊</div>
        <div className="brand-text">
          <span className="brand-name">HCP CRM</span>
          <span className="brand-sub">AI-Powered</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <p className="nav-section-label">MAIN MENU</p>
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
            {activePage === item.id && <span className="nav-indicator" />}
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="ai-badge">
          <span className="ai-dot" />
          <span>Powered by Groq + LangGraph</span>
        </div>
        <p className="model-label">gemma2-9b-it</p>
      </div>
    </aside>
  );
}

export default Sidebar;
