import { useEffect } from 'react';
import { Canvas } from './components/canvas/Canvas';
import { useSessionStore } from './stores/sessionStore';
import { useLayoutStore } from './stores/layoutStore';
import { ipc } from './utils/ipc';
import './App.css';

function App() {
  const addSession = useSessionStore((state) => state.addSession);
  const updateSession = useSessionStore((state) => state.updateSession);
  const deleteSession = useSessionStore((state) => state.deleteSession);
  const updateWorktreeInfo = useSessionStore((state) => state.updateWorktreeInfo);
  const removeCardLayout = useLayoutStore((state) => state.removeCardLayout);

  useEffect(() => {
    // Load existing sessions on startup
    const loadSessions = async () => {
      try {
        const sessions = await ipc.listSessions();
        sessions.forEach((session) => {
          addSession(session);
        });
      } catch (error) {
        console.error('Failed to load sessions:', error);
      }
    };

    // Set up IPC event listeners
    const unsubscribers = [
      // Session events
      ipc.onSessionCreated((session) => {
        addSession(session);
      }),

      ipc.onSessionUpdated((session) => {
        updateSession(session.id, session);
      }),

      ipc.onSessionDeleted((id) => {
        deleteSession(id);
        removeCardLayout(id);
      }),

      ipc.onSessionStateChanged(({ sessionId, state }) => {
        updateSession(sessionId, { state });
      }),

      // Worktree events
      ipc.onWorktreeStatus(({ sessionId, info }) => {
        updateWorktreeInfo(sessionId, info);
      }),
    ];

    // Initial load
    loadSessions();

    // Cleanup
    return () => {
      unsubscribers.forEach((unsub) => unsub());
    };
  }, [addSession, updateSession, deleteSession, updateWorktreeInfo, removeCardLayout]);

  return (
    <div className="app">
      <Canvas className="w-full h-screen" />
    </div>
  );
}

export default App;