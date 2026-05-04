import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [ticker, setTicker] = useState('AAPL');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async (selectedTicker) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/api/sentiment/${selectedTicker}`);
      if (!response.ok) throw new Error('Failed to fetch data');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(ticker);
  }, [ticker]);

  return (
    <div className="min-h-screen bg-gray-100 p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8 flex justify-between items-center bg-white p-6 rounded-lg shadow-md">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Market Sentiment Orchestrator</h1>
            <p className="text-gray-600">Real-time analysis of volatility drivers</p>
          </div>
          <div className="flex space-x-4">
            {['AAPL', 'MSFT'].map((t) => (
              <button
                key={t}
                onClick={() => setTicker(t)}
                className={`px-4 py-2 rounded-md font-semibold transition ${
                  ticker === t ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </header>

        {loading && <div className="text-center py-10">Loading sentiment data...</div>}
        {error && <div className="text-center py-10 text-red-600 font-bold">Error: {error}</div>}

        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4 text-gray-800 border-b pb-2">Sentiment Trend</h2>
              <div className="space-y-4">
                {data.length === 0 ? (
                  <p className="text-gray-500 italic">No data available for {ticker}</p>
                ) : (
                  data.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md border">
                      <div className="flex-1">
                        <p className="font-semibold text-gray-800 text-sm">{item.headline}</p>
                        <p className="text-xs text-gray-500">{new Date(item.timestamp).toLocaleString()}</p>
                      </div>
                      <div className={`ml-4 px-3 py-1 rounded-full text-sm font-bold ${
                        item.sentiment_score > 0 ? 'bg-green-100 text-green-700' : 
                        item.sentiment_score < 0 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {item.sentiment_score.toFixed(2)}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4 text-gray-800 border-b pb-2">Volatility Drivers</h2>
              <div className="flex flex-wrap gap-2">
                {data.length === 0 ? (
                  <p className="text-gray-500 italic">No drivers identified</p>
                ) : (
                  Array.from(new Set(data.flatMap(d => d.volatility_drivers))).map((driver, idx) => (
                    <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-md text-sm border border-purple-200">
                      {driver}
                    </span>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
