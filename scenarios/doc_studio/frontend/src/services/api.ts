import type { FileNode, GenerationJob, Template } from '../types'

const API_BASE = '/api'

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new ApiError(error.detail || 'Request failed', response.status)
  }
  return response.json()
}

export const api = {
  async getHealth() {
    const response = await fetch(`${API_BASE}/health`)
    return handleResponse<{ status: string; api_version: string }>(response)
  },

  async getFileTree(): Promise<FileNode> {
    const response = await fetch(`${API_BASE}/files/tree`)
    return handleResponse<FileNode>(response)
  },

  async getTemplate(name: string): Promise<Template> {
    const response = await fetch(`${API_BASE}/templates/${name}`)
    return handleResponse<Template>(response)
  },

  async addSourceToSection(
    templateName: string,
    sectionId: string,
    filePath: string,
  ): Promise<{ message: string; file_path: string }> {
    const response = await fetch(
      `${API_BASE}/templates/${templateName}/sections/${sectionId}/sources`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_path: filePath }),
      },
    )
    return handleResponse(response)
  },

  async removeSourceFromSection(
    templateName: string,
    sectionId: string,
    filePath: string,
  ): Promise<{ message: string; file_path: string }> {
    const response = await fetch(
      `${API_BASE}/templates/${templateName}/sections/${sectionId}/sources/${encodeURIComponent(filePath)}`,
      {
        method: 'DELETE',
      },
    )
    return handleResponse(response)
  },

  async generateDocument(
    templateName: string,
    outputPath: string,
  ): Promise<GenerationJob> {
    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        template_name: templateName,
        output_path: outputPath,
      }),
    })
    return handleResponse<GenerationJob>(response)
  },
}
