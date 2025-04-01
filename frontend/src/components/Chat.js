import React, { useState } from "react";
import axios from "axios";
import "../styles/Chat.css";
import Notification from "./Notification";
import { useOktaAuth } from "@okta/okta-react";

function Chat() {
  const { oktaAuth } = useOktaAuth();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ message: "", type: "" });
  const [modelType, setModelType] = useState("4o");

  const createThread = async () => {
    //TODO: Implement logic to delete old thread if there was one
    try {
      setLoading(true);
      const response = await axios.post(
        "https://skid-msche-chatbot.us.reclaim.cloud/api/create-thread"
      );
      console.log("Response: ");
      console.log(response);
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

  const handleModelChange = async (e) => {
    const selectedModel = e.target.value;
    setModelType(selectedModel);

    try {
      // 1. Update the active model on the backend
      await axios.post("http://127.0.0.1:8080/set-model", {
        model_type: selectedModel,
      });

      // 2. Create a new thread tied to that model
      await createThread();
    } catch (error) {
      console.error("Error switching model and creating thread:", error);
      showNotification("Failed to switch model or create new thread.", "error");
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

      const response = await axios.post(
        "https://skid-msche-chatbot.us.reclaim.cloud/api/ask-question",
        {
          thread_id: threadId,
          question: input,
        }
      );

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
        {/* Model Select */}
        <div className="model-select-container">
          <select
            className="model-select"
            value={modelType}
            onChange={handleModelChange}
            disabled={loading}
          >
            <option value="4o">4o Model</option>
            <option value="4o-mini">4o-mini Model</option>
          </select>
        </div>

        {/* Text Input */}
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
        />

        {/* Chat Submit Button */}
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
      {/* Log Out Button */}
      <button
        className="logout-button"
        onClick={() => oktaAuth.signOut()}
        disabled={loading}
      >
        Log Out
      </button>
    </div>
  );
}

export default Chat;
