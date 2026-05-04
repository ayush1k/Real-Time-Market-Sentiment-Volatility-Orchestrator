from flask import Flask, request, jsonify
from flask_cors import CORS
import clickhouse_connect
import os

app = Flask(__name__)
CORS(app) # Enable CORS for React frontend

# ClickHouse connection settings
CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')
CLICKHOUSE_PORT = int(os.getenv('CLICKHOUSE_PORT', 8123))
CLICKHOUSE_USER = os.getenv('CLICKHOUSE_USER', 'default')
CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD', '')

def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD
    )

@app.route('/ingest', methods=['POST'])
def ingest():
    data = request.json
    if not isinstance(data, list):
        data = [data]
    
    client = get_clickhouse_client()
    
    rows = []
    for item in data:
        rows.append([
            item['timestamp'],
            item['ticker'],
            item['headline'],
            item.get('sentiment_score', 0.0),
            item.get('volatility_drivers', []),
            item['content']
        ])
    
    client.insert('market_sentiment', rows, column_names=[
        'timestamp', 'ticker', 'headline', 'sentiment_score', 'volatility_drivers', 'content'
    ])
    
    return jsonify({"status": "success", "count": len(rows)}), 201

@app.route('/api/sentiment/<ticker>', methods=['GET'])
def get_sentiment(ticker):
    client = get_clickhouse_client()
    
    query = f"SELECT timestamp, sentiment_score, volatility_drivers, headline FROM market_sentiment WHERE ticker = '{ticker}' ORDER BY timestamp DESC LIMIT 100"
    result = client.query(query)
    
    data = []
    for row in result.result_rows:
        data.append({
            "timestamp": row[0].isoformat(),
            "sentiment_score": row[1],
            "volatility_drivers": row[2],
            "headline": row[3]
        })
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
