import { useState } from 'react'
import type { FileNode } from '../types'
import { FileType } from '../types'
import './FileTree.css'

interface FileTreeProps {
  node: FileNode
  onFileClick?: (path: string) => void
  onFileDragStart?: (path: string, event: React.DragEvent) => void
  level?: number
}

function FileTreeNode({ node, onFileClick, onFileDragStart, level = 0 }: FileTreeProps) {
  const [isExpanded, setIsExpanded] = useState(level < 2) // Expand first 2 levels by default

  const handleClick = () => {
    if (node.type === FileType.DIRECTORY) {
      setIsExpanded(!isExpanded)
    } else if (onFileClick) {
      onFileClick(node.path)
    }
  }

  const handleDragStart = (event: React.DragEvent) => {
    if (node.type === FileType.FILE && onFileDragStart) {
      onFileDragStart(node.path, event)
    }
  }

  const isDirectory = node.type === FileType.DIRECTORY
  const hasChildren = isDirectory && node.children && node.children.length > 0
  const icon = isDirectory ? (isExpanded ? '📂' : '📁') : '📄'
  const includedIndicator = node.is_included ? '✓' : ''

  return (
    <div className="file-tree-node">
      <div
        className={`node-label ${isDirectory ? 'directory' : 'file'} ${node.is_included ? 'included' : ''}`}
        onClick={handleClick}
        draggable={!isDirectory}
        onDragStart={handleDragStart}
        style={{ paddingLeft: `${level * 16}px` }}
      >
        {isDirectory && (
          <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
        )}
        <span className="node-icon">{icon}</span>
        <span className="node-name">{node.name}</span>
        {includedIndicator && (
          <span className="included-indicator" title="Included in template">
            {includedIndicator}
          </span>
        )}
      </div>

      {isDirectory && isExpanded && hasChildren && (
        <div className="node-children">
          {node.children!.map((child) => (
            <FileTreeNode
              key={child.path}
              node={child}
              onFileClick={onFileClick}
              onFileDragStart={onFileDragStart}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}

interface FileTreeComponentProps {
  tree: FileNode | null
  onFileClick?: (path: string) => void
  onFileDragStart?: (path: string, event: React.DragEvent) => void
}

export function FileTree({ tree, onFileClick, onFileDragStart }: FileTreeComponentProps) {
  if (!tree) {
    return (
      <div className="file-tree-empty">
        <p>Loading file tree...</p>
      </div>
    )
  }

  return (
    <div className="file-tree">
      <FileTreeNode
        node={tree}
        onFileClick={onFileClick}
        onFileDragStart={onFileDragStart}
      />
    </div>
  )
}
