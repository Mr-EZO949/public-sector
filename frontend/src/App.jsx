import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [links, setLinks] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError("Per favore, inserisci una domanda prima di inviare.");
      return;
    }
    setError(null);
    setResponse("Elaborazione della tua richiesta...");
    setLinks([]);

    try {
      const res = await axios.post('http://localhost:5000/query', { query });
      setResponse(res.data.answer);
      setLinks(res.data.links || []);
    } catch (error) {
      setResponse("Si è verificato un errore durante l'elaborazione della tua richiesta.");
      console.error("Errore nel recupero dei dati dal backend:", error);
    }
  };

  return (
    <div className="flex flex-col items-center min-h-screen bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white font-sans p-6">
      <div className="w-full max-w-2xl flex flex-col items-center">
        <h1 className="text-4xl font-bold mb-8 text-center text-gradient bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400">
          Assistente per i Servizi Pubblici
        </h1>

        <div className="flex flex-col items-center space-y-4 mb-6 w-full px-4">
          <input
            type="text"
            placeholder="Chiedi informazioni su tasse, residenza, sanità e altro..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full p-3 bg-gray-700 border border-gray-600 rounded-full text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={handleSubmit}
            className="w-full bg-gradient-to-r from-purple-500 to-blue-500 text-white py-3 rounded-full hover:from-purple-600 hover:to-blue-600 transition-all"
          >
            Invia
          </button>
        </div>

        {error && <p className="text-red-400 mb-4">{error}</p>}

        <div className="w-full bg-gray-700 p-6 rounded-3xl shadow-lg mb-8">
          <h2 className="text-xl font-semibold mb-2 text-purple-300">Risposta:</h2>
          <p className="text-gray-200 whitespace-pre-line">{response}</p>

          {links.length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold mb-2 text-purple-300">Fonti:</h3>
              <ul className="list-disc list-inside text-blue-400">
                {links.map((link, index) => (
                  <li key={index}>
                    <a href={link} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
