"""
FastAPI Server for Git Subway Map.
Serves schematic subway topology graphs, repository analytics,
and static frontend SPA assets.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Optional, List

# Ensure backend directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from models import (
    SubwayGraph,
    SubwayLine,
    SubwayStation,
    HealthResponse,
)
from parser import parse_git_repository
from layout import SubwayLayoutEngine
from demo_repo import create_demo_repository

app = FastAPI(
    title="Git Subway Map API",
    description="Transforms Git DAG commit histories into schematic transit subway maps.",
    version="1.0.0",
)

# Enable CORS for modern web frontends (Vite, React, Vue, Next.js, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
DEFAULT_DEMO_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "demo-repo"))
STATIC_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "frontend", "dist"))
ASSETS_DIR = os.path.join(STATIC_DIR, "assets")


def get_default_repo_path() -> str:
    """Returns the default repository path configured via environment or demo fallback."""
    env_repo = os.environ.get("GIT_SUBWAY_REPO")
    if env_repo and env_repo.strip():
        resolved_env = os.path.abspath(env_repo.strip())
        if os.path.exists(resolved_env):
            return resolved_env
    return DEFAULT_DEMO_DIR


def _ensure_default_repo(repo_path: Optional[str]) -> str:
    """Returns resolved repo path, generating demo repo if no path given."""
    if repo_path and repo_path.strip():
        resolved = os.path.abspath(repo_path.strip())
        if not os.path.exists(resolved):
            raise HTTPException(status_code=404, detail=f"Repository path does not exist: {resolved}")
        return resolved

    default_path = get_default_repo_path()
    # Fallback to demo repo if default_path doesn't exist or is not a git repo
    if not os.path.exists(default_path) or not os.path.exists(os.path.join(default_path, ".git")):
        create_demo_repository(default_path)
        
    return default_path


def generate_subway_graph(
    repo_path: Optional[str] = None,
    step_x: float = 140.0,
    step_y: float = 90.0,
) -> SubwayGraph:
    """Internal service to parse and lay out subway graph for any repository."""
    target_path = _ensure_default_repo(repo_path)
    
    try:
        parsed_repo = parse_git_repository(target_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Git repository: {str(e)}")

    try:
        engine = SubwayLayoutEngine(
            parsed_repo=parsed_repo,
            grid_step_x=step_x,
            grid_step_y=step_y,
        )
        return engine.build_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Subway topology layout error: {str(e)}")


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def get_health():
    """Health check endpoint returning service status and UTC timestamp."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        service="git-subway-map",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/api/subway-graph", response_model=SubwayGraph, tags=["Subway"])
def get_subway_graph(
    repo_path: Optional[str] = Query(
        None,
        description="Absolute or relative path to a local Git repository. Defaults to sample demo repo.",
    ),
    step_x: float = Query(140.0, description="Horizontal grid step in pixels (station spacing)"),
    step_y: float = Query(90.0, description="Vertical grid step in pixels (track corridor spacing)"),
):
    """
    Parses Git commit DAG and returns complete schematic Subway Graph JSON.
    Includes stations, transit lines, interchange hubs, and octolinear track vectors.
    """
    return generate_subway_graph(repo_path=repo_path, step_x=step_x, step_y=step_y)


@app.get("/api/lines", response_model=List[SubwayLine], tags=["Subway"])
def get_transit_lines(
    repo_path: Optional[str] = Query(None, description="Path to repository"),
):
    """Returns only the transit lines and legend for the repository."""
    graph = generate_subway_graph(repo_path=repo_path)
    return graph.lines


@app.get("/api/stations", response_model=List[SubwayStation], tags=["Subway"])
def get_stations(
    repo_path: Optional[str] = Query(None, description="Path to repository"),
):
    """Returns only the list of subway stations for the repository."""
    graph = generate_subway_graph(repo_path=repo_path)
    return graph.stations


@app.post("/api/demo/reset", tags=["Demo"])
def reset_demo_repo():
    """Rebuilds the demo Git repository with multi-branch DAG topology."""
    try:
        path = create_demo_repository(DEFAULT_DEMO_DIR)
        return {"status": "ok", "message": f"Demo repository reset at {path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset demo repo: {str(e)}")


# ---------------------------------------------------------------------------
# Static Files & SPA Fallback Route Handling
# ---------------------------------------------------------------------------

if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/", include_in_schema=False)
async def serve_index():
    """Serves the frontend SPA index.html at root."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file, media_type="text/html")
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "message": "Git Subway Map API is running. Frontend build not found in frontend/dist.",
        },
    )


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa_or_static(full_path: str):
    """
    Handles static files in frontend/dist (e.g. favicon.svg, icons.svg)
    and falls back to index.html for SPA client-side routing.
    Guards API routes from serving HTML 404s.
    """
    # Guard API routes from returning HTML when endpoint is not found
    if full_path == "api" or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail=f"API endpoint not found: /{full_path}")

    # Prevent intercepting OpenAPI documentation
    if full_path in ("docs", "redoc", "openapi.json"):
        raise HTTPException(status_code=404, detail="Not Found")

    # Serve static file if exists within STATIC_DIR
    target_file = os.path.abspath(os.path.join(STATIC_DIR, full_path))
    if target_file.startswith(STATIC_DIR) and os.path.isfile(target_file):
        return FileResponse(target_file)

    # SPA Fallback: serve index.html for non-file routes
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file, media_type="text/html")

    raise HTTPException(status_code=404, detail="Resource not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
