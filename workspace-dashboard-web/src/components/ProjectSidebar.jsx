import React, { useMemo } from 'react';
import { FiChevronLeft, FiFolder, FiCircle, FiEdit2, FiPlus } from 'react-icons/fi';
import './ProjectSidebar.css';

// Project color palette - carefully chosen for dark theme
const PROJECT_COLORS = [
  '#3b82f6', // Blue
  '#10b981', // Emerald
  '#f59e0b', // Amber
  '#ef4444', // Red
  '#8b5cf6', // Purple
  '#ec4899', // Pink
  '#14b8a6', // Teal
  '#f97316', // Orange
  '#84cc16', // Lime
  '#06b6d4', // Cyan
];

function ProjectSidebar({
  sessions,
  selectedProject,
  onProjectSelect,
  isCollapsed,
  onToggle,
  onRenameProject
}) {
  // Calculate project stats and assign colors
  const projectData = useMemo(() => {
    const projectMap = new Map();

    sessions.forEach(session => {
      if (!projectMap.has(session.project_name)) {
        projectMap.set(session.project_name, {
          name: session.project_name,
          sessions: [],
          color: PROJECT_COLORS[projectMap.size % PROJECT_COLORS.length]
        });
      }
      projectMap.get(session.project_name).sessions.push(session);
    });

    // Calculate stats for each project
    return Array.from(projectMap.values()).map(project => {
      const activeSessions = project.sessions.filter(s =>
        s.state === 'WORKING' || s.state === 'NEEDS_INPUT'
      );

      return {
        ...project,
        totalSessions: project.sessions.length,
        activeSessions: activeSessions.length,
        lastActivity: Math.max(...project.sessions.map(s =>
          s.last_activity ? new Date(s.last_activity).getTime() : 0
        ))
      };
    }).sort((a, b) => b.lastActivity - a.lastActivity); // Sort by most recent activity
  }, [sessions]);

  const totalStats = useMemo(() => ({
    totalSessions: sessions.length,
    activeSessions: sessions.filter(s =>
      s.state === 'WORKING' || s.state === 'NEEDS_INPUT'
    ).length
  }), [sessions]);

  return (
    <div className={`project-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <h3 className="sidebar-title">
          {!isCollapsed && 'Projects'}
        </h3>
        <button
          className="sidebar-toggle"
          onClick={onToggle}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <FiChevronLeft className={isCollapsed ? 'rotated' : ''} />
        </button>
      </div>

      {!isCollapsed && (
        <>
          <div className="projects-list">
            {/* All Projects Option */}
            <div
              className={`project-item ${!selectedProject ? 'selected' : ''}`}
              onClick={() => onProjectSelect(null)}
            >
              <div className="project-indicator">
                <FiFolder className="project-icon" />
              </div>
              <div className="project-info">
                <div className="project-name">All Projects</div>
                <div className="project-meta">
                  {totalStats.totalSessions} sessions
                  {totalStats.activeSessions > 0 && (
                    <span className="active-count">
                      • {totalStats.activeSessions} active
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="sidebar-divider" />

            {/* Individual Projects */}
            {projectData.map(project => (
              <div
                key={project.name}
                className={`project-item ${selectedProject === project.name ? 'selected' : ''}`}
                onClick={() => onProjectSelect(project.name)}
              >
                <div className="project-indicator">
                  <FiFolder className="project-icon" />
                </div>
                <div className="project-info">
                  <div className="project-name">
                    {project.name}
                    <button
                      className="rename-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRenameProject(project.name);
                      }}
                      title="Rename project"
                    >
                      <FiEdit2 />
                    </button>
                  </div>
                  <div className="project-meta">
                    {project.totalSessions} {project.totalSessions === 1 ? 'session' : 'sessions'}
                    {project.activeSessions > 0 && (
                      <span className="active-count">
                        • {project.activeSessions} active
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default ProjectSidebar;
export { PROJECT_COLORS };