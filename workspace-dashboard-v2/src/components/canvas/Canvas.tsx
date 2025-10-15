import React, { useCallback, useEffect, useRef, useState } from 'react';
import GridLayout from 'react-grid-layout';
import { useSessionStore } from '../../stores/sessionStore';
import { useLayoutStore } from '../../stores/layoutStore';
import { useCanvasStore } from '../../stores/canvasStore';
import { SessionCard } from '../session/SessionCard';
import { CanvasControls } from './CanvasControls';
import { CanvasMinimap } from './CanvasMinimap';
import { cn } from '../../utils/cn';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

interface CanvasProps {
  className?: string;
}

export const Canvas: React.FC<CanvasProps> = ({ className }) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isPanning, setPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });

  const sessions = useSessionStore((state) => state.sessions);
  const selectedSessionId = useSessionStore((state) => state.selectedSessionId);
  const setSelectedSession = useSessionStore((state) => state.setSelectedSession);

  const layouts = useLayoutStore((state) => state.layouts);
  const setCardLayout = useLayoutStore((state) => state.setCardLayout);
  const findEmptySpace = useLayoutStore((state) => state.findEmptySpace);

  const {
    gridSize,
    showGrid,
    zoom,
    panX,
    panY,
    canvasWidth,
    canvasHeight,
    setPan,
  } = useCanvasStore();

  // Convert our layout format to react-grid-layout format
  const gridLayouts = Array.from(layouts.entries()).map(([sessionId, layout]) => ({
    i: sessionId,
    x: layout.position.x,
    y: layout.position.y,
    w: layout.position.w,
    h: layout.position.h,
    static: layout.isLocked,
  }));

  // Handle layout changes
  const handleLayoutChange = useCallback((newLayouts: any[]) => {
    newLayouts.forEach((layout) => {
      setCardLayout(layout.i, {
        x: layout.x,
        y: layout.y,
        w: layout.w,
        h: layout.h,
      });
    });
  }, [setCardLayout]);

  // Handle canvas panning
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 1 || (e.button === 0 && e.shiftKey)) {
      setPanning(true);
      setPanStart({ x: e.clientX - panX, y: e.clientY - panY });
      e.preventDefault();
    }
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isPanning) {
      setPan(e.clientX - panStart.x, e.clientY - panStart.y);
    }
  }, [isPanning, panStart, setPan]);

  const handleMouseUp = useCallback(() => {
    setPanning(false);
  }, []);

  useEffect(() => {
    if (isPanning) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isPanning, handleMouseMove, handleMouseUp]);

  // Handle wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      const newZoom = Math.max(0.5, Math.min(2, zoom * delta));
      useCanvasStore.setState({ zoom: newZoom });
    }
  };

  // Handle drag start/stop
  const handleDragStart = () => {
    setIsDragging(true);
  };

  const handleDragStop = () => {
    setIsDragging(false);
  };

  // Create mock sessions for demo if none exist
  useEffect(() => {
    if (sessions.size === 0) {
      // Add some demo sessions
      const demoSessions = [
        {
          id: 'session-1',
          title: 'Feature: User Authentication',
          project: 'auth-service',
          state: 'active' as const,
          lastActivity: new Date(),
          notes: 'Implementing JWT tokens and refresh logic. Need to handle edge cases for token expiry.',
          createdAt: new Date(Date.now() - 86400000),
          updatedAt: new Date(),
          tags: ['backend', 'security', 'high-priority'],
        },
        {
          id: 'session-2',
          title: 'Bug Fix: Memory Leak',
          project: 'data-processor',
          state: 'idle' as const,
          lastActivity: new Date(Date.now() - 3600000),
          notes: 'Found memory leak in event listener cleanup.',
          createdAt: new Date(Date.now() - 172800000),
          updatedAt: new Date(Date.now() - 3600000),
          tags: ['bug', 'performance'],
        },
        {
          id: 'session-3',
          title: 'Refactor: Database Layer',
          project: 'core-api',
          state: 'stale' as const,
          lastActivity: new Date(Date.now() - 86400000 * 7),
          notes: 'Moving from MongoDB to PostgreSQL',
          createdAt: new Date(Date.now() - 86400000 * 14),
          updatedAt: new Date(Date.now() - 86400000 * 7),
          tags: ['refactor', 'database'],
        },
        {
          id: 'session-4',
          title: 'Docs: API Documentation',
          project: 'documentation',
          state: 'archived' as const,
          lastActivity: new Date(Date.now() - 86400000 * 30),
          notes: 'Complete API documentation with examples',
          createdAt: new Date(Date.now() - 86400000 * 45),
          updatedAt: new Date(Date.now() - 86400000 * 30),
          tags: ['docs'],
        },
      ];

      demoSessions.forEach((session) => {
        useSessionStore.getState().addSession(session);
        const position = findEmptySpace(4, 3) || { x: 0, y: 0, w: 4, h: 3 };
        setCardLayout(session.id, position);
      });
    }
  }, [sessions.size, findEmptySpace, setCardLayout]);

  return (
    <div className={cn('relative w-full h-full overflow-hidden bg-gray-50 dark:bg-gray-950', className)}>
      {/* Controls */}
      <CanvasControls />

      {/* Canvas container */}
      <div
        ref={canvasRef}
        className="absolute inset-0"
        onMouseDown={handleMouseDown}
        onWheel={handleWheel}
        style={{
          cursor: isPanning ? 'grabbing' : isDragging ? 'move' : 'default',
        }}
      >
        {/* Grid background */}
        {showGrid && (
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundImage: `
                linear-gradient(to right, rgba(0,0,0,0.05) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(0,0,0,0.05) 1px, transparent 1px)
              `,
              backgroundSize: `${gridSize * zoom}px ${gridSize * zoom}px`,
              backgroundPosition: `${panX}px ${panY}px`,
            }}
          />
        )}

        {/* Grid layout container */}
        <div
          className="absolute"
          style={{
            transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
            transformOrigin: '0 0',
            width: canvasWidth * gridSize,
            height: canvasHeight * gridSize,
          }}
        >
          <GridLayout
            className="layout"
            layout={gridLayouts}
            cols={canvasWidth}
            rowHeight={gridSize}
            width={canvasWidth * gridSize}
            onLayoutChange={handleLayoutChange}
            onDragStart={handleDragStart}
            onDragStop={handleDragStop}
            isResizable={true}
            compactType={null}
            preventCollision={true}
            margin={[0, 0]}
            containerPadding={[0, 0]}
          >
            {Array.from(sessions.values()).map((session) => {
              const layout = layouts.get(session.id);
              if (!layout) return null;

              return (
                <div key={session.id}>
                  <SessionCard
                    session={session}
                    isSelected={selectedSessionId === session.id}
                    isDragging={isDragging}
                    onSelect={() => setSelectedSession(session.id)}
                    onFork={() => console.log('Fork:', session.id)}
                    onArchive={() => console.log('Archive:', session.id)}
                    onOpen={() => console.log('Open:', session.id)}
                    className="w-full h-full"
                  />
                </div>
              );
            })}
          </GridLayout>
        </div>
      </div>

      {/* Minimap */}
      <CanvasMinimap />
    </div>
  );
};