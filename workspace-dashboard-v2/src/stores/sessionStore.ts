import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { SessionMetadata, WorktreeInfo } from '../types';

interface SessionStore {
  sessions: Map<string, SessionMetadata>;
  worktreeInfo: Map<string, WorktreeInfo>;
  selectedSessionId: string | null;

  // Actions
  addSession: (session: SessionMetadata) => void;
  updateSession: (id: string, updates: Partial<SessionMetadata>) => void;
  deleteSession: (id: string) => void;
  setSelectedSession: (id: string | null) => void;
  updateWorktreeInfo: (sessionId: string, info: WorktreeInfo) => void;

  // Getters
  getSession: (id: string) => SessionMetadata | undefined;
  getSessionsByState: (state: SessionMetadata['state']) => SessionMetadata[];
}

export const useSessionStore = create<SessionStore>()(
  persist(
    (set, get) => ({
      sessions: new Map(),
      worktreeInfo: new Map(),
      selectedSessionId: null,

      addSession: (session) =>
        set((state) => ({
          sessions: new Map(state.sessions).set(session.id, session),
        })),

      updateSession: (id, updates) =>
        set((state) => {
          const sessions = new Map(state.sessions);
          const existing = sessions.get(id);
          if (existing) {
            sessions.set(id, { ...existing, ...updates, updatedAt: new Date() });
          }
          return { sessions };
        }),

      deleteSession: (id) =>
        set((state) => {
          const sessions = new Map(state.sessions);
          sessions.delete(id);
          return {
            sessions,
            selectedSessionId: state.selectedSessionId === id ? null : state.selectedSessionId,
          };
        }),

      setSelectedSession: (id) =>
        set({ selectedSessionId: id }),

      updateWorktreeInfo: (sessionId, info) =>
        set((state) => ({
          worktreeInfo: new Map(state.worktreeInfo).set(sessionId, info),
        })),

      getSession: (id) => {
        return get().sessions.get(id);
      },

      getSessionsByState: (state) => {
        return Array.from(get().sessions.values()).filter((s) => s.state === state);
      },
    }),
    {
      name: 'session-store',
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
              sessions: new Map(state.state.sessions),
              worktreeInfo: new Map(state.state.worktreeInfo),
            },
          };
        },
        setItem: (name, value) => {
          const state = {
            ...value,
            state: {
              ...value.state,
              sessions: Array.from(value.state.sessions.entries()),
              worktreeInfo: Array.from(value.state.worktreeInfo.entries()),
            },
          };
          localStorage.setItem(name, JSON.stringify(state));
        },
        removeItem: (name) => localStorage.removeItem(name),
      },
    }
  )
);