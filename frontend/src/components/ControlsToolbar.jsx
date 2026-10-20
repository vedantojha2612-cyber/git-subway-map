import React from 'react';
import { 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  RotateCcw, 
  Type, 
  Grid, 
  HelpCircle
} from 'lucide-react';

export default function ControlsToolbar({
  zoomScale,
  onZoomIn,
  onZoomOut,
  onFitView,
  onResetView,
  showLabels,
  onToggleLabels,
  showGrid,
  onToggleGrid,
  onToggleShortcuts
}) {
  const zoomPercent = Math.round(zoomScale * 100);

  return (
    <div className="transit-controls-toolbar">
      {/* Zoom Controls */}
      <div className="controls-group">
        <button 
          className="control-btn"
          onClick={onZoomIn}
          title="Zoom In (Scroll Up)"
        >
          <ZoomIn size={16} />
        </button>
        <div className="zoom-indicator" title="Current Zoom Scale">
          {zoomPercent}%
        </div>
        <button 
          className="control-btn"
          onClick={onZoomOut}
          title="Zoom Out (Scroll Down)"
        >
          <ZoomOut size={16} />
        </button>
      </div>

      <div className="controls-divider" />

      {/* Frame & Fit */}
      <div className="controls-group">
        <button 
          className="control-btn"
          onClick={onFitView}
          title="Fit Whole Map to Screen (F)"
        >
          <Maximize2 size={16} />
        </button>
        <button 
          className="control-btn"
          onClick={onResetView}
          title="Reset to 100% Zoom & Origin (R)"
        >
          <RotateCcw size={16} />
        </button>
      </div>

      <div className="controls-divider" />

      {/* View Toggles */}
      <div className="controls-group">
        <button 
          className={`control-btn ${showLabels ? 'active' : ''}`}
          onClick={onToggleLabels}
          title="Toggle Station Name Labels (L)"
        >
          <Type size={16} />
        </button>
        <button 
          className={`control-btn ${showGrid ? 'active' : ''}`}
          onClick={onToggleGrid}
          title="Toggle Blueprint Grid Lines (G)"
        >
          <Grid size={16} />
        </button>
        <button 
          className="control-btn"
          onClick={onToggleShortcuts}
          title="Keyboard & Navigation Guide (?)"
        >
          <HelpCircle size={16} />
        </button>
      </div>
    </div>
  );
}
