import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchDashboardStats } from '../store/slices/dashboardSlice';
import './Dashboard.css';

/**
 * Dashboard page showing CRM overview statistics and recent interactions.
 */
function Dashboard({ onNavigate }) {
  const dispatch = useDispatch();
  const { stats, loading } = useSelector((state) => state.dashboard);

  useEffect(() => {
    dispatch(fetchDashboardStats());
  }, [dispatch]);

  const statCards = stats
    ? [
        {
          label: 'Total Interactions',
          value: stats.total_interactions,
          icon: '📋',
          color: 'var(--primary)',
          bg: 'rgba(79, 70, 229, 0.1)',
        },
        {
          label: 'Positive Sentiment',
          value: stats.sentiment_breakdown?.positive || 0,
          icon: '✅',
          color: 'var(--success)',
          bg: 'rgba(16, 185, 129, 0.1)',
        },
        {
          label: 'Upcoming Follow-ups',
          value: stats.upcoming_followups || 0,
          icon: '📅',
          color: 'var(--warning)',
          bg: 'rgba(245, 158, 11, 0.1)',
        },
        {
          label: 'Negative Sentiment',
          value: stats.sentiment_breakdown?.negative || 0,
          icon: '⚠️',
          color: 'var(--danger)',
          bg: 'rgba(239, 68, 68, 0.1)',
        },
      ]
    : [];

  return (
    <div className="dashboard-page">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">HCP Interaction Overview</p>
        </div>
        <button className="btn-log" onClick={() => onNavigate('log')}>
          + Log Interaction
        </button>
      </div>

      {/* Stats Cards */}
      {loading ? (
        <div className="stats-loading">Loading stats...</div>
      ) : (
        <div className="stats-grid">
          {statCards.map((card, i) => (
            <div key={i} className="stat-card" style={{ '--card-color': card.color, '--card-bg': card.bg }}>
              <div className="stat-icon">{card.icon}</div>
              <div className="stat-info">
                <p className="stat-value">{card.value}</p>
                <p className="stat-label">{card.label}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Sentiment Breakdown */}
      {stats && (
        <div className="sentiment-section">
          <h2 className="section-title">Sentiment Breakdown</h2>
          <div className="sentiment-bar-container">
            {(() => {
              const total = stats.total_interactions || 1;
              const pos = stats.sentiment_breakdown?.positive || 0;
              const neu = stats.sentiment_breakdown?.neutral || 0;
              const neg = stats.sentiment_breakdown?.negative || 0;
              return (
                <>
                  <div className="sentiment-bar">
                    <div
                      className="bar-segment positive"
                      style={{ width: `${(pos / total) * 100}%` }}
                      title={`Positive: ${pos}`}
                    />
                    <div
                      className="bar-segment neutral"
                      style={{ width: `${(neu / total) * 100}%` }}
                      title={`Neutral: ${neu}`}
                    />
                    <div
                      className="bar-segment negative"
                      style={{ width: `${(neg / total) * 100}%` }}
                      title={`Negative: ${neg}`}
                    />
                  </div>
                  <div className="sentiment-legend">
                    <span className="legend-item positive">✅ Positive ({pos})</span>
                    <span className="legend-item neutral">⚪ Neutral ({neu})</span>
                    <span className="legend-item negative">❌ Negative ({neg})</span>
                  </div>
                </>
              );
            })()}
          </div>
        </div>
      )}

      {/* Recent Interactions */}
      {stats?.recent_interactions?.length > 0 && (
        <div className="recent-section">
          <div className="section-header">
            <h2 className="section-title">Recent Interactions</h2>
            <button className="btn-view-all" onClick={() => onNavigate('log')}>
              View All →
            </button>
          </div>
          <div className="recent-list">
            {stats.recent_interactions.map((item) => (
              <div key={item.id} className="recent-card">
                <div className="recent-avatar">
                  {item.hcp_name?.charAt(0) || '?'}
                </div>
                <div className="recent-info">
                  <p className="recent-name">{item.hcp_name}</p>
                  <p className="recent-meta">
                    {item.hospital || 'Unknown Hospital'} •{' '}
                    {item.interaction_type || 'Interaction'} •{' '}
                    {item.products || 'No products'}
                  </p>
                  {item.summary && (
                    <p className="recent-summary">{item.summary.slice(0, 120)}...</p>
                  )}
                </div>
                <div className="recent-right">
                  <span
                    className={`badge badge-${item.sentiment || 'neutral'}`}
                  >
                    {item.sentiment || 'neutral'}
                  </span>
                  <p className="recent-date">
                    {item.created_at
                      ? new Date(item.created_at).toLocaleDateString('en-IN', {
                          day: '2-digit',
                          month: 'short',
                        })
                      : '—'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && stats?.total_interactions === 0 && (
        <div className="empty-dashboard">
          <p className="empty-icon">💊</p>
          <h3>No interactions yet</h3>
          <p>Start logging your HCP interactions to see insights here.</p>
          <button className="btn-log" onClick={() => onNavigate('log')}>
            Log Your First Interaction
          </button>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
