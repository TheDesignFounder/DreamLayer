-- Add composition_metrics table to DreamLayer database
-- Migration script for composition correctness metrics
-- Date: 2025-08-26

-- Composition metrics table - stores precision, recall, F1 scores
CREATE TABLE IF NOT EXISTS composition_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    prompt_text TEXT,
    image_path TEXT,
    macro_precision REAL,
    macro_recall REAL,
    macro_f1 REAL,
    per_class_metrics TEXT,  -- JSON string
    detected_objects TEXT,   -- JSON string
    missing_objects TEXT,    -- JSON string
    timestamp TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

-- Indexes for composition_metrics table
CREATE INDEX IF NOT EXISTS idx_composition_metrics_run_id ON composition_metrics(run_id);
CREATE INDEX IF NOT EXISTS idx_composition_metrics_timestamp ON composition_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_composition_metrics_f1 ON composition_metrics(macro_f1);
CREATE INDEX IF NOT EXISTS idx_composition_metrics_precision ON composition_metrics(macro_precision);
CREATE INDEX IF NOT EXISTS idx_composition_metrics_recall ON composition_metrics(macro_recall);
