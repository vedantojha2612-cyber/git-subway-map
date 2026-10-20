import React, { useRef } from 'react';
import { MapPin, Navigation } from 'lucide-react';

export default function Minimap({
  graph,
  transform,
  viewportSize,
  onNavigateTo
}) {
  const minimapRef = useRef(null);

  if (!graph || !graph.bounds) return null;

  const { min_x, min_y, width, height } = graph.bounds;
  const padding = 60;
  const totalW = (width || 800) + padding * 2;
  const totalH = (height || 400) + padding * 2;

  const minimapWidth = 200;
  const minimapHeight = 120;

  const scaleX = minimapWidth / totalW;
  const scaleY = minimapHeight / totalH;
  const scale = Math.min(scaleX, scaleY);

  const offsetX = (minimapWidth - totalW * scale) / 2;
  const offsetY = (minimapHeight - totalH * scale) / 2;

  // Calculate visible viewport rectangle in graph coordinates
  const viewX1 = (-transform.x) / transform.scale;
  const viewY1 = (-transform.y) / transform.scale;
  const viewW = viewportSize.width / transform.scale;
  const viewH = viewportSize.height / transform.scale;

  // Map to minimap coordinates
  const miniViewX = offsetX + ((viewX1 - (min_x - padding)) * scale);
  const miniViewY = offsetY + ((viewY1 - (min_y - padding)) * scale);
  const miniViewW = viewW * scale;
  const miniViewH = viewH * scale;

  const handleMinimapClick = (e) => {
    if (!minimapRef.current) return;
    const rect = minimapRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    // Convert click position to graph coordinates
    const graphX = (clickX - offsetX) / scale + (min_x - padding);
    const graphY = (clickY - offsetY) / scale + (min_y - padding);

    onNavigateTo(graphX, graphY);
  };

  return (
    <div className="minimap-container" title="Radar Overview - Click to jump">
      <div className="minimap-header">
        <Navigation size={12} className="radar-icon" />
        <span className="minimap-title">TRANSIT RADAR</span>
      </div>
      <div 
        className="minimap-canvas-wrapper" 
        ref={minimapRef}
        onClick={handleMinimapClick}
      >
        <svg 
          width={minimapWidth} 
          height={minimapHeight} 
          className="minimap-svg"
        >
          {/* Schematic Tracks */}
          <g transform={`translate(${offsetX}, ${offsetY}) scale(${scale}) translate(${-(min_x - padding)}, ${-(min_y - padding)})`}>
            {graph.tracks.map((track) => (
              <path
                key={track.id}
                d={track.svg_path}
                fill="none"
                stroke={track.line_color}
                strokeWidth={5}
                strokeOpacity={0.8}
              />
            ))}

            {/* Stations */}
            {graph.stations.map((stn) => (
              <circle
                key={stn.id}
                cx={stn.x}
                cy={stn.y}
                r={stn.is_interchange ? 7 : 4}
                fill="#ffffff"
                stroke={stn.line_color}
                strokeWidth={2}
              />
            ))}
          </g>

          {/* Viewport Indicator Rectangle */}
          <rect
            x={Math.max(0, miniViewX)}
            y={Math.max(0, miniViewY)}
            width={Math.max(10, Math.min(minimapWidth, miniViewW))}
            height={Math.max(10, Math.min(minimapHeight, miniViewH))}
            fill="rgba(59, 130, 246, 0.15)"
            stroke="#60a5fa"
            strokeWidth={1.5}
            strokeDasharray="3 2"
            rx={2}
            className="viewport-rect"
          />
        </svg>
      </div>
    </div>
  );
}
