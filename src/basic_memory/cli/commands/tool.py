"""CLI tool commands for Basic Memory."""

import asyncio
import sys
from typing import Annotated, List, Optional

import typer
from loguru import logger
from rich import print as rprint

from basic_memory.cli.app import app

# Import prompts
from basic_memory.mcp.prompts.continue_conversation import (
    continue_conversation as mcp_continue_conversation,
)
from basic_memory.mcp.prompts.recent_activity import (
    recent_activity_prompt as recent_activity_prompt,
)
from basic_memory.mcp.tools import build_context as mcp_build_context
from basic_memory.mcp.tools import read_note as mcp_read_note
from basic_memory.mcp.tools import recent_activity as mcp_recent_activity
from basic_memory.mcp.tools import search_notes as mcp_search
from basic_memory.mcp.tools import write_note as mcp_write_note
from basic_memory.schemas.base import TimeFrame
from basic_memory.schemas.memory import MemoryUrl
from basic_memory.schemas.search import SearchItemType

tool_app = typer.Typer()
app.add_typer(tool_app, name="tool", help="Access to MCP tools via CLI")


@tool_app.command()
def write_note(
    title: Annotated[str, typer.Option(help="The title of the note")],
    folder: Annotated[str, typer.Option(help="The folder to create the note in")],
    content: Annotated[
        Optional[str],
        typer.Option(
            help="The content of the note. If not provided, content will be read from stdin. This allows piping content from other commands, e.g.: cat file.md | basic-memory tools write-note"
        ),
    ] = None,
    tags: Annotated[
        Optional[List[str]], typer.Option(help="A list of tags to apply to the note")
    ] = None,
):
    """Create or update a markdown note. Content can be provided as an argument or read from stdin.

    Content can be provided in two ways:
    1. Using the --content parameter
    2. Piping content through stdin (if --content is not provided)

    Examples:

    # Using content parameter
    basic-memory tools write-note --title "My Note" --folder "notes" --content "Note content"

    # Using stdin pipe
    echo "# My Note Content" | basic-memory tools write-note --title "My Note" --folder "notes"

    # Using heredoc
    cat << EOF | basic-memory tools write-note --title "My Note" --folder "notes"
    # My Document

    This is my document content.

    - Point 1
    - Point 2
    EOF

    # Reading from a file
    cat document.md | basic-memory tools write-note --title "Document" --folder "docs"
    """
    try:
        # If content is not provided, read from stdin
        if content is None:
            # Check if we're getting data from a pipe or redirect
            if not sys.stdin.isatty():
                content = sys.stdin.read()
            else:  # pragma: no cover
                # If stdin is a terminal (no pipe/redirect), inform the user
                typer.echo(
                    "No content provided. Please provide content via --content or by piping to stdin.",
                    err=True,
                )
                raise typer.Exit(1)

        # Also check for empty content
        if content is not None and not content.strip():
            typer.echo("Empty content provided. Please provide non-empty content.", err=True)
            raise typer.Exit(1)

        note = asyncio.run(mcp_write_note.fn(title, content, folder, tags))
        rprint(note)
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            typer.echo(f"Error during write_note: {e}", err=True)
            raise typer.Exit(1)
        raise


@tool_app.command()
def read_note(identifier: str, page: int = 1, page_size: int = 10):
    """Read a markdown note from the knowledge base."""
    try:
        note = asyncio.run(mcp_read_note.fn(identifier, page, page_size))
        rprint(note)
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            typer.echo(f"Error during read_note: {e}", err=True)
            raise typer.Exit(1)
        raise


@tool_app.command()
def build_context(
    url: MemoryUrl,
    depth: Optional[int] = 1,
    timeframe: Optional[TimeFrame] = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
):
    """Get context needed to continue a discussion."""
    async def _build_context_direct():
        from basic_memory.mcp.tools.utils import get_direct_services
        from basic_memory.schemas.base import parse_timeframe
        from basic_memory.schemas.memory import normalize_memory_url
        from basic_memory.api.routers.utils import to_graph_context
        
        services = await get_direct_services()
        context_service = services['context_service']
        entity_repository = services['entity_repository']
        
        memory_url = normalize_memory_url(url)
        since = parse_timeframe(timeframe) if timeframe else None
        limit = page_size
        offset = (page - 1) * page_size
        
        context = await context_service.build_context(
            memory_url, depth=depth, since=since, limit=limit, offset=offset, max_related=max_related
        )
        
        result = await to_graph_context(
            context, entity_repository=entity_repository, page=page, page_size=page_size
        )
        
        return result
        
    try:
        result = asyncio.run(_build_context_direct())
        import json
        context_dict = result.model_dump(exclude_none=True)
        print(json.dumps(context_dict, indent=2, ensure_ascii=True, default=str))
    except Exception as e:
        if not isinstance(e, typer.Exit):
            typer.echo(f"Error during build_context: {e}", err=True)
            raise typer.Exit(1)
        raise


@tool_app.command()
def recent_activity(
    type: Annotated[Optional[List[SearchItemType]], typer.Option()] = None,
    depth: Optional[int] = 1,
    timeframe: Optional[TimeFrame] = "7d",
    page: int = 1,
    page_size: int = 10,
    max_related: int = 10,
):
    """Get recent activity across the knowledge base."""
    try:
        context = asyncio.run(
            mcp_recent_activity.fn(
                type=type,  # pyright: ignore [reportArgumentType]
                depth=depth,
                timeframe=timeframe,
                page=page,
                page_size=page_size,
                max_related=max_related,
            )
        )
        # Use json module for more controlled serialization
        import json

        context_dict = context.model_dump(exclude_none=True)
        print(json.dumps(context_dict, indent=2, ensure_ascii=True, default=str))
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            typer.echo(f"Error during build_context: {e}", err=True)
            raise typer.Exit(1)
        raise


@tool_app.command("search-notes")
def search_notes(
    query: str,
    permalink: Annotated[bool, typer.Option("--permalink", help="Search permalink values")] = False,
    title: Annotated[bool, typer.Option("--title", help="Search title values")] = False,
    after_date: Annotated[
        Optional[str],
        typer.Option("--after_date", help="Search results after date, eg. '2d', '1 week'"),
    ] = None,
    page: int = 1,
    page_size: int = 10,
):
    """Search across all content in the knowledge base."""
    if permalink and title:  # pragma: no cover
        print("Cannot search both permalink and title")
        raise typer.Abort()

    try:
        if permalink and title:  # pragma: no cover
            typer.echo(
                "Use either --permalink or --title, not both. Exiting.",
                err=True,
            )
            raise typer.Exit(1)

        # set search type
        search_type = ("permalink" if permalink else None,)
        search_type = ("permalink_match" if permalink and "*" in query else None,)
        search_type = ("title" if title else None,)
        search_type = "text" if search_type is None else search_type

        results = asyncio.run(
            mcp_search.fn(
                query,
                search_type=search_type,
                page=page,
                after_date=after_date,
                page_size=page_size,
            )
        )
        # Use json module for more controlled serialization
        import json

        results_dict = results.model_dump(exclude_none=True)
        print(json.dumps(results_dict, indent=2, ensure_ascii=True, default=str))
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            logger.exception("Error during search", e)
            typer.echo(f"Error during search: {e}", err=True)
            raise typer.Exit(1)
        raise


@tool_app.command(name="continue-conversation")
def continue_conversation(
    topic: Annotated[Optional[str], typer.Option(help="Topic or keyword to search for")] = None,
    timeframe: Annotated[
        Optional[str], typer.Option(help="How far back to look for activity")
    ] = None,
):
    """Prompt to continue a previous conversation or work session."""
    try:
        # Prompt functions return formatted strings directly
        session = asyncio.run(mcp_continue_conversation.fn(topic=topic, timeframe=timeframe))  # type: ignore
        rprint(session)
    except Exception as e:  # pragma: no cover
        if not isinstance(e, typer.Exit):
            logger.exception("Error continuing conversation", e)
            typer.echo(f"Error continuing conversation: {e}", err=True)
            raise typer.Exit(1)
        raise


# @tool_app.command(name="show-recent-activity")
# def show_recent_activity(
#     timeframe: Annotated[
#         str, typer.Option(help="How far back to look for activity")
#     ] = "7d",
# ):
#     """Prompt to show recent activity."""
#     try:
#         # Prompt functions return formatted strings directly
#         session = asyncio.run(recent_activity_prompt(timeframe=timeframe))
#         rprint(session)
#     except Exception as e:  # pragma: no cover
#         if not isinstance(e, typer.Exit):
#             logger.exception("Error continuing conversation", e)
#             typer.echo(f"Error continuing conversation: {e}", err=True)
#             raise typer.Exit(1)
#         raise


@tool_app.command()
def canvas(
    nodes: Annotated[str, typer.Option(help="JSON string of nodes array following JSON Canvas 1.0 spec")],
    edges: Annotated[str, typer.Option(help="JSON string of edges array following JSON Canvas 1.0 spec")], 
    title: Annotated[str, typer.Option(help="The title of the canvas (will be saved as title.canvas)")],
    folder: Annotated[str, typer.Option(help="Folder path relative to project root where the canvas should be saved")],
    project: Annotated[Optional[str], typer.Option(help="Optional project name to create canvas in")] = None,
):
    """Create an Obsidian canvas file to visualize concepts and connections.
    
    This tool creates a .canvas file compatible with Obsidian's Canvas feature,
    allowing visualization of relationships between concepts or documents.
    
    Examples:
        basic-memory tool canvas --nodes '[{"id":"node1","type":"text","text":"Hello","x":0,"y":0,"width":200,"height":100}]' --edges '[]' --title "My Canvas" --folder "diagrams"
    """
    try:
        import json
        
        try:
            nodes_list = json.loads(nodes)
            edges_list = json.loads(edges)
        except json.JSONDecodeError as e:
            typer.echo(f"Invalid JSON format: {e}", err=True)
            raise typer.Exit(1)
        
        result = asyncio.run(_create_canvas_direct(nodes_list, edges_list, title, folder, project))
        rprint(result)
    except Exception as e:
        if not isinstance(e, typer.Exit):
            typer.echo(f"Error during canvas creation: {e}", err=True)
            raise typer.Exit(1)
        raise


async def _create_canvas_direct(nodes, edges, title, folder, project):
    """Create canvas using direct service calls."""
    from basic_memory.mcp.tools.utils import get_direct_services
    import json
    from pathlib import Path
    from datetime import datetime
    
    services = await get_direct_services(project)
    file_service = services['entity_service'].file_service
    entity_repository = services['entity_repository']
    search_service = services['search_service']
    project_config = services['project_config']
    
    # Ensure path has .canvas extension
    file_title = title if title.endswith(".canvas") else f"{title}.canvas"
    file_path = f"{folder}/{file_title}"
    
    # Create canvas data structure
    canvas_data = {"nodes": nodes, "edges": edges}
    canvas_json = json.dumps(canvas_data, indent=2)
    
    checksum = await file_service.write_file(file_path, canvas_json)
    
    full_path = Path(f"{project_config.home}/{file_path}")
    file_stats = file_service.file_stats(full_path)
    
    existing_entity = await entity_repository.get_by_file_path(file_path)
    
    if existing_entity:
        # Update existing entity
        entity = await entity_repository.update(
            existing_entity.id,
            {
                "title": file_title,
                "entity_type": "canvas",
                "content_type": "application/json",
                "file_path": file_path,
                "checksum": checksum,
                "updated_at": datetime.fromtimestamp(file_stats.st_mtime),
            },
        )
        action = "Updated"
    else:
        # Create new entity
        from basic_memory.models.knowledge import Entity as EntityModel
        entity = EntityModel(
            title=file_title,
            entity_type="canvas",
            content_type="application/json",
            file_path=file_path,
            checksum=checksum,
            created_at=datetime.fromtimestamp(file_stats.st_ctime),
            updated_at=datetime.fromtimestamp(file_stats.st_mtime),
        )
        entity = await entity_repository.add(entity)
        action = "Created"
    
    await search_service.index_entity(entity)
    
    # Build summary
    summary = [f"# {action}: {file_path}", "\nThe canvas is ready to open in Obsidian."]
    return "\n".join(summary)
