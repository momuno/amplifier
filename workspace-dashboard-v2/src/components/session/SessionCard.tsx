import React, { memo } from 'react';
import { SessionMetadata, SessionState, WorktreeInfo } from '../../types';
import {
  Clock,
  GitBranch,
  Archive,
  GitFork,
  Activity,
  MoreVertical,
  Folder,
  FileText,
  PlayCircle
} from 'lucide-react';
import { cn } from '../../utils/cn';

interface SessionCardProps {
  session: SessionMetadata;
  worktree?: WorktreeInfo;
  isSelected?: boolean;
  isDragging?: boolean;
  onSelect?: () => void;
  onFork?: () => void;
  onArchive?: () => void;
  onOpen?: () => void;
  className?: string;
}

const STATE_COLORS: Record<SessionState, string> = {
  active: 'bg-green-500/10 border-green-500 shadow-green-500/20',
  idle: 'bg-yellow-500/10 border-yellow-500 shadow-yellow-500/20',
  stale: 'bg-orange-500/10 border-orange-500 shadow-orange-500/20',
  archived: 'bg-gray-500/10 border-gray-500 shadow-gray-500/20',
  forked: 'bg-blue-500/10 border-blue-500 shadow-blue-500/20',
};

const STATE_ICONS: Record<SessionState, React.ReactNode> = {
  active: <Activity className="w-4 h-4 text-green-500" />,
  idle: <Clock className="w-4 h-4 text-yellow-500" />,
  stale: <Clock className="w-4 h-4 text-orange-500" />,
  archived: <Archive className="w-4 h-4 text-gray-500" />,
  forked: <GitFork className="w-4 h-4 text-blue-500" />,
};

export const SessionCard = memo(({
  session,
  worktree,
  isSelected = false,
  isDragging = false,
  onSelect,
  onFork,
  onArchive,
  onOpen,
  className,
}: SessionCardProps) => {
  const formatDate = (date: Date) => {
    const d = new Date(date);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'just now';
  };

  const handleClick = (_e: React.MouseEvent) => {
    if (!isDragging && onSelect) {
      onSelect();
    }
  };

  return (
    <div
      className={cn(
        'relative rounded-lg border-2 p-3 bg-white dark:bg-gray-900',
        'transition-all duration-200 cursor-pointer select-none',
        'hover:shadow-lg',
        STATE_COLORS[session.state],
        isSelected && 'ring-2 ring-blue-500 ring-offset-2',
        isDragging && 'opacity-50 rotate-3 scale-105',
        className
      )}
      onClick={handleClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          {STATE_ICONS[session.state]}
          <h3 className="font-semibold text-sm truncate dark:text-white">
            {session.title}
          </h3>
        </div>
        <button
          className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
          onClick={(e) => e.stopPropagation()}
        >
          <MoreVertical className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {/* Project Info */}
      <div className="flex items-center gap-2 mb-2 text-xs text-gray-600 dark:text-gray-400">
        <Folder className="w-3 h-3" />
        <span className="truncate">{session.project}</span>
      </div>

      {/* Branch Info */}
      {worktree && (
        <div className="flex items-center gap-2 mb-2 text-xs text-gray-600 dark:text-gray-400">
          <GitBranch className="w-3 h-3" />
          <span className="truncate">{worktree.branch}</span>
          {worktree.isDirty && (
            <span className="text-yellow-600 dark:text-yellow-500">●</span>
          )}
        </div>
      )}

      {/* Notes Preview */}
      {session.notes && (
        <div className="mb-2">
          <div className="flex items-center gap-1 mb-1">
            <FileText className="w-3 h-3 text-gray-500" />
            <span className="text-xs text-gray-500">Notes</span>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
            {session.notes}
          </p>
        </div>
      )}

      {/* Tags */}
      {session.tags && session.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {session.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-800 rounded-full"
            >
              {tag}
            </span>
          ))}
          {session.tags.length > 3 && (
            <span className="text-xs text-gray-500">+{session.tags.length - 3}</span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
        <span className="text-xs text-gray-500">
          {formatDate(session.lastActivity)}
        </span>
        <div className="flex gap-1">
          {onOpen && (
            <button
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
              onClick={(e) => {
                e.stopPropagation();
                onOpen();
              }}
              title="Open"
            >
              <PlayCircle className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>
          )}
          {onFork && session.state !== 'archived' && (
            <button
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
              onClick={(e) => {
                e.stopPropagation();
                onFork();
              }}
              title="Fork"
            >
              <GitFork className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>
          )}
          {onArchive && session.state !== 'archived' && (
            <button
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
              onClick={(e) => {
                e.stopPropagation();
                onArchive();
              }}
              title="Archive"
            >
              <Archive className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>
          )}
        </div>
      </div>

      {/* Parent indicator for forked sessions */}
      {session.parentId && (
        <div className="absolute -top-2 -right-2 bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full">
          Forked
        </div>
      )}
    </div>
  );
});

SessionCard.displayName = 'SessionCard';