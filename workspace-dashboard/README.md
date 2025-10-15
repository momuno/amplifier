# Claude Code Workspace Dashboard

A powerful visual workspace for managing multiple Claude Code sessions simultaneously across multiple monitors.

## 🎯 Features

- **Multi-Monitor Support**: Spans across multiple displays for maximum visibility
- **Draggable Grid Layout**: Azure Portal-style tiles that snap to grid positions
- **Real-time Status Updates**: Live session monitoring via Server-Sent Events (SSE)
- **Visual Status Indicators**: Color-coded cards (Active, Idle, Completed, Needs Attention)
- **Session Management**: Track project, last action, next task, and interaction time
- **File Browser**: Explore outputs from each session
- **Meta-Session Overview**: Compare and coordinate multiple sessions
- **Multi-Repo Support**: Handle concurrent sessions across different repositories

## 🏗️ Architecture

The application follows a modular "bricks and studs" philosophy with two main components:

### Backend (FastAPI + Python)
- **Session Orchestrator**: Manages Claude Code sessions
- **SSE Manager**: Handles real-time event broadcasting
- **File Watcher**: Monitors session output directories
- **Claude Integration**: SDK wrapper for Claude Code interaction
- **State Persistence**: JSON-based storage for simplicity

### Frontend (React + Vite)
- **Workspace Grid**: Draggable/resizable session cards
- **Session Cards**: Real-time status display
- **File Sidebar**: Browse session outputs
- **Meta View**: Cross-session comparison tools

## 🚀 Quick Start

### Development Mode

1. **Start the Backend:**
```bash
cd workspace-dashboard-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend runs on: http://localhost:8000

2. **Start the Frontend:**
```bash
cd workspace-dashboard-frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:3000

### Docker Deployment

```bash
docker-compose up --build
```

Access the dashboard at: http://localhost:3000

## 📡 API Endpoints

### Session Management
- `POST /sessions` - Create new session
- `GET /sessions` - List all sessions
- `GET /sessions/{id}` - Get session details
- `PUT /sessions/{id}` - Update session
- `DELETE /sessions/{id}` - Close session
- `GET /sessions/{id}/outputs` - Get session files

### Dashboard
- `GET /dashboard/layouts` - Get saved layouts
- `PUT /dashboard/layouts` - Save layout configuration

### Real-time Events (SSE)
- `GET /events` - Subscribe to real-time updates

## 🎨 Visual Status Codes

- **🟢 Green**: Task completed
- **🟡 Yellow**: Needs attention/approval
- **🔵 Blue**: Active/running
- **⚫ Gray**: Idle

## 🔧 Configuration

### Backend Configuration
Edit `workspace-dashboard-backend/main.py`:
```python
SESSION_DIR = Path("sessions")  # Session storage location
OUTPUT_DIR = Path("session_outputs")  # Output files location
```

### Frontend Configuration
Edit `workspace-dashboard-frontend/src/config.js`:
```javascript
export const API_URL = import.meta.env.DEV
  ? 'http://localhost:8000'
  : '/api';
```

## 📁 Project Structure

```
workspace-dashboard/
├── workspace-dashboard-backend/
│   ├── main.py                 # FastAPI application
│   ├── session_state.py        # Session persistence
│   ├── sse_manager.py          # Real-time events
│   ├── file_watcher.py         # File monitoring
│   └── claude_integration.py   # Claude SDK wrapper
├── workspace-dashboard-frontend/
│   ├── src/
│   │   ├── App.jsx            # Main dashboard
│   │   ├── SessionCard.jsx    # Session status cards
│   │   ├── WorkspaceGrid.jsx  # Grid layout manager
│   │   ├── FileSidebar.jsx    # File browser
│   │   └── MetaSession.jsx    # Overview component
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🔌 Claude Code SDK Integration

The backend includes a placeholder for Claude Code SDK integration. To connect real Claude sessions:

1. Install the Claude Code SDK
2. Update `claude_integration.py` with actual SDK calls
3. Configure authentication in `main.py`

## 🧪 Testing

### Backend Tests
```bash
cd workspace-dashboard-backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd workspace-dashboard-frontend
npm test
```

### API Contract Tests
```bash
cd workspace_dashboard_api
python contract_test_example.py
```

## 🎯 Use Cases

1. **Development Teams**: Monitor multiple feature branches being developed
2. **Code Reviews**: Compare implementations across sessions
3. **Learning**: Track multiple tutorial sessions simultaneously
4. **Experimentation**: Try different approaches in parallel

## 📝 Next Steps

- [ ] Implement actual Claude Code SDK integration
- [ ] Add authentication/user management
- [ ] Enhance meta-session comparison tools
- [ ] Add session history/replay functionality
- [ ] Implement session templates
- [ ] Add export/import for session configurations

## 📄 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

Built with the philosophy of ruthless simplicity and modular design for easy iteration and enhancement.