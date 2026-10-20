import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Header from './components/Header';
import SubwayCanvas from './components/SubwayCanvas';
import Legend from './components/Legend';
import StationDrawer from './components/StationDrawer';
import Minimap from './components/Minimap';
import ControlsToolbar from './components/ControlsToolbar';
import ShortcutsModal from './components/ShortcutsModal';
import { fetchSubwayGraph, resetDemoRepo, fetchHealth } from './services/api';
import { Loader2, AlertTriangle, RefreshCw } from 'lucide-react';
import './styles/subway.css';

export default function App() {
  const [graph, setGraph] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  // Interaction State
  const [selectedStation, setSelectedStation] = useState(null);
  const [selectedLineId, setSelectedLineId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [repoPathInput, setRepoPathInput] = useState('');
  const [currentRepoPath, setCurrentRepoPath] = useState(null);

  // Viewport & Transform State
  const [transform, setTransform] = useState({ scale: 1, x: 0, y: 0 });
  const [viewportSize, setViewportSize] = useState({ 
    width: typeof window !== 'undefined' ? window.innerWidth : 1200, 
    height: typeof window !== 'undefined' ? window.innerHeight : 800 
  });

  // Display Toggles
  const [showLabels, setShowLabels] = useState(true);
  const [showGrid, setShowGrid] = useState(true);
  const [isLegendOpen, setIsLegendOpen] = useState(true);
  const [showShortcuts, setShowShortcuts] = useState(false);

  // Maps for O(1) station and line lookups
  const stationsMap = useMemo(() => {
    if (!graph || !graph.stations) return {};
    return Object.fromEntries(graph.stations.map(s => [s.id, s]));
  }, [graph]);

  const linesMap = useMemo(() => {
    if (!graph || !graph.lines) return {};
    return Object.fromEntries(graph.lines.map(l => [l.id, l]));
  }, [graph]);

  // Fit to screen calculation
  const handleFitView = useCallback((targetGraph = graph) => {
    if (!targetGraph || !targetGraph.bounds) return;
    const { min_x, min_y, width, height } = targetGraph.bounds;
    const padding = 120;
    const availW = Math.max(viewportSize.width - 320, 400); // Leave room for legend
    const availH = Math.max(viewportSize.height - 140, 300);

    const fullW = width + padding * 2;
    const fullH = height + padding * 2;

    const scaleX = availW / fullW;
    const scaleY = availH / fullH;
    const newScale = Math.min(Math.max(Math.min(scaleX, scaleY), 0.35), 1.6);

    const centerX = min_x + width / 2;
    const centerY = min_y + height / 2;

    const newX = (viewportSize.width / 2) - (centerX * newScale);
    const newY = (viewportSize.height / 2) - (centerY * newScale);

    setTransform({
      scale: newScale,
      x: newX,
      y: newY
    });
  }, [graph, viewportSize]);

  // Reset to 100% zoom and center
  const handleResetView = useCallback(() => {
    if (!graph || !graph.bounds) {
      setTransform({ scale: 1, x: 100, y: 100 });
      return;
    }
    const { min_x, min_y, width, height } = graph.bounds;
    const centerX = min_x + width / 2;
    const centerY = min_y + height / 2;

    setTransform({
      scale: 1,
      x: (viewportSize.width / 2) - centerX,
      y: (viewportSize.height / 2) - centerY
    });
  }, [graph, viewportSize]);

  // Load Subway Graph Data
  const loadGraph = useCallback(async (path = currentRepoPath, autoFit = false) => {
    setIsLoading(true);
    setError(null);
    try {
      // Check health
      try {
        await fetchHealth();
        setIsConnected(true);
      } catch (hErr) {
        setIsConnected(false);
      }

      const data = await fetchSubwayGraph(path);
      setGraph(data);
      setIsConnected(true);

      // Select first head station or latest station by default if none selected
      if (autoFit || !graph) {
        handleFitView(data);
      }
    } catch (err) {
      console.error('Failed to load subway graph:', err);
      setError(err.message || 'Failed to connect to Subway Map API');
      setIsConnected(false);
    } finally {
      setIsLoading(false);
    }
  }, [currentRepoPath, graph, handleFitView]);

  // Initial load
  useEffect(() => {
    loadGraph(null, true);
  }, []);

  // Jump to specific coordinate (from minimap or search)
  const handleNavigateTo = useCallback((targetX, targetY) => {
    setTransform(prev => ({
      ...prev,
      x: (viewportSize.width / 2) - (targetX * prev.scale),
      y: (viewportSize.height / 2) - (targetY * prev.scale)
    }));
  }, [viewportSize]);

  // Focus on a specific station
  const handleSelectStation = useCallback((stn) => {
    setSelectedStation(stn);
    if (stn) {
      // Center map gently on selected station
      handleNavigateTo(stn.x, stn.y);
    }
  }, [handleNavigateTo]);

  // Reset Demo Repository
  const handleResetDemo = async () => {
    try {
      setIsLoading(true);
      await resetDemoRepo();
      await loadGraph(null, true);
    } catch (err) {
      setError(`Failed to reset demo: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Switch custom repository
  const handleLoadCustomRepo = (path) => {
    setCurrentRepoPath(path || null);
    loadGraph(path || null, true);
  };

  // Zoom In / Out buttons
  const handleZoomIn = () => {
    setTransform(prev => {
      const newScale = Math.min(prev.scale * 1.25, 4.5);
      const factor = newScale / prev.scale;
      return {
        scale: newScale,
        x: (viewportSize.width / 2) - ((viewportSize.width / 2) - prev.x) * factor,
        y: (viewportSize.height / 2) - ((viewportSize.height / 2) - prev.y) * factor
      };
    });
  };

  const handleZoomOut = () => {
    setTransform(prev => {
      const newScale = Math.max(prev.scale * 0.8, 0.15);
      const factor = newScale / prev.scale;
      return {
        scale: newScale,
        x: (viewportSize.width / 2) - ((viewportSize.width / 2) - prev.x) * factor,
        y: (viewportSize.height / 2) - ((viewportSize.height / 2) - prev.y) * factor
      };
    });
  };

  // Global Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Don't trigger if user is typing in an input
      if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;

      if (e.key === 'Escape') {
        setSelectedStation(null);
        setShowShortcuts(false);
      } else if (e.key === 'f' || e.key === 'F') {
        handleFitView();
      } else if (e.key === 'r' || e.key === 'R') {
        handleResetView();
      } else if (e.key === 'l' || e.key === 'L') {
        setShowLabels(prev => !prev);
      } else if (e.key === 'g' || e.key === 'G') {
        setShowGrid(prev => !prev);
      } else if (e.key === '?') {
        setShowShortcuts(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleFitView, handleResetView]);

  // Search results count
  const searchResultsCount = useMemo(() => {
    if (!graph || !searchQuery.trim()) return 0;
    const q = searchQuery.toLowerCase().trim();
    return graph.stations.filter(s =>
      s.short_hash.toLowerCase().includes(q) ||
      s.message.toLowerCase().includes(q) ||
      s.author_name.toLowerCase().includes(q) ||
      (s.branches && s.branches.some(b => b.toLowerCase().includes(q))) ||
      (s.tags && s.tags.some(t => t.toLowerCase().includes(q)))
    ).length;
  }, [graph, searchQuery]);

  return (
    <div className="subway-app-container">
      {/* Top Retro Metro Header */}
      <Header
        graph={graph}
        isConnected={isConnected}
        isLoading={isLoading}
        onRefresh={() => loadGraph()}
        onResetDemo={handleResetDemo}
        repoPathInput={repoPathInput}
        setRepoPathInput={setRepoPathInput}
        onLoadCustomRepo={handleLoadCustomRepo}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        searchResultsCount={searchResultsCount}
        onResetView={handleResetView}
        onFitView={handleFitView}
      />

      {/* Main Schematic Transit Viewport */}
      <main className="main-viewport">
        {isLoading && !graph ? (
          <div className="state-container">
            <Loader2 size={36} className="spin-icon text-transit-blue" />
            <p>Loading Transit Schematic DAG...</p>
          </div>
        ) : error && !graph ? (
          <div className="state-container">
            <AlertTriangle size={36} className="text-red-500" />
            <p>{error}</p>
            <button className="retry-btn" onClick={() => loadGraph()}>
              Retry Connection
            </button>
          </div>
        ) : (
          <>
            {/* SVG Interactive Canvas */}
            <SubwayCanvas
              graph={graph}
              selectedStation={selectedStation}
              onSelectStation={handleSelectStation}
              selectedLineId={selectedLineId}
              searchQuery={searchQuery}
              showLabels={showLabels}
              showGrid={showGrid}
              transform={transform}
              setTransform={setTransform}
              onViewportChange={setViewportSize}
            />

            {/* Metro Transit Line Legend */}
            <Legend
              lines={graph?.lines || []}
              selectedLineId={selectedLineId}
              onSelectLine={setSelectedLineId}
              isOpen={isLegendOpen}
              onToggleOpen={() => setIsLegendOpen(!isLegendOpen)}
            />

            {/* Radar Minimap Overview */}
            <Minimap
              graph={graph}
              transform={transform}
              viewportSize={viewportSize}
              onNavigateTo={handleNavigateTo}
            />

            {/* Floating Glassmorphic Control Toolbar */}
            <ControlsToolbar
              zoomScale={transform.scale}
              onZoomIn={handleZoomIn}
              onZoomOut={handleZoomOut}
              onFitView={handleFitView}
              onResetView={handleResetView}
              showLabels={showLabels}
              onToggleLabels={() => setShowLabels(!showLabels)}
              showGrid={showGrid}
              onToggleGrid={() => setShowGrid(!showGrid)}
              onToggleShortcuts={() => setShowShortcuts(true)}
            />

            {/* Commit Dossier & Station Telemetry Drawer */}
            {selectedStation && (
              <StationDrawer
                station={selectedStation}
                stationsMap={stationsMap}
                linesMap={linesMap}
                onClose={() => setSelectedStation(null)}
                onSelectStation={handleSelectStation}
              />
            )}
          </>
        )}
      </main>

      {/* Keyboard Shortcuts & Guide Modal */}
      <ShortcutsModal
        isOpen={showShortcuts}
        onClose={() => setShowShortcuts(false)}
      />
    </div>
  );
}
