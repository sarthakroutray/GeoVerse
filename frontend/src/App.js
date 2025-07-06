import React from 'react';
import './styles/globals.css';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                GeoVerse 🌍
              </h1>
            </div>
            <nav className="flex items-center space-x-4">
              <a href="#" className="text-gray-500 hover:text-gray-700">
                Home
              </a>
              <a href="#" className="text-gray-500 hover:text-gray-700">
                Chat
              </a>
              <a href="#" className="text-gray-500 hover:text-gray-700">
                Search
              </a>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            AI-Powered Geospatial Data Assistant
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Ask questions about MOSDAC satellite data and earth observation information
          </p>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="max-w-md mx-auto">
              <input
                type="text"
                placeholder="Ask me about satellite data..."
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
                Ask Question
              </button>
            </div>
          </div>

          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">🛰️ Satellite Data</h3>
              <p className="text-gray-600">
                Access information about INSAT, SCATSAT, and other satellite missions
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">🌊 Ocean Data</h3>
              <p className="text-gray-600">
                Query sea surface temperature, ocean currents, and marine data
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2">🌡️ Weather Data</h3>
              <p className="text-gray-600">
                Get meteorological data and atmospheric measurements
              </p>
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500">
            GeoVerse - Built with ❤️ for advancing geospatial data accessibility
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
