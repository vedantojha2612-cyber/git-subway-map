import React, { useState } from 'react';
import { 
  GitCommit, 
  GitBranch, 
  Tag, 
  User, 
  Clock, 
  ArrowRight, 
  CornerDownRight, 
  Copy, 
  Check, 
  X, 
  Shuffle, 
  Radio, 
  Compass,
  CornerUpRight
} from 'lucide-react';

export default function StationDrawer({
  station,
  stationsMap,
  linesMap,
  onClose,
  onSelectStation
}) {
  const [copied, setCopied] = useState(false);

  if (!station) return null;

  const handleCopyHash = () => {
    const textToCopy = station.id;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(textToCopy).catch(() => {
        fallbackCopy(textToCopy);
      });
    } else {
      fallbackCopy(textToCopy);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const fallbackCopy = (text) => {
    try {
      const el = document.createElement('textarea');
      el.value = text;
      el.setAttribute('readonly', '');
      el.style.position = 'absolute';
      el.style.left = '-9999px';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
    } catch (e) {
      console.warn('Fallback copy failed', e);
    }
  };

  const formattedDate = station.timestamp 
    ? new Date(station.timestamp * 1000).toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short'
      })
    : 'Unknown date';

  const parentStations = (station.parents || [])
    .map(pId => stationsMap[pId])
    .filter(Boolean);

  const childStations = (station.children || [])
    .map(cId => stationsMap[cId])
    .filter(Boolean);

  return (
    <div className="station-drawer-overlay" onClick={onClose}>
      <aside 
        className="station-drawer" 
        onClick={(e) => e.stopPropagation()}
        aria-label="Station Telemetry Drawer"
      >
        {/* Drawer Banner */}
        <div 
          className="drawer-banner"
          style={{ borderTop: `4px solid ${station.line_color}` }}
        >
          <div className="drawer-route-meta">
            <span 
              className="line-pill"
              style={{ backgroundColor: station.line_color, color: '#ffffff' }}
            >
              {station.line_name}
            </span>
            {station.is_interchange && (
              <span className="interchange-pill">
                <Shuffle size={12} /> INTERCHANGE HUB
              </span>
            )}
            {station.is_head && (
              <span className="head-pill">
                HEAD SIGNAL
              </span>
            )}
            {station.is_root && (
              <span className="root-pill">
                TERMINUS STOP
              </span>
            )}
          </div>
          <button 
            className="drawer-close-btn" 
            onClick={onClose}
            aria-label="Close station telemetry"
          >
            <X size={18} />
          </button>
        </div>

        {/* Drawer Body */}
        <div className="drawer-body">
          {/* Station Title & Hash */}
          <div className="station-title-section">
            <div 
              className="station-rondel-icon"
              style={{ borderColor: station.line_color }}
            >
              {station.is_interchange ? (
                <Shuffle size={20} color={station.line_color} />
              ) : (
                <GitCommit size={20} color={station.line_color} />
              )}
            </div>
            <div className="station-title-content">
              <h2 className="station-title">{station.message}</h2>
              <div className="station-hash-row">
                <span className="station-short-hash">{station.short_hash}</span>
                <button 
                  className="copy-hash-btn"
                  onClick={handleCopyHash}
                  title="Copy full 40-character commit hash"
                >
                  {copied ? <Check size={12} color="#10b981" /> : <Copy size={12} />}
                  <span>{copied ? 'Copied!' : 'Copy Hash'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Full SHA Telemetry */}
          <div className="telemetry-box">
            <span className="telemetry-label">COMMIT HASH</span>
            <code className="full-hash-code">{station.id}</code>
          </div>

          {/* Platform Tags & Branches */}
          {((station.branches && station.branches.length > 0) || (station.tags && station.tags.length > 0)) && (
            <div className="telemetry-box">
              <span className="telemetry-label">STATION PLATFORMS & REFS</span>
              <div className="refs-container">
                {station.branches && station.branches.map(branch => (
                  <span key={branch} className="ref-badge branch-badge">
                    <GitBranch size={11} /> {branch}
                  </span>
                ))}
                {station.tags && station.tags.map(tag => (
                  <span key={tag} className="ref-badge tag-badge">
                    <Tag size={11} /> {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Author & Dispatch Info */}
          <div className="telemetry-box">
            <span className="telemetry-label">DISPATCH TELEMETRY</span>
            <div className="author-details">
              <div className="author-row">
                <div 
                  className="avatar-circle"
                  style={{ backgroundColor: station.line_color, color: '#ffffff' }}
                >
                  {(station.author_name || 'G')[0].toUpperCase()}
                </div>
                <div className="author-info">
                  <span className="author-name">{station.author_name || 'Unknown Conductor'}</span>
                  <span className="author-email">{station.author_email || 'no-email@git'}</span>
                </div>
              </div>

              <div className="time-row">
                <Clock size={13} />
                <span>{formattedDate}</span>
              </div>

              <div className="coords-row">
                <Compass size={13} />
                <span>
                  Grid Track: Lane {station.grid_y}, Column {station.grid_x} ({station.x}px, {station.y}px)
                </span>
              </div>
            </div>
          </div>

          {/* Interchange Transfer Lines */}
          {station.is_interchange && station.transfer_lines && station.transfer_lines.length > 0 && (
            <div className="telemetry-box">
              <span className="telemetry-label">TRANSFER CONCOURSE CONNECTIONS</span>
              <div className="transfer-list">
                {station.transfer_lines.map(lineId => {
                  const line = linesMap[lineId];
                  if (!line) return null;
                  return (
                    <div key={lineId} className="transfer-card">
                      <span 
                        className="transfer-dot" 
                        style={{ backgroundColor: line.color }}
                      />
                      <span className="transfer-name">{line.name}</span>
                      <span className="transfer-branch">{line.branch_name}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* DAG Lineage / Junctions */}
          <div className="telemetry-box">
            <span className="telemetry-label">TRACK LINEAGE CONNECTIONS</span>
            
            {/* Parents / Inbound */}
            <div className="lineage-group">
              <span className="lineage-group-title">
                <CornerUpRight size={13} /> Parent Stations ({parentStations.length})
              </span>
              {parentStations.length === 0 ? (
                <div className="lineage-empty">Origin terminus (Initial commit)</div>
              ) : (
                <div className="lineage-list">
                  {parentStations.map(pStn => (
                    <div 
                      key={pStn.id}
                      className="lineage-item"
                      onClick={() => onSelectStation(pStn)}
                      title={`Jump to parent: ${pStn.message}`}
                    >
                      <span 
                        className="lineage-dot"
                        style={{ backgroundColor: pStn.line_color }}
                      />
                      <div className="lineage-content">
                        <span className="lineage-hash">{pStn.short_hash}</span>
                        <span className="lineage-msg">{pStn.message}</span>
                      </div>
                      <span className="lineage-jump">Jump ↗</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Children / Outbound */}
            <div className="lineage-group">
              <span className="lineage-group-title">
                <CornerDownRight size={13} /> Next Stations ({childStations.length})
              </span>
              {childStations.length === 0 ? (
                <div className="lineage-empty">Line terminus (HEAD of route)</div>
              ) : (
                <div className="lineage-list">
                  {childStations.map(cStn => (
                    <div 
                      key={cStn.id}
                      className="lineage-item"
                      onClick={() => onSelectStation(cStn)}
                      title={`Jump to child: ${cStn.message}`}
                    >
                      <span 
                        className="lineage-dot"
                        style={{ backgroundColor: cStn.line_color }}
                      />
                      <div className="lineage-content">
                        <span className="lineage-hash">{cStn.short_hash}</span>
                        <span className="lineage-msg">{cStn.message}</span>
                      </div>
                      <span className="lineage-jump">Jump ↘</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}
