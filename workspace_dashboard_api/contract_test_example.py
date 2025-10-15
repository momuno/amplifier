"""
Contract tests to validate API implementation against specification.
These tests ensure any implementation follows the defined contracts.
"""

import json

import httpx
import pytest

# Test configuration
BASE_URL = "http://localhost:8080/api/v1"
API_KEY = "key_test_user"
HEADERS = {"X-API-Key": API_KEY}


class TestSessionContract:
    """Test session endpoints match OpenAPI specification"""

    def test_create_session_required_fields(self, client: httpx.Client):
        """POST /sessions must accept required fields and return specified response"""
        # Test with only required field
        response = client.post(f"{BASE_URL}/sessions", headers=HEADERS, json={"workspace": "/test/workspace"})

        assert response.status_code == 201
        data = response.json()

        # Verify all required fields are present
        required_fields = {"id", "workspace", "status", "last_interaction"}
        assert all(field in data for field in required_fields)

        # Verify status is valid enum value
        assert data["status"] in ["active", "idle", "thinking", "executing", "error"]

        # Verify id format
        assert data["id"].startswith("sess_")

    def test_create_session_optional_fields(self, client: httpx.Client):
        """POST /sessions must accept optional fields per spec"""
        response = client.post(
            f"{BASE_URL}/sessions",
            headers=HEADERS,
            json={"workspace": "/test/workspace", "project_name": "Test Project", "initial_prompt": "Help me test"},
        )

        assert response.status_code == 201
        data = response.json()

        # Optional fields should be included if provided
        assert data.get("project_name") == "Test Project"

    def test_list_sessions_response_structure(self, client: httpx.Client):
        """GET /sessions must return array structure per spec"""
        response = client.get(f"{BASE_URL}/sessions", headers=HEADERS)

        assert response.status_code == 200
        data = response.json()

        # Must have sessions array
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

        # Each session must have required summary fields
        if data["sessions"]:
            session = data["sessions"][0]
            required = {"id", "workspace", "status", "last_interaction"}
            assert all(field in session for field in required)

    def test_update_session_partial_update(self, client: httpx.Client):
        """PATCH /sessions/{id} must support partial updates"""
        # Create session first
        create_response = client.post(f"{BASE_URL}/sessions", headers=HEADERS, json={"workspace": "/test"})
        session_id = create_response.json()["id"]

        # Update only status
        update_response = client.patch(
            f"{BASE_URL}/sessions/{session_id}", headers=HEADERS, json={"status": "executing"}
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["status"] == "executing"

        # Update only tasks
        update_response = client.patch(
            f"{BASE_URL}/sessions/{session_id}",
            headers=HEADERS,
            json={"current_task": "Running tests", "next_task": "Deploy"},
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data.get("current_task") == "Running tests"
        assert data.get("next_task") == "Deploy"

    def test_get_session_outputs_structure(self, client: httpx.Client):
        """GET /sessions/{id}/outputs must return specified structure"""
        # Create session
        create_response = client.post(f"{BASE_URL}/sessions", headers=HEADERS, json={"workspace": "/test"})
        session_id = create_response.json()["id"]

        response = client.get(f"{BASE_URL}/sessions/{session_id}/outputs", headers=HEADERS)

        assert response.status_code == 200
        data = response.json()

        # Verify structure matches spec
        assert "files_modified" in data
        assert "artifacts" in data
        assert isinstance(data["files_modified"], list)
        assert isinstance(data["artifacts"], list)

        # If files present, verify structure
        if data["files_modified"]:
            file_entry = data["files_modified"][0]
            assert "path" in file_entry
            assert "action" in file_entry
            assert file_entry["action"] in ["created", "modified", "deleted"]
            assert "timestamp" in file_entry


class TestErrorContract:
    """Test error responses match specification"""

    def test_unauthorized_error_format(self, client: httpx.Client):
        """401 errors must follow standard format"""
        response = client.get(f"{BASE_URL}/sessions", headers={})

        assert response.status_code == 401
        data = response.json()

        # Verify error structure
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "details" in data["error"]
        assert data["error"]["code"] == "UNAUTHORIZED"

    def test_not_found_error_format(self, client: httpx.Client):
        """404 errors must follow standard format"""
        response = client.get(f"{BASE_URL}/sessions/nonexistent", headers=HEADERS)

        assert response.status_code == 404
        data = response.json()

        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
        assert "nonexistent" in data["error"]["message"]

        # Details should include resource info
        details = data["error"].get("details", {})
        assert details.get("resource_type") == "session"
        assert details.get("resource_id") == "nonexistent"

    def test_bad_request_error_format(self, client: httpx.Client):
        """400 errors must follow standard format"""
        response = client.post(
            f"{BASE_URL}/sessions",
            headers=HEADERS,
            json={},  # Missing required field
        )

        assert response.status_code == 400
        data = response.json()

        assert "error" in data
        assert data["error"]["code"] == "INVALID_REQUEST"
        assert "workspace" in data["error"]["message"].lower()


class TestSSEContract:
    """Test SSE events match AsyncAPI specification"""

    @pytest.mark.asyncio
    async def test_session_event_format(self):
        """Session events must follow specified format"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            # Create a test session first
            async with session.post(f"{BASE_URL}/sessions", headers=HEADERS, json={"workspace": "/test"}) as resp:
                session_data = await resp.json()
                session_id = session_data["id"]

            # Connect to SSE stream
            async with session.get(f"{BASE_URL}/events/sessions/{session_id}", headers=HEADERS) as resp:
                assert resp.headers["Content-Type"] == "text/event-stream"

                # Read first event
                async for line in resp.content:
                    if line.startswith(b"data: "):
                        data = json.loads(line[6:])

                        # Verify event structure
                        assert "event" in data or "session_id" in data

                        if "event" in data:
                            # Verify event name matches spec
                            assert data["event"] in [
                                "session.status",
                                "session.task",
                                "session.output",
                                "session.error",
                            ]

                            # Verify data field exists
                            assert "data" in data
                            event_data = data["data"]

                            # Verify required fields based on event type
                            assert "session_id" in event_data
                            assert "timestamp" in event_data
                        break


class TestLayoutContract:
    """Test layout endpoints match specification"""

    def test_get_layout_structure(self, client: httpx.Client):
        """GET /layouts must return specified structure"""
        response = client.get(f"{BASE_URL}/layouts", headers=HEADERS)

        assert response.status_code == 200
        data = response.json()

        # Verify required fields
        assert "tiles" in data
        assert isinstance(data["tiles"], list)

        # If tiles present, verify structure
        if data["tiles"]:
            tile = data["tiles"][0]
            required_fields = {"id", "type", "position", "size"}
            assert all(field in tile for field in required_fields)

            # Verify type enum
            assert tile["type"] in ["session", "stats", "logs", "workspace"]

            # Verify position structure
            assert "x" in tile["position"]
            assert "y" in tile["position"]
            assert tile["position"]["x"] >= 0
            assert tile["position"]["y"] >= 0

            # Verify size structure and constraints
            assert "width" in tile["size"]
            assert "height" in tile["size"]
            assert 1 <= tile["size"]["width"] <= 12
            assert 1 <= tile["size"]["height"] <= 12

    def test_save_layout_validation(self, client: httpx.Client):
        """PUT /layouts must validate input structure"""
        valid_layout = {
            "version": "1.0",
            "tiles": [
                {
                    "id": "tile_1",
                    "type": "session",
                    "session_id": "sess_123",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 6, "height": 4},
                }
            ],
        }

        response = client.put(f"{BASE_URL}/layouts", headers=HEADERS, json=valid_layout)

        assert response.status_code == 200
        data = response.json()
        assert data == valid_layout


class TestMetaOperationsContract:
    """Test meta operations match specification"""

    def test_compare_sessions_validation(self, client: httpx.Client):
        """POST /sessions/compare must validate input"""
        # Test with too few sessions
        response = client.post(f"{BASE_URL}/sessions/compare", headers=HEADERS, json={"session_ids": ["sess_1"]})
        assert response.status_code == 400

        # Test with too many sessions
        response = client.post(
            f"{BASE_URL}/sessions/compare", headers=HEADERS, json={"session_ids": [f"sess_{i}" for i in range(11)]}
        )
        assert response.status_code == 400

        # Test with valid number (would be 404 if sessions don't exist)
        response = client.post(
            f"{BASE_URL}/sessions/compare", headers=HEADERS, json={"session_ids": ["sess_1", "sess_2"]}
        )
        assert response.status_code in [200, 404]

    def test_stats_response_structure(self, client: httpx.Client):
        """GET /sessions/stats must return specified metrics"""
        response = client.get(f"{BASE_URL}/sessions/stats", headers=HEADERS)

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields
        required_fields = {
            "total_sessions",
            "active_sessions",
            "tasks_completed_today",
            "files_modified_today",
            "average_session_duration",
        }
        assert all(field in data for field in required_fields)

        # Verify types
        assert isinstance(data["total_sessions"], int)
        assert isinstance(data["active_sessions"], int)
        assert isinstance(data["average_session_duration"], int)

        # Verify logical constraints
        assert data["active_sessions"] <= data["total_sessions"]
        assert data["average_session_duration"] >= 0


@pytest.fixture
def client():
    """Create HTTP client for tests"""
    return httpx.Client()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
