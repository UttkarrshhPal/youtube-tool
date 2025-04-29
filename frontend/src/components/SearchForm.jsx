import { useState } from "react";

function SearchForm({ onSearch }) {
  const [keyword, setKeyword] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [minDate, setMinDate] = useState("");
  const [maxDate, setMaxDate] = useState("");
  const [minViews, setMinViews] = useState("");
  const [channelName, setChannelName] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!keyword.trim()) return;

    const filters = {
      minDate,
      maxDate,
      minViews,
      channelName,
    };

    onSearch(keyword, filters);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <form onSubmit={handleSubmit}>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-grow">
            <input
              type="text"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter brand name, website domain, or keyword"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
            />
          </div>
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition duration-200"
          >
            Search
          </button>
        </div>

        <div className="mt-4">
          <button
            type="button"
            className="text-blue-600 text-sm font-medium flex items-center"
            onClick={() => setShowFilters(!showFilters)}
          >
            {showFilters ? "Hide Filters" : "Show Filters"}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className={`h-4 w-4 ml-1 transition-transform ${
                showFilters ? "rotate-180" : ""
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>

          {showFilters && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Min Upload Date
                </label>
                <input
                  type="date"
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={minDate}
                  onChange={(e) => setMinDate(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Max Upload Date
                </label>
                <input
                  type="date"
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={maxDate}
                  onChange={(e) => setMaxDate(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Min Views
                </label>
                <input
                  type="number"
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="e.g. 1000"
                  value={minViews}
                  onChange={(e) => setMinViews(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Channel Name
                </label>
                <input
                  type="text"
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="e.g. TechReview"
                  value={channelName}
                  onChange={(e) => setChannelName(e.target.value)}
                />
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  );
}

export default SearchForm;
