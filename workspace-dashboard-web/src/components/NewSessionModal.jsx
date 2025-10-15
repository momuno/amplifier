import React, { useState, useEffect } from 'react';
import { FiX } from 'react-icons/fi';
import './NewSessionModal.css';

function NewSessionModal({ isOpen, onClose, onSubmit, existingProjects }) {
  const [projectName, setProjectName] = useState('');
  const [isNewProject, setIsNewProject] = useState(false);
  const [taskName, setTaskName] = useState('');
  const [notes, setNotes] = useState('');

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setProjectName('');
      setIsNewProject(false);
      setTaskName('');
      setNotes('');
    }
  }, [isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (projectName.trim() && taskName.trim()) {
      onSubmit({
        projectName: projectName.trim(),
        taskName: taskName.trim(),
        notes: notes.trim()
      });
      onClose();
    }
  };

  const handleProjectChange = (value) => {
    if (value === '__new__') {
      setIsNewProject(true);
      setProjectName('');
    } else {
      setIsNewProject(false);
      setProjectName(value);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">New Session</h2>
          <button className="modal-close" onClick={onClose}>
            <FiX />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="project" className="form-label">Project</label>
            {!isNewProject ? (
              <select
                id="project"
                className="form-select"
                value={projectName}
                onChange={(e) => handleProjectChange(e.target.value)}
                required
              >
                <option value="">Select a project...</option>
                {existingProjects.map(project => (
                  <option key={project} value={project}>{project}</option>
                ))}
                <option value="__new__">+ Create New Project</option>
              </select>
            ) : (
              <div className="form-input-group">
                <input
                  type="text"
                  id="project"
                  className="form-input"
                  placeholder="Enter new project name"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  autoFocus
                  required
                />
                <button
                  type="button"
                  className="btn-link"
                  onClick={() => setIsNewProject(false)}
                >
                  Choose existing
                </button>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="taskName" className="form-label">Task Name</label>
            <input
              type="text"
              id="taskName"
              className="form-input"
              placeholder="Enter task name"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="notes" className="form-label">Notes (optional)</label>
            <textarea
              id="notes"
              className="form-textarea"
              placeholder="Add any initial notes about this task..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
            />
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Session
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default NewSessionModal;
