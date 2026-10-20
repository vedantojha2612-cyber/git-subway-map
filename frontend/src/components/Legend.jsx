import React from 'react';
import { Layers, Eye, EyeOff, Check, GitBranch } from 'lucide-react';

export default function Legend({ 
  lines = [], 
  selectedLineId, 
  onSelectLine, 
  isOpen, 
  onToggleOpen 
}) {
  return (
    <aside className={`transit-legend-panel ${isOpen ? 'open' : 'collapsed'}`}>
      <div className="legend-header" onClick={onToggleOpen}>
        <div className="legend-title-group">
          <Layers size={16} className="legend-icon" />
          <span className="legend-title">TRANSIT LINES & LEGEND</span>
          <span className="legend-count">{lines.length}</span>
        </div>
        <button 
          className="legend-toggle-btn"
          aria-label={isOpen ? 'Collapse Legend' : 'Expand Legend'}
        >
          {isOpen ? '◀' : '▶'}
        </button>
      </div>

      {isOpen && (
        <div className="legend-content">
          <div className="legend-tip">
            Click a line to isolate and highlight its schematic corridor.
          </div>

          {selectedLineId && (
            <button 
              className="show-all-btn"
              onClick={() => onSelectLine(null)}
            >
              <Eye size={13} />
              <span>Show All Lines</span>
            </button>
          )}

          <div className="lines-list">
            {lines.map((line) => {
              const isSelected = selectedLineId === line.id;
              const isDimmed = selectedLineId && !isSelected;

              return (
                <div
                  key={line.id}
                  className={`line-item ${isSelected ? 'selected' : ''} ${isDimmed ? 'dimmed' : ''}`}
                  onClick={() => onSelectLine(isSelected ? null : line.id)}
                >
                  {/* Route color bar / bullet */}
                  <div 
                    className="line-bullet"
                    style={{ backgroundColor: line.color }}
                  >
                    <span className="line-bullet-inner" />
                  </div>

                  <div className="line-info">
                    <div className="line-name-row">
                      <span className="line-name">{line.name}</span>
                      {line.is_trunk && (
                        <span className="trunk-tag">TRUNK</span>
                      )}
                    </div>
                    <div className="line-branch-row">
                      <GitBranch size={11} className="branch-icon" />
                      <span className="branch-name">{line.branch_name}</span>
                    </div>
                  </div>

                  <div className="line-stations-badge">
                    {line.station_count} {line.station_count === 1 ? 'stn' : 'stns'}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Symbol Key / Map Reading Guide */}
          <div className="legend-symbols">
            <h4 className="symbols-title">STATION SYMBOLS</h4>
            <div className="symbol-row">
              <div className="symbol-icon standard-stn-symbol" />
              <span className="symbol-label">Standard Station (Commit)</span>
            </div>
            <div className="symbol-row">
              <div className="symbol-icon interchange-stn-symbol">
                <span className="inner-ring" />
              </div>
              <span className="symbol-label">Interchange Hub (Merge Commit)</span>
            </div>
            <div className="symbol-row">
              <div className="symbol-icon head-stn-symbol">
                <span className="pulse-dot" />
              </div>
              <span className="symbol-label">HEAD Station (Active Ref)</span>
            </div>
            <div className="symbol-row">
              <div className="symbol-icon root-stn-symbol" />
              <span className="symbol-label">Origin / Terminal (Root Commit)</span>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
