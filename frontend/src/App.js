import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

function App() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [availableGenres, setAvailableGenres] = useState([]);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [contentType, setContentType] = useState('movie'); // 'movie' or 'anime'

  // Fetch movies/anime function
  const fetchData = useCallback(() => {
    setLoading(true);

    // Construct query string
    const queryParams = new URLSearchParams();
    selectedGenres.forEach(genre => queryParams.append('selected_genres', genre));

    // Determine endpoint based on content type
    const endpoint = contentType === 'movie'
      ? '/api/movies/best-last-year'
      : '/api/anime/best-last-year';

    fetch(`${endpoint}?${queryParams.toString()}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        const newItems = data.movies || data.anime; // Handle both 'movies' and 'anime' keys
        setItems(newItems);

        // Update available genres based on the full list
        const counts = {};
        newItems.forEach(item => {
          if (item.genres) {
            item.genres.forEach((name) => {
               if (name) {
                   counts[name] = (counts[name] || 0) + 1;
               }
            });
          }
        });

        const newAvailableGenres = Object.keys(counts).map(name => ({
            name: name,
            count: counts[name],
            id: name
        })).sort((a, b) => a.name.localeCompare(b.name));

        setAvailableGenres(newAvailableGenres);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
        setError(error.message);
        setLoading(false);
      });
  }, [selectedGenres, contentType]);

  // Initial fetch and filter change
  useEffect(() => {
    fetchData();
  }, [selectedGenres, contentType, fetchData]);

  const handleGenreClick = (genreName) => {
    if (selectedGenres.includes(genreName)) {
      setSelectedGenres(selectedGenres.filter(g => g !== genreName));
    } else {
      setSelectedGenres([...selectedGenres, genreName]);
    }
  };

  const handleContentTypeChange = (type) => {
    if (type !== contentType) {
      setContentType(type);
      setSelectedGenres([]); // Reset filters when switching type
      setItems([]); // Clear current list
    }
  };

  const handleItemClick = (title) => {
    const query = encodeURIComponent(title + (contentType === 'movie' ? " movie" : " anime"));
    window.open(`https://www.google.com/search?q=${query}`, '_blank');
  };

  const handleStremioClick = (e, stremioUrl) => {
    e.stopPropagation(); // Prevent triggering the card click
    if (stremioUrl) {
        window.location.href = stremioUrl;
    }
  };

  if (error) return <div className="container">Error: {error}</div>;

  return (
    <div className="App">
      <header className="App-header">
        <h1>Best {contentType === 'movie' ? 'Movies' : 'Anime'} of the Last Year</h1>

        <div className="content-type-toggle">
          <button
            className={`type-btn ${contentType === 'movie' ? 'active' : ''}`}
            onClick={() => handleContentTypeChange('movie')}
          >
            Movies
          </button>
          <button
            className={`type-btn ${contentType === 'anime' ? 'active' : ''}`}
            onClick={() => handleContentTypeChange('anime')}
          >
            Anime
          </button>
        </div>

        <div className="genre-filter">
          <h3>Filter by Genre:</h3>
          <div className="genre-buttons">
            {availableGenres.map(genre => {
              const isSelected = selectedGenres.includes(genre.name);
              return (
                <button
                  key={genre.name}
                  onClick={() => handleGenreClick(genre.name)}
                  className={`genre-btn ${isSelected ? 'selected' : ''}`}
                >
                  {genre.name} ({genre.count})
                </button>
              );
            })}
          </div>
        </div>
      </header>

      <div className="item-list">
        {items.map((item, index) => (
          <div
            key={`${item.id}-${index}`}
            className="item-card"
            onClick={() => handleItemClick(item.title)}
          >
            <div className="item-content">
              {item.poster_url && (
                <img
                  src={item.poster_url}
                  alt={`${item.title} poster`}
                  className="item-poster"
                />
              )}
              <div className="item-details">
                <h2><span className="item-number">{index + 1}.</span> {item.title}</h2>
                <div className="item-info-row">
                  <span className="release-date">Released: {item.release_date}</span>
                </div>
                <div className="item-info-row">
                  <span className="rating">Rating: {item.rating}/10 ({item.votes} votes)</span>
                </div>
                <div className="item-info-row">
                  <span className="genres">Genres: {item.genres ? item.genres.join(', ') : 'N/A'}</span>
                </div>
                {item.stremio_url && (
                  <div className="item-actions">
                    <button
                        className="stremio-btn"
                        onClick={(e) => handleStremioClick(e, item.stremio_url)}
                        title="Watch on Stremio"
                    >
                        <img
                            src="https://stremio.com/website/stremio-logo-small.png"
                            alt="Stremio"
                            className="stremio-logo"
                        />
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
        </div>
      )}

      <footer className="App-footer">
        <p>Data provided by {contentType === 'movie' ? 'The Movie Database (TMDB)' : 'Jikan API (MyAnimeList)'}.</p>
      </footer>
    </div>
  );
}

export default App;
