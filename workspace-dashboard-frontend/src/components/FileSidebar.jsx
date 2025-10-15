import React, { useState, useEffect } from 'react';
import './FileSidebar.css';

const FileSidebar = ({ selectedSession }) => {
  const [fileTree, setFileTree] = useState(null);
  const [expandedFolders, setExpandedFolders] = useState(new Set());
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [contentLoading, setContentLoading] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Fetch file tree when session changes
  useEffect(() => {
    if (selectedSession?.id) {
      fetchFileTree(selectedSession.id);
      // Set up auto-refresh every 5 seconds
      const interval = setInterval(() => {
        fetchFileTree(selectedSession.id);
      }, 5000);
      return () => clearInterval(interval);
    } else {
      setFileTree(null);
      setSelectedFile(null);
      setFileContent(null);
    }
  }, [selectedSession?.id, refreshKey]);

  const fetchFileTree = async (sessionId) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/sessions/${sessionId}/files`);
      if (response.ok) {
        const data = await response.json();
        setFileTree(data.tree);
      }
    } catch (error) {
      console.error('Error fetching file tree:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFileContent = async (sessionId, filePath) => {
    setContentLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/sessions/${sessionId}/files/${encodeURIComponent(filePath)}`
      );
      if (response.ok) {
        const data = await response.json();
        setFileContent(data);
      }
    } catch (error) {
      console.error('Error fetching file content:', error);
      setFileContent({ error: 'Failed to load file' });
    } finally {
      setContentLoading(false);
    }
  };

  const toggleFolder = (path) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  };

  const handleFileClick = (file) => {
    if (file.type === 'file') {
      setSelectedFile(file);
      fetchFileContent(selectedSession.id, file.path);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getFileIcon = (fileName, isDirectory) => {
    if (isDirectory) return '📁';

    const extension = fileName.split('.').pop().toLowerCase();
    const iconMap = {
      'js': '📜',
      'jsx': '⚛️',
      'ts': '📘',
      'tsx': '⚛️',
      'py': '🐍',
      'json': '📋',
      'md': '📝',
      'html': '🌐',
      'css': '🎨',
      'txt': '📄',
      'log': '📊',
      'yml': '⚙️',
      'yaml': '⚙️',
      'sh': '💻',
      'env': '🔐'
    };

    return iconMap[extension] || '📄';
  };

  const renderTree = (node, level = 0) => {
    if (!node) return null;

    const isExpanded = expandedFolders.has(node.path);
    const isDirectory = node.type === 'directory';
    const isSelected = selectedFile?.path === node.path;

    return (
      <div key={node.path || node.name} className="tree-node">
        <div
          className={`tree-item ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${level * 20}px` }}
          onClick={() => {
            if (isDirectory) {
              toggleFolder(node.path);
            } else {
              handleFileClick(node);
            }
          }}
        >
          <span className="tree-icon">
            {isDirectory && (isExpanded ? '▼' : '▶')}
          </span>
          <span className="file-icon">
            {getFileIcon(node.name, isDirectory)}
          </span>
          <span className="file-name">{node.name}</span>
          {node.size !== undefined && (
            <span className="file-size">{formatFileSize(node.size)}</span>
          )}
        </div>
        {isDirectory && isExpanded && node.children && (
          <div className="tree-children">
            {node.children.map(child => renderTree(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const renderFileContent = () => {
    if (!fileContent) return null;

    if (fileContent.error) {
      return (
        <div className="content-error">
          {fileContent.error}
        </div>
      );
    }

    if (fileContent.type === 'binary') {
      return (
        <div className="content-binary">
          Binary file ({formatFileSize(fileContent.size)})
        </div>
      );
    }

    if (fileContent.content) {
      const extension = selectedFile?.name.split('.').pop().toLowerCase();
      const isCode = ['js', 'jsx', 'ts', 'tsx', 'py', 'json', 'html', 'css', 'sh', 'yml', 'yaml'].includes(extension);

      return (
        <pre className={`file-content ${isCode ? 'code' : ''}`}>
          <code>{fileContent.content}</code>
        </pre>
      );
    }

    return null;
  };

  return (
    <div className="file-sidebar">
      <div className="sidebar-header">
        <h3>📂 Files</h3>
        <button
          className="refresh-btn"
          onClick={() => setRefreshKey(k => k + 1)}
          title="Refresh files"
        >
          🔄
        </button>
      </div>

      {selectedSession && (
        <div className="project-label">
          <strong>Project:</strong> {selectedSession.project_name}
        </div>
      )}

      <div className="sidebar-content">
        {!selectedSession ? (
          <div className="no-session">
            Select a session to view files
          </div>
        ) : loading ? (
          <div className="loading">Loading files...</div>
        ) : fileTree ? (
          <div className="file-tree">
            {renderTree(fileTree)}
          </div>
        ) : (
          <div className="no-files">
            No files yet in this session
          </div>
        )}
      </div>

      {selectedFile && (
        <div className="file-preview">
          <div className="preview-header">
            <span className="preview-title">
              {getFileIcon(selectedFile.name, false)} {selectedFile.name}
            </span>
            <button
              className="close-preview"
              onClick={() => {
                setSelectedFile(null);
                setFileContent(null);
              }}
            >
              ✖
            </button>
          </div>
          <div className="preview-content">
            {contentLoading ? (
              <div className="loading">Loading content...</div>
            ) : (
              renderFileContent()
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileSidebar;