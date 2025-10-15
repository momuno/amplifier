import React, { useState, useCallback, useEffect, useMemo } from 'react';
import GridLayout from 'react-grid-layout';
import { FiPlus, FiZoomIn, FiZoomOut, FiGrid, FiRefreshCw, FiMenu } from 'react-icons/fi';
import SessionCard from './components/SessionCard';
import ProjectSidebar, { PROJECT_COLORS } from './components/ProjectSidebar';
import NewSessionModal from './components/NewSessionModal';
import { sessionAPI, layoutAPI } from './services/api';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import './App.css';

// No mock data - loaded from API

// Generate initial layout
const generateLayout = (sessions) => {
  return sessions.map((session, index) => ({
    i: session.id,
    x: (index % 4) * 4,
    y: Math.floor(index / 4) * 5,
    w: session.size === 'small' ? 3 : 4,
    h: session.size === 'small' ? 3 : 5,
    minW: 3,
    minH: 3,
    maxW: 8,
    maxH: 8
  }));
};

function App() {
  const [sessions, setSessions] = useState([]);
  const [layout, setLayout] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [zoom, setZoom] = useState(100);
  const [gridVisible, setGridVisible] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [showNewSessionModal, setShowNewSessionModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load sessions and layout from API on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [sessionsData, layoutsData] = await Promise.all([
          sessionAPI.getAll(),
          layoutAPI.get()
        ]);

        setSessions(sessionsData);

        // If we have saved layouts, use them; otherwise generate from sessions
        if (layoutsData && Object.keys(layoutsData).length > 0) {
          setLayout(Object.values(layoutsData));
        } else {
          setLayout(generateLayout(sessionsData));
        }
      } catch (err) {
        console.error('Failed to load data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Filter sessions by selected project
  const filteredSessions = useMemo(() => {
    if (!selectedProject) return sessions;
    return sessions.filter(s => s.project_name === selectedProject);
  }, [sessions, selectedProject]);

  // Filter layout to match filtered sessions
  const filteredLayout = useMemo(() => {
    if (!selectedProject) return layout;
    const filteredIds = new Set(filteredSessions.map(s => s.id));
    return layout.filter(l => filteredIds.has(l.i));
  }, [layout, filteredSessions, selectedProject]);

  // Get project color for a session
  const getProjectColor = useCallback((projectName) => {
    const uniqueProjects = [...new Set(sessions.map(s => s.project_name))].sort();
    const index = uniqueProjects.indexOf(projectName);
    return PROJECT_COLORS[index % PROJECT_COLORS.length];
  }, [sessions]);

  // Calculate stats
  const stats = {
    total: filteredSessions.length,
    active: filteredSessions.filter(s => s.state === 'WORKING').length,
    needsInput: filteredSessions.filter(s => s.state === 'NEEDS_INPUT').length
  };

  const handleLayoutChange = async (newLayout) => {
    // Only update layout if not filtering - preserve original positions
    if (!selectedProject) {
      setLayout(newLayout);
      // Save layout to backend
      try {
        const layoutsObj = newLayout.reduce((acc, item) => {
          acc[item.i] = item;
          return acc;
        }, {});
        await layoutAPI.save(layoutsObj);
      } catch (err) {
        console.error('Failed to save layout:', err);
      }
    } else {
      // When filtering, merge the new layout changes back into the main layout
      setLayout(prevLayout => {
        const layoutMap = new Map(prevLayout.map(l => [l.i, l]));
        newLayout.forEach(l => {
          layoutMap.set(l.i, l);
        });
        const updatedLayout = Array.from(layoutMap.values());

        // Save merged layout
        const layoutsObj = updatedLayout.reduce((acc, item) => {
          acc[item.i] = item;
          return acc;
        }, {});
        layoutAPI.save(layoutsObj).catch(err => console.error('Failed to save layout:', err));

        return updatedLayout;
      });
    }
  };

  const handleSessionClick = (sessionId) => {
    setSelectedSession(sessionId);
  };

  const handleSessionUpdate = async (sessionId, updates) => {
    try {
      const updatedSession = await sessionAPI.update(sessionId, updates);
      setSessions(prev =>
        prev.map(s => s.id === sessionId ? updatedSession : s)
      );
    } catch (err) {
      console.error('Failed to update session:', err);
    }
  };

  const handleSessionDelete = async (sessionId) => {
    try {
      await sessionAPI.delete(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      setLayout(prev => prev.filter(l => l.i !== sessionId));
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const handleSessionFork = async (sessionId) => {
    try {
      const forkedSession = await sessionAPI.fork(sessionId);
      setSessions(prev => [...prev, forkedSession]);

      // Add to layout next to parent
      const parentLayout = layout.find(l => l.i === sessionId);
      if (parentLayout) {
        const newLayoutItem = {
          i: forkedSession.id,
          x: parentLayout.x + parentLayout.w,
          y: parentLayout.y,
          w: parentLayout.w,
          h: parentLayout.h,
          minW: 3,
          minH: 3,
          maxW: 8,
          maxH: 8
        };
        setLayout(prev => [...prev, newLayoutItem]);
      }
    } catch (err) {
      console.error('Failed to fork session:', err);
    }
  };

  const handleAddSession = () => {
    setShowNewSessionModal(true);
  };

  const handleCreateSession = async ({ projectName, taskName, notes }) => {
    try {
      const newSession = await sessionAPI.create({
        project_name: projectName,
        name: taskName,
        notes: notes,
        branch: `feature/${taskName.toLowerCase().replace(/\s+/g, '-')}`,
        size: 'medium'
      });

      setSessions(prev => [...prev, newSession]);

      // Find empty spot in grid
      const maxY = Math.max(...layout.map(l => l.y + l.h), 0);
      const newLayoutItem = {
        i: newSession.id,
        x: 0,
        y: maxY,
        w: 4,
        h: 5,
        minW: 3,
        minH: 3,
        maxW: 8,
        maxH: 8
      };
      setLayout(prev => [...prev, newLayoutItem]);
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 10, 150));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 10, 50));
  };

  const handleRefresh = async () => {
    try {
      const sessionsData = await sessionAPI.getAll();
      setSessions(sessionsData);
      console.log('Sessions refreshed');
    } catch (err) {
      console.error('Failed to refresh sessions:', err);
    }
  };

  const handleProjectSelect = (projectName) => {
    setSelectedProject(projectName);
  };

  // Get unique project names for the modal
  const existingProjects = useMemo(() => {
    return [...new Set(sessions.map(s => s.project_name))].sort();
  }, [sessions]);

  const handleRenameProject = (oldName) => {
    const newName = prompt(`Rename project "${oldName}" to:`, oldName);
    if (newName && newName.trim() && newName !== oldName) {
      // Update all sessions with this project name
      setSessions(prev =>
        prev.map(s => s.project_name === oldName
          ? { ...s, project_name: newName.trim() }
          : s
        )
      );
      // Update selected project if it was the renamed one
      if (selectedProject === oldName) {
        setSelectedProject(newName.trim());
      }
    }
  };

  return (
    <div className="app">
      <header className={`app-header ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
          <div className="header-left">
            <div>
              <h1 className="app-title">Workspace Dashboard</h1>
              {selectedProject && (
                <div className="project-subtitle">{selectedProject}</div>
              )}
              {!selectedProject && (
                <div className="project-subtitle">All Projects</div>
              )}
            </div>
            <div className="stats-container">
            <div className="stat-badge">
              {stats.total} Sessions
            </div>
            {stats.active > 0 && (
              <div className="stat-badge active">
                {stats.active} Active
              </div>
            )}
            {stats.needsInput > 0 && (
              <div className="stat-badge warning">
                {stats.needsInput} Need Input
              </div>
            )}
          </div>
        </div>

        <div className="header-controls">
          <div className="zoom-controls">
            <button className="zoom-btn" onClick={handleZoomOut} title="Zoom out">
              <FiZoomOut />
            </button>
            <span className="zoom-level">{zoom}%</span>
            <button className="zoom-btn" onClick={handleZoomIn} title="Zoom in">
              <FiZoomIn />
            </button>
          </div>

          <button
            className={`btn-secondary ${gridVisible ? 'active' : ''}`}
            onClick={() => setGridVisible(!gridVisible)}
            title="Toggle grid"
          >
            <FiGrid />
          </button>

          <button className="btn-secondary" onClick={handleRefresh} title="Refresh">
            <FiRefreshCw />
          </button>

          <button className="btn-primary" onClick={handleAddSession}>
            <FiPlus />
            New Session
          </button>
        </div>
      </header>

      <ProjectSidebar
        sessions={sessions}
        selectedProject={selectedProject}
        onProjectSelect={handleProjectSelect}
        isCollapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        onRenameProject={handleRenameProject}
      />

      <NewSessionModal
        isOpen={showNewSessionModal}
        onClose={() => setShowNewSessionModal(false)}
        onSubmit={handleCreateSession}
        existingProjects={existingProjects}
      />

      <div className={`app-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <div
          className="canvas-container"
          style={{
            transform: `scale(${zoom / 100})`,
            transformOrigin: 'top left',
            backgroundImage: gridVisible ? undefined : 'none'
          }}
        >
          {loading ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Loading sessions...</p>
            </div>
          ) : error ? (
            <div className="empty-state">
              <div className="empty-icon">⚠️</div>
              <h2 className="empty-title">Failed to Load</h2>
              <p className="empty-subtitle">{error}</p>
              <button className="btn-primary" onClick={handleRefresh}>
                <FiRefreshCw />
                Retry
              </button>
            </div>
          ) : filteredSessions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              <FiGrid />
            </div>
            <h2 className="empty-title">No Sessions Yet</h2>
            <p className="empty-subtitle">Create your first session to get started</p>
            <button className="btn-primary" onClick={handleAddSession}>
              <FiPlus />
              Create First Session
            </button>
          </div>
        ) : (
          <GridLayout
            className="react-grid-layout"
            layout={filteredLayout}
            onLayoutChange={handleLayoutChange}
            cols={48}
            rowHeight={50}
            width={4800}
            draggableHandle=".drag-handle"
            compactType={null}
            preventCollision={true}
            autoSize={false}
            verticalCompact={false}
          >
            {filteredSessions.map(session => (
              <div key={session.id}>
                <SessionCard
                  session={session}
                  selected={selectedSession === session.id}
                  onClick={handleSessionClick}
                  onUpdate={handleSessionUpdate}
                  onDelete={handleSessionDelete}
                  onFork={handleSessionFork}
                  projectColor={getProjectColor(session.project_name)}
                />
              </div>
            ))}
          </GridLayout>
        )}
        </div>
      </div>
    </div>
  );
}

export default App;