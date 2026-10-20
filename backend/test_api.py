"""
Automated test suite for Git Subway Map backend and CLI launcher.
Tests DAG parsing, subway layout calculation, interchange marking,
FastAPI endpoints, static SPA mounting, SPA fallback routing, and CLI utilities.
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from main import app, generate_subway_graph, STATIC_DIR
from demo_repo import create_demo_repository
from parser import parse_git_repository
from layout import SubwayLayoutEngine
from cli import parse_args, resolve_repo_path, is_git_repo


class TestGitSubwayMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_root = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
        cls.demo_dir = os.path.join(cls.project_root, "test-repo")
        create_demo_repository(cls.demo_dir)
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        """Health check returns status ok and service name."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "git-subway-map")

    def test_parser_extracts_all_refs_and_commits(self):
        """Git DAG parser extracts commits, branches, and tags."""
        parsed = parse_git_repository(self.demo_dir)
        self.assertGreaterEqual(len(parsed.commits), 10)
        self.assertIn("master", parsed.branches)
        self.assertIn("feature/auth", parsed.branches)
        self.assertIn("v1.0.0", parsed.tags)

    def test_layout_engine_topology(self):
        """Subway layout engine computes stations, tracks, and interchanges."""
        parsed = parse_git_repository(self.demo_dir)
        engine = SubwayLayoutEngine(parsed)
        graph = engine.build_graph()

        # Verify station count matches commit count
        self.assertEqual(len(graph.stations), len(parsed.commits))
        
        # Verify trunk line exists
        trunk_lines = [l for l in graph.lines if l.is_trunk]
        self.assertGreaterEqual(len(trunk_lines), 1)

        # Verify interchange stations exist for merges
        interchanges = [s for s in graph.stations if s.is_interchange]
        self.assertGreaterEqual(len(interchanges), 1)
        for interchange in interchanges:
            self.assertGreaterEqual(len(interchange.parents), 2)
            self.assertGreaterEqual(len(interchange.transfer_lines), 1)

        # Verify track geometry contains valid SVG paths
        for track in graph.tracks:
            self.assertTrue(track.svg_path.startswith("M "))
            self.assertIn("L ", track.svg_path)
            self.assertGreaterEqual(len(track.points), 2)

    def test_subway_graph_api_endpoint(self):
        """API endpoint /api/subway-graph returns complete valid graph JSON."""
        res = self.client.get(f"/api/subway-graph?repo_path={self.demo_dir}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["repo_name"], "test-repo")
        self.assertGreater(data["total_commits"], 0)
        self.assertGreater(data["total_lines"], 0)
        self.assertIn("bounds", data)
        self.assertGreater(data["bounds"]["width"], 0)
        self.assertIsInstance(data["stations"], list)
        self.assertIsInstance(data["lines"], list)
        self.assertIsInstance(data["tracks"], list)

    def test_lines_and_stations_endpoints(self):
        """API endpoints /api/lines and /api/stations return list structures."""
        res_lines = self.client.get(f"/api/lines?repo_path={self.demo_dir}")
        self.assertEqual(res_lines.status_code, 200)
        self.assertIsInstance(res_lines.json(), list)

        res_stations = self.client.get(f"/api/stations?repo_path={self.demo_dir}")
        self.assertEqual(res_stations.status_code, 200)
        self.assertIsInstance(res_stations.json(), list)

    def test_root_serves_frontend_html(self):
        """Root GET / cleanly serves index.html with 200 OK and text/html."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("<div id=\"root\">", res.text)
        self.assertIn("Git Subway Map", res.text)

    def test_static_assets_serve_correctly(self):
        """Mounted /assets serves built JavaScript and CSS bundles."""
        res_js = self.client.get("/assets/index-C3WlD3-2.js")
        self.assertEqual(res_js.status_code, 200)
        self.assertTrue(
            "javascript" in res_js.headers.get("content-type", "") or
            "application/octet-stream" in res_js.headers.get("content-type", "")
        )

        res_css = self.client.get("/assets/index-DBbwAuXo.css")
        self.assertEqual(res_css.status_code, 200)
        self.assertIn("css", res_css.headers.get("content-type", ""))

    def test_static_root_files_serve(self):
        """Frontend root assets like favicon.svg and icons.svg are served."""
        res_fav = self.client.get("/favicon.svg")
        self.assertEqual(res_fav.status_code, 200)

        res_icons = self.client.get("/icons.svg")
        self.assertEqual(res_icons.status_code, 200)

    def test_spa_fallback_routing(self):
        """Non-API routes fallback to index.html for client-side SPA routing."""
        res_spa = self.client.get("/view/master")
        self.assertEqual(res_spa.status_code, 200)
        self.assertIn("text/html", res_spa.headers.get("content-type", ""))
        self.assertIn("<div id=\"root\">", res_spa.text)

    def test_api_404_not_masked_by_spa(self):
        """Unknown /api routes return 404 JSON, NOT HTML fallback."""
        res = self.client.get("/api/unknown-endpoint")
        self.assertEqual(res.status_code, 404)
        self.assertIn("application/json", res.headers.get("content-type", ""))
        self.assertIn("API endpoint not found", res.json()["detail"])

    def test_cli_argument_parsing(self):
        """CLI argument parser correctly handles all options and defaults."""
        args_default = parse_args([])
        self.assertIsNone(args_default.repo)
        self.assertEqual(args_default.port, 8000)
        self.assertEqual(args_default.host, "127.0.0.1")
        self.assertFalse(args_default.no_browser)

        args_custom = parse_args([
            "--repo", "/tmp/my-repo",
            "--port", "8005",
            "--host", "0.0.0.0",
            "--no-browser",
        ])
        self.assertEqual(args_custom.repo, "/tmp/my-repo")
        self.assertEqual(args_custom.port, 8005)
        self.assertEqual(args_custom.host, "0.0.0.0")
        self.assertTrue(args_custom.no_browser)

    def test_cli_repo_resolution(self):
        """CLI correctly resolves custom repo, git repo, or fallback demo repo."""
        # Custom repo resolution
        custom_res = resolve_repo_path(self.demo_dir, self.project_root)
        self.assertEqual(custom_res, self.demo_dir)

        # Non-existent custom repo raises FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            resolve_repo_path("/non/existent/repo/path/xyz", self.project_root)

        # Fallback to demo repo when not in git repo
        fallback_res = resolve_repo_path(None, self.project_root)
        self.assertTrue(os.path.exists(fallback_res))
        self.assertTrue(is_git_repo(fallback_res))


if __name__ == "__main__":
    unittest.main()
