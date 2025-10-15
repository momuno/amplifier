import React from 'react';
import {
  ZoomIn,
  ZoomOut,
  Grid,
  Maximize2,
  Home,
  Plus,
  Settings
} from 'lucide-react';
import { useCanvasStore } from '../../stores/canvasStore';
import { useSessionStore } from '../../stores/sessionStore';
import { useLayoutStore } from '../../stores/layoutStore';
import { cn } from '../../utils/cn';

interface CanvasControlsProps {
  className?: string;
}

export const CanvasControls: React.FC<CanvasControlsProps> = ({ className }) => {
  const {
    zoom,
    showGrid,
    setZoom,
    toggleGrid,
    resetView,
  } = useCanvasStore();

  const addSession = useSessionStore((state) => state.addSession);
  const getNextAvailablePosition = useLayoutStore((state) => state.getNextAvailablePosition);
  const setCardLayout = useLayoutStore((state) => state.setCardLayout);

  const handleZoomIn = () => {
    setZoom(Math.min(2, zoom * 1.1));
  };

  const handleZoomOut = () => {
    setZoom(Math.max(0.5, zoom * 0.9));
  };

  const handleAddSession = () => {
    // Create a new session
    const newSession = {
      id: `session-${Date.now()}`,
      title: 'New Session',
      project: 'untitled',
      state: 'active' as const,
      lastActivity: new Date(),
      notes: '',
      createdAt: new Date(),
      updatedAt: new Date(),
      tags: [],
    };

    addSession(newSession);

    // Find position and add layout
    const position = getNextAvailablePosition();
    setCardLayout(newSession.id, position);
  };

  const zoomPercentage = Math.round(zoom * 100);

  return (
    <div className={cn('absolute top-4 left-4 z-10', className)}>
      {/* Main controls */}
      <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-800 p-2">
        <div className="flex items-center gap-1">
          {/* Add Session */}
          <button
            onClick={handleAddSession}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
            title="Add New Session"
          >
            <Plus className="w-4 h-4" />
          </button>

          <div className="w-px h-6 bg-gray-200 dark:bg-gray-700" />

          {/* Zoom controls */}
          <button
            onClick={handleZoomOut}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>

          <div className="px-2 min-w-[60px] text-center text-sm font-medium">
            {zoomPercentage}%
          </div>

          <button
            onClick={handleZoomIn}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>

          <div className="w-px h-6 bg-gray-200 dark:bg-gray-700" />

          {/* Grid toggle */}
          <button
            onClick={toggleGrid}
            className={cn(
              'p-2 rounded-md transition-colors',
              showGrid
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                : 'hover:bg-gray-100 dark:hover:bg-gray-800'
            )}
            title="Toggle Grid"
          >
            <Grid className="w-4 h-4" />
          </button>

          {/* Reset view */}
          <button
            onClick={resetView}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
            title="Reset View"
          >
            <Home className="w-4 h-4" />
          </button>

          <div className="w-px h-6 bg-gray-200 dark:bg-gray-700" />

          {/* Additional controls */}
          <button
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
            title="Fullscreen"
            onClick={() => {
              if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
              } else {
                document.exitFullscreen();
              }
            }}
          >
            <Maximize2 className="w-4 h-4" />
          </button>

          <button
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Help text */}
      <div className="mt-2 bg-white/90 dark:bg-gray-900/90 rounded-lg shadow-sm border border-gray-200 dark:border-gray-800 px-3 py-2 text-xs text-gray-600 dark:text-gray-400">
        <div className="space-y-1">
          <div>
            <span className="font-medium">Shift + Drag</span> or <span className="font-medium">Middle Click</span> to pan
          </div>
          <div>
            <span className="font-medium">Ctrl + Scroll</span> to zoom
          </div>
          <div>
            <span className="font-medium">Drag cards</span> to reposition
          </div>
        </div>
      </div>
    </div>
  );
};