"""
Sample Git repository generator for testing and demonstration.
Constructs a multi-branch Git DAG with forks, merges, and tags using Dulwich.
"""

import os
import shutil
import time
from dulwich import porcelain
from dulwich.objects import Commit


def create_demo_repository(target_path: str) -> str:
    """
    Initializes a sample git repository with rich branch history.
    Overwrites if target_path already exists or uses existing.
    """
    target_path = os.path.abspath(target_path)
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
        
    os.makedirs(target_path, exist_ok=True)
    repo = porcelain.init(target_path)
    
    base_time = int(time.time()) - 86400 * 14  # 14 days ago
    
    def commit_file(filename: str, content: str, msg: str, author: str, ts_offset: int):
        fpath = os.path.join(target_path, filename)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        porcelain.add(repo, filename)
        ts = base_time + ts_offset
        author_bytes = author.encode("utf-8")
        
        # Low-level commit to set exact timestamp and author
        index = repo.open_index()
        tree_id = index.commit(repo.object_store)
        
        c = Commit()
        c.tree = tree_id
        try:
            head_ref = repo.head()
            c.parents = [head_ref]
        except KeyError:
            c.parents = []
            
        c.author = author_bytes
        c.committer = author_bytes
        c.author_time = ts
        c.commit_time = ts
        c.author_timezone = 0
        c.commit_timezone = 0
        c.message = msg.encode("utf-8")
        
        repo.object_store.add_object(c)
        
        # Update current branch ref
        curr_ref = repo.refs.follow(b"HEAD")[0][1]
        repo.refs[curr_ref] = c.id
        return c.id

    # 1. Main trunk initial commits
    c1 = commit_file("README.md", "# Git Subway Map\nInteractive visualizer", "Initial commit: scaffold project", "Linus <linus@transit.dev>", 0)
    c2 = commit_file("setup.py", "from setuptools import setup\nsetup(name='subway')", "Add build configuration and package setup", "Ada Lovelace <ada@transit.dev>", 3600 * 6)
    porcelain.tag_create(repo, b"v0.1.0", objectish=c1)

    # 2. Branch feature/auth
    porcelain.branch_create(repo, b"feature/auth")
    repo.refs.set_symbolic_ref(b"HEAD", b"refs/heads/feature/auth")
    c3 = commit_file("auth.py", "def login(user, pw):\n    return True\n", "Implement OAuth2 token authentication", "Grace Hopper <grace@transit.dev>", 3600 * 18)
    c4 = commit_file("jwt.py", "def decode_token():\n    pass\n", "Add JWT payload encryption & validation", "Grace Hopper <grace@transit.dev>", 3600 * 30)

    # 3. Branch bugfix/token-expiry off feature/auth
    porcelain.branch_create(repo, b"bugfix/token-expiry")
    repo.refs.set_symbolic_ref(b"HEAD", b"refs/heads/bugfix/token-expiry")
    c5 = commit_file("jwt.py", "def decode_token():\n    # check expiration\n    pass\n", "Fix token clock skew expiration bug", "Alan Turing <alan@transit.dev>", 3600 * 42)

    # 4. Continue main trunk
    repo.refs.set_symbolic_ref(b"HEAD", b"refs/heads/master")
    c6 = commit_file("router.py", "class Router:\n    pass\n", "Add high-speed HTTP request router", "Margaret Hamilton <margaret@transit.dev>", 3600 * 50)

    # 5. Merge bugfix into feature/auth
    repo.refs.set_symbolic_ref(b"HEAD", b"refs/heads/feature/auth")
    # Low-level merge commit
    tree = repo[c5].tree
    merge1 = Commit()
    merge1.tree = tree
    merge1.parents = [c4, c5]
    merge1.author = b"Grace Hopper <grace@transit.dev>"
    merge1.committer = b"Grace Hopper <grace@transit.dev>"
    merge1.author_time = base_time + 3600 * 58
    merge1.commit_time = base_time + 3600 * 58
    merge1.author_timezone = 0
    merge1.commit_timezone = 0
    merge1.message = b"Merge branch 'bugfix/token-expiry' into feature/auth"
    repo.object_store.add_object(merge1)
    repo.refs[b"refs/heads/feature/auth"] = merge1.id

    # 6. Merge feature/auth into master (Interchange Transfer Station)
    repo.refs.set_symbolic_ref(b"HEAD", b"refs/heads/master")
    tree2 = repo[c6].tree
    merge2 = Commit()
    merge2.tree = tree2
    merge2.parents = [c6, merge1.id]
    merge2.author = b"Linus <linus@transit.dev>"
    merge2.committer = b"Linus <linus@transit.dev>"
    merge2.author_time = base_time + 3600 * 70
    merge2.commit_time = base_time + 3600 * 70
    merge2.author_timezone = 0
    merge2.commit_timezone = 0
    merge2.message = b"Merge pull request #1 from feature/auth: Full transit auth module"
    repo.object_store.add_object(merge2)
    repo.refs[b"refs/heads/master"] = merge2.id

    # 7. Release branch
    porcelain.branch_create(repo, b"release/v1.0")
    repo.refs.set_symbolic_ref(b"HEAD", b"refs/heads/release/v1.0")
    c7 = commit_file("version.py", "__version__ = '1.0.0'\n", "Bump version to 1.0.0 for general release", "Ada Lovelace <ada@transit.dev>", 3600 * 82)
    porcelain.tag_create(repo, b"v1.0.0", objectish=c7)

    # 8. Master post-release commit
    repo.refs.set_symbolic_ref(b"HEAD", b"refs/heads/master")
    c8 = commit_file("docs.md", "# Release notes 1.0\nReady for production deployment", "Docs: Publish Subway Map release notes", "Margaret Hamilton <margaret@transit.dev>", 3600 * 95)

    return target_path


if __name__ == "__main__":
    import sys
    dest = sys.argv[1] if len(sys.argv) > 1 else "/tmp/git-subway-demo"
    path = create_demo_repository(dest)
    print(f"Created demo repository at {path}")
