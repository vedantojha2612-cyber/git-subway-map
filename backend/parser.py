"""
Git DAG Parser for Git Subway Map.
Extracts commits, parents, branches, tags, and HEAD information from a local Git repository.
Supports pure-Python Dulwich and optional CLI fallback.
"""

import os
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class RawCommit:
    hash: str
    short_hash: str
    parents: List[str]
    author_name: str
    author_email: str
    timestamp: int
    iso_time: str
    message: str
    branches: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_head: bool = False


@dataclass
class ParsedRepo:
    repo_name: str
    repo_path: str
    head_commit: Optional[str]
    active_branch: Optional[str]
    commits: Dict[str, RawCommit]
    branches: Dict[str, str]  # branch_name -> commit_hash
    tags: Dict[str, str]      # tag_name -> commit_hash


def _parse_git_iso(timestamp: int) -> str:
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def read_repo_dulwich(repo_path: str) -> ParsedRepo:
    from dulwich.repo import Repo
    from dulwich.errors import NotGitRepository
    
    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"Path does not exist: {repo_path}")
    
    try:
        repo = Repo(repo_path)
    except NotGitRepository:
        raise ValueError(f"Not a valid git repository: {repo_path}")
    
    repo_name = os.path.basename(os.path.abspath(repo_path))
    
    # 1. Resolve HEAD and active branch
    head_commit: Optional[str] = None
    active_branch: Optional[str] = None
    
    try:
        head_ref = repo.refs.read_ref(b"HEAD")
        if head_ref:
            if repo.refs.is_symbolic(b"HEAD"):
                sym = repo.refs.read_symbolic_ref(b"HEAD")
                if sym:
                    sym_str = sym.decode("utf-8", errors="replace")
                    if sym_str.startswith("refs/heads/"):
                        active_branch = sym_str[len("refs/heads/"):]
                    else:
                        active_branch = sym_str
            head_commit = repo.head().decode("ascii")
    except Exception:
        pass

    # 2. Extract branches and tags
    branches: Dict[str, str] = {}
    tags: Dict[str, str] = {}
    commit_branches: Dict[str, List[str]] = {}
    commit_tags: Dict[str, List[str]] = {}
    
    ref_dict = repo.get_refs()
    all_target_hashes: Set[bytes] = set()
    
    for ref_bytes, target_bytes in ref_dict.items():
        ref_str = ref_bytes.decode("utf-8", errors="replace")
        target_hash = target_bytes.decode("ascii")
        
        # Dereference annotated tags if necessary
        try:
            obj = repo[target_bytes]
            if obj.type_name == b"tag":
                target_hash = obj.object[1].decode("ascii")
                target_bytes = obj.object[1]
        except Exception:
            pass
        
        if ref_str.startswith("refs/heads/"):
            b_name = ref_str[len("refs/heads/"):]
            branches[b_name] = target_hash
            commit_branches.setdefault(target_hash, []).append(b_name)
            all_target_hashes.add(target_bytes)
        elif ref_str.startswith("refs/tags/"):
            t_name = ref_str[len("refs/tags/"):]
            tags[t_name] = target_hash
            commit_tags.setdefault(target_hash, []).append(t_name)
            all_target_hashes.add(target_bytes)
        elif ref_str.startswith("refs/remotes/"):
            r_name = ref_str[len("refs/remotes/"):]
            if not r_name.endswith("/HEAD"):
                branches[r_name] = target_hash
                commit_branches.setdefault(target_hash, []).append(r_name)
                all_target_hashes.add(target_bytes)

    if head_commit and head_commit.encode("ascii") not in all_target_hashes:
        all_target_hashes.add(head_commit.encode("ascii"))
        
    # If no refs found, try head
    if not all_target_hashes and head_commit:
        all_target_hashes.add(head_commit.encode("ascii"))

    # 3. Walk all commits topologically
    commits: Dict[str, RawCommit] = {}
    if all_target_hashes:
        try:
            walker = repo.get_walker(include=list(all_target_hashes), order="topo")
            for entry in walker:
                commit = entry.commit
                c_hash = commit.id.decode("ascii")
                parents = [p.decode("ascii") for p in commit.parents]
                
                # Parse author
                author_str = commit.author.decode("utf-8", errors="replace")
                if "<" in author_str and ">" in author_str:
                    a_name = author_str.split("<")[0].strip()
                    a_email = author_str.split("<")[1].split(">")[0].strip()
                else:
                    a_name = author_str
                    a_email = ""
                
                ts = int(commit.commit_time or commit.author_time or 0)
                msg = commit.message.decode("utf-8", errors="replace").strip().split("\n")[0]
                
                is_head = (c_hash == head_commit)
                b_list = commit_branches.get(c_hash, [])
                t_list = commit_tags.get(c_hash, [])
                
                commits[c_hash] = RawCommit(
                    hash=c_hash,
                    short_hash=c_hash[:7],
                    parents=parents,
                    author_name=a_name or "Anonymous",
                    author_email=a_email,
                    timestamp=ts,
                    iso_time=_parse_git_iso(ts),
                    message=msg or "No commit message",
                    branches=b_list,
                    tags=t_list,
                    is_head=is_head,
                )
        except Exception as e:
            # Fallback if walker fails
            print(f"Dulwich walker warning: {e}")

    return ParsedRepo(
        repo_name=repo_name,
        repo_path=os.path.abspath(repo_path),
        head_commit=head_commit,
        active_branch=active_branch,
        commits=commits,
        branches=branches,
        tags=tags,
    )


def read_repo_cli(repo_path: str) -> Optional[ParsedRepo]:
    """Fallback using git CLI if git is installed."""
    try:
        proc = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.returncode != 0:
            return None
    except Exception:
        return None

    repo_name = os.path.basename(os.path.abspath(repo_path))
    
    # Get HEAD and branch
    head_proc = subprocess.run(
        ["git", "-C", repo_path, "rev-parse", "HEAD"],
        capture_output=True, text=True
    )
    head_commit = head_proc.stdout.strip() if head_proc.returncode == 0 else None
    
    branch_proc = subprocess.run(
        ["git", "-C", repo_path, "branch", "--show-current"],
        capture_output=True, text=True
    )
    active_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 and branch_proc.stdout.strip() else None

    # Get log
    # %H = commit hash, %P = parent hashes, %an = author name, %ae = email, %at = timestamp, %s = subject, %D = ref names
    fmt = "%H|%P|%an|%ae|%at|%s|%D"
    log_proc = subprocess.run(
        ["git", "-C", repo_path, "log", "--all", "--date-order", f"--pretty=format:{fmt}"],
        capture_output=True, text=True
    )
    if log_proc.returncode != 0:
        return None

    commits: Dict[str, RawCommit] = {}
    branches: Dict[str, str] = {}
    tags: Dict[str, str] = {}

    for line in log_proc.stdout.splitlines():
        parts = line.split("|")
        if len(parts) < 7:
            continue
        c_hash, p_str, an, ae, at, msg, refs_str = (
            parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
        )
        parents = [p for p in p_str.split() if p]
        ts = int(at) if at.isdigit() else 0
        b_list = []
        t_list = []
        
        for ref_item in [r.strip() for r in refs_str.split(",") if r.strip()]:
            if ref_item.startswith("tag: "):
                tag_name = ref_item[5:]
                t_list.append(tag_name)
                tags[tag_name] = c_hash
            elif ref_item.startswith("HEAD -> "):
                b_name = ref_item[8:]
                b_list.append(b_name)
                branches[b_name] = c_hash
            elif ref_item != "HEAD":
                b_list.append(ref_item)
                branches[ref_item] = c_hash

        commits[c_hash] = RawCommit(
            hash=c_hash,
            short_hash=c_hash[:7],
            parents=parents,
            author_name=an or "Anonymous",
            author_email=ae,
            timestamp=ts,
            iso_time=_parse_git_iso(ts),
            message=msg or "No commit message",
            branches=b_list,
            tags=t_list,
            is_head=(c_hash == head_commit),
        )

    return ParsedRepo(
        repo_name=repo_name,
        repo_path=os.path.abspath(repo_path),
        head_commit=head_commit,
        active_branch=active_branch,
        commits=commits,
        branches=branches,
        tags=tags,
    )


def parse_git_repository(repo_path: str) -> ParsedRepo:
    """Parses a Git repository, trying Dulwich first and falling back to git CLI."""
    try:
        return read_repo_dulwich(repo_path)
    except Exception as e_dulwich:
        cli_result = read_repo_cli(repo_path)
        if cli_result is not None:
            return cli_result
        raise e_dulwich
