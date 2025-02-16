import React, { useEffect, useState } from "react";
import Chat from "./Chat";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { Security, LoginCallback, useOktaAuth } from "@okta/okta-react";
import { OktaAuth } from "@okta/okta-auth-js";

/**
 * Custom component to handle authentication redirect.
 */
const RequireAuth = ({ children }) => {
  const { authState, oktaAuth } = useOktaAuth();
  //console.log("AuthState:", authState);
  //console.log("OktaAuth:", oktaAuth);

  useEffect(() => {
    if (authState && !authState.isAuthenticated) {
      oktaAuth.signInWithRedirect();
    }
  }, [authState, oktaAuth]);

  if (!authState) {
    return <h2>Loading authentication...</h2>;
  }

  return authState.isAuthenticated ? children : null;
};

/**
 * App component securely fetches Okta config before initializing authentication.
 */
function App() {
  const [oktaConfig, setOktaConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch Okta configuration securely from FastAPI backend
  useEffect(() => {
    fetch("http://127.0.0.1:8080/auth-config")
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to fetch Okta config");
        }
        return res.json();
      })
      .then((data) => {
        console.log("Fetched Okta Config:", data);
        setOktaConfig(data);
      })
      .catch((err) => {
        console.error("Error loading Okta config:", err);
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, []);

  // Show loading or error message before initializing authentication
  if (loading) return <h2>Loading Okta configuration...</h2>;
  if (error) return <h2>Error: {error}</h2>;

  // Initialize OktaAuth with fetched config
  const oktaAuth = new OktaAuth(oktaConfig);

  return (
    <Router>
      <Security
        oktaAuth={oktaAuth}
        restoreOriginalUri={async (_oktaAuth, originalUri) => {
          window.location.replace(originalUri || "/");
        }}
      >
        <div className="app-container">
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
