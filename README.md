<div align="center">

# 🚇 Git Subway Map

**Turn your messy Git commit tree into a gorgeous Tokyo / London Underground schematic subway transit map.**

[![CI Workflow](https://img.shields.io/github/actions/workflow/status/vedantojha2612-cyber/git-subway-map/ci.yml?branch=main&style=flat-square&logo=githubactions&logoColor=white&label=CI)](https://github.com/vedantojha2612-cyber/git-subway-map/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 19 & Vite](https://img.shields.io/badge/Frontend-React%2019%20%2F%20Vite-61DAFB?style=flat-square&logo=react&logoColor=black)](https://vitejs.dev)
[![Topology Engine](https://img.shields.io/badge/Topology-Octolinear%2045%C2%B0%2F90%C2%B0-E1140A?style=flat-square)](https://github.com/vedantojha2612-cyber/git-subway-map)

<br/>

```text
  ○====●====================◎====================●====> [main / Yamanote Line]
        \                  / \                  /
         \--○------------○/   \--●------------○/        [feature/auth / Ginza Line]
             \          /
              \--●----○/                                [bugfix/cors / Marunouchi Line]
```

*Commits become stations. Branches become color-coded transit lines. Merge commits become multi-track interchange transfer hubs.*

[Quickstart](#-quickstart) • [Feature Matrix](#-feature-matrix) • [Architecture](#-architecture) • [CLI Reference](#-cli-reference) • [API Docs](#-rest-api-endpoints)

</div>

---

## ⚡ What is Git Subway Map?

Standard git log graphs (`git log --graph --oneline`) are dense, jagged, and hard to decipher once a project grows beyond a handful of branches. 

**Git Subway Map** parses your repository's raw commit Directed Acyclic Graph (DAG) and reformulates it through an **octolinear transit layout engine** inspired by Harry Beck’s iconic 1931 London Underground map and the Tokyo Metro network:

- **Horizontal Trunk Lines**: Primary branches run along strict horizontal tracks.
- **Strict 45° and 90° Routing**: Branch splits and merges glide along clean 45-degree diagonal transitions with dual-stroke ballast rails.
- **Interchange Concourse Hubs**: Merge commits are styled as multi-ring transit interchange stations showing parent connections.
- **Zero Configuration**: A single command runs the backend and immediately launches an interactive SVG canvas in your web browser.

---

## 🚀 Quickstart

### 1. Installation

Clone the repository and install the minimal backend dependencies:

```bash
git clone https://github.com/vedantojha2612-cyber/git-subway-map.git
cd git-subway-map

# Install Python requirements (FastAPI, Uvicorn, Pydantic, Dulwich)
pip install -r backend/requirements.txt
```

> **Note**: No Node.js build step is required for end users. The production-optimized React/Vite single-page application is pre-compiled in `frontend/dist/`.

### 2. Launch the Visualizer

Launch with the unified single-command runner:

```bash
# 1. Visualize current repository (or synthetic multi-branch demo if not in a Git repo)
python run.py

# 2. Visualize a specific local Git repository
python run.py --repo /path/to/my-repo

# 3. Custom port without auto-launching web browser
python run.py --port 8080 --no-browser
```

Your browser will automatically open to `http://localhost:8000`.

---

## 🎛️ Feature Matrix

| Capability | Standard Git Graph (`git log --graph`) | Git Subway Map |
| :--- | :---: | :---: |
| **Visual Philosophy** | Monospaced ASCII lines | Schematic Tokyo / London Underground board |
| **Track Geometry** | Jagged arbitrary angles | Pure octolinear (horizontal + 45° / 90° fillets) |
| **Branch Identification** | Plain text ref labels | Distinct color-coded transit routes with badges |
| **Interchange Terminus** | Asterisk points | Concentric station rings & transfer concourses |
| **Navigation & Canvas** | Vertical terminal scroll | Infinite pan, smooth cursor zoom (15%–450%), minimap radar |
| **Station Inspection** | Static terminal output | Dossier drawer with 1-click SHA copy, author avatars & lineage |
| **Search & Filtering** | Shell `grep` | Real-time interactive commit message & author filter |
| **Git Engine Dependency** | Requires system `git` CLI | Standalone pure-Python DAG parser via **Dulwich** |

---

## 🗺️ Interactive Transit Map Controls

- **Pan & Zoom Canvas**: Click and drag anywhere on the obsidian map board to pan. Use your mouse scroll wheel or trackpad pinch to zoom smoothly with cursor anchoring.
- **Station Telemetry Drawer**: Click any station circle to open the sliding station dossier with full commit SHA, commit author, timestamp, branch tags, and direct jump links to parent/child stations.
- **Line Filter / Route Isolation**: Click any metro line in the bottom transit legend to isolate that specific route and dim background tracks.
- **Transit Radar Minimap**: A live picture-in-picture minimap in the lower right corner displays the entire topological network with an interactive viewport indicator. Click anywhere on the minimap to jump the camera instantly.
- **Instant Search**: Press `/` or click the search bar to locate commits by hash, commit message, author name, or branch ref.
- **Keyboard Shortcuts**:
  - `F`: Fit entire subway network to current screen.
  - `0`: Reset zoom and pan to 100% origin.
  - `+` / `-`: Zoom in / Zoom out.
  - `Esc`: Close open drawers and modals.
  - `?`: Toggle keyboard shortcuts overlay.

---

## 🏗️ Architecture & Data Pipeline

Git Subway Map is designed as a decoupled, high-performance system:

```text
┌────────────────────────┐
│   Target Git Repo      │ (Local working directory or --repo target)
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│    Dulwich Git DAG     │ backend/parser.py
│     Commit Parser      │ Extracts commits, parent links, branches, and tags
└───────────┬────────────┘
            │ CommitDAG (Topological Order)
            ▼
┌────────────────────────┐
│ Subway Topology Engine │ backend/layout.py
│  (Octolinear Routing)  │ Assigns track lanes, calculates 45°/90° curves & hubs
└───────────┬────────────┘
            │ SubwayGraph (Stations, Tracks, Lines, Bounds)
            ▼
┌────────────────────────┐
│  FastAPI REST Server   │ backend/main.py & backend/cli.py
│   & SPA Asset Server   │ Serves /api endpoints, Swagger docs, and frontend bundle
└───────────┬────────────┘
            │ JSON via HTTP & Static Bundles
            ▼
┌────────────────────────┐
│  React 19 Canvas SPA   │ frontend/src/components/SubwayCanvas.jsx
│ (Interactive SVG Map)  │ Dual-stroke SVG tracks, interactive stations, minimap
└────────────────────────┘
```

### Component Breakdown

1. **Git DAG Parser (`backend/parser.py`)**:
   Uses Dulwich to read the object database directly. Builds an in-memory topological commit graph including parent hashes, commit messages, authors, dates, and ref pointers (HEAD, branch heads, tags).
2. **Subway Layout Topology Engine (`backend/layout.py`)**:
   - Assigns branch commits to designated horizontal transit lanes ($Y$-spacing: $90\text{px}$, $X$-spacing: $140\text{px}$).
   - Discovers interchange points where branches diverge or merge into parent trunks.
   - Generates SVG path commands with smooth 45° diagonal octolinear arcs (`M ... L ... Q ...`).
3. **FastAPI Application (`backend/main.py`)**:
   - REST endpoints for graphs, lines, and stations.
   - Clean static mounting of the React SPA (`frontend/dist`) with client-side routing fallback.
4. **Retro Metro Map UI (`frontend/`)**:
   - React 19 + Vite canvas rendering high-DPI SVG tracks.
   - Tokyo Metro and London Underground color palette (Marunouchi Red, Ginza Orange, Yamanote Green, Tozai Sky Blue, Hanzomon Purple, Chiyoda Emerald).

---

## 💻 CLI Reference

```text
usage: git-subway-map [-h] [--repo REPO] [--port PORT] [--host HOST]
                      [--no-browser]
                      [--log-level {critical,error,warning,info,debug,trace}]

Git Subway Map - Schematic Transit Timeline Visualizer

options:
  -h, --help            Show this help message and exit
  --repo REPO           Path to Git repository to visualize (defaults to
                        current working directory if in a Git repo, or demo-repo if not)
  --port PORT           Port number to bind to (default: 8000)
  --host HOST           Host address to bind to (default: 127.0.0.1)
  --no-browser          Do not auto-launch the web browser on startup (default: False)
  --log-level LEVEL     Uvicorn server log level (default: info)
```

---

## 🔌 REST API Endpoints

The FastAPI server provides automated Swagger / OpenAPI documentation available at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the interactive React subway map SPA |
| `GET` | `/api/health` | Health status and server timestamp |
| `GET` | `/api/subway-graph` | Full schematic graph payload: stations, lines, tracks, and map bounds |
| `GET` | `/api/lines` | List of transit lines with assigned metro colors and branch names |
| `GET` | `/api/stations` | List of all commit stations with coordinate telemetry |
| `POST` | `/api/demo/reset` | Resets and regenerates the synthetic multi-branch demo repository |
| `GET` | `/docs` | Interactive Swagger / OpenAPI documentation |

---

## 🧪 Testing

The test suite covers API routing, SPA fallback handling, CLI argument resolution, and layout topology calculations.

Run the test suite via `unittest`:

```bash
python3 -m unittest discover -s backend -p "test_*.py" -v
```

All 12 unit and integration tests execute in under 0.5s with zero external mock servers.

---

## 📦 PyPI & Packaging

Git Subway Map is packaged using modern `pyproject.toml` standards (PEP 517/518/621).

To build the source distribution and wheel locally:

```bash
pip install build
python -m build
```

Once installed, the CLI command is available globally:

```bash
git-subway-map --repo /path/to/my-repo
```

---

## 🛠️ Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository and create your branch: `git checkout -b feature/my-new-feature`.
2. Ensure backend tests pass: `python3 -m unittest discover -s backend -p "test_*.py"`.
3. If modifying frontend components, run linter and build:
   ```bash
   cd frontend
   npm run lint
   npm run build
   ```
4. Commit your changes with descriptive messages and open a Pull Request.

---

## 🗺️ Roadmap

- [x] Dulwich-powered Git commit DAG parser
- [x] Octolinear 45°/90° path layout engine
- [x] Retro Tokyo & London Underground dark theme
- [x] Station telemetry dossier drawer & 1-click SHA copy
- [x] Picture-in-picture minimap radar
- [x] Zero-config single-command CLI launcher
- [ ] Export map as high-resolution PNG / SVG poster
- [ ] Time-lapse replay animation of repository commit evolution
- [ ] Git tag milestone landmark badges (e.g. Major Terminal Hubs)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) © 2026 Git Subway Map Contributors.
