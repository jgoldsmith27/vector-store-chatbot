import React, { useState } from "react";
import axios from "axios";

function Chat() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState([]);

    /**
     * Handles form submission, sends message to the backend, and waits for a response.
     * @param {Event} e - form submission event.
     */
    const handleSubmit = async (e) => {
        e.preventDefault();

        const userMessage = { role: "user", content: input };
        setMessages((prevMessages) => [...prevMessages, userMessage]);

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
        } finally {
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
            </div>
            <form onSubmit={handleSubmit} className="chat-form">
                <input
                    type="text"
                    placeholder="Type your message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="chat-input"
                />
                <button type="submit" className="chat-submit">Send</button>
            </form>
        </div>
    );
}

export default Chat;