-- DreamLayer Database Schema
-- Updated: 2025-08-23

-- Runs table - stores generation metadata
CREATE TABLE runs (
    run_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    model TEXT,
    vae TEXT,
    loras TEXT,
    controlnets TEXT,
    prompt TEXT,
    negative_prompt TEXT,
    seed INTEGER,
    sampler TEXT,
    steps INTEGER,
    cfg_scale REAL,
    width INTEGER,
    height INTEGER,
    batch_size INTEGER,
    batch_count INTEGER,
    workflow TEXT,
    version TEXT,
    generation_type TEXT,
    generated_images TEXT
);

CREATE INDEX idx_runs_timestamp ON runs(timestamp);
CREATE INDEX idx_runs_model ON runs(model);
CREATE INDEX idx_runs_generation_type ON runs(generation_type);

-- Assets table - stores file paths and metadata
CREATE TABLE assets (
    run_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    asset_key TEXT NOT NULL,
    asset_value TEXT,
    full_path TEXT,
    file_size INTEGER,
    metadata TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE,
    PRIMARY KEY (run_id, asset_key)
);

CREATE INDEX idx_assets_timestamp ON assets(timestamp);
CREATE INDEX idx_assets_run_id ON assets(run_id);

-- Metrics table - NEW DEDICATED COLUMNS STRUCTURE
CREATE TABLE metrics (
    run_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    clip_score_mean REAL,
    fid_score REAL,
    computed_at TEXT DEFAULT (datetime('now')),
    metadata TEXT,
    FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE,
    PRIMARY KEY (run_id)
);

CREATE INDEX idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX idx_metrics_run_id ON metrics(run_id);
