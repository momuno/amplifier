import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import { StorageModule } from './modules/storage';

let mainWindow: BrowserWindow | null = null;
let storage: StorageModule | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // In development, load from Vite dev server
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    // In production, load from built files
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  // Initialize storage module
  const userDataPath = app.getPath('userData');
  storage = new StorageModule(path.join(userDataPath, 'workspace.db'));
  await storage.initialize();

  // Register IPC handlers for storage operations
  ipcMain.handle('storage:getWorkspaces', async () => {
    return storage?.getWorkspaces() || [];
  });

  ipcMain.handle('storage:createWorkspace', async (_, data) => {
    return storage?.createWorkspace(data);
  });

  ipcMain.handle('storage:updateWorkspace', async (_, id, data) => {
    return storage?.updateWorkspace(id, data);
  });

  ipcMain.handle('storage:deleteWorkspace', async (_, id) => {
    return storage?.deleteWorkspace(id);
  });

  ipcMain.handle('storage:getProjects', async (_, workspaceId) => {
    return storage?.getProjects(workspaceId) || [];
  });

  ipcMain.handle('storage:createProject', async (_, data) => {
    return storage?.createProject(data);
  });

  ipcMain.handle('storage:updateProject', async (_, id, data) => {
    return storage?.updateProject(id, data);
  });

  ipcMain.handle('storage:deleteProject', async (_, id) => {
    return storage?.deleteProject(id);
  });

  ipcMain.handle('storage:getTasks', async (_, projectId) => {
    return storage?.getTasks(projectId) || [];
  });

  ipcMain.handle('storage:createTask', async (_, data) => {
    return storage?.createTask(data);
  });

  ipcMain.handle('storage:updateTask', async (_, id, data) => {
    return storage?.updateTask(id, data);
  });

  ipcMain.handle('storage:deleteTask', async (_, id) => {
    return storage?.deleteTask(id);
  });

  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    storage?.close();
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});