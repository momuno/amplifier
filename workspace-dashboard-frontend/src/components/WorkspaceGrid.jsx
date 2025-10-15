import React, { useState, useEffect, useCallback } from 'react';
import { Responsive, WidthProvider } from 'react-grid-layout';
import SessionCard from './SessionCard';
import './WorkspaceGrid.css';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

const WorkspaceGrid = ({ sessions, onUpdateSession, onDeleteSession, onLayoutChange, onSessionSelect, selectedSessionId }) => {
  const [layouts, setLayouts] = useState({});
  const [mounted, setMounted] = useState(false);
  const [layoutsLoaded, setLayoutsLoaded] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Load saved layouts from backend
    loadSavedLayouts();
  }, []);

  // Load saved layouts from backend
  const loadSavedLayouts = async () => {
    try {
      const response = await fetch('http://localhost:8000/dashboard/layouts');
      const data = await response.json();
      if (data.layouts && Object.keys(data.layouts).length > 0) {
        setLayouts(data.layouts);
      }
      setLayoutsLoaded(true);
    } catch (error) {
      console.error('Failed to load layouts:', error);
      setLayoutsLoaded(true);
    }
  };

  // Generate layout for a new session
  const generateLayoutForSession = useCallback((sessionId, index) => {
    // Find a position that doesn't overlap with existing items
    const findOpenPosition = () => {
      let x = (index * 3) % 12;
      let y = Math.floor(index / 4) * 3;

      // Simple algorithm to find next open spot
      const maxY = 100; // Reasonable max rows to check
      for (let row = 0; row < maxY; row++) {
        for (let col = 0; col <= 12 - 3; col++) { // 3 is default width
          // Check if this position would overlap with any existing layout
          let overlaps = false;
          if (layouts.lg) {
            overlaps = layouts.lg.some(item => {
              return !(col + 3 <= item.x || col >= item.x + item.w ||
                       row * 3 + 3 <= item.y || row * 3 >= item.y + item.h);
            });
          }
          if (!overlaps) {
            return { x: col, y: row * 3 };
          }
        }
      }
      // Fallback to calculated position
      return { x, y };
    };

    const pos = findOpenPosition();
    return {
      i: sessionId,
      x: pos.x,
      y: pos.y,
      w: 3,
      h: 3,
      minW: 2,
      minH: 2,
      static: false,
    };
  }, [layouts]);

  // Merge layouts - preserve existing and add new ones
  const getMergedLayouts = useCallback(() => {
    const result = { lg: [], md: [], sm: [], xs: [] };

    sessions.forEach((session, index) => {
      // Check if layout exists for this session
      const existingLg = layouts.lg?.find(l => l.i === session.id);
      const existingMd = layouts.md?.find(l => l.i === session.id);
      const existingSm = layouts.sm?.find(l => l.i === session.id);
      const existingXs = layouts.xs?.find(l => l.i === session.id);

      // Use existing layout or generate new one
      result.lg.push(existingLg || generateLayoutForSession(session.id, index));
      result.md.push(existingMd || generateLayoutForSession(session.id, index));
      result.sm.push(existingSm || {
        i: session.id,
        x: (index * 6) % 12,
        y: Math.floor(index / 2) * 3,
        w: 6,
        h: 3,
        minW: 2,
        minH: 2,
      });
      result.xs.push(existingXs || {
        i: session.id,
        x: 0,
        y: index * 3,
        w: 12,
        h: 3,
        minW: 2,
        minH: 2,
      });
    });

    return result;
  }, [sessions, layouts, generateLayoutForSession]);

  // Handle layout changes - preserve exact positions
  const handleLayoutChange = useCallback((currentLayout, allLayouts) => {
    // Only update layouts, don't let grid compact them
    const preservedLayouts = {};

    Object.keys(allLayouts).forEach(breakpoint => {
      preservedLayouts[breakpoint] = allLayouts[breakpoint].map(item => ({
        ...item,
        moved: false,
        static: false
      }));
    });

    setLayouts(preservedLayouts);
    if (onLayoutChange) {
      onLayoutChange(preservedLayouts);
    }
  }, [onLayoutChange]);

  if (!mounted || !layoutsLoaded) {
    return <div className="loading-container">Loading layouts...</div>;
  }

  const currentLayouts = getMergedLayouts();

  return (
    <ResponsiveGridLayout
      className="workspace-grid"
      layouts={currentLayouts}
      breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480 }}
      cols={{ lg: 12, md: 12, sm: 6, xs: 1 }}
      rowHeight={60}
      onLayoutChange={handleLayoutChange}
      isDraggable={true}
      isResizable={true}
      draggableHandle=".drag-handle"
      margin={[16, 16]}
      containerPadding={[16, 16]}
      useCSSTransforms={true}
      transformScale={1}
      preventCollision={false}
      compactType={null}
      isBounded={false}
      autoSize={false}
    >
      {sessions.map((session) => (
        <div key={session.id} className="grid-item-wrapper">
          <SessionCard
            session={session}
            onUpdate={onUpdateSession}
            onDelete={onDeleteSession}
            onSelect={() => {
              console.log('Session clicked:', session.id);
              if (onSessionSelect) {
                onSessionSelect(session);
              }
            }}
            isSelected={selectedSessionId === session.id}
          />
        </div>
      ))}
    </ResponsiveGridLayout>
  );
};

export default WorkspaceGrid;