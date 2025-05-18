import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { host } from "../host";

function ProjectsPage() {
  const { moduleName } = useParams();
  const navigate = useNavigate();

  const [moduleConfig, setModuleConfig] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [hasRun, setHasRun] = useState(false);
  const [resultItems, setResultItems] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetch(`${host()}/api/module/${moduleName}`)
      .then(res => res.json())
      .then(config => {
        setModuleConfig(config);
        const initialData = {};
        config.inputs.forEach(field => {
          initialData[field.name] = "";
        });
        setFormData(initialData);
      })
      .catch(err => console.error("Error loading config:", err));
  }, [moduleName]);

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleRunmodule = () => {
    const emptyFields = Object.entries(formData).filter(([_, v]) => !v.trim());
    if (emptyFields.length > 0) {
      setErrorMessage(`Please fill in all fields: ${emptyFields.map(([f]) => f).join(', ')}`);
      return;
    }

    setLoading(true);
    setHasRun(false);
    setResultItems([]);
    setErrorMessage("");

    fetch(`${host()}/api/run-module`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ module: moduleName, data: formData }),
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to start module");
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
        setErrorMessage("Failed to start module: " + err.message);
        setLoading(false);
      });
  };

  const capitalize = s => s.charAt(0).toUpperCase() + s.slice(1);

  return (
    <div className="scraper-page">
      {moduleConfig && (
        <>
          <div className="scraper-header">
            <h2 className="scraper-title">🧩 {moduleConfig.name}</h2>
            <p className="scraper-description">{moduleConfig.description}</p>
          </div>

          <div className="scraper-form">
            {moduleConfig.inputs.map((field, idx) => (
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
            <button onClick={handleRunmodule} className="btn btn-primary" disabled={loading}>
              {loading ? "Running..." : "Run module"}
            </button>
          </div>

          {errorMessage && (
            <p className="error-message">⚠️ {errorMessage}</p>
          )}

          {hasRun && resultItems.length > 0 && (
            <>
              <p className="results-note">
                ⚠️ This is a demo version. More modules on{' '}
                <a href={moduleConfig.repository} target="_blank" rel="noopener noreferrer">GitHub</a>.
              </p>
              <div className="table-container">
                <table className="results-table">
                  <thead>
                    <tr>
                      {moduleConfig.outputs.map((key) => (
                        <th key={key}>{capitalize(key)}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {resultItems.map((item, idx) => (
                      <tr key={idx}>
                        {moduleConfig.outputs.map((key) => {
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
