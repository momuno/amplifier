"""REST API routes for doc-studio."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from doc_studio.api.sse import sse_manager
from doc_studio.models import AppState
from doc_studio.models import FileNode
from doc_studio.models import GenerationJob
from doc_studio.models import JobStatus
from doc_studio.models import Template
from doc_studio.services.chat_service import ChatService
from doc_studio.services.generation_service import GenerationService
from doc_studio.utils.file_tree import build_file_tree

router = APIRouter()


# Request/Response models
class StateResponse(BaseModel):
    """Response model for app state."""

    workspace_path: str
    has_template: bool
    template_name: str | None = None


def get_app_state() -> AppState:
    """Get the global app state from server module."""
    from doc_studio.server import app_state

    return app_state


@router.get("/state", response_model=StateResponse)
async def get_state():
    """Get current application state."""
    state = get_app_state()
    return StateResponse(
        workspace_path=state.workspace_path,
        has_template=state.current_template is not None,
        template_name=state.current_template.name if state.current_template else None,
    )


@router.get("/health")
async def api_health():
    """API-specific health check."""
    return {"status": "healthy", "api_version": "0.1.0"}


@router.get("/files/tree", response_model=FileNode)
async def get_file_tree():
    """Get the repository file tree with inclusion status.

    Returns:
        FileNode tree structure
    """
    state = get_app_state()
    workspace = Path(state.workspace_path)

    # Get included files from current template
    included_files = state.get_included_files()

    # Build and return file tree
    tree = build_file_tree(workspace, included_files)
    return tree


@router.get("/templates/{template_name}", response_model=Template)
async def get_template(template_name: str):
    """Get a template by name.

    Args:
        template_name: Name of template to load

    Returns:
        Template object

    Raises:
        HTTPException: If template not found
    """
    state = get_app_state()
    from doc_studio.services.template_service import TemplateService

    service = TemplateService(state.workspace_path)
    template = service.load_template(template_name)

    if template is None:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    return template


class AddSourceRequest(BaseModel):
    """Request body for adding a source file."""

    file_path: str


@router.post("/templates/{template_name}/sections/{section_id}/sources")
async def add_source_to_section(
    template_name: str,
    section_id: str,
    request: AddSourceRequest,
):
    """Add a source file to a template section.

    Args:
        template_name: Name of template
        section_id: Section ID
        request: Request body with file_path

    Returns:
        Success message
    """
    file_path = request.file_path
    state = get_app_state()
    from doc_studio.services.template_service import TemplateService

    service = TemplateService(state.workspace_path)

    # Load or use current template
    if state.current_template and state.current_template.name == template_name:
        template = state.current_template
    else:
        template = service.load_template(template_name)
        if template is None:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        state.current_template = template

    # Add source to section
    success = service.add_source_to_section(template, section_id, file_path)
    if not success:
        raise HTTPException(status_code=404, detail=f"Section '{section_id}' not found")

    # Save template
    service.save_template(template)

    return {"message": "Source added successfully", "file_path": file_path}


@router.delete("/templates/{template_name}/sections/{section_id}/sources/{file_path:path}")
async def remove_source_from_section(
    template_name: str,
    section_id: str,
    file_path: str,
):
    """Remove a source file from a template section.

    Args:
        template_name: Name of template
        section_id: Section ID
        file_path: Path to source file

    Returns:
        Success message
    """
    state = get_app_state()
    from doc_studio.services.template_service import TemplateService

    service = TemplateService(state.workspace_path)

    # Load or use current template
    if state.current_template and state.current_template.name == template_name:
        template = state.current_template
    else:
        template = service.load_template(template_name)
        if template is None:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        state.current_template = template

    # Remove source from section
    success = service.remove_source_from_section(template, section_id, file_path)
    if not success:
        raise HTTPException(status_code=404, detail=f"Section '{section_id}' not found")

    # Save template
    service.save_template(template)

    return {"message": "Source removed successfully", "file_path": file_path}


@router.get("/events/{resource_id}")
async def event_stream(resource_id: str):
    """Server-Sent Events stream for real-time updates.

    Args:
        resource_id: Resource ID to subscribe to (e.g., "job:123", "generation:default")

    Returns:
        SSE event stream
    """

    async def event_generator():
        """Generate SSE events from the queue."""
        queue, connection_id = await sse_manager.add_connection(resource_id)

        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            sse_manager.remove_connection(connection_id)

    return EventSourceResponse(event_generator())


class GenerateRequest(BaseModel):
    """Request body for document generation."""

    template_name: str
    output_path: str


@router.post("/generate", response_model=GenerationJob)
async def start_generation(request: GenerateRequest):
    """Start document generation.

    Args:
        request: Generation request with template name and output path

    Returns:
        GenerationJob with initial status
    """
    import uuid

    state = get_app_state()
    from doc_studio.services.template_service import TemplateService

    service = TemplateService(state.workspace_path)
    template = service.load_template(request.template_name)

    if template is None:
        raise HTTPException(status_code=404, detail=f"Template '{request.template_name}' not found")

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Create generation service
    gen_service = GenerationService(state.workspace_path)

    # Start generation in background
    import asyncio

    async def run_generation():
        """Run generation in background."""
        job = await gen_service.generate_document(template, request.output_path, job_id)
        state.active_job = job

    asyncio.create_task(run_generation())

    # Return initial job status
    return GenerationJob(
        id=job_id,
        template_name=request.template_name,
        status=JobStatus.RUNNING,
        progress=0.0,
        result_path=request.output_path,
    )


class ChatRequest(BaseModel):
    """Request body for chat messages."""

    message: str
    user_id: str = "default"


@router.post("/chat")
async def send_chat_message(request: ChatRequest):
    """Send a chat message to the AI assistant.

    Args:
        request: Chat request with message and user ID

    Returns:
        Success response
    """
    chat_service = ChatService()
    resource_id = f"chat:{request.user_id}"

    # Process message in background
    import asyncio

    asyncio.create_task(chat_service.process_message(request.user_id, request.message, resource_id))

    return {"message": "Message received", "resource_id": resource_id}


@router.get("/documents/{document_path:path}")
async def get_document(document_path: str):
    """Get a generated document.

    Args:
        document_path: Path to the generated document

    Returns:
        Document content as plain text
    """
    state = get_app_state()
    workspace = Path(state.workspace_path)
    doc_file = workspace / document_path

    if not doc_file.exists():
        raise HTTPException(status_code=404, detail=f"Document '{document_path}' not found")

    if not doc_file.is_relative_to(workspace):
        raise HTTPException(status_code=403, detail="Access denied")

    content = doc_file.read_text(encoding="utf-8")
    return PlainTextResponse(content=content)


class SourceAttribution(BaseModel):
    """Source attribution for a template section."""

    section_id: str
    source_files: list[str]


@router.get("/templates/{template_name}/attributions")
async def get_template_attributions(template_name: str) -> list[SourceAttribution]:
    """Get source attributions for a template.

    Args:
        template_name: Name of the template

    Returns:
        List of source attributions by section
    """
    state = get_app_state()
    from doc_studio.services.template_service import TemplateService

    service = TemplateService(state.workspace_path)
    template = service.load_template(template_name)

    if template is None:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    attributions = [
        SourceAttribution(section_id=section.id, source_files=section.source_files) for section in template.sections
    ]

    return attributions
