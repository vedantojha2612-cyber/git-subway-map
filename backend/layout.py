"""
Subway Topology and Schematic Layout Engine.
Assigns transit lines, subway colors, grid coordinates, interchange badges,
and calculates 45-degree octolinear track geometries.
"""

from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
from models import (
    Point,
    SubwayStation,
    SubwayTrack,
    SubwayLine,
    SubwayBounds,
    SubwayGraph,
)
from parser import ParsedRepo, RawCommit

# Transit Line Palette - High-contrast iconic metro line colors
TRANSIT_PALETTE = [
    {"name": "Red Line", "color": "#E53935", "secondary": "#FFCDD2"},
    {"name": "Blue Line", "color": "#1E88E5", "secondary": "#BBDEFB"},
    {"name": "Green Line", "color": "#43A047", "secondary": "#C8E6C9"},
    {"name": "Orange Line", "color": "#FB8C00", "secondary": "#FFE0B2"},
    {"name": "Purple Line", "color": "#8E24AA", "secondary": "#E1BEE7"},
    {"name": "Teal Line", "color": "#00ACC1", "secondary": "#B2EBF2"},
    {"name": "Amber Line", "color": "#FFB300", "secondary": "#FFECB3"},
    {"name": "Pink Line", "color": "#D81B60", "secondary": "#F8BBD0"},
    {"name": "Indigo Line", "color": "#3949AB", "secondary": "#C5CAE9"},
    {"name": "Cyan Line", "color": "#00BCD4", "secondary": "#B2EBF2"},
    {"name": "Lime Line", "color": "#7CB342", "secondary": "#DCEDC8"},
    {"name": "Brown Line", "color": "#6D4C41", "secondary": "#D7CCC8"},
]


class SubwayLayoutEngine:
    def __init__(
        self,
        parsed_repo: ParsedRepo,
        grid_step_x: float = 140.0,
        grid_step_y: float = 90.0,
        margin_x: float = 80.0,
        margin_y: float = 80.0,
    ):
        self.repo = parsed_repo
        self.commits = parsed_repo.commits
        self.step_x = grid_step_x
        self.step_y = grid_step_y
        self.margin_x = margin_x
        self.margin_y = margin_y
        
        # Build children adjacency
        self.children: Dict[str, List[str]] = defaultdict(list)
        for c_hash, c in self.commits.items():
            for p_hash in c.parents:
                if p_hash in self.commits:
                    self.children[p_hash].append(c_hash)

    def _determine_trunk_branch(self) -> str:
        """Finds the main trunk branch name (e.g. main, master, or active branch)."""
        candidates = ["main", "master", "develop", "trunk"]
        
        # 1. Active branch if it matches candidates
        if self.repo.active_branch and self.repo.active_branch in self.repo.branches:
            return self.repo.active_branch
            
        # 2. Candidate names in branches
        for cand in candidates:
            if cand in self.repo.branches:
                return cand
                
        # 3. Any branch
        if self.repo.branches:
            return next(iter(self.repo.branches.keys()))
            
        return "trunk"

    def _assign_lines_and_lanes(self) -> Tuple[Dict[str, str], Dict[str, SubwayLine], Dict[str, int]]:
        """
        Assigns each commit to a transit line, defines lines, and assigns lanes.
        Returns:
            commit_to_line: commit_hash -> line_id
            lines: line_id -> SubwayLine
            line_lanes: line_id -> grid_y lane index
        """
        trunk_branch = self._determine_trunk_branch()
        commit_to_line: Dict[str, str] = {}
        lines: Dict[str, SubwayLine] = {}
        line_lanes: Dict[str, int] = {}
        
        # Sort branch names: trunk first, then active branch, then others
        sorted_branches = []
        if trunk_branch in self.repo.branches:
            sorted_branches.append((trunk_branch, self.repo.branches[trunk_branch]))
        
        for b_name, b_hash in self.repo.branches.items():
            if b_name != trunk_branch:
                sorted_branches.append((b_name, b_hash))
                
        # If no branches exist, use HEAD or latest commit
        if not sorted_branches and self.commits:
            # Pick latest commit by timestamp
            latest_hash = max(self.commits.keys(), key=lambda h: self.commits[h].timestamp)
            sorted_branches.append((trunk_branch, latest_hash))

        color_idx = 0
        current_lane = 0
        
        for b_name, tip_hash in sorted_branches:
            line_id = f"line-{b_name.replace('/', '-').replace(' ', '-')}"
            is_trunk = (b_name == trunk_branch)
            palette = TRANSIT_PALETTE[color_idx % len(TRANSIT_PALETTE)]
            color_idx += 1
            
            line_name = f"{palette['name']} ({b_name})"
            line = SubwayLine(
                id=line_id,
                name=line_name,
                color=palette["color"],
                secondary_color=palette["secondary"],
                branch_name=b_name,
                lane_index=current_lane,
                station_count=0,
                is_trunk=is_trunk,
            )
            lines[line_id] = line
            line_lanes[line_id] = current_lane
            current_lane += 1
            
            # Trace backwards from tip along first parent
            curr = tip_hash
            while curr and curr in self.commits:
                if curr in commit_to_line:
                    # Already claimed by earlier branch (e.g. trunk)
                    break
                commit_to_line[curr] = line_id
                line.station_count += 1
                parents = self.commits[curr].parents
                curr = parents[0] if parents else None

        # Any unassigned commits (e.g. dangling commits, deleted branch merges)
        unassigned = [c_hash for c_hash in self.commits if c_hash not in commit_to_line]
        if unassigned:
            aux_line_id = "line-auxiliary"
            palette = TRANSIT_PALETTE[color_idx % len(TRANSIT_PALETTE)]
            lines[aux_line_id] = SubwayLine(
                id=aux_line_id,
                name=f"{palette['name']} (shuttle)",
                color=palette["color"],
                secondary_color=palette["secondary"],
                branch_name="shuttle",
                lane_index=current_lane,
                station_count=len(unassigned),
                is_trunk=False,
            )
            line_lanes[aux_line_id] = current_lane
            for c_hash in unassigned:
                commit_to_line[c_hash] = aux_line_id

        return commit_to_line, lines, line_lanes

    def _compute_topological_columns(self) -> Dict[str, int]:
        """
        Computes the topological sequence (grid_x) for each commit.
        Roots are on the left, newer commits towards the right.
        Ensures parents are strictly to the left of their children.
        """
        # Calculate topological depth
        memo_depth: Dict[str, int] = {}
        
        def get_depth(c_hash: str, visited: Set[str]) -> int:
            if c_hash in memo_depth:
                return memo_depth[c_hash]
            if c_hash in visited:
                return 0
            visited.add(c_hash)
            
            commit = self.commits.get(c_hash)
            if not commit or not commit.parents:
                depth = 0
            else:
                valid_parents = [p for p in commit.parents if p in self.commits]
                if not valid_parents:
                    depth = 0
                else:
                    depth = max(get_depth(p, visited.copy()) for p in valid_parents) + 1
            memo_depth[c_hash] = depth
            return depth

        for c_hash in self.commits:
            get_depth(c_hash, set())

        # Sort commits primarily by topological depth, secondarily by timestamp
        sorted_hashes = sorted(
            self.commits.keys(),
            key=lambda h: (memo_depth.get(h, 0), self.commits[h].timestamp, h),
        )

        # Assign unique column index to each commit
        grid_x_map: Dict[str, int] = {}
        for col_idx, c_hash in enumerate(sorted_hashes):
            grid_x_map[c_hash] = col_idx

        return grid_x_map

    def _generate_track_geometry(
        self,
        from_st: SubwayStation,
        to_st: SubwayStation,
        line: SubwayLine,
        is_merge: bool,
        is_fork: bool,
    ) -> SubwayTrack:
        """
        Generates 45-degree and 90-degree octolinear schematic track geometry.
        """
        x1, y1 = from_st.x, from_st.y
        x2, y2 = to_st.x, to_st.y
        track_id = f"track-{from_st.short_hash}-{to_st.short_hash}"
        
        # Case 1: Straight horizontal track (same lane)
        if abs(y1 - y2) < 0.001:
            points = [Point(x=x1, y=y1), Point(x=x2, y=y2)]
            svg_path = f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"
            return SubwayTrack(
                id=track_id,
                from_station_id=from_st.id,
                to_station_id=to_st.id,
                line_id=line.id,
                line_color=line.color,
                points=points,
                svg_path=svg_path,
                is_merge=is_merge,
                is_fork=is_fork,
                is_trunk=(from_st.line_id == to_st.line_id and line.is_trunk),
            )

        # Case 2: Schematic 45-degree transit bend
        dy = y2 - y1
        diag = abs(dy)
        dx = x2 - x1
        lead = 24.0  # Horizontal lead segment before/after bend

        if dx >= diag + 2 * lead:
            if is_merge:
                # Approach destination at 45 degrees
                # [x1, y1] -> [x2 - diag - lead, y1] -> [x2 - lead, y2] -> [x2, y2]
                p0 = Point(x=x1, y=y1)
                p1 = Point(x=x2 - diag - lead, y=y1)
                p2 = Point(x=x2 - lead, y=y2)
                p3 = Point(x=x2, y=y2)
            else:
                # Fork from origin at 45 degrees
                # [x1, y1] -> [x1 + lead, y1] -> [x1 + lead + diag, y2] -> [x2, y2]
                p0 = Point(x=x1, y=y1)
                p1 = Point(x=x1 + lead, y=y1)
                p2 = Point(x=x1 + lead + diag, y=y2)
                p3 = Point(x=x2, y=y2)
            points = [p0, p1, p2, p3]
            svg_path = (
                f"M {p0.x:.1f} {p0.y:.1f} "
                f"L {p1.x:.1f} {p1.y:.1f} "
                f"L {p2.x:.1f} {p2.y:.1f} "
                f"L {p3.x:.1f} {p3.y:.1f}"
            )
        elif dx > 0:
            # 90-degree schematic dogleg when space is tight
            mid_x = (x1 + x2) / 2.0
            p0 = Point(x=x1, y=y1)
            p1 = Point(x=mid_x, y=y1)
            p2 = Point(x=mid_x, y=y2)
            p3 = Point(x=x2, y=y2)
            points = [p0, p1, p2, p3]
            svg_path = (
                f"M {p0.x:.1f} {p0.y:.1f} "
                f"L {p1.x:.1f} {p1.y:.1f} "
                f"L {p2.x:.1f} {p2.y:.1f} "
                f"L {p3.x:.1f} {p3.y:.1f}"
            )
        else:
            # Fallback for identical X or backwards edges
            points = [Point(x=x1, y=y1), Point(x=x2, y=y2)]
            svg_path = f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"

        return SubwayTrack(
            id=track_id,
            from_station_id=from_st.id,
            to_station_id=to_st.id,
            line_id=line.id,
            line_color=line.color,
            points=points,
            svg_path=svg_path,
            is_merge=is_merge,
            is_fork=is_fork,
            is_trunk=False,
        )

    def build_graph(self) -> SubwayGraph:
        """Executes full layout engine and returns SubwayGraph."""
        if not self.commits:
            # Empty graph
            bounds = SubwayBounds(min_x=0, max_x=800, min_y=0, max_y=400, width=800, height=400)
            return SubwayGraph(
                repo_name=self.repo.repo_name,
                repo_path=self.repo.repo_path,
                head_commit=self.repo.head_commit,
                active_branch=self.repo.active_branch,
                total_commits=0,
                total_lines=0,
                stations=[],
                tracks=[],
                lines=[],
                bounds=bounds,
                grid_step_x=self.step_x,
                grid_step_y=self.step_y,
            )

        # 1. Assign Lines and Lanes
        commit_to_line, lines_dict, line_lanes = self._assign_lines_and_lanes()

        # 2. Compute Topological Columns
        grid_x_map = self._compute_topological_columns()

        # 3. Create SubwayStation objects
        stations_map: Dict[str, SubwayStation] = {}
        for c_hash, raw in self.commits.items():
            line_id = commit_to_line[c_hash]
            line = lines_dict[line_id]
            grid_x = grid_x_map[c_hash]
            grid_y = line_lanes[line_id]
            
            px_x = self.margin_x + grid_x * self.step_x
            px_y = self.margin_y + grid_y * self.step_y
            
            is_interchange = len(raw.parents) > 1
            transfer_lines: List[str] = []
            if is_interchange:
                transfer_set = {line_id}
                for p_hash in raw.parents:
                    if p_hash in commit_to_line:
                        transfer_set.add(commit_to_line[p_hash])
                transfer_lines = sorted(list(transfer_set))

            st = SubwayStation(
                id=c_hash,
                short_hash=raw.short_hash,
                message=raw.message,
                author_name=raw.author_name,
                author_email=raw.author_email,
                timestamp=raw.timestamp,
                iso_time=raw.iso_time,
                grid_x=grid_x,
                grid_y=grid_y,
                x=px_x,
                y=px_y,
                line_id=line_id,
                line_name=line.name,
                line_color=line.color,
                is_interchange=is_interchange,
                transfer_lines=transfer_lines,
                parents=raw.parents,
                children=self.children.get(c_hash, []),
                branches=raw.branches,
                tags=raw.tags,
                is_head=raw.is_head,
                is_root=(len(raw.parents) == 0),
            )
            stations_map[c_hash] = st

        # 4. Generate Tracks between parents and children
        tracks: List[SubwayTrack] = []
        for c_hash, child_st in stations_map.items():
            for p_idx, p_hash in enumerate(child_st.parents):
                if p_hash not in stations_map:
                    continue
                parent_st = stations_map[p_hash]
                
                # Line assignment for track:
                # If parent and child share a line, use that line.
                # If child is interchange, incoming branch track uses parent's line.
                # If parent forked into child, track uses child's line.
                is_merge = (child_st.is_interchange and p_idx > 0)
                is_fork = (parent_st.line_id != child_st.line_id and not is_merge)
                
                track_line_id = parent_st.line_id if is_merge else child_st.line_id
                track_line = lines_dict.get(track_line_id, lines_dict[child_st.line_id])
                
                track = self._generate_track_geometry(
                    from_st=parent_st,
                    to_st=child_st,
                    line=track_line,
                    is_merge=is_merge,
                    is_fork=is_fork,
                )
                tracks.append(track)

        # 5. Compute Bounding Box
        all_x = [s.x for s in stations_map.values()]
        all_y = [s.y for s in stations_map.values()]
        min_x = min(all_x) if all_x else 0.0
        max_x = max(all_x) if all_x else 800.0
        min_y = min(all_y) if all_y else 0.0
        max_y = max(all_y) if all_y else 400.0
        
        bounds = SubwayBounds(
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            width=max((max_x - min_x) + self.margin_x * 2, 800.0),
            height=max((max_y - min_y) + self.margin_y * 2, 400.0),
        )

        # Sort stations by grid_x for natural traversal
        sorted_stations = sorted(stations_map.values(), key=lambda s: (s.grid_x, s.grid_y))

        return SubwayGraph(
            repo_name=self.repo.repo_name,
            repo_path=self.repo.repo_path,
            head_commit=self.repo.head_commit,
            active_branch=self.repo.active_branch,
            total_commits=len(sorted_stations),
            total_lines=len(lines_dict),
            stations=sorted_stations,
            tracks=tracks,
            lines=list(lines_dict.values()),
            bounds=bounds,
            grid_step_x=self.step_x,
            grid_step_y=self.step_y,
        )
