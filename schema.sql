CREATE TABLE IF NOT EXISTS user_optout (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS replied_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT,
    comment_id TEXT,
    UNIQUE(post_id, comment_id)
);

CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote TEXT,
    episode_name TEXT,
    wiki_url URL
);