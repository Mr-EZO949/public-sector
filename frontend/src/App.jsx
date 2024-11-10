import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError("Please enter a question before submitting.");
      return;
    }
    setError(null);
    setResponse("Processing your request...");

    try {
      const res = await axios.post('http://localhost:5000/query', { query });
      setResponse(res.data.answer);
    } catch (error) {
      setResponse("There was an error processing your request.");
      console.error("Error fetching data from backend:", error);
    }
  };

  return (
    <div className="flex flex-col items-center min-h-screen bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white font-sans p-6">
      <div className="w-full max-w-2xl flex flex-col items-center">
        <h1 className="text-4xl font-bold mb-8 text-center text-gradient bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400">
          Public Service Assistant
        </h1>
        
        <div className="flex flex-col items-center space-y-4 mb-6 w-full px-4">
          <input
            type="text"
            placeholder="Ask about taxes, residency, healthcare, and more..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={handleSubmit}
            className="w-full bg-gradient-to-r from-purple-500 to-blue-500 text-white py-3 rounded-full hover:from-purple-600 hover:to-blue-600 transition-all"
          >
            Submit
          </button>
        </div>

        {error && <p className="text-red-400 mb-4">{error}</p>}

        <div className="w-full bg-gray-700 p-6 rounded-3xl shadow-lg mb-8">
          <h2 className="text-xl font-semibold mb-2 text-purple-300">Response:</h2>
          <p className="text-gray-200">{response}</p>
        </div>
      </div>
    </div>
  );
}

export default App;
