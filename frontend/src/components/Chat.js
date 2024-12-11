import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/Chat.css";
import Notification from "./Notification";

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ message: "", type: "" });

  const createThread = async () => {
    //TODO: Implement logic to delete old thread if there was one
    try {
      setLoading(true);
      const response = await axios.post("http://127.0.0.1:8080/create-thread/");
      setThreadId(response.data.thread_id);
      setMessages([]);
      showNotification("New chat thread created!", "success");
      setLoading(false);
    } catch (error) {
      console.error("Error creating thread:", error);
      showNotification(
        "Failed to create a new thread. Please try again.",
        "error"
      );
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!threadId) {
      showNotification("Please create a new chat thread first!", "error");
      return;
    }

    if (!input.trim()) {
      showNotification("Message cannot be empty.", "error");
      return;
    }

    try {
      const userMessage = { role: "user", content: input };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");

      setLoading(true);

      const response = await axios.post("http://127.0.0.1:8080/ask-question/", {
        thread_id: threadId,
        question: input,
      });

      let assistantContent = response.data.response;

      if (typeof assistantContent === "object" && assistantContent.value) {
        assistantContent = assistantContent.value;
      }

      // Get citations if available
      const citations = response.data.citations || [];

      const assistantMessage = {
        role: "assistant",
        content: assistantContent,
        citations: citations,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      setLoading(false);
    } catch (error) {
      console.error("Error sending message:", error);
      showNotification(
        "Failed to send the message. Please try again.",
        "error"
      );
      setLoading(false);
    }
  };

  const showNotification = (message, type) => {
    setNotification({ message, type });

    // Automatically clear notification after 5 seconds
    setTimeout(() => {
      setNotification({ message: "", type: "" });
    }, 5000);
  };

  return (
    <div className="chat-container">
      {/* Notification */}
      {notification.message && (
        <Notification message={notification.message} type={notification.type} />
      )}

      {/* Chat Messages */}
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`chat-message ${
              message.role === "user" ? "user" : "assistant"
            }`}
          >
            {message.content}
            {message.citations && message.citations.length > 0 && (
              <div className="citations">
                <strong>
                  <br></br>Citations:
                </strong>
                <ul>
                  {message.citations.map((citation, i) => (
                    <li key={i}>{citation}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="loading-indicator">
            <div className="loading-message"></div>
          </div>
        )}
      </div>

      {/* Chat Form */}
      <div className="chat-form">
        <input
          type="text"
          className="chat-input"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !loading) {
              e.preventDefault();
              sendMessage();
            }
          }}
          disabled={loading}
        />
        <button
          className="chat-submit"
          onClick={sendMessage}
          disabled={loading}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </div>

      {/* New Chat Button */}
      <button
        className="new-chat-button"
        onClick={createThread}
        disabled={loading}
      >
        New Chat
      </button>
    </div>
  );
}

export default Chat;
