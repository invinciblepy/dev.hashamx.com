import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { host } from "../host";

function HomePage() {
  const navigate = useNavigate();
  const [modules, setModules] = useState([]);

  useEffect(() => {
    fetch(`${host()}/api/modules`)
      .then(response => response.json())
      .then(data => setModules(data))
      .catch(error => console.error('Error fetching modules:', error));
  }, []);

  return (
    <div className="app">
      <header className="hero-header header">
        <h1>👨‍💻 Welcome to <span className="brand">dev.hashamx.com</span> 🚀</h1>
        <p className="subtitle">
          Explore live Python modules, automation tools, and open-source projects — ready to run, right here in your browser. ⚙️🐍
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
        {modules.map((module, index) => (
          <div key={index} className="card-advanced" onClick={() => navigate(`/project/${module.name}`)}>
            <div className="card-icon">🛰️</div>
            <h3>{module.name}</h3>
            <p>{module.description}</p>
            <span className="badge">{module.premium ? "Premium" : "Free"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HomePage;
