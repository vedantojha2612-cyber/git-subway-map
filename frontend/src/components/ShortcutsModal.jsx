import React from 'react';
import { X, Navigation, MousePointer, Search, Keyboard } from 'lucide-react';

export default function ShortcutsModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="shortcuts-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-row">
            <Keyboard size={18} className="modal-icon" />
            <h3 className="modal-title">Subway Map Navigation Guide</h3>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        <div className="modal-content">
          <div className="shortcuts-section">
            <h4 className="section-title">Canvas Navigation</h4>
            <div className="shortcut-row">
              <span className="key-badge">Click + Drag</span>
              <span className="shortcut-desc">Pan transit board smoothly in any direction</span>
            </div>
            <div className="shortcut-row">
              <span className="key-badge">Mouse Wheel</span>
              <span className="shortcut-desc">Zoom in / out centered on your cursor</span>
            </div>
            <div className="shortcut-row">
              <span className="key-badge">Click Station</span>
              <span className="shortcut-desc">Open commit dossier & track lineage drawer</span>
            </div>
            <div className="shortcut-row">
              <span className="key-badge">Click Minimap</span>
              <span className="shortcut-desc">Instantly jump radar viewport to coordinate</span>
            </div>
          </div>

          <div className="shortcuts-section">
            <h4 className="section-title">Keyboard Shortcuts</h4>
            <div className="shortcut-row">
              <span className="key-badge">F</span>
              <span className="shortcut-desc">Fit entire subway graph to screen</span>
            </div>
            <div className="shortcut-row">
              <span className="key-badge">R</span>
              <span className="shortcut-desc">Reset zoom to 100% and center origin</span>
            </div>
            <div className="shortcut-row">
              <span className="key-badge">L</span>
              <span className="shortcut-desc">Toggle station labels and commit titles</span>
            </div>
            <div className="shortcut-row">
              <span className="key-badge">G</span>
              <span className="shortcut-desc">Toggle blueprint grid background</span>
            </div>
            <div className="shortcut-row">
              <span className="key-badge">Esc</span>
              <span className="shortcut-desc">Close station telemetry drawer or dialog</span>
            </div>
          </div>

          <div className="shortcuts-section">
            <h4 className="section-title">Transit Schematic Legend</h4>
            <div className="transit-rules">
              <p>• <strong>Horizontal Trunk Lines</strong>: Primary branches (e.g. master/main) run straight left-to-right.</p>
              <p>• <strong>Octolinear Angles</strong>: Branch lines diverge and merge at strict 45°/90° curves.</p>
              <p>• <strong>Interchange Hubs</strong>: Merge commits feature multi-line transfer rings linking divergent branches.</p>
              <p>• <strong>Radar Minimap</strong>: Bottom right radar displays the full topology with dynamic viewport rectangle.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
