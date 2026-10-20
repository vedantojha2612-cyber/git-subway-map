"""
Data models for the Git Subway Map schema.
Defines stations, transit lines, schematic tracks, and graph structures.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Point(BaseModel):
    x: float
    y: float


class SubwayLine(BaseModel):
    id: str = Field(..., description="Unique transit line identifier, e.g. 'line-red'")
    name: str = Field(..., description="Display name, e.g. 'Red Line (main)'")
    color: str = Field(..., description="Primary hex color, e.g. '#E53935'")
    secondary_color: str = Field("#FFFFFF", description="Contrasting color for borders/text")
    branch_name: str = Field(..., description="Underlying Git branch or ref name")
    lane_index: int = Field(0, description="Corridor track lane index on Y axis")
    station_count: int = Field(0, description="Total stations on this line")
    is_trunk: bool = Field(False, description="True if this is the primary trunk line (main/master)")


class SubwayStation(BaseModel):
    id: str = Field(..., description="Full 40-character commit hash")
    short_hash: str = Field(..., description="Truncated 7-character commit hash")
    message: str = Field(..., description="Commit subject message")
    author_name: str = Field(..., description="Author display name")
    author_email: str = Field(..., description="Author email address")
    timestamp: int = Field(..., description="Commit timestamp in Unix epoch seconds")
    iso_time: str = Field(..., description="ISO 8601 formatted datetime string")
    
    grid_x: int = Field(..., description="Integer grid X coordinate (topological sequence)")
    grid_y: int = Field(..., description="Integer grid Y coordinate (lane index)")
    x: float = Field(..., description="Rendered schematic pixel X coordinate")
    y: float = Field(..., description="Rendered schematic pixel Y coordinate")
    
    line_id: str = Field(..., description="Assigned transit line identifier")
    line_name: str = Field(..., description="Assigned transit line name")
    line_color: str = Field(..., description="Assigned transit line hex color")
    
    is_interchange: bool = Field(False, description="True if station is a merge commit (transfer station)")
    transfer_lines: List[str] = Field(default_factory=list, description="IDs of lines transferring at this station")
    
    parents: List[str] = Field(default_factory=list, description="Parent commit hashes")
    children: List[str] = Field(default_factory=list, description="Child commit hashes")
    branches: List[str] = Field(default_factory=list, description="Branch names pointing to this commit")
    tags: List[str] = Field(default_factory=list, description="Git tags pointing to this commit")
    
    is_head: bool = Field(False, description="True if HEAD points directly to this commit")
    is_root: bool = Field(False, description="True if initial root commit with 0 parents")


class SubwayTrack(BaseModel):
    id: str = Field(..., description="Unique track segment ID")
    from_station_id: str = Field(..., description="Origin commit hash")
    to_station_id: str = Field(..., description="Destination commit hash")
    line_id: str = Field(..., description="Transit line identifier for this track")
    line_color: str = Field(..., description="Hex color of the track")
    points: List[Point] = Field(default_factory=list, description="Waypoints defining the schematic path")
    svg_path: str = Field(..., description="SVG path 'd' attribute with 45/90 degree bends")
    is_merge: bool = Field(False, description="True if this track connects a branch into an interchange")
    is_fork: bool = Field(False, description="True if this track diverges from parent line to a branch")
    is_trunk: bool = Field(False, description="True if between trunk stations")


class SubwayBounds(BaseModel):
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    width: float
    height: float


class SubwayGraph(BaseModel):
    repo_name: str = Field(..., description="Base directory or repository name")
    repo_path: str = Field(..., description="Absolute path of the Git repository")
    head_commit: Optional[str] = Field(None, description="Current HEAD commit hash")
    active_branch: Optional[str] = Field(None, description="Active Git branch name")
    total_commits: int = Field(..., description="Total commits processed")
    total_lines: int = Field(..., description="Total transit lines created")
    stations: List[SubwayStation] = Field(default_factory=list, description="List of subway stations")
    tracks: List[SubwayTrack] = Field(default_factory=list, description="List of transit track segments")
    lines: List[SubwayLine] = Field(default_factory=list, description="Active transit lines and legend")
    bounds: SubwayBounds = Field(..., description="Canvas bounding box dimensions")
    grid_step_x: float = Field(140.0, description="Horizontal grid step in pixels")
    grid_step_y: float = Field(90.0, description="Vertical grid step in pixels")


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    service: str = "git-subway-map"
    timestamp: str
