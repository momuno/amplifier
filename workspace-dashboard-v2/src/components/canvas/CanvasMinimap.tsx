import React, { useRef, useEffect } from 'react';
import { useSessionStore } from '../../stores/sessionStore';
import { useLayoutStore } from '../../stores/layoutStore';
import { useCanvasStore } from '../../stores/canvasStore';
import { cn } from '../../utils/cn';
import { SessionState } from '../../types';

interface CanvasMinimapProps {
  className?: string;
}

const STATE_COLORS: Record<SessionState, string> = {
  active: '#10b981',
  idle: '#eab308',
  stale: '#f97316',
  archived: '#6b7280',
  forked: '#3b82f6',
};

export const CanvasMinimap: React.FC<CanvasMinimapProps> = ({ className }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const sessions = useSessionStore((state) => state.sessions);
  const layouts = useLayoutStore((state) => state.layouts);
  const {
    gridSize,
    zoom,
    panX,
    panY,
    canvasWidth,
    canvasHeight,
    setPan,
  } = useCanvasStore();

  const minimapWidth = 200;
  const minimapHeight = 150;
  const scale = Math.min(
    minimapWidth / (canvasWidth * gridSize),
    minimapHeight / (canvasHeight * gridSize)
  );

  // Calculate viewport rectangle
  const viewportWidth = (window.innerWidth / zoom) * scale;
  const viewportHeight = (window.innerHeight / zoom) * scale;
  const viewportX = (-panX / zoom) * scale;
  const viewportY = (-panY / zoom) * scale;

  // Draw minimap
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, minimapWidth, minimapHeight);

    // Draw canvas background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvasWidth * gridSize * scale, canvasHeight * gridSize * scale);

    // Draw session cards
    layouts.forEach((layout, sessionId) => {
      const session = sessions.get(sessionId);
      if (!session) return;

      const x = layout.position.x * gridSize * scale;
      const y = layout.position.y * gridSize * scale;
      const w = layout.position.w * gridSize * scale;
      const h = layout.position.h * gridSize * scale;

      // Card background
      ctx.fillStyle = STATE_COLORS[session.state];
      ctx.globalAlpha = 0.3;
      ctx.fillRect(x, y, w, h);

      // Card border
      ctx.globalAlpha = 1;
      ctx.strokeStyle = STATE_COLORS[session.state];
      ctx.lineWidth = 1;
      ctx.strokeRect(x, y, w, h);
    });

    // Draw viewport rectangle
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.strokeRect(viewportX, viewportY, viewportWidth, viewportHeight);

    // Viewport overlay
    ctx.fillStyle = 'rgba(59, 130, 246, 0.1)';
    ctx.fillRect(viewportX, viewportY, viewportWidth, viewportHeight);
  }, [
    sessions,
    layouts,
    scale,
    viewportX,
    viewportY,
    viewportWidth,
    viewportHeight,
    canvasWidth,
    canvasHeight,
    gridSize,
  ]);

  // Handle click to navigate
  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Convert minimap coordinates to canvas coordinates
    const canvasX = (x / scale) * zoom;
    const canvasY = (y / scale) * zoom;

    // Center the viewport on the clicked position
    const newPanX = -canvasX + window.innerWidth / 2;
    const newPanY = -canvasY + window.innerHeight / 2;

    setPan(newPanX, newPanY);
  };

  return (
    <div
      className={cn(
        'absolute bottom-4 right-4 z-10',
        'bg-white dark:bg-gray-900 rounded-lg shadow-lg',
        'border border-gray-200 dark:border-gray-800 p-2',
        className
      )}
    >
      <div className="mb-1 text-xs font-medium text-gray-600 dark:text-gray-400">
        Minimap
      </div>
      <canvas
        ref={canvasRef}
        width={minimapWidth}
        height={minimapHeight}
        onClick={handleClick}
        className="cursor-pointer rounded border border-gray-200 dark:border-gray-700"
        style={{ imageRendering: 'pixelated' }}
      />
      <div className="mt-1 text-xs text-gray-500 dark:text-gray-500">
        Click to navigate
      </div>
    </div>
  );
};