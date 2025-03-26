import React, { useEffect, useState } from "react";
import RequireAuth from "./RequireAuth";
import Chat from "./Chat";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { Security, LoginCallback } from "@okta/okta-react";
import { OktaAuth } from "@okta/okta-auth-js";
import "../styles/App.css";

/**
 * App component securely fetches Okta config before initializing authentication.
 */
function App() {
  const [oktaConfig, setOktaConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch Okta configuration securely from backend
  useEffect(() => {
    fetch("https://skid-msche-chatbot.us.reclaim.cloud/api/auth-config")
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to fetch Okta config");
        }
        return res.json();
      })
      .then((data) => {
        setOktaConfig(data);
      })
      .catch((err) => {
        console.error("Error loading Okta config:", err);
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, []);

  // Show loading or error message before initializing authentication
  if (loading)
    return (
      <div className="loading-container">
        <div className="loading-message"></div>
        <h2>Loading Okta configuration...</h2>
      </div>
    );

  if (error)
    return (
      <div className="loading-container">
        <h2>Error: {error}</h2>
      </div>
    );

  // Initialize OktaAuth with fetched config
  const oktaAuth = new OktaAuth(oktaConfig);

  return (
    <Router basename="/">
      <Security
        oktaAuth={oktaAuth}
        restoreOriginalUri={async (_oktaAuth, originalUri) => {
          window.location.replace(originalUri || "/");
        }}
      >
        <div>
          <Routes>
            <Route
              path="/"
              element={
                <RequireAuth>
                  <Chat />
                </RequireAuth>
              }
            />
            <Route path="/login/callback" element={<LoginCallback />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Security>
    </Router>
  );
}

export default App;










