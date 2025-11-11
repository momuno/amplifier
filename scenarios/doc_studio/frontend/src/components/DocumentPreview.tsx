import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './DocumentPreview.css'

interface SourceAttribution {
  sectionId: string
  sourceFiles: string[]
}

interface DocumentPreviewProps {
  documentPath?: string
  templateName?: string
}

export function DocumentPreview({ documentPath, templateName }: DocumentPreviewProps) {
  const [content, setContent] = useState<string>('')
  const [attributions, setAttributions] = useState<SourceAttribution[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!documentPath) {
      setContent('')
      setAttributions([])
      return
    }

    const loadDocument = async () => {
      setLoading(true)
      setError(null)

      try {
        // Load the generated document
        const response = await fetch(`/api/documents/${documentPath}`)

        if (!response.ok) {
          throw new Error('Failed to load document')
        }

        const text = await response.text()
        setContent(text)

        // Load attributions if template name is provided
        if (templateName) {
          const attrResponse = await fetch(`/api/templates/${templateName}/attributions`)
          if (attrResponse.ok) {
            const attrData = await attrResponse.json()
            setAttributions(attrData)
          }
        }
      } catch (err) {
        console.error('Failed to load document:', err)
        setError(err instanceof Error ? err.message : 'Failed to load document')
      } finally {
        setLoading(false)
      }
    }

    loadDocument()
  }, [documentPath, templateName])

  if (loading) {
    return (
      <div className="document-preview">
        <div className="preview-loading">
          <p>Loading document...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="document-preview">
        <div className="preview-error">
          <p>⚠ {error}</p>
        </div>
      </div>
    )
  }

  if (!content) {
    return (
      <div className="document-preview">
        <div className="preview-empty">
          <p>No document to preview</p>
          <p className="preview-hint">Generate a document to see the preview here</p>
        </div>
      </div>
    )
  }

  return (
    <div className="document-preview">
      <div className="preview-header">
        <h3>Document Preview</h3>
        {documentPath && (
          <span className="preview-path">{documentPath}</span>
        )}
      </div>

      <div className="preview-content">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>

      {attributions.length > 0 && (
        <div className="preview-attributions">
          <h4>Source Attribution</h4>
          {attributions.map((attr) => (
            <div key={attr.sectionId} className="attribution-item">
              <h5>{attr.sectionId}</h5>
              <ul>
                {attr.sourceFiles.map((file) => (
                  <li key={file}>
                    <code>{file}</code>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
