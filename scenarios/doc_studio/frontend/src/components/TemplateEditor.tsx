import { useState } from 'react'
import type { Template, TemplateSection } from '../types'
import './TemplateEditor.css'

interface TemplateEditorProps {
  template: Template | null
  onSectionDrop?: (sectionId: string, filePath: string) => void
  onRemoveSource?: (sectionId: string, filePath: string) => void
}

export function TemplateEditor({ template, onSectionDrop, onRemoveSource }: TemplateEditorProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())

  if (!template) {
    return (
      <div className="template-editor-empty">
        <p>Loading template...</p>
      </div>
    )
  }

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId)
    } else {
      newExpanded.add(sectionId)
    }
    setExpandedSections(newExpanded)
  }

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'copy'
  }

  const handleDrop = (sectionId: string) => (event: React.DragEvent) => {
    event.preventDefault()
    const filePath = event.dataTransfer.getData('text/plain')
    if (filePath && onSectionDrop) {
      onSectionDrop(sectionId, filePath)
    }
  }

  const handleRemoveSource = (sectionId: string, filePath: string) => {
    if (onRemoveSource) {
      onRemoveSource(sectionId, filePath)
    }
  }

  const sortedSections = [...template.sections].sort((a, b) => a.order - b.order)

  return (
    <div className="template-editor">
      <div className="template-header">
        <h2>{template.name}</h2>
        {template.description && <p className="template-description">{template.description}</p>}
      </div>

      <div className="sections-list">
        {sortedSections.map((section) => {
          const isExpanded = expandedSections.has(section.id)
          const sourceCount = section.source_files.length

          return (
            <div key={section.id} className="section-card">
              <div className="section-header" onClick={() => toggleSection(section.id)}>
                <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                <h3 className="section-title">{section.title}</h3>
                <span className="source-count" title={`${sourceCount} source files`}>
                  {sourceCount} {sourceCount === 1 ? 'file' : 'files'}
                </span>
              </div>

              {isExpanded && (
                <div className="section-content">
                  <div className="section-preview">
                    <pre>{section.content}</pre>
                  </div>

                  <div
                    className="source-files-area"
                    onDragOver={handleDragOver}
                    onDrop={handleDrop(section.id)}
                  >
                    <h4>Source Files:</h4>
                    {sourceCount === 0 ? (
                      <p className="drop-hint">Drag files here from the file tree</p>
                    ) : (
                      <ul className="source-files-list">
                        {section.source_files.map((filePath) => (
                          <li key={filePath} className="source-file-item">
                            <span className="file-path">{filePath}</span>
                            <button
                              className="remove-button"
                              onClick={() => handleRemoveSource(section.id, filePath)}
                              title="Remove from section"
                            >
                              ✕
                            </button>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
