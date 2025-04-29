CREATE DATABASE dbgetnews;

CREATE USER mono WITH PASSWORD 'Crypto888';

CREATE TABLE crypto_panic_news (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    source_url VARCHAR(255),
    source VARCHAR(50),
    published_at TIMESTAMP WITH TIME ZONE,
    tags TEXT,
    votes_positive INT,
    votes_negative INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE telegram_messages (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    username VARCHAR(255),
    message_text TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tweets (
    id SERIAL PRIMARY KEY,
    tweet_id BIGINT UNIQUE,
    username VARCHAR(255),
    text TEXT,
    created_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_published_at ON crypto_panic_news(published_at);
CREATE INDEX idx_source ON crypto_panic_news(source);

GRANT ALL PRIVILEGES ON DATABASE dbgetnews TO mono;