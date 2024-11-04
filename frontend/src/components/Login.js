import React, { useState } from "react";
import { authenticateUser } from "../services/authService";
import Notification from "./Notification";
import "../styles/Login.css";

function Login({ onAuthenticate }) {
    const [password, setPassword] = useState("");
    const [notification, setNotification] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const isAuthenticated = await authenticateUser(password);
            if (isAuthenticated) {
                onAuthenticate(true);
                setNotification({ message: "Login successful!", type: "success" });
            } else {
                setNotification({ message: "Incorrect password. Please try again.", type: "error" });
            }
        } catch (error) {
            console.error("Login error:", error);
            setNotification({ message: "An error occurred. Please try again.", type: "error" });
        }
    };

    return (
        <div className="login-container">
            <form onSubmit={handleSubmit} className="login-form">
                <h2>Welcome Back</h2>
                <input
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="login-input"
                />
                <button type="submit" className="login-submit">Login</button>
            </form>
            {notification && (
                <Notification
                    message={notification.message}
                    type={notification.type}
                    onClose={() => setNotification(null)}
                />
            )}
        </div>
    );
}

export default Login;