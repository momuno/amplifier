# Claude Code Workspace Dashboard API

Minimal, clear API contracts for managing multiple Claude Code sessions through a visual dashboard. Built following the 'bricks and studs' philosophy where each endpoint serves a single, clear purpose.

## 📐 Design Philosophy

This API embodies ruthless simplicity:
- **Every endpoint has ONE clear purpose**
- **Contracts are stable promises** - internal implementations can change, interfaces don't
- **Documentation IS the specification** - if it's not documented, it doesn't exist
- **Prefer one good endpoint over three mediocre ones**
- **Test the contract, not the implementation**

## 🏗️ API Structure

The API is organized into four self-contained modules:

### 1. Session Management (`/sessions`)
Manages individual Claude Code sessions - create, monitor, update, and close sessions.

### 2. Dashboard Layout (`/layouts`)
Handles visual dashboard configuration - save and restore tile positions and sizes.

### 3. Workspace Management (`/workspaces`)
Lists and manages available workspaces/repositories.

### 4. Meta Operations (`/sessions/compare`, `/sessions/stats`)
Cross-session operations for comparing outputs and gathering statistics.

## 🔌 Connection Points (The "Studs")

### REST API
- Base URL: `http://localhost:8080/api/v1`
- Authentication: Simple API key via `X-API-Key` header
- Content-Type: `application/json`
- Error Format: Consistent structure across all endpoints

### Server-Sent Events (SSE)
- Base URL: `http://localhost:8080/api/v1/events`
- Authentication: Same API key as REST
- Event Format: JSON payloads with `event` and `data` fields

## 📋 Quick Start Examples

### Creating a New Session

```bash
curl -X POST http://localhost:8080/api/v1/sessions \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "workspace": "/home/user/my-project",
    "project_name": "My Project",
    "initial_prompt": "Help me refactor the authentication module"
  }'
```

Response:
```json
{
  "id": "sess_abc123",
  "workspace": "/home/user/my-project",
  "project_name": "My Project",
  "status": "active",
  "created_at": "2025-01-23T10:30:00Z",
  "thread_id": "thread_xyz789"
}
```

### Subscribing to Real-time Updates

```javascript
// Session-specific events
const eventSource = new EventSource('/api/v1/events/sessions/sess_abc123', {
  headers: { 'X-API-Key': 'your-api-key' }
});

eventSource.addEventListener('session.status', (e) => {
  const { data } = JSON.parse(e.data);
  console.log(`Status changed to: ${data.status}`);
});

eventSource.addEventListener('session.task', (e) => {
  const { data } = JSON.parse(e.data);
  console.log(`Current task: ${data.current_task}`);
  console.log(`Progress: ${data.task_progress}%`);
});

// Dashboard-wide events
const dashboardEvents = new EventSource('/api/v1/events/dashboard', {
  headers: { 'X-API-Key': 'your-api-key' }
});

dashboardEvents.addEventListener('dashboard.session.created', (e) => {
  const { data } = JSON.parse(e.data);
  console.log(`New session created: ${data.session_id}`);
  // Add new tile to dashboard
});
```

### Updating Session State

```bash
curl -X PATCH http://localhost:8080/api/v1/sessions/sess_abc123 \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "executing",
    "current_task": "Running test suite",
    "next_task": "Fix failing tests"
  }'
```

### Saving Dashboard Layout

```bash
curl -X PUT http://localhost:8080/api/v1/layouts \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.0",
    "tiles": [
      {
        "id": "tile_1",
        "type": "session",
        "session_id": "sess_abc123",
        "position": { "x": 0, "y": 0 },
        "size": { "width": 6, "height": 4 }
      },
      {
        "id": "tile_2",
        "type": "stats",
        "position": { "x": 6, "y": 0 },
        "size": { "width": 6, "height": 4 }
      }
    ]
  }'
```

### Comparing Multiple Sessions

```bash
curl -X POST http://localhost:8080/api/v1/sessions/compare \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_ids": ["sess_abc123", "sess_def456"]
  }'
```

## 🔒 Authentication & Session Isolation

The API uses a simple API key mechanism for authentication and session isolation:

1. **API Key Required**: All endpoints require `X-API-Key` header
2. **User Isolation**: Each API key maps to a user; sessions are isolated per user
3. **Session Ownership**: Users can only access their own sessions
4. **Simple Implementation**: No complex OAuth flows or JWT tokens

Example:
```javascript
const headers = {
  'X-API-Key': 'user_specific_api_key',
  'Content-Type': 'application/json'
};
```

## ⚠️ Error Handling

All errors follow a consistent structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "additional": "context"
    }
  }
}
```

Common error codes:
- `INVALID_REQUEST` - Missing or invalid parameters
- `NOT_FOUND` - Resource doesn't exist
- `UNAUTHORIZED` - Missing or invalid API key
- `SESSION_CONFLICT` - Session state conflict
- `WORKSPACE_UNAVAILABLE` - Workspace cannot be accessed

## 🧱 Implementation as a "Brick"

This API module is designed as a self-contained brick:

### Inputs (What it needs)
- Claude Code backend service for session management
- File system access for workspace discovery
- Simple key-value store for layouts and preferences

### Outputs (What it provides)
- REST endpoints as documented in `openapi.yaml`
- SSE events as documented in `realtime-events.yaml`
- Consistent error responses

### Side Effects
- Creates/modifies session state in Claude backend
- Reads file system for workspace information
- Persists layout preferences

### Dependencies
- HTTP server (FastAPI, Express, etc.)
- SSE library for real-time events
- Claude Code SDK or API client
- Simple storage (Redis, SQLite, or even JSON files)

## 🔄 Regeneration Contract

This module can be regenerated from its specifications without breaking consumers:

1. **Stable Contracts**: The OpenAPI and AsyncAPI specs define the unchanging interface
2. **Internal Freedom**: Implementation can be completely rewritten
3. **Test Coverage**: Contract tests ensure compatibility
4. **Version Path**: If breaking changes needed, create `/v2` endpoints

## 📁 Module Structure

```
workspace_dashboard_api/
├── specs/
│   ├── openapi.yaml          # REST API specification
│   └── realtime-events.yaml  # SSE events specification
├── README.md                  # This file - the module contract
├── src/                       # Implementation (regeneratable)
│   ├── routes/               
│   │   ├── sessions.py
│   │   ├── layouts.py
│   │   ├── workspaces.py
│   │   └── meta.py
│   ├── events/
│   │   └── sse_manager.py
│   ├── models/
│   │   └── schemas.py
│   └── main.py
└── tests/
    ├── contract/              # Tests against the spec
    │   ├── test_endpoints.py
    │   └── test_events.py
    └── integration/           # End-to-end tests
        └── test_flows.py
```

## 🚀 Next Steps

### For Implementers
1. Choose your framework (FastAPI recommended for Python)
2. Implement endpoints following the OpenAPI spec exactly
3. Use the SSE specification for real-time events
4. Write contract tests that validate against the specs
5. Keep implementations simple - this is a coordination layer, not business logic

### For Consumers
1. Generate client code from the OpenAPI spec
2. Subscribe to relevant SSE events
3. Handle errors using the consistent error structure
4. Don't depend on undocumented behavior

### For Maintainers
1. Changes to specs require version bump
2. Internal refactoring is always allowed
3. Run contract tests before any release
4. Keep this README in sync with specs

## 📊 API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/sessions` | List all active sessions |
| POST | `/sessions` | Create new session |
| GET | `/sessions/{id}` | Get session details |
| PATCH | `/sessions/{id}` | Update session state |
| DELETE | `/sessions/{id}` | Close/archive session |
| GET | `/sessions/{id}/outputs` | Get session outputs |
| GET | `/layouts` | Get current layout |
| PUT | `/layouts` | Save layout |
| GET | `/workspaces` | List available workspaces |
| POST | `/sessions/compare` | Compare multiple sessions |
| GET | `/sessions/stats` | Get aggregate statistics |

## 📡 SSE Event Types

| Event | Channel | Description |
|-------|---------|-------------|
| `session.status` | `/sessions/{id}` | Status changed |
| `session.task` | `/sessions/{id}` | Task updated |
| `session.output` | `/sessions/{id}` | Output generated |
| `session.error` | `/sessions/{id}` | Error occurred |
| `dashboard.session.created` | `/dashboard` | New session created |
| `dashboard.session.closed` | `/dashboard` | Session closed |
| `dashboard.layout.changed` | `/dashboard` | Layout modified |

## 🧪 Testing the Contract

Example contract test:

```python
def test_create_session_contract():
    """Verify create session endpoint matches specification"""
    response = client.post("/sessions", json={
        "workspace": "/test/path",
        "project_name": "Test"
    })
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify required fields per spec
    assert "id" in data
    assert "workspace" in data
    assert "status" in data
    assert data["status"] in ["active", "idle", "thinking", "executing", "error"]
    
    # Verify no undocumented fields
    documented_fields = {"id", "workspace", "project_name", "status", 
                        "created_at", "thread_id", "current_task", 
                        "next_task", "context", "last_action", "last_interaction"}
    assert set(data.keys()).issubset(documented_fields)
```

---

*Built with the 'bricks and studs' philosophy - simple, stable, regeneratable.*
