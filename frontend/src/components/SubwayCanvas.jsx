import React, { useRef, useState, useEffect, useCallback } from 'react';
import { GitCommit, Shuffle, GitBranch, Tag, ArrowRight } from 'lucide-react';

export default function SubwayCanvas({
  graph,
  selectedStation,
  onSelectStation,
  selectedLineId,
  searchQuery,
  showLabels,
  showGrid,
  transform,
  setTransform,
  onViewportChange
}) {
  const containerRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [hoveredStation, setHoveredStation] = useState(null);
  const [hoverPos, setHoverPos] = useState({ x: 0, y: 0 });

  // Update viewport size reporting
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        const { clientWidth, clientHeight } = containerRef.current;
        onViewportChange({ width: clientWidth, height: clientHeight });
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [onViewportChange]);

  // Mouse drag pan handlers
  const handleMouseDown = (e) => {
    // Only pan on primary button or middle button
    if (e.button !== 0 && e.button !== 1) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - transform.x, y: e.clientY - transform.y });
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      setTransform(prev => ({
        ...prev,
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      }));
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Smooth wheel zoom centered on cursor
  const handleWheel = useCallback((e) => {
    e.preventDefault();
    if (!containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const cursorX = e.clientX - rect.left;
    const cursorY = e.clientY - rect.top;

    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
    
    setTransform(prev => {
      const newScale = Math.min(Math.max(prev.scale * zoomFactor, 0.15), 4.5);
      // Zoom centered at mouse position
      const newX = cursorX - (cursorX - prev.x) * (newScale / prev.scale);
      const newY = cursorY - (cursorY - prev.y) * (newScale / prev.scale);

      return {
        scale: newScale,
        x: newX,
        y: newY
      };
    });
  }, [setTransform]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    container.addEventListener('wheel', handleWheel, { passive: false });
    return () => container.removeEventListener('wheel', handleWheel);
  }, [handleWheel]);

  // Touch support for tablets/mobile
  const touchStartRef = useRef({ x: 0, y: 0, dist: 0 });
  const handleTouchStart = (e) => {
    if (e.touches.length === 1) {
      setIsDragging(true);
      setDragStart({
        x: e.touches[0].clientX - transform.x,
        y: e.touches[0].clientY - transform.y
      });
    } else if (e.touches.length === 2) {
      setIsDragging(false);
      const dist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      touchStartRef.current = {
        x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
        y: (e.touches[0].clientY + e.touches[1].clientY) / 2,
        dist
      };
    }
  };

  const handleTouchMove = (e) => {
    if (e.touches.length === 1 && isDragging) {
      setTransform(prev => ({
        ...prev,
        x: e.touches[0].clientX - dragStart.x,
        y: e.touches[0].clientY - dragStart.y
      }));
    } else if (e.touches.length === 2) {
      const dist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      const factor = dist / (touchStartRef.current.dist || dist);
      touchStartRef.current.dist = dist;

      setTransform(prev => {
        const newScale = Math.min(Math.max(prev.scale * factor, 0.15), 4.5);
        return { ...prev, scale: newScale };
      });
    }
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  if (!graph) return null;

  // Filter highlights from search
  const isStationMatched = (stn) => {
    if (!searchQuery || !searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase().trim();
    return (
      stn.short_hash.toLowerCase().includes(q) ||
      stn.message.toLowerCase().includes(q) ||
      stn.author_name.toLowerCase().includes(q) ||
      (stn.line_name && stn.line_name.toLowerCase().includes(q)) ||
      (stn.branches && stn.branches.some(b => b.toLowerCase().includes(q))) ||
      (stn.tags && stn.tags.some(t => t.toLowerCase().includes(q)))
    );
  };

  return (
    <div
      ref={containerRef}
      className={`subway-canvas-container ${isDragging ? 'is-dragging' : ''}`}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <svg
        className="subway-svg"
        style={{
          transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`,
          transformOrigin: '0 0'
        }}
      >
        <defs>
          {/* Blueprint Grid Pattern */}
          <pattern
            id="subway-grid-pattern"
            width={graph.grid_step_x || 140}
            height={graph.grid_step_y || 90}
            patternUnits="userSpaceOnUse"
          >
            <path
              d={`M ${graph.grid_step_x || 140} 0 L 0 0 0 ${graph.grid_step_y || 90}`}
              fill="none"
              stroke="rgba(255, 255, 255, 0.035)"
              strokeWidth="1"
              strokeDasharray="2 4"
            />
            <circle cx="0" cy="0" r="1.5" fill="rgba(255, 255, 255, 0.08)" />
          </pattern>

          {/* Station Glow Filter */}
          <filter id="station-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#ffffff" floodOpacity="0.4" />
          </filter>

          {/* Head Signal Pulse */}
          <filter id="head-signal-glow" x="-100%" y="-100%" width="300%" height="300%">
            <feDropShadow dx="0" dy="0" stdDeviation="8" floodColor="#eab308" floodOpacity="0.8" />
          </filter>
        </defs>

        {/* Optional Blueprint Grid Lines */}
        {showGrid && (
          <rect
            x={graph.bounds.min_x - 1000}
            y={graph.bounds.min_y - 1000}
            width={graph.bounds.width + 2000}
            height={graph.bounds.height + 2000}
            fill="url(#subway-grid-pattern)"
            pointerEvents="none"
          />
        )}

        {/* LAYER 1: TRACK CASING (Under-ballast for high contrast) */}
        <g className="tracks-casing-layer" pointerEvents="none">
          {graph.tracks.map((track) => {
            const isDimmed = selectedLineId && track.line_id !== selectedLineId;
            return (
              <path
                key={`casing-${track.id}`}
                d={track.svg_path}
                fill="none"
                stroke="#080c14"
                strokeWidth={13}
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity={isDimmed ? 0.2 : 0.9}
              />
            );
          })}
        </g>

        {/* LAYER 2: SCHEMATIC TRANSIT TRACKS */}
        <g className="tracks-layer" pointerEvents="none">
          {graph.tracks.map((track) => {
            const isSelected = selectedLineId === track.line_id;
            const isDimmed = selectedLineId && !isSelected;

            return (
              <g key={track.id} className="track-group">
                {/* Main colored subway track line */}
                <path
                  d={track.svg_path}
                  fill="none"
                  stroke={track.line_color}
                  strokeWidth={isSelected ? 8.5 : 7}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  opacity={isDimmed ? 0.15 : 1}
                  className="subway-track-line"
                />

                {/* Subtle center conductor line for trunk tracks */}
                {track.is_trunk && !isDimmed && (
                  <path
                    d={track.svg_path}
                    fill="none"
                    stroke="#ffffff"
                    strokeWidth={1.8}
                    strokeLinecap="round"
                    strokeDasharray="6 8"
                    opacity={0.35}
                  />
                )}
              </g>
            );
          })}
        </g>

        {/* LAYER 3: STATIONS */}
        <g className="stations-layer">
          {graph.stations.map((stn) => {
            const isSelected = selectedStation?.id === stn.id;
            const isHovered = hoveredStation?.id === stn.id;
            const isLineDimmed = selectedLineId && stn.line_id !== selectedLineId;
            const isMatch = isStationMatched(stn);
            const opacity = isLineDimmed || !isMatch ? 0.2 : 1;

            return (
              <g
                key={stn.id}
                className={`station-node ${isSelected ? 'is-selected' : ''} ${isHovered ? 'is-hovered' : ''}`}
                opacity={opacity}
                transform={`translate(${stn.x}, ${stn.y})`}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectStation(stn);
                }}
                onMouseEnter={() => {
                  setHoveredStation(stn);
                  setHoverPos({
                    x: stn.x * transform.scale + transform.x,
                    y: stn.y * transform.scale + transform.y
                  });
                }}
                onMouseLeave={() => setHoveredStation(null)}
                style={{ cursor: 'pointer' }}
              >
                {/* Generous Invisible Click Hitbox */}
                <circle r={22} fill="transparent" pointerEvents="all" />

                {/* HEAD station animated pulse ring */}
                {stn.is_head && (
                  <g className="head-beacon" pointerEvents="none">
                    <circle r={18} fill="none" stroke="#eab308" strokeWidth={2} opacity={0.6} className="ping-ring" />
                    <circle r={25} fill="none" stroke="#eab308" strokeWidth={1} strokeDasharray="3 3" opacity={0.4} />
                  </g>
                )}

                {/* Selected Station Target Reticle */}
                {isSelected && (
                  <g className="station-reticle" pointerEvents="none">
                    <circle r={20} fill="none" stroke="#60a5fa" strokeWidth={2} strokeDasharray="4 3" className="reticle-spin" />
                    <circle r={26} fill="rgba(96, 165, 250, 0.12)" />
                  </g>
                )}

                {/* STATION BADGE RENDERING */}
                {stn.is_root ? (
                  /* ROOT TERMINAL: Double terminal stop */
                  <g pointerEvents="none">
                    <rect x={-4} y={-12} width={8} height={24} rx={2} fill={stn.line_color} />
                    <circle r={7} fill="#ffffff" stroke={stn.line_color} strokeWidth={3} />
                  </g>
                ) : stn.is_interchange ? (
                  /* INTERCHANGE HUB: Tokyo/London Interchange Rondel */
                  <g className="interchange-hub" pointerEvents="none">
                    {/* Outer dark casing halo */}
                    <circle r={13} fill="#0d131f" stroke="#ffffff" strokeWidth={2} />
                    {/* Outer transfer ring */}
                    <circle r={10} fill="#ffffff" stroke={stn.line_color} strokeWidth={3} />
                    {/* Center interchange hub dot */}
                    <circle r={4.5} fill="#1e293b" />
                    {/* Adjacent mini beads for transferring lines */}
                    {stn.transfer_lines && stn.transfer_lines.slice(0, 3).map((tId, idx) => (
                      <circle
                        key={tId}
                        cx={14 * Math.cos((idx * 2 * Math.PI) / 3)}
                        cy={14 * Math.sin((idx * 2 * Math.PI) / 3)}
                        r={3}
                        fill="#ffffff"
                        stroke="#0d131f"
                        strokeWidth={1}
                      />
                    ))}
                  </g>
                ) : (
                  /* STANDARD TRANSIT STATION BADGE */
                  <g className="standard-station" pointerEvents="none">
                    {/* Casing */}
                    <circle r={9.5} fill="#0d131f" />
                    {/* White Core with Line Color Rim */}
                    <circle
                      r={7}
                      fill="#ffffff"
                      stroke={stn.line_color}
                      strokeWidth={3.5}
                      className="station-circle"
                    />
                    {/* Small inner transit dot for HEAD or tagged commits */}
                    {(stn.is_head || (stn.tags && stn.tags.length > 0)) && (
                      <circle r={2.5} fill={stn.line_color} />
                    )}
                  </g>
                )}

                {/* STATION LABELS */}
                {showLabels && (
                  <g 
                    className="station-label-group"
                    transform="translate(14, -10)"
                    pointerEvents="none"
                  >
                    {/* Short commit hash pill */}
                    <rect
                      x={-2}
                      y={-12}
                      width={52}
                      height={16}
                      rx={3}
                      fill="#0f172a"
                      stroke="rgba(255, 255, 255, 0.15)"
                      strokeWidth={1}
                    />
                    <text
                      x={24}
                      y={0}
                      textAnchor="middle"
                      fill="#e2e8f0"
                      fontSize={10}
                      fontFamily="'Fira Code', monospace"
                      fontWeight="600"
                    >
                      {stn.short_hash}
                    </text>

                    {/* Commit Message Headline preview */}
                    <text
                      x={56}
                      y={0}
                      fill="#cbd5e1"
                      fontSize={11}
                      fontFamily="'Space Grotesk', -apple-system, sans-serif"
                      fontWeight="500"
                      className="label-message"
                    >
                      {stn.message.length > 36 ? stn.message.slice(0, 36) + '…' : stn.message}
                    </text>

                    {/* Branch / Tag Badges on the map */}
                    {stn.branches && stn.branches.length > 0 && (
                      <g transform="translate(0, 10)">
                        <rect
                          x={-2}
                          y={-9}
                          width={Math.min(stn.branches[0].length * 7 + 16, 120)}
                          height={14}
                          rx={3}
                          fill={stn.line_color}
                        />
                        <text
                          x={6}
                          y={1}
                          fill="#ffffff"
                          fontSize={9}
                          fontWeight="700"
                          fontFamily="'Inter', sans-serif"
                        >
                          {stn.branches[0]}
                        </text>
                      </g>
                    )}

                    {stn.tags && stn.tags.length > 0 && (
                      <g transform="translate(65, 10)">
                        <rect
                          x={-2}
                          y={-9}
                          width={stn.tags[0].length * 6.5 + 14}
                          height={14}
                          rx={3}
                          fill="#f59e0b"
                        />
                        <text
                          x={5}
                          y={1}
                          fill="#0f172a"
                          fontSize={9}
                          fontWeight="700"
                          fontFamily="'Inter', sans-serif"
                        >
                          {stn.tags[0]}
                        </text>
                      </g>
                    )}
                  </g>
                )}
              </g>
            );
          })}
        </g>
      </svg>

      {/* FLOATING HOVER TOOLTIP */}
      {hoveredStation && !isDragging && (
        <div
          className="station-hover-tooltip"
          style={{
            left: `${hoverPos.x + 18}px`,
            top: `${hoverPos.y - 30}px`,
            borderLeft: `4px solid ${hoveredStation.line_color}`
          }}
        >
          <div className="tooltip-header">
            <span className="tooltip-line-badge" style={{ backgroundColor: hoveredStation.line_color }}>
              {hoveredStation.line_name}
            </span>
            <span className="tooltip-hash">{hoveredStation.short_hash}</span>
            {hoveredStation.is_interchange && (
              <span className="tooltip-interchange-badge">
                <Shuffle size={10} /> Transfer Hub
              </span>
            )}
            {hoveredStation.is_head && (
              <span className="tooltip-head-badge">HEAD</span>
            )}
          </div>
          <div className="tooltip-message">{hoveredStation.message}</div>
          <div className="tooltip-meta">
            <span className="tooltip-author">{hoveredStation.author_name}</span>
            <span className="tooltip-sep">•</span>
            <span className="tooltip-time">
              {new Date(hoveredStation.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
          <div className="tooltip-hint">Click station for full telemetry & lineage</div>
        </div>
      )}
    </div>
  );
}
