//src/App.jsx

import { useState, useEffect } from 'react';
import VideoCard from './components/VideoCard';
import SearchForm from './components/SearchForm';
import './App.css';

function App() {
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nextPageToken, setNextPageToken] = useState(null);
  const [totalResults, setTotalResults] = useState(0);
  
  // Filter states
  const [filters, setFilters] = useState({
    minDate: '',
    maxDate: '',
    minViews: '',
    channelName: ''
  });
  
  const handleSearch = async (searchKeyword, searchFilters) => {
    if (!searchKeyword.trim()) return;
    
    setKeyword(searchKeyword);
    setFilters(searchFilters);
    setLoading(true);
    setError(null);
    setResults([]);
    setNextPageToken(null);
    
    try {
      const params = new URLSearchParams();
      params.append('keyword', searchKeyword);
      
      if (searchFilters.minDate) params.append('min_date', searchFilters.minDate);
      if (searchFilters.maxDate) params.append('max_date', searchFilters.maxDate);
      if (searchFilters.minViews) params.append('min_views', searchFilters.minViews);
      if (searchFilters.channelName) params.append('channel_name', searchFilters.channelName);
      
      const response = await fetch(`/api/search?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      
      const data = await response.json();
      setResults(data.videos);
      setNextPageToken(data.next_page_token);
      setTotalResults(data.total_results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const loadMore = async () => {
    if (!nextPageToken || loading) return;
    
    setLoading(true);
    
    try {
      const params = new URLSearchParams();
      params.append('keyword', keyword);
      params.append('page_token', nextPageToken);
      
      if (filters.minDate) params.append('min_date', filters.minDate);
      if (filters.maxDate) params.append('max_date', filters.maxDate);
      if (filters.minViews) params.append('min_views', filters.minViews);
      if (filters.channelName) params.append('channel_name', filters.channelName);
      
      const response = await fetch(`/api/search?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      
      const data = await response.json();
      setResults([...results, ...data.videos]);
      setNextPageToken(data.next_page_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 shadow-md">
        <div className="container mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-white">YouTube Brand Mentions Finder</h1>
        </div>
      </header>
      
      <main className="container mx-auto py-8 px-4">
        <SearchForm onSearch={handleSearch} />
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            <p>{error}</p>
          </div>
        )}
        
        {results.length > 0 && (
          <div className="mb-4">
            <p className="text-gray-600">
              Found {totalResults} videos mentioning "{keyword}"
            </p>
          </div>
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results.map((video) => (
            <VideoCard key={video.id} video={video} keyword={keyword} />
          ))}
        </div>
        
        {loading && (
          <div className="flex justify-center my-8">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
          </div>
        )}
        
        {nextPageToken && !loading && (
          <div className="flex justify-center mt-8">
            <button
              className="px-6 py-2 bg-gray-200 text-gray-800 font-medium rounded-lg hover:bg-gray-300 transition duration-200"
              onClick={loadMore}
            >
              Load More
            </button>
          </div>
        )}
        
        {results.length === 0 && !loading && keyword && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No results found for "{keyword}"</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;