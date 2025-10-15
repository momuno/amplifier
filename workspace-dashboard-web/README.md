# Workspace Dashboard V2 - Web Application

A clean, professional React-based dashboard for managing multiple Claude Code sessions with a visual, grid-based interface.

## Features

- **Grid-based Canvas**: Azure Portal-style snap-to-grid layout
- **Draggable & Resizable Cards**: Full control over session placement
- **Visual State Indicators**: Color-coded session states (Working, Needs Input, Review Ready, etc.)
- **Professional Dark Theme**: Clean, modern interface
- **Session Management**: Fork, delete, and organize sessions
- **Zoom Controls**: Scale the canvas for better overview
- **Real-time Statistics**: Track active sessions and those needing attention

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **react-grid-layout** - Powerful grid system with drag & drop
- **react-icons** - Feather icons for clean UI
- **Plain CSS** - Simple, maintainable styling

## Getting Started

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
workspace-dashboard-web/
├── src/
│   ├── components/
│   │   ├── SessionCard.jsx      # Individual session card component
│   │   └── SessionCard.css      # Card-specific styles
│   ├── App.jsx                  # Main application component
│   ├── App.css                  # Application styles
│   ├── index.css                # Global styles
│   └── main.jsx                 # Application entry point
├── public/                      # Static assets
├── package.json                 # Dependencies and scripts
└── vite.config.js              # Vite configuration
```

## Session States

- 🔵 **WORKING** - Active progress, no action needed
- 🔴 **NEEDS_INPUT** - Claude is blocked, requires response
- 🟡 **REVIEW_READY** - Work complete, awaiting review
- ⏸️ **PAUSED** - Idle but incomplete
- ✅ **COMPLETED** - Finished and reviewed
- 📋 **PLANNING** - Initial setup phase

## Keyboard Shortcuts (Planned)

- `Ctrl/Cmd + N` - New session
- `Arrow Keys` - Navigate between cards
- `Delete` - Remove selected session
- `Ctrl/Cmd + D` - Duplicate (fork) session

## Mock Data

The application currently uses mock data for demonstration. In production, it will connect to the backend API at `http://localhost:8000/api`.

## Customization

### Grid Settings

Modify grid behavior in `App.jsx`:

```javascript
<GridLayout
  cols={12}              // Number of columns
  rowHeight={50}         // Height of each grid unit
  width={1200}          // Total grid width
  compactType={null}    // Disable auto-compacting
/>
```

### Card Sizes

Three preset sizes available:
- **Small**: 2x2 grid units (compact view)
- **Medium**: 3x3 grid units (standard view)
- **Large**: 4x4 grid units (detailed view)

## Future Enhancements

- Backend API integration
- Real-time updates via WebSocket
- Session persistence
- Advanced filtering and search
- Keyboard navigation
- Export/import layouts
- Multi-monitor support

## Development

This is a simple, clean implementation focused on:
- **Professional appearance** from day one
- **Simple, maintainable code**
- **Functional grid system** with manual control
- **Visual polish** for a production-ready feel

The design philosophy emphasizes simplicity and functionality over complexity, making it easy to understand and extend.