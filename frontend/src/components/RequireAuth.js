import React, { useEffect } from "react";
import { useOktaAuth } from "@okta/okta-react";
import "../styles/App.css";

const RequireAuth = ({ children }) => {
  const { authState, oktaAuth } = useOktaAuth();

  useEffect(() => {
    if (authState && !authState.isAuthenticated) {
      oktaAuth.signInWithRedirect();
    }
  }, [authState, oktaAuth]);

  if (!authState) {
    return (
      <div className="loading-container">
        <div className="loading-message"></div>
        <h2>Loading authentication...</h2>
      </div>
    );
  }

  return authState.isAuthenticated ? children : null;
};

export default RequireAuth;
