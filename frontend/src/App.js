import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("drivers");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRound, setSelectedRound] = useState("");

  const apiUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";

  useEffect(() => {
    if (activeTab !== "result_chart") {
      fetchData(activeTab);
    }
  }, [activeTab, selectedRound]);

  const fetchData = (endpoint) => {
    setLoading(true);
    setError(null);

    let url = `${apiUrl}/${endpoint}`;

    if (endpoint === "results_2025" && selectedRound) {
      url += `?round=${selectedRound}`;
    }

    fetch(url)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP Error: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(`Błąd ładowania danych (${endpoint}):`, err);
        setError(`Nie udało się załadować danych: ${err.message}`);
        setLoading(false);
      });
  };

  const handleRefresh = () => {
    fetch(`${apiUrl}/refresh`)
      .then((res) => res.json())
      .then((data) => {
        alert(data.message);
        fetchData(activeTab);
      })
      .catch((err) => {
        console.error("Błąd odświeżania danych:", err);
        alert("Wystąpił błąd podczas odświeżania danych");
      });
  };

  const renderContent = () => {
    if (loading) {
      return <div className="loading">Ładowanie danych...</div>;
    }

    if (error) {
      return <div className="error">{error}</div>;
    }

    switch (activeTab) {
      case "drivers":
        return (
          <div className="drivers-container">
            <h2>Lista kierowców</h2>
            {data && data.length > 0 ? (
              <div className="drivers-grid">
                {data.map((driver, index) => (
                  <div key={index} className="driver-card">
                    <div className="driver-number">
                      {driver.driver_number || "?"}
                    </div>
                    <h3>{driver.full_name || "Nieznany kierowca"}</h3>
                    <p className="team-name">
                      {driver.team_name || "Brak zespołu"}
                    </p>
                    {driver.country_code && (
                      <p className="driver-country">
                        Kraj: {driver.country_code}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-data">
                Brak danych o kierowcach do wyświetlenia
              </div>
            )}
          </div>
        );

      case "teams":
        return (
          <div className="teams-container">
            <h2>Zespoły F1</h2>
            {data && data.length > 0 ? (
              <div className="teams-grid">
                {data.map((team, index) => (
                  <div key={index} className="team-card">
                    <h3>{team.team_name || "Nieznany zespół"}</h3>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-data">
                Brak danych o zespołach do wyświetlenia
              </div>
            )}
          </div>
        );

      case "results_2025":
        return (
          <div className="results-container">
            <h2>Wyniki sezonu 2025</h2>

            <div className="filter-section">
              <label htmlFor="round-select">Wybierz rundę:</label>
              <select
                id="round-select"
                value={selectedRound}
                onChange={(e) => setSelectedRound(e.target.value)}
              >
                <option value="">Wszystkie rundy</option>
                {[...Array(23)].map((_, i) => (
                  <option key={i + 1} value={i + 1}>
                    Runda {i + 1}
                  </option>
                ))}
              </select>
            </div>

            {data && data.length > 0 ? (
              <div className="results-table-container">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Wyścig</th>
                      <th>Pozycja</th>
                      <th>Kierowca</th>
                      <th>Konstruktor</th>
                      <th>Czas</th>
                      <th>Status</th>
                      <th>Punkty</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.map((result, index) => (
                      <tr key={index}>
                        <td>
                          {result.raceName} (R{result.round})
                          <div className="race-date">{result.date}</div>
                        </td>
                        <td className="position-cell">{result.position}</td>
                        <td>
                          <div className="driver-name">
                            {result.Driver?.givenName}{" "}
                            {result.Driver?.familyName}
                          </div>
                          <div className="driver-code">
                            {result.Driver?.code}
                          </div>
                        </td>
                        <td>{result.Constructor?.name}</td>
                        <td>{result.Time?.time || "-"}</td>
                        <td>{result.status}</td>
                        <td className="points-cell">{result.points}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="no-data">
                Brak danych do wyświetlenia dla wybranej rundy
              </div>
            )}
          </div>
        );

      case "result_chart":
        return (
          <div className="chart-container">
            <h2>Punktacja kierowców</h2>
            <iframe
              src="http://localhost:3000/d-solo/bekscsrvux4owc/driverpoints?orgId=1&from=1746273346193&to=1746294946193&timezone=browser&panelId=1&__feature.dashboardSceneSolo"
              width="900"
              height="400"
              frameborder="0"
            ></iframe>
          </div>
        );

      default:
        return <div>Wybierz zakładkę, aby zobaczyć dane</div>;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <span className="f1-logo">F1</span> Data Explorer
        </div>
        <button className="refresh-button" onClick={handleRefresh}>
          Odśwież dane
        </button>
      </header>

      <nav className="navbar">
        <ul>
          <li className={activeTab === "drivers" ? "active" : ""}>
            <button onClick={() => setActiveTab("drivers")}>Kierowcy</button>
          </li>
          <li className={activeTab === "teams" ? "active" : ""}>
            <button onClick={() => setActiveTab("teams")}>Zespoły</button>
          </li>
          <li className={activeTab === "results_2025" ? "active" : ""}>
            <button onClick={() => setActiveTab("results_2025")}>
              Wyniki 2025
            </button>
          </li>
          <li className={activeTab === "result_chart" ? "active" : ""}>
            <button onClick={() => setActiveTab("result_chart")}>
              Punkty kierowców
            </button>
          </li>
        </ul>
      </nav>

      <main className="content">{renderContent()}</main>

      <footer className="app-footer">
        <p>Maciej Lencewicz 245860</p>
      </footer>
    </div>
  );
}

export default App;
