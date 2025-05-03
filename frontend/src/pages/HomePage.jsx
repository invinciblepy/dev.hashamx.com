import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

function HomePage() {
  const navigate = useNavigate();
  const [scrapers, setScrapers] = useState([]);

  useEffect(() => {
    // Fetch scrapers from the backend API
    fetch('http://localhost:5000/api/scrapers')
      .then(response => response.json())
      .then(data => setScrapers(data))
      .catch(error => console.error('Error fetching scrapers:', error));
  }, []);

  return (
    <div className="app">
      <header className="hero-header header">
        <h1>👨‍💻 Welcome to <span className="brand">dev.hashamx.com</span> 🚀</h1>
        <p className="subtitle">
          Explore live Python scrapers, automation tools, and open-source projects — ready to run, right here in your browser. ⚙️🐍
        </p>
        <a
          href="https://github.com/invinciblepy"
          className="github-button"
          target="_blank"
          rel="noopener noreferrer"
        >
          ⭐ Check out my GitHub (@invinciblepy)
        </a>
      </header>
      <div className="cards">
        {scrapers.map((scraper, index) => (
          <div key={index} className="card-advanced" onClick={() => navigate(`/project/${scraper}`)}>
            <div className="card-icon">🛰️</div>
            <h3>{scraper}</h3>
            <p>Explore this scraper in real-time</p>
            <span className="badge">Live</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HomePage;
