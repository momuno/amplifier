import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { CanvasSettings } from '../types';

interface CanvasStore extends CanvasSettings {
  // Actions
  setZoom: (zoom: number) => void;
  setPan: (x: number, y: number) => void;
  toggleGrid: () => void;
  setCanvasSize: (width: number, height: number) => void;
  resetView: () => void;
}

const DEFAULT_SETTINGS: CanvasSettings = {
  gridSize: 50,
  showGrid: true,
  zoom: 1,
  panX: 0,
  panY: 0,
  canvasWidth: 24, // Grid units (1200px at 50px/unit)
  canvasHeight: 16, // Grid units (800px at 50px/unit)
};

export const useCanvasStore = create<CanvasStore>()(
  persist(
    (set) => ({
      ...DEFAULT_SETTINGS,

      setZoom: (zoom) =>
        set({ zoom: Math.max(0.5, Math.min(2, zoom)) }),

      setPan: (panX, panY) =>
        set({ panX, panY }),

      toggleGrid: () =>
        set((state) => ({ showGrid: !state.showGrid })),

      setCanvasSize: (canvasWidth, canvasHeight) =>
        set({ canvasWidth, canvasHeight }),

      resetView: () =>
        set({
          zoom: DEFAULT_SETTINGS.zoom,
          panX: DEFAULT_SETTINGS.panX,
          panY: DEFAULT_SETTINGS.panY,
        }),
    }),
    {
      name: 'canvas-settings',
    }
  )
);