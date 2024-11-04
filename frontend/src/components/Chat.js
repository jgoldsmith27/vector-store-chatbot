import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "../styles/Chat.css";

function Chat() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    /**
     * Scroll to the bottom of the chat when a new message is added.
     */
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    /**
     * Handles form submission, sends message to the backend, and waits for a response.
     * @param {Event} e - form submission event.
     */
    const handleSubmit = async (e) => {
        e.preventDefault();

        const userMessage = { role: "user", content: input };
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setIsLoading(true);  // Set loading state to true

        try {
            // Send the user's message to the backend
            const response = await axios.post("http://localhost:5000/api/chat", {
                message: input
            });

            // Display the backend's response
            const botMessage = { role: "assistant", content: response.data.response };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (error) {
            console.error("Error communicating with backend:", error);
            const errorMessage = { role: "assistant", content: "There was an error processing your message." };
            setMessages((prevMessages) => [...prevMessages, errorMessage]);
        } finally {
            setIsLoading(false);  // Set loading state to false
            setInput("");
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <p
                        key={index}
                        className={`chat-message ${msg.role}`}
                    >
                        {msg.content}
                    </p>
                ))}
                {/* Display a loading message when waiting for a response */}
                {isLoading && <p className="loading-message"></p>}
                <div ref={messagesEndRef} />
            </div>
            <form onSubmit={handleSubmit} className="chat-form">
                <input
                    type="text"
                    placeholder="Type your message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="chat-input"
                    disabled={isLoading} // Disable input when loading
                />
                <button
                    type="submit"
                    className="chat-submit"
                    style={{
                        backgroundColor: isLoading ? "#ddd" : "#007BFF",
                        cursor: isLoading ? "not-allowed" : "pointer"
                    }}
                    disabled={isLoading} // Disable button when loading
                >
                    {isLoading ? "Sending..." : "Send"}
                </button>
            </form>
        </div>
    );
}

export default Chat;