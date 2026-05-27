import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAllInteractions, deleteInteraction } from '../store/slices/interactionsSlice';
import { toast } from 'react-toastify';
import './InteractionTable.css';

/**
 * Table component displaying all logged HCP interactions.
 * Supports search, sentiment filtering, and delete.
 */
function InteractionTable() {
  const dispatch = useDispatch();
  const { list, loading } = useSelector((state) => state.interactions);
  const [search, setSearch] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('all');

  useEffect(() => {
    dispatch(fetchAllInteractions());
  }, [dispatch]);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this interaction?')) return;
    try {
      await dispatch(deleteInteraction(id)).unwrap();
      toast.success('Interaction deleted');
    } catch (err) {
      toast.error('Failed to delete');
    }
  };

  // Filter interactions
  const filtered = list.filter((item) => {
    const matchSearch =
      !search ||
      item.hcp_name?.toLowerCase().includes(search.toLowerCase()) ||
      item.hospital?.toLowerCase().includes(search.toLowerCase()) ||
      item.products?.toLowerCase().includes(search.toLowerCase());

    const matchSentiment =
      sentimentFilter === 'all' || item.sentiment === sentimentFilter;

    return matchSearch && matchSentiment;
  });

  const sentimentBadge = (sentiment) => {
    const map = {
      positive: { label: '✅ Positive', cls: 'badge-positive' },
      neutral: { label: '⚪ Neutral', cls: 'badge-neutral' },
      negative: { label: '❌ Negative', cls: 'badge-negative' },
    };
    const s = map[sentiment] || map.neutral;
    return <span className={`badge ${s.cls}`}>{s.label}</span>;
  };

  const typeBadge = (type) => {
    const map = {
      Visit: '🏥',
      Call: '📞',
      Meeting: '🤝',
    };
    return `${map[type] || '📋'} ${type || 'N/A'}`;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div className="table-container">
      {/* Filters */}
      <div className="table-filters">
        <input
          type="text"
          className="search-input"
          placeholder="🔍 Search by HCP, hospital, or product..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="filter-buttons">
          {['all', 'positive', 'neutral', 'negative'].map((s) => (
            <button
              key={s}
              className={`filter-btn ${sentimentFilter === s ? 'active' : ''}`}
              onClick={() => setSentimentFilter(s)}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="table-loading">
          <div className="spinner" />
          <p>Loading interactions...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="table-empty">
          <p>📭 No interactions found</p>
          <p className="empty-sub">Log your first interaction using the form or chat above.</p>
        </div>
      ) : (
        <div className="table-scroll">
          <table className="interactions-table">
            <thead>
              <tr>
                <th>#</th>
                <th>HCP Name</th>
                <th>Specialty</th>
                <th>Hospital</th>
                <th>Type</th>
                <th>Date</th>
                <th>Products</th>
                <th>Sentiment</th>
                <th>Follow-up</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.id}>
                  <td className="id-cell">{item.id}</td>
                  <td className="hcp-cell">
                    <strong>{item.hcp_name}</strong>
                  </td>
                  <td>{item.specialty || '—'}</td>
                  <td>{item.hospital || '—'}</td>
                  <td>{typeBadge(item.interaction_type)}</td>
                  <td>{formatDate(item.datetime || item.created_at)}</td>
                  <td className="products-cell">
                    {item.products ? (
                      <span title={item.products}>
                        {item.products.length > 30
                          ? item.products.slice(0, 30) + '...'
                          : item.products}
                      </span>
                    ) : '—'}
                  </td>
                  <td>{sentimentBadge(item.sentiment)}</td>
                  <td>{formatDate(item.follow_up_date)}</td>
                  <td>
                    <button
                      className="btn-delete"
                      onClick={() => handleDelete(item.id)}
                      title="Delete interaction"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="table-count">
        Showing {filtered.length} of {list.length} interactions
      </p>
    </div>
  );
}

export default InteractionTable;
