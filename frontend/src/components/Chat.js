import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "../styles/Chat.css";

function Chat() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
    
        const userMessage = { role: "user", content: input };
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setIsLoading(true);
    
        try {
            const response = await axios.post("http://localhost:5000/api/chat", {
                message: input,
            });
    
            let assistantMessageContent = response.data.response[0]?.text?.value || "There was an error processing the message content.";
    
            // Loop to remove all occurrences of 【...】
            while (assistantMessageContent.includes("【")) {
                assistantMessageContent = assistantMessageContent.replace(/【[^】]*】/, '');
            }
    
            // Trim any extra whitespace that might be left after removing patterns
            assistantMessageContent = assistantMessageContent.trim();
    
            const botMessage = { role: "assistant", content: assistantMessageContent };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (error) {
            console.error("Error communicating with backend:", error);
            const errorMessage = { role: "assistant", content: "There was an error processing your message." };
            setMessages((prevMessages) => [...prevMessages, errorMessage]);
        } finally {
            setIsLoading(false);
            setInput("");
        }
    };
    
    
    
    

    return (
        <div className="chat-container">
            <div className="chat-messages">
                {messages.map((msg, index) => (
                <p key={index} className={`chat-message ${msg.role}`}>
                    {typeof msg.content === "string" ? msg.content : JSON.stringify(msg.content)}
                </p>
                ))}

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
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    className="chat-submit"
                    disabled={isLoading}
                >
                    {isLoading ? "Sending..." : "Send"}
                </button>
            </form>
        </div>
    );
}

export default Chat;
