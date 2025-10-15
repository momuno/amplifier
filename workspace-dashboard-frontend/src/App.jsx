import React, { useState, useEffect, useCallback } from 'react';
import WorkspaceGrid from './components/WorkspaceGrid';
import FileSidebar from './components/FileSidebar';
import { sessionAPI, dashboardAPI, SSEClient } from './services/api';
import { FiPlus, FiLayout, FiSidebar } from 'react-icons/fi';
import './App.css';

function App() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sseClient, setSseClient] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [selectedSession, setSelectedSession] = useState(null);
  const [existingProjects, setExistingProjects] = useState([]);
  const [projectInputMode, setProjectInputMode] = useState('select'); // 'select' or 'new'
  const [newSessionData, setNewSessionData] = useState({
    projectName: '',
    taskName: '',
  });

  // Load sessions on mount
  useEffect(() => {
    loadSessions();
    setupSSE();

    return () => {
      if (sseClient) {
        sseClient.disconnect();
      }
    };
  }, []);

  // Load all sessions
  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await sessionAPI.list();
      setSessions(data);
      setError(null);
    } catch (err) {
      console.error('Error loading sessions:', err);
      setError('Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  // Load existing projects
  const loadProjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/projects');
      if (response.ok) {
        const projects = await response.json();
        setExistingProjects(projects);
        // If there are existing projects, default to select mode
        if (projects.length > 0) {
          setProjectInputMode('select');
          setNewSessionData(prev => ({ ...prev, projectName: projects[0] }));
        } else {
          setProjectInputMode('new');
        }
      }
    } catch (err) {
      console.error('Error loading projects:', err);
    }
  };

  // Setup SSE connection
  const setupSSE = () => {
    const client = new SSEClient(
      (eventType, data) => {
        handleSSEMessage(eventType, data);
      },
      (error) => {
        console.error('SSE Error:', error);
      }
    );
    client.connect();
    setSseClient(client);
  };

  // Handle SSE messages
  const handleSSEMessage = (eventType, data) => {
    switch (eventType) {
      case 'session.status.changed':
        updateSessionInList(data.data.session_id, {
          status: data.data.new_status,
          last_accomplishment: data.data.last_accomplishment,
          next_action: data.data.next_action,
        });
        break;

      case 'session.task.completed':
        updateSessionInList(data.data.session_id, {
          last_accomplishment: data.data.result,
        });
        break;

      case 'session.outputs.created':
        updateSessionInList(data.data.session_id, {
          outputs: data.data.outputs,
        });
        break;

      case 'session.error':
        updateSessionInList(data.data.session_id, {
          status: 'error',
        });
        break;

      default:
        break;
    }
  };

  // Update session in the list
  const updateSessionInList = (sessionId, updates) => {
    setSessions((prevSessions) =>
      prevSessions.map((session) =>
        session.id === sessionId
          ? { ...session, ...updates, last_interaction: new Date().toISOString() }
          : session
      )
    );
  };

  // Create new session
  const createSession = async () => {
    if (!newSessionData.projectName || !newSessionData.taskName) {
      alert('Please fill in all fields');
      return;
    }

    try {
      const newSession = await sessionAPI.create(
        newSessionData.projectName,
        newSessionData.taskName
      );
      setSessions((prev) => [...prev, newSession]);
      setShowCreateForm(false);
      setNewSessionData({ projectName: '', taskName: '' });
    } catch (err) {
      console.error('Error creating session:', err);
      alert('Failed to create session');
    }
  };

  // Update session
  const handleUpdateSession = async (sessionId, updates) => {
    try {
      const updatedSession = await sessionAPI.update(sessionId, updates);
      // If project name changed, reload all sessions to get updated project names
      if (updates.project_name) {
        await loadSessions();
      } else {
        updateSessionInList(sessionId, updatedSession);
      }
    } catch (err) {
      console.error('Error updating session:', err);
    }
  };

  // Delete session
  const handleDeleteSession = async (sessionId) => {
    if (!confirm('Are you sure you want to delete this session?')) {
      return;
    }

    try {
      await sessionAPI.delete(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    } catch (err) {
      console.error('Error deleting session:', err);
    }
  };

  // Save layout changes
  const handleLayoutChange = async (layouts) => {
    try {
      await dashboardAPI.saveLayouts(layouts);
    } catch (err) {
      console.error('Error saving layout:', err);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1>Claude Code Workspace Dashboard</h1>
          <span className="session-count">{sessions.length} sessions</span>
        </div>
        <div className="header-actions">
          <button
            className="header-button"
            onClick={() => setShowSidebar(!showSidebar)}
            title="Toggle Sidebar"
          >
            <FiSidebar />
          </button>
          <button
            className="header-button primary"
            onClick={() => {
              loadProjects();
              setShowCreateForm(true);
            }}
            title="New Session"
          >
            <FiPlus /> New Session
          </button>
        </div>
      </header>

      {showCreateForm && (
        <div className="modal-overlay" onClick={() => setShowCreateForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Task</h2>
            <div className="form-group">
              <label>Project</label>
              {existingProjects.length > 0 ? (
                <div>
                  <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <input
                        type="radio"
                        checked={projectInputMode === 'select'}
                        onChange={() => {
                          setProjectInputMode('select');
                          setNewSessionData({ ...newSessionData, projectName: existingProjects[0] });
                        }}
                      />
                      Existing Project
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <input
                        type="radio"
                        checked={projectInputMode === 'new'}
                        onChange={() => {
                          setProjectInputMode('new');
                          setNewSessionData({ ...newSessionData, projectName: '' });
                        }}
                      />
                      New Project
                    </label>
                  </div>
                  {projectInputMode === 'select' ? (
                    <select
                      value={newSessionData.projectName}
                      onChange={(e) =>
                        setNewSessionData({ ...newSessionData, projectName: e.target.value })
                      }
                      style={{
                        width: '100%',
                        background: '#0f0f0f',
                        border: '1px solid #374151',
                        borderRadius: '6px',
                        padding: '10px 12px',
                        color: '#e5e7eb',
                        fontSize: '14px'
                      }}
                    >
                      {existingProjects.map(project => (
                        <option key={project} value={project}>{project}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="text"
                      value={newSessionData.projectName}
                      onChange={(e) =>
                        setNewSessionData({ ...newSessionData, projectName: e.target.value })
                      }
                      placeholder="e.g., My New Project"
                    />
                  )}
                </div>
              ) : (
                <input
                  type="text"
                  value={newSessionData.projectName}
                  onChange={(e) =>
                    setNewSessionData({ ...newSessionData, projectName: e.target.value })
                  }
                  placeholder="e.g., My Project"
                />
              )}
            </div>
            <div className="form-group">
              <label>Task Description</label>
              <input
                type="text"
                value={newSessionData.taskName}
                onChange={(e) =>
                  setNewSessionData({ ...newSessionData, taskName: e.target.value })
                }
                placeholder="e.g., Implement feature X"
              />
            </div>
            <div className="modal-actions">
              <button className="button secondary" onClick={() => setShowCreateForm(false)}>
                Cancel
              </button>
              <button className="button primary" onClick={createSession}>
                Create Session
              </button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading sessions...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <p>{error}</p>
          <button onClick={loadSessions}>Retry</button>
        </div>
      ) : sessions.length === 0 ? (
        <div className="empty-state">
          <FiLayout size={48} />
          <h2>No Active Sessions</h2>
          <p>Create a new session to get started</p>
          <button
            className="button primary"
            onClick={() => setShowCreateForm(true)}
          >
            <FiPlus /> Create First Session
          </button>
        </div>
      ) : (
        <div className="main-content">
          <WorkspaceGrid
            sessions={sessions}
            onUpdateSession={handleUpdateSession}
            onDeleteSession={handleDeleteSession}
            onLayoutChange={handleLayoutChange}
            onSessionSelect={setSelectedSession}
            selectedSessionId={selectedSession?.id}
          />
          {showSidebar && (
            <FileSidebar selectedSession={selectedSession} />
          )}
        </div>
      )}
    </div>
  );
}

export default App;