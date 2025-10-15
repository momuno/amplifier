import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { SessionCardLayout, CardPosition } from '../types';

interface LayoutStore {
  layouts: Map<string, SessionCardLayout>;
  nextPosition: CardPosition; // For placing new cards

  // Actions
  setCardLayout: (sessionId: string, position: CardPosition) => void;
  removeCardLayout: (sessionId: string) => void;
  lockCard: (sessionId: string, locked: boolean) => void;
  setCardZIndex: (sessionId: string, zIndex: number) => void;
  getNextAvailablePosition: () => CardPosition;

  // Grid helpers
  findEmptySpace: (width: number, height: number) => CardPosition | null;
  isSpaceOccupied: (position: CardPosition) => boolean;
}

const DEFAULT_CARD_SIZE = { w: 4, h: 3 }; // 200px x 150px at 50px grid
const GRID_COLUMNS = 24; // 1200px canvas width at 50px grid
const GRID_ROWS = 16; // 800px canvas height at 50px grid

export const useLayoutStore = create<LayoutStore>()(
  persist(
    (set, get) => ({
      layouts: new Map(),
      nextPosition: { x: 0, y: 0, ...DEFAULT_CARD_SIZE },

      setCardLayout: (sessionId, position) =>
        set((state) => {
          const layouts = new Map(state.layouts);
          const existing = layouts.get(sessionId);
          layouts.set(sessionId, {
            sessionId,
            position,
            isLocked: existing?.isLocked || false,
            zIndex: existing?.zIndex || 0,
          });
          return { layouts };
        }),

      removeCardLayout: (sessionId) =>
        set((state) => {
          const layouts = new Map(state.layouts);
          layouts.delete(sessionId);
          return { layouts };
        }),

      lockCard: (sessionId, locked) =>
        set((state) => {
          const layouts = new Map(state.layouts);
          const existing = layouts.get(sessionId);
          if (existing) {
            layouts.set(sessionId, { ...existing, isLocked: locked });
          }
          return { layouts };
        }),

      setCardZIndex: (sessionId, zIndex) =>
        set((state) => {
          const layouts = new Map(state.layouts);
          const existing = layouts.get(sessionId);
          if (existing) {
            layouts.set(sessionId, { ...existing, zIndex });
          }
          return { layouts };
        }),

      getNextAvailablePosition: () => {
        const state = get();
        const position = state.findEmptySpace(DEFAULT_CARD_SIZE.w, DEFAULT_CARD_SIZE.h);
        return position || { x: 0, y: 0, ...DEFAULT_CARD_SIZE };
      },

      findEmptySpace: (width, height) => {
        const layouts = Array.from(get().layouts.values());

        // Try to find an empty space in the grid
        for (let y = 0; y <= GRID_ROWS - height; y++) {
          for (let x = 0; x <= GRID_COLUMNS - width; x++) {
            const testPosition: CardPosition = { x, y, w: width, h: height };

            // Check if this position overlaps with any existing cards
            const overlaps = layouts.some((layout) => {
              const pos = layout.position;
              return !(
                testPosition.x + testPosition.w <= pos.x ||
                testPosition.x >= pos.x + pos.w ||
                testPosition.y + testPosition.h <= pos.y ||
                testPosition.y >= pos.y + pos.h
              );
            });

            if (!overlaps) {
              return testPosition;
            }
          }
        }

        // If no space found, place at bottom
        const maxY = Math.max(0, ...layouts.map(l => l.position.y + l.position.h));
        return { x: 0, y: maxY, w: width, h: height };
      },

      isSpaceOccupied: (position) => {
        const layouts = Array.from(get().layouts.values());
        return layouts.some((layout) => {
          const pos = layout.position;
          return !(
            position.x + position.w <= pos.x ||
            position.x >= pos.x + pos.w ||
            position.y + position.h <= pos.y ||
            position.y >= pos.y + pos.h
          );
        });
      },
    }),
    {
      name: 'layout-store',
      // Custom serialization for Map
      storage: {
        getItem: (name) => {
          const str = localStorage.getItem(name);
          if (!str) return null;
          const state = JSON.parse(str);
          return {
            ...state,
            state: {
              ...state.state,
              layouts: new Map(state.state.layouts),
            },
          };
        },
        setItem: (name, value) => {
          const state = {
            ...value,
            state: {
              ...value.state,
              layouts: Array.from(value.state.layouts.entries()),
            },
          };
          localStorage.setItem(name, JSON.stringify(state));
        },
        removeItem: (name) => localStorage.removeItem(name),
      },
    }
  )
);