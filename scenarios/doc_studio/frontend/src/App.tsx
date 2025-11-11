import { useState, useEffect } from 'react'
import { FileTree } from './components/FileTree'
import { TemplateEditor } from './components/TemplateEditor'
import { ProgressMonitor } from './components/ProgressMonitor'
import { ChatPanel } from './components/ChatPanel'
import { DocumentPreview } from './components/DocumentPreview'
import { api, ApiError } from './services/api'
import type { FileNode, Template } from './types'
import './App.css'

function App() {
  const [health, setHealth] = useState<{ status: string; workspace?: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [fileTree, setFileTree] = useState<FileNode | null>(null)
  const [template, setTemplate] = useState<Template | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activeJobId, setActiveJobId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedDocPath, setGeneratedDocPath] = useState<string | null>(null)

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load health
        const healthData = await api.getHealth()
        setHealth(healthData)

        // Load default template
        const templateData = await api.getTemplate('default')
        setTemplate(templateData)

        // Load file tree
        const treeData = await api.getFileTree()
        setFileTree(treeData)

        setLoading(false)
      } catch (err) {
        console.error('Failed to load data:', err)
        setError(err instanceof ApiError ? err.message : 'Failed to load data')
        setLoading(false)
      }
    }

    loadData()
  }, [])

  const handleFileDragStart = (filePath: string, event: React.DragEvent) => {
    event.dataTransfer.setData('text/plain', filePath)
    event.dataTransfer.effectAllowed = 'copy'
  }

  const handleSectionDrop = async (sectionId: string, filePath: string) => {
    if (!template) return

    try {
      await api.addSourceToSection(template.name, sectionId, filePath)

      // Reload template and file tree to reflect changes
      const [updatedTemplate, updatedTree] = await Promise.all([
        api.getTemplate(template.name),
        api.getFileTree(),
      ])

      setTemplate(updatedTemplate)
      setFileTree(updatedTree)
    } catch (err) {
      console.error('Failed to add source:', err)
      setError(err instanceof ApiError ? err.message : 'Failed to add source')
    }
  }

  const handleRemoveSource = async (sectionId: string, filePath: string) => {
    if (!template) return

    try {
      await api.removeSourceFromSection(template.name, sectionId, filePath)

      // Reload template and file tree to reflect changes
      const [updatedTemplate, updatedTree] = await Promise.all([
        api.getTemplate(template.name),
        api.getFileTree(),
      ])

      setTemplate(updatedTemplate)
      setFileTree(updatedTree)
    } catch (err) {
      console.error('Failed to remove source:', err)
      setError(err instanceof ApiError ? err.message : 'Failed to remove source')
    }
  }

  const handleGenerate = async () => {
    if (!template || isGenerating) return

    try {
      setIsGenerating(true)
      setError(null)

      const outputPath = `generated_${template.name}.md`
      const job = await api.generateDocument(template.name, outputPath)
      setActiveJobId(job.id)
      setGeneratedDocPath(outputPath)
    } catch (err) {
      console.error('Failed to start generation:', err)
      setError(err instanceof ApiError ? err.message : 'Failed to start generation')
      setIsGenerating(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>doc-studio</h1>
        <p className="subtitle">AI-amplified interactive workspace for documentation</p>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            {error}
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <div className="chat-section">
          <ChatPanel />
        </div>

        <div className="layout-grid">
          <div className="panel sidebar">
            <h3>File Tree</h3>
            <FileTree
              tree={fileTree}
              onFileDragStart={handleFileDragStart}
            />
          </div>

          <div className="panel main-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3>Template Editor</h3>
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !template}
                style={{
                  padding: '8px 16px',
                  background: isGenerating ? '#555' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: isGenerating || !template ? 'not-allowed' : 'pointer',
                  fontWeight: '600'
                }}
              >
                {isGenerating ? 'Generating...' : '▶ Generate Document'}
              </button>
            </div>
            <TemplateEditor
              template={template}
              onSectionDrop={handleSectionDrop}
              onRemoveSource={handleRemoveSource}
            />
          </div>

          <div className="panel progress">
            <h3>Progress & Preview</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', height: 'calc(100% - 40px)' }}>
              <div style={{ flex: '0 0 300px', overflow: 'hidden' }}>
                <ProgressMonitor jobId={activeJobId} />
              </div>
              <div style={{ flex: '1', overflow: 'hidden', borderTop: '1px solid #444', paddingTop: '16px' }}>
                <DocumentPreview
                  documentPath={generatedDocPath || undefined}
                  templateName={template?.name}
                />
              </div>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="status-card">
            <p>Loading...</p>
          </div>
        ) : health ? (
          <div className="status-card">
            <h2>System Status</h2>
            <p>Status: <span className="status-ok">{health.status}</span></p>
          </div>
        ) : (
          <p className="status-error">Failed to connect to backend</p>
        )}
      </main>
    </div>
  )
}

export default App
