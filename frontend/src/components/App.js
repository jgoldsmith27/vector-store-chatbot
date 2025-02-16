import React, { useEffect } from "react";
import Chat from "./Chat";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { Security, LoginCallback, useOktaAuth } from "@okta/okta-react";
import { OktaAuth } from "@okta/okta-auth-js";
import oktaConfig from "../services/oktaConfig";

const oktaAuth = new OktaAuth(oktaConfig);

// Custom component to handle authentication redirect
const RequireAuth = ({ children }) => {
  const { authState, oktaAuth } = useOktaAuth();
  console.log("AuthState:", authState);
  console.log("OktaAuth:", oktaAuth);

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
 * App component handles user authentication and conditional rendering.
 *
 * @returns JSX.Element
 */
function App() {
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
            {/* Redirect to Okta login before showing the Chat */}
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
