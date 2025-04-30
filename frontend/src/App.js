import React, { useEffect, useState } from "react";

function App() {
  const [drivers, setDrivers] = useState([]);

  useEffect(() => {
    console.log("API URL:", process.env.REACT_APP_API_URL);  // Sprawdzanie zmiennej
    fetch(`${process.env.REACT_APP_API_URL}/drivers`)
      .then((res) => res.json())
      .then((data) => setDrivers(data))
      .catch((err) => console.error("Błąd ładowania danych:", err));
  }, []);

  return (
    <div>
      <h1>Kierowcy F1</h1>
      {drivers.length === 0 ? (
        <p>Ładowanie...</p>
      ) : (
        <ul>
          {drivers.map((driver, index) => (
            <li key={index}>
              {driver.full_name || "Brak imienia"} – {driver.team_name || "Brak zespołu"}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
