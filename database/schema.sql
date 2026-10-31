-- SQLite Schema for MY YOUTUBE CREATOR STUDIO (Repaired & Scaled Architecture)

CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    custom_url TEXT,
    description TEXT,
    subscriber_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    video_count INTEGER DEFAULT 0,
    profile_image TEXT,
    banner_image TEXT,
    data_source TEXT DEFAULT 'Public Ingestion',
    is_cached INTEGER DEFAULT 0,
    last_refreshed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data_json TEXT
);

CREATE TABLE IF NOT EXISTS channel_audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT NOT NULL,
    audit_score INTEGER NOT NULL,
    score_breakdown_json TEXT,
    audit_data_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS video_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL, -- 'upload' or 'url'
    video_id TEXT,
    file_name TEXT,
    file_size INTEGER DEFAULT 0,
    duration REAL DEFAULT 0.0,
    aspect_ratio TEXT,
    resolution TEXT,
    fps REAL DEFAULT 0.0,
    bitrate INTEGER DEFAULT 0,
    audio_channels INTEGER DEFAULT 0,
    sample_rate INTEGER DEFAULT 0,
    hook_score REAL DEFAULT 0.0,
    pacing_score REAL DEFAULT 0.0,
    readiness_score REAL DEFAULT 0.0,
    scores_json TEXT,
    analysis_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS competitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competitor_group TEXT DEFAULT 'default',
    channel_id TEXT UNIQUE NOT NULL,
    channel_title TEXT NOT NULL,
    handle TEXT,
    subscriber_count INTEGER DEFAULT 0,
    video_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    upload_frequency REAL DEFAULT 0.0,
    raw_data_json TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS publishing_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id TEXT,
    title TEXT NOT NULL,
    format_type TEXT DEFAULT 'Long-form',
    target_date TEXT,
    target_time TEXT,
    status TEXT DEFAULT 'Scheduled', -- 'Draft', 'Scheduled', 'Published'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assistant_chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    channel_id TEXT,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    message TEXT NOT NULL,
    context_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
