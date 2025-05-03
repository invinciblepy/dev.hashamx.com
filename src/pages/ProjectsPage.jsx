import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { host } from "../host";

function ProjectsPage() {
  const { scraperName } = useParams();
  const navigate = useNavigate();

  const [scraperConfig, setScraperConfig] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [hasRun, setHasRun] = useState(false);
  const [resultItems, setResultItems] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetch(`${host()}/api/scraper/${scraperName}`)
      .then(res => res.json())
      .then(config => {
        setScraperConfig(config);
        const initialData = {};
        config.fields.forEach(field => {
          initialData[field.name] = "";
        });
        setFormData(initialData);
      })
      .catch(err => console.error("Error loading config:", err));
  }, [scraperName]);

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleRunScraper = () => {
    const emptyFields = Object.entries(formData).filter(([_, v]) => !v.trim());
    if (emptyFields.length > 0) {
      setErrorMessage(`Please fill in all fields: ${emptyFields.map(([f]) => f).join(', ')}`);
      return;
    }

    setLoading(true);
    setHasRun(false);
    setResultItems([]);
    setErrorMessage("");

    fetch(`${host()}/api/run-scraper`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scraper: scraperName, data: formData }),
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to start scraper");
        return res.json();
      })
      .then(({ task_id }) => {
        const interval = setInterval(() => {
          fetch(`${host()}/api/status/${task_id}`)
            .then(res => res.json())
            .then(statusData => {
              if (statusData.status === "done") {
                clearInterval(interval);
                setResultItems(statusData.data?.items || []);
                setHasRun(true);
                setLoading(false);
              } else if (statusData.status === "error") {
                clearInterval(interval);
                setErrorMessage(statusData.error || "Unknown error");
                setLoading(false);
              }
            })
            .catch(err => {
              clearInterval(interval);
              setErrorMessage("Polling failed: " + err.message);
              setLoading(false);
            });
        }, 5000);
      })
      .catch(err => {
        setErrorMessage("Failed to start scraper: " + err.message);
        setLoading(false);
      });
  };

  const capitalize = s => s.charAt(0).toUpperCase() + s.slice(1);

  return (
    <div className="scraper-page">
      {scraperConfig && (
        <>
          <div className="scraper-header">
            <h2 className="scraper-title">🧩 {scraperConfig.name}</h2>
            <p className="scraper-description">{scraperConfig.description}</p>
          </div>

          <div className="scraper-form">
            {scraperConfig.fields.map((field, idx) => (
              <div key={idx} className="form-group">
                <label>{field.label}</label>
                <input
                  type={field.type}
                  name={field.name}
                  placeholder={field.placeholder}
                  value={formData[field.name] || ""}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  className="form-input"
                  required
                />
              </div>
            ))}
          </div>

          <div className="button-group">
            <button onClick={() => navigate("/")} className="btn btn-secondary">
              ← Back to Home
            </button>
            <button onClick={handleRunScraper} className="btn btn-primary" disabled={loading}>
              {loading ? "Running..." : "Run Scraper"}
            </button>
          </div>

          {errorMessage && (
            <p className="error-message">⚠️ {errorMessage}</p>
          )}

          {hasRun && resultItems.length > 0 && (
            <>
              <p className="results-note">
                ⚠️ This is a demo version. More scrapers on{' '}
                <a href="https://github.com/invinciblepy" target="_blank" rel="noopener noreferrer">GitHub</a>.
              </p>
              <div className="table-container">
                <table className="results-table">
                  <thead>
                    <tr>
                      {scraperConfig.header.map((key) => (
                        <th key={key}>{capitalize(key)}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {resultItems.map((item, idx) => (
                      <tr key={idx}>
                        {scraperConfig.header.map((key) => {
                          const value = item[key] || "";
                          const shortValue = value.length > 30 ? value.slice(0, 27) + "..." : value;
                          return (
                            <td key={key} title={value}>{shortValue}</td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
          {hasRun && resultItems.length === 0 && !loading && (
            <p className="no-results">No results found.</p>
          )}
        </>
      )}
    </div>
  );
}

export default ProjectsPage;
