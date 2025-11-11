// Type definitions matching backend Pydantic models

export enum FileType {
  FILE = 'file',
  DIRECTORY = 'directory',
}

export interface FileNode {
  path: string
  name: string
  type: FileType
  children?: FileNode[]
  is_included: boolean
}

export interface TemplateSection {
  id: string
  title: string
  content: string
  source_files: string[]
  order: number
}

export interface Template {
  name: string
  description: string
  sections: TemplateSection[]
  created_at: string
  updated_at: string
}

export enum JobStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export interface GenerationJob {
  id: string
  template_name: string
  status: JobStatus
  progress: number
  current_stage: string
  error?: string
  started_at?: string
  completed_at?: string
  result_path?: string
}

export interface AppState {
  current_template?: Template
  file_tree?: FileNode
  active_job?: GenerationJob
  workspace_path: string
}
