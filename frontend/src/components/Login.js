import React, { useState } from "react";
import { authenticateUser } from "../services/authService";

/**
 * Login component for user password authentication.
 * 
 * @param {Function} onAuthenticate - Function to update authentication state in App.
 * @returns JSX.Element
 */
function Login({ onAuthenticate }) {
    const [password, setPassword] = useState("");

    /**
     * Handles form submission for password authentication.
     * @param {Event} e - form submission event.
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const isAuthenticated = await authenticateUser(password);
            if (isAuthenticated) {
                onAuthenticate(true);
                alert("Login successful");
            } else {
                alert("Incorrect password. Please try again.");
            }
        } catch (error) {
            console.error("Login error:", error);
            alert("An error occurred. Please try again.");
        }
    };

    return (
        <div className="login-container">
            <form onSubmit={handleSubmit} className="login-form">
                <h2>Login</h2>
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="login-input"
                />
                <button type="submit" className="login-submit">Login</button>
            </form>
        </div>
    );
}

export default Login;