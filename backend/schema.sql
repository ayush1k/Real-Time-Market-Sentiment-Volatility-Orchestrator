-- ClickHouse DDL for market sentiment data
CREATE TABLE IF NOT EXISTS market_sentiment (
    timestamp DateTime64(3, 'UTC'),
    ticker String,
    headline String,
    sentiment_score Float32,
    volatility_drivers Array(String),
    content String
) ENGINE = MergeTree()
ORDER BY (ticker, timestamp);
