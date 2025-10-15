import React, { useState, useEffect } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { FiActivity, FiCheckCircle, FiAlertCircle, FiClock, FiX, FiEdit2 } from 'react-icons/fi';
import './SessionCard.css';

const SessionCard = ({ session, onUpdate, onDelete, onSelect, isSelected }) => {
  const [editingProject, setEditingProject] = useState(false);
  const [editingTask, setEditingTask] = useState(false);
  const [projectName, setProjectName] = useState(session.project_name);
  const [taskName, setTaskName] = useState(session.task_name);

  // Update local state when session prop changes
  useEffect(() => {
    setProjectName(session.project_name);
    setTaskName(session.task_name);
  }, [session.project_name, session.task_name]);

  const handleProjectSave = () => {
    if (projectName.trim() && projectName !== session.project_name) {
      onUpdate(session.id, { project_name: projectName.trim() });
    } else {
      setProjectName(session.project_name);
    }
    setEditingProject(false);
  };

  const handleTaskSave = () => {
    if (taskName.trim() && taskName !== session.task_name) {
      onUpdate(session.id, { task_name: taskName.trim() });
    } else {
      setTaskName(session.task_name);
    }
    setEditingTask(false);
  };

  const getStatusIcon = () => {
    switch (session.status) {
      case 'active':
        return <FiActivity className="status-icon active" />;
      case 'completed':
        return <FiCheckCircle className="status-icon completed" />;
      case 'error':
        return <FiAlertCircle className="status-icon error" />;
      default:
        return <FiClock className="status-icon idle" />;
    }
  };

  const getStatusColor = () => {
    switch (session.status) {
      case 'active':
        return '#3b82f6'; // Blue
      case 'completed':
        return '#10b981'; // Green
      case 'error':
        return '#ef4444'; // Red
      default:
        return '#6b7280'; // Gray
    }
  };

  const timeSinceInteraction = session.last_interaction
    ? formatDistanceToNow(new Date(session.last_interaction), { addSuffix: true })
    : 'Never';

  const handleCardClick = (e) => {
    // Don't trigger selection when clicking on drag handle
    if (e.target.closest('.drag-handle')) {
      return;
    }
    if (onSelect) {
      onSelect();
    }
  };

  return (
    <div
      className={`session-card ${isSelected ? 'selected' : ''}`}
      style={{ borderColor: getStatusColor() }}
      onClick={handleCardClick}
    >
      <div className="session-header">
        <div className="drag-handle" title="Drag to reorder">⋮⋮</div>
        <div className="session-title">
          {editingProject ? (
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              onBlur={handleProjectSave}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleProjectSave();
                if (e.key === 'Escape') {
                  setProjectName(session.project_name);
                  setEditingProject(false);
                }
              }}
              onClick={(e) => e.stopPropagation()}
              autoFocus
              className="edit-input project-edit"
            />
          ) : (
            <h3 onClick={(e) => {
              e.stopPropagation();
              setEditingProject(true);
            }}>
              {session.project_name}
              <FiEdit2 className="edit-icon" />
            </h3>
          )}
          {getStatusIcon()}
        </div>
        <button
          className="close-button"
          onClick={(e) => {
            e.stopPropagation();
            onDelete(session.id);
          }}
        >
          <FiX />
        </button>
      </div>

      <div className="session-task">
        <span className="label">Task:</span>
        {editingTask ? (
          <input
            type="text"
            value={taskName}
            onChange={(e) => setTaskName(e.target.value)}
            onBlur={handleTaskSave}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleTaskSave();
              if (e.key === 'Escape') {
                setTaskName(session.task_name);
                setEditingTask(false);
              }
            }}
            onClick={(e) => e.stopPropagation()}
            autoFocus
            className="edit-input task-edit"
          />
        ) : (
          <span className="value editable" onClick={(e) => {
            e.stopPropagation();
            setEditingTask(true);
          }}>
            {session.task_name}
            <FiEdit2 className="edit-icon" />
          </span>
        )}
      </div>

      {session.last_accomplishment && (
        <div className="session-accomplishment">
          <span className="label">Last Accomplishment:</span>
          <span className="value">{session.last_accomplishment}</span>
        </div>
      )}

      {session.next_action && (
        <div className="session-action">
          <span className="label">Next Action:</span>
          <span className="value">{session.next_action}</span>
        </div>
      )}

      <div className="session-footer">
        <div className="session-time">
          <FiClock size={14} />
          <span>{timeSinceInteraction}</span>
        </div>
        <div className="session-outputs">
          {session.outputs && session.outputs.length > 0 && (
            <span>{session.outputs.length} outputs</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default SessionCard;