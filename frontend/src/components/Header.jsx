import React, { useState } from 'react';
import { 
  GitBranch, 
  GitCommit, 
  RotateCcw, 
  Search, 
  FolderGit2, 
  Activity, 
  ExternalLink,
  TrainTrack
} from 'lucide-react';

export default function Header({ 
  graph, 
  isConnected, 
  isLoading, 
  onRefresh, 
  onResetDemo, 
  repoPathInput, 
  setRepoPathInput, 
  onLoadCustomRepo,
  searchQuery,
  setSearchQuery,
  searchResultsCount,
  onResetView,
  onFitView
}) {
  const [showRepoInput, setShowRepoInput] = useState(false);

  const handleSubmitRepo = (e) => {
    e.preventDefault();
    onLoadCustomRepo(repoPathInput);
    setShowRepoInput(false);
  };

  return (
    <header className="transit-header">
      {/* Brand Identity / Metro Roundel */}
      <div className="header-brand">
        <div className="metro-roundel" title="Git Transit Authority">
          <div className="roundel-circle"></div>
          <div className="roundel-bar">
            <span>METRO</span>
          </div>
        </div>
        <div className="brand-text">
          <div className="brand-title-row">
            <h1 className="brand-title">GIT SUBWAY MAP</h1>
            <span className="brand-badge">OCTOLINEAR DAG</span>
          </div>
          <p className="brand-sub">Tokyo & London Transit Schematic System</p>
        </div>
      </div>

      {/* Center Search & Repository Info */}
      <div className="header-center">
        {/* Repo Status Display */}
        <div className="repo-pill">
          <FolderGit2 size={16} className="text-transit-gold" />
          <span className="repo-name" title={graph?.repo_path || 'Demo Repository'}>
            {graph?.repo_name || 'Loading repo...'}
          </span>
          {graph && (
            <div className="repo-stats">
              <span className="stat-item" title="Total Stations (Commits)">
                <GitCommit size={13} /> {graph.total_commits}
              </span>
              <span className="stat-separator">•</span>
              <span className="stat-item" title="Transit Lines (Branches)">
                <GitBranch size={13} /> {graph.total_lines}
              </span>
            </div>
          )}
        </div>

        {/* Commit / Station Search Input */}
        <div className="search-container">
          <Search size={15} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search station, commit hash, author, branch..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <span className="search-count-badge">
              {searchResultsCount} found
            </span>
          )}
        </div>
      </div>

      {/* Header Actions & Controls */}
      <div className="header-actions">
        {/* Switch / Input Repo Path */}
        <button 
          className={`action-btn ${showRepoInput ? 'active' : ''}`}
          onClick={() => setShowRepoInput(!showRepoInput)}
          title="Switch Git Repository Path"
        >
          <FolderGit2 size={15} />
          <span>Switch Repo</span>
        </button>

        {/* Reset Demo Repo */}
        <button 
          className="action-btn"
          onClick={onResetDemo}
          title="Rebuild multi-branch sample Git repository"
          disabled={isLoading}
        >
          <RotateCcw size={15} className={isLoading ? 'spin-icon' : ''} />
          <span>Reset Demo</span>
        </button>

        {/* API Health Indicator */}
        <div className="health-badge" title={isConnected ? 'Backend Connected (/api)' : 'Backend Disconnected'}>
          <span className={`status-dot ${isConnected ? 'online' : 'offline'}`} />
          <span className="status-label">{isConnected ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </div>

      {/* Dropdown Repo Path Modal / Bar */}
      {showRepoInput && (
        <div className="repo-input-popover">
          <form onSubmit={handleSubmitRepo} className="repo-input-form">
            <label className="repo-input-label">Local Git Repository Absolute Path:</label>
            <div className="repo-input-row">
              <input
                type="text"
                className="path-text-input"
                placeholder="/path/to/your/git/project"
                value={repoPathInput}
                onChange={(e) => setRepoPathInput(e.target.value)}
                autoFocus
              />
              <button type="submit" className="submit-path-btn">Load Graph</button>
              <button 
                type="button" 
                className="cancel-path-btn" 
                onClick={() => {
                  setRepoPathInput('');
                  onLoadCustomRepo('');
                  setShowRepoInput(false);
                }}
              >
                Use Demo
              </button>
            </div>
          </form>
        </div>
      )}
    </header>
  );
}
