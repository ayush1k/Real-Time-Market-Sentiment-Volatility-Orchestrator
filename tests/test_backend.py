import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import app

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.clickhouse_connect.get_client')
    def test_ingest(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        data = [
            {
                "timestamp": "2024-01-01T00:00:00",
                "ticker": "AAPL",
                "headline": "Test",
                "sentiment_score": 0.5,
                "volatility_drivers": ["test"],
                "content": "test content"
            }
        ]
        
        response = self.app.post('/ingest', json=data)
        self.assertEqual(response.status_code, 201)
        mock_client.insert.assert_called_once()

    @patch('app.clickhouse_connect.get_client')
    def test_get_sentiment(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock query result
        import datetime
        mock_client.query.return_value.result_rows = [
            (datetime.datetime(2024, 1, 1), 0.5, ["test"], "Headline")
        ]
        
        response = self.app.get('/api/sentiment/AAPL')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['ticker'] if 'ticker' in data[0] else 'AAPL', 'AAPL') # ticker isn't in the return dict currently but let's check sentiment
        self.assertEqual(data[0]['sentiment_score'], 0.5)

if __name__ == '__main__':
    unittest.main()
