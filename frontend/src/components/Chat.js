import React, { useState } from "react";
import axios from "axios";
import "../styles/Chat.css";
import Notification from "./Notification";
import ModelSwitchModal from "./ModelSwitchModal";
import FileUpload from "./FileUpload";
import { useOktaAuth } from "@okta/okta-react";
import ReactMarkdown from "react-markdown";
import "github-markdown-css/github-markdown.css";

function Chat() {
  const { oktaAuth } = useOktaAuth();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState({ message: "", type: "" });
  const [modelType, setModelType] = useState("4o");
  const [showModelWarning, setShowModelWarning] = useState(false);
  const [dontShowAgain, setDontShowAgain] = useState(
    localStorage.getItem("hideModelWarning") === "true"
  );
  const [pendingModelType, setPendingModelType] = useState(null);
  const [fileNames, setFileNames] = useState([]);

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
      setFileNames([]);
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

  const handleModelChange = (e) => {
    const selected = e.target.value;

    if (dontShowAgain) {
      switchModel(selected);
    } else {
      setPendingModelType(selected);
      setShowModelWarning(true);
    }
  };

  const switchModel = async (model) => {
    setModelType(model);
    try {
      await axios.post(
        "https://skid-msche-chatbot.us.reclaim.cloud/api/set-model",
        {
          model_type: model,
        }
      );
      await createThread(); // reset thread
    } catch (err) {
      console.error("Model switch error:", err);
      showNotification("Failed to switch model.", "error");
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

  const handleFileUpload = async (files) => {
    if (!threadId) {
      showNotification(
        "Please create a chat thread before uploading files.",
        "error"
      );
      return;
    }

    const newFiles = files.filter((file) => {
      if (fileNames.includes(file.name)) {
        showNotification(`"${file.name}" has already been uploaded.`, "error");
        return false;
      }
      return true;
    });

    if (newFiles.length === 0) return;

    setLoading(true);
    const uploaded = [];

    try {
      for (const file of newFiles) {
        const formData = new FormData();
        formData.append("file", file);

        const res = await axios.post(
          "https://skid-msche-chatbot.us.reclaim.cloud/api/upload",
          formData
        );
        const fileId = res.data.file_id;

        await axios.post(
          "https://skid-msche-chatbot.us.reclaim.cloud/api/attach-file",
          {
            thread_id: threadId,
            file_id: fileId,
          }
        );

        uploaded.push(file.name);
      }

      setFileNames((prev) => [...prev, ...uploaded]);
      showNotification(
        "File(s) uploaded and attached successfully!",
        "success"
      );
    } catch (err) {
      console.error("File upload error:", err);
      showNotification("One or more file uploads failed.", "error");
    } finally {
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

      {/* Chat Message */}
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`chat-message ${
              message.role === "user" ? "user" : "assistant"
            }`}
          >
            {message.role === "assistant" ? (
              <div className="markdown-body">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            ) : (
              message.content
            )}

            {message.citations && message.citations.length > 0 && (
              <div className="citations">
                <strong>
                  <br />
                  Citations:
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

        {/* File Upload */}
        <FileUpload
          fileNames={fileNames}
          onFileUpload={handleFileUpload}
          disabled={loading || !threadId}
        />

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

      {/* Model Switch Modal */}
      <ModelSwitchModal
        visible={showModelWarning}
        onConfirm={() => {
          setShowModelWarning(false);
          switchModel(pendingModelType);
          setPendingModelType(null);
        }}
        onCancel={() => {
          setShowModelWarning(false);
          setPendingModelType(null);
        }}
        dontShowAgain={dontShowAgain}
        setDontShowAgain={setDontShowAgain}
      />
    </div>
  );
}

export default Chat;
