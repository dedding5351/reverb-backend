-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY,
    phone_number VARCHAR(191) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_phone_number ON users (phone_number);

-- Posts Table
CREATE TABLE IF NOT EXISTS posts (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    url VARCHAR NOT NULL UNIQUE,
    description TEXT,
    authors JSON DEFAULT '[]',
    published_date TIMESTAMP,
    site_name VARCHAR,
    source_id VARCHAR,
    image_url VARCHAR,
    content TEXT,
    embedding vector(3072),
    read_time_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_posts_id ON posts (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_posts_url ON posts (url);

-- Likes Table
CREATE TABLE IF NOT EXISTS likes (
    user_id VARCHAR NOT NULL,
    post_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id),
    CONSTRAINT fk_likes_users FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_likes_posts FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
);

-- Bookmarks Table
CREATE TABLE IF NOT EXISTS bookmarks (
    user_id VARCHAR NOT NULL,
    post_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id),
    CONSTRAINT fk_bookmarks_users FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_bookmarks_posts FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
);
