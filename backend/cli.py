"""
Unified CLI Entry Point for Git Subway Map.
Serves the FastAPI backend with embedded frontend SPA and auto-launches the browser.
"""

import argparse
import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from typing import Optional

# Ensure project root and backend are in sys.path
CLI_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CLI_DIR, ".."))
if CLI_DIR not in sys.path:
    sys.path.insert(0, CLI_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn
from main import app
from demo_repo import create_demo_repository


def is_git_repo(path: str) -> bool:
    """Checks if a directory is a valid Git repository."""
    if not os.path.isdir(path):
        return False
    git_dir = os.path.join(path, ".git")
    if os.path.exists(git_dir):
        return True
    try:
        from dulwich.repo import Repo
        Repo(path)
        return True
    except Exception:
        pass
    try:
        import subprocess
        res = subprocess.run(
            ["git", "-C", path, "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2,
        )
        return res.returncode == 0
    except Exception:
        return False


def resolve_repo_path(repo_arg: Optional[str], project_root: str) -> str:
    """
    Resolves repository path based on CLI argument or defaults.
    Defaults to current working directory if in a Git repo, or demo-repo if not.
    """
    if repo_arg and repo_arg.strip():
        resolved = os.path.abspath(repo_arg.strip())
        if not os.path.exists(resolved):
            raise FileNotFoundError(f"Specified repository does not exist: {resolved}")
        return resolved

    # Defaults to current working directory if it's a git repo
    cwd = os.getcwd()
    if is_git_repo(cwd):
        return os.path.abspath(cwd)

    # Otherwise fallback to demo-repo
    demo_dir = os.path.abspath(os.path.join(project_root, "demo-repo"))
    if not os.path.exists(demo_dir) or not os.path.exists(os.path.join(demo_dir, ".git")):
        create_demo_repository(demo_dir)
    return demo_dir


def check_port_in_use(host: str, port: int) -> bool:
    """Checks if a host/port combination is already bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True


def open_browser_when_ready(url: str, host: str, port: int, timeout_sec: float = 12.0):
    """Polls health check until server is ready, then opens browser."""
    check_host = "127.0.0.1" if host in ("0.0.0.0", "::", "") else host
    health_url = f"http://{check_host}:{port}/api/health"
    start_time = time.time()

    while time.time() - start_time < timeout_sec:
        try:
            req = urllib.request.Request(
                health_url,
                headers={"User-Agent": "GitSubwayMapLauncher/1.0"},
            )
            with urllib.request.urlopen(req, timeout=0.5) as resp:
                if resp.status == 200:
                    break
        except Exception:
            time.sleep(0.15)

    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[*] Note: Could not auto-launch browser ({e}). Please open {url} manually.")


def parse_args(argv=None) -> argparse.Namespace:
    """Configures and parses CLI command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="git-subway-map",
        description="Git Subway Map - Schematic Transit Timeline Visualizer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=None,
        help="Path to Git repository to visualize (defaults to current working directory if in a Git repo, or demo-repo if not)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number to bind to",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind to",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        default=False,
        help="Do not auto-launch the web browser on startup",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Uvicorn server log level",
    )
    return parser.parse_args(argv)


def run(argv=None):
    """Main CLI runner function."""
    args = parse_args(argv)

    # Resolve target Git repository
    try:
        target_repo = resolve_repo_path(args.repo, PROJECT_ROOT)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Set environment variable so backend routes pick up the default repo
    os.environ["GIT_SUBWAY_REPO"] = target_repo

    # Check port conflicts with automatic fallback to next available port
    active_port = args.port
    if check_port_in_use(args.host, active_port):
        raw_args = argv if argv is not None else sys.argv[1:]
        port_explicitly_set = any(a == "--port" or a.startswith("--port=") for a in raw_args)

        if not port_explicitly_set:
            orig_port = active_port
            candidate = orig_port + 1
            while candidate < orig_port + 50 and check_port_in_use(args.host, candidate):
                candidate += 1
            if not check_port_in_use(args.host, candidate):
                active_port = candidate
                print(f"[*] Notice: Port {orig_port} is already in use. Automatically switched to port {active_port}.\n")
            else:
                print(
                    f"Error: Port {orig_port} and subsequent ports are already in use on {args.host}.\n"
                    f"Please specify an alternate port with --port (e.g. python run.py --port 8080).",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
            print(
                f"Error: Port {active_port} is already in use on {args.host}.\n"
                f"Please specify an alternate port with --port (e.g. python run.py --port {active_port + 1}).",
                file=sys.stderr,
            )
            sys.exit(1)

    display_host = "localhost" if args.host in ("127.0.0.1", "0.0.0.0") else args.host
    browser_url = f"http://{display_host}:{active_port}"

    print("=" * 64)
    print("  GIT SUBWAY MAP | SCHEMATIC TRANSIT TIMELINE")
    print("=" * 64)
    print(f"  Target Repository   : {target_repo}")
    print(f"  Web Interface       : {browser_url}")
    print(f"  API Documentation   : {browser_url}/docs")
    print(f"  Browser Auto-Launch : {'Disabled (--no-browser)' if args.no_browser else 'Enabled'}")
    print("=" * 64)
    print("Starting server... Press Ctrl+C to stop.\n")

    if not args.no_browser:
        browser_thread = threading.Thread(
            target=open_browser_when_ready,
            args=(browser_url, args.host, active_port),
            daemon=True,
        )
        browser_thread.start()

    config = uvicorn.Config(
        app=app,
        host=args.host,
        port=active_port,
        log_level=args.log_level,
    )
    server = uvicorn.Server(config)

    try:
        server.run()
    except KeyboardInterrupt:
        print("\nShutting down Git Subway Map...")
        sys.exit(0)


if __name__ == "__main__":
    run()
