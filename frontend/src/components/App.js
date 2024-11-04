import React, { useState } from "react";
import Chat from "./Chat";
import Login from "./Login";

/**
 * App component handles user authentication and conditional rendering.
 * 
 * @returns JSX.Element
 */
function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    /**
     * Function to authenticate user by setting the authentication state.
     * @param {boolean} authStatus - User authentication status.
     */
    const handleAuthentication = (authStatus) => {
        setIsAuthenticated(authStatus);
    };

    return (
        <div className="app-container">
            {isAuthenticated ? <Chat /> : <Login onAuthenticate={handleAuthentication} />}
        </div>
    );
}

export default App;
