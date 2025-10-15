import { contextBridge, ipcRenderer } from 'electron';
import type { Workspace, Project, Task } from '../shared/contracts/types';

const storageAPI = {
  // Workspace operations
  getWorkspaces: () => ipcRenderer.invoke('storage:getWorkspaces'),
  createWorkspace: (data: Omit<Workspace, 'id' | 'createdAt' | 'updatedAt'>) =>
    ipcRenderer.invoke('storage:createWorkspace', data),
  updateWorkspace: (id: string, data: Partial<Omit<Workspace, 'id' | 'createdAt' | 'updatedAt'>>) =>
    ipcRenderer.invoke('storage:updateWorkspace', id, data),
  deleteWorkspace: (id: string) =>
    ipcRenderer.invoke('storage:deleteWorkspace', id),

  // Project operations
  getProjects: (workspaceId: string) =>
    ipcRenderer.invoke('storage:getProjects', workspaceId),
  createProject: (data: Omit<Project, 'id' | 'createdAt' | 'updatedAt'>) =>
    ipcRenderer.invoke('storage:createProject', data),
  updateProject: (id: string, data: Partial<Omit<Project, 'id' | 'createdAt' | 'updatedAt'>>) =>
    ipcRenderer.invoke('storage:updateProject', id, data),
  deleteProject: (id: string) =>
    ipcRenderer.invoke('storage:deleteProject', id),

  // Task operations
  getTasks: (projectId: string) =>
    ipcRenderer.invoke('storage:getTasks', projectId),
  createTask: (data: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) =>
    ipcRenderer.invoke('storage:createTask', data),
  updateTask: (id: string, data: Partial<Omit<Task, 'id' | 'createdAt' | 'updatedAt'>>) =>
    ipcRenderer.invoke('storage:updateTask', id, data),
  deleteTask: (id: string) =>
    ipcRenderer.invoke('storage:deleteTask', id)
};

contextBridge.exposeInMainWorld('electronAPI', {
  storage: storageAPI
});

// Type declarations for TypeScript
export type ElectronAPI = {
  storage: typeof storageAPI;
};

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}