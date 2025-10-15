import React from 'react';
import {
  FiClock,
  FiGitBranch,
  FiMoreVertical,
  FiCopy,
  FiTrash2,
  FiEdit3,
  FiCheckCircle,
  FiAlertCircle,
  FiPauseCircle,
  FiPlayCircle,
  FiFileText,
  FiLoader
} from 'react-icons/fi';
import './SessionCard.css';

const SessionCard = ({ session, onUpdate, onDelete, onFork, selected, onClick, projectColor }) => {
  const getStatusIcon = (state) => {
    switch (state) {
      case 'WORKING':
        return <FiPlayCircle />;
      case 'NEEDS_INPUT':
        return <FiAlertCircle />;
      case 'REVIEW_READY':
        return <FiCheckCircle />;
      case 'COMPLETED':
        return <FiCheckCircle />;
      case 'PAUSED':
        return <FiPauseCircle />;
      case 'PLANNING':
        return <FiFileText />;
      default:
        return <FiLoader />;
    }
  };

  const getStatusClass = (state) => {
    return state.toLowerCase().replace('_', '-');
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return `${Math.floor(diff / 86400000)}d ago`;
  };

  const handleCardClick = (e) => {
    // Don't trigger if clicking on buttons
    if (e.target.closest('button')) return;
    onClick && onClick(session.id);
  };

  return (
    <div
      className={`session-card ${selected ? 'selected' : ''} state-${getStatusClass(session.state)} size-${session.size || 'medium'}`}
      onClick={handleCardClick}
    >
      <div className="drag-handle" />

      <div className="card-header">
        <div className="card-title-group">
          <div className="card-project">{session.project_name || 'Untitled Project'}</div>
          <h3 className="card-title">{session.name || 'Untitled Session'}</h3>
        </div>
        <div className="card-actions">
          <button
            className="card-action-btn"
            onClick={() => onFork && onFork(session.id)}
            title="Fork session"
          >
            <FiCopy />
          </button>
          <button
            className="card-action-btn danger"
            onClick={() => onDelete && onDelete(session.id)}
            title="Delete session"
          >
            <FiTrash2 />
          </button>
        </div>
      </div>

      <div className="card-status">
        <div className={`status-indicator ${getStatusClass(session.state)}`} />
        <span className="status-text">{session.state.replace('_', ' ')}</span>
        <span className="status-time">{formatTime(session.last_activity)}</span>
      </div>

      {session.size !== 'small' && (
        <>
          <div className="card-content">
            <div className="card-notes">
              {session.notes || ''}
            </div>
          </div>

          <div className="card-stats">
            <div className="stat-item">
              <div className="stat-value">{session.files_changed || 0}</div>
              <div className="stat-label">Files</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{session.commits || 0}</div>
              <div className="stat-label">Commits</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{session.todos_complete || 0}/{session.todos_total || 0}</div>
              <div className="stat-label">TODOs</div>
            </div>
          </div>
        </>
      )}

      <div className="card-footer">
        <div className="card-branch">
          <FiGitBranch className="card-branch-icon" />
          <span className="card-branch-name">{session.branch || 'main'}</span>
        </div>
        <div className="card-id">#{session.id.slice(0, 8)}</div>
      </div>
    </div>
  );
};

export default SessionCard;