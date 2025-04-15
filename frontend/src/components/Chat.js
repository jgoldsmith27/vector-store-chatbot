import React, { useEffect, useState } from "react";
import axios from "axios";
import "../styles/Chat.css";
import Notification from "./Notification";
import ModelSwitchModal from "./ModelSwitchModal";
import FileUpload from "./FileUpload";
import { useOktaAuth } from "@okta/okta-react";
import ReactMarkdown from "react-markdown";
import "github-markdown-css/github-markdown.css";
import rehypeRaw from "rehype-raw";

function Chat() {
  const { oktaAuth, authState } = useOktaAuth();

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
  const [userEmail, setUserEmail] = useState(null);

  // Retrieves user email to use as user id
  useEffect(() => {
    const fetchUserEmail = async () => {
      if (authState?.isAuthenticated) {
        const idToken = await oktaAuth.tokenManager.get("idToken");
        const email = idToken?.claims?.email;

        if (email) {
          //console.log("User Email from Token:", email);
          setUserEmail(email);
        } else {
          console.error("Email not found in idToken claims.");
        }
      }
    };

    fetchUserEmail();
  }, [authState, oktaAuth]);

  const createThread = async () => {
    //TODO: Implement logic to delete old thread if there was one
    try {
      setLoading(true);
      const response = await axios.post(
        "https://skid-msche-chatbot.us.reclaim.cloud/api/create-thread"
      );
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
          user_id: userEmail, // Pass email as user_id
        }
      );
      await createThread(); // reset thread
    } catch (err) {
      console.error("Model switch error:", err);
      showNotification("Failed to switch model.", "error");
    }
  };

  const convertMarkdownTablesToHTML = (text) => {
    return text.replace(
      /((?:\|.*\|\n?)+)/g, // detect table blocks
      (tableBlock) => {
        const lines = tableBlock
          .split("\n")
          .map((line) => line.trim())
          .filter((line) => line.length > 0);

        if (lines.length < 2) return tableBlock; // Not a real table

        const headerCells = lines[0]
          .split("|")
          .filter((cell) => cell.trim() !== "")
          .map((cell) => cell.trim());
        const dataLines = lines.slice(2); // Skip header & separator line

        const thead = `<thead><tr>${headerCells
          .map((cell) => `<th>${cell}</th>`)
          .join("")}</tr></thead>`;

        const tbody = `<tbody>${dataLines
          .map((line) => {
            const cells = line
              .split("|")
              .filter((cell) => cell.trim() !== "")
              .map((cell) => cell.trim());
            return `<tr>${cells
              .map((cell) => `<td>${cell}</td>`)
              .join("")}</tr>`;
          })
          .join("")}</tbody>`;

        return `<div class="table-container"><table>${thead}${tbody}</table></div>`;
      }
    );
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
          user_id: userEmail, // Pass email as user_id
        }
      );

      let assistantContent = response.data.response;

      if (typeof assistantContent === "object" && assistantContent.value) {
        assistantContent = assistantContent.value;
      }

      assistantContent = convertMarkdownTablesToHTML(assistantContent);

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
        formData.append("user_id", userEmail); // email in form data

        const res = await axios.post(
          "https://skid-msche-chatbot.us.reclaim.cloud/api/upload",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        const fileId = res.data.file_id;

        await axios.post(
          "https://skid-msche-chatbot.us.reclaim.cloud/api/attach-file",
          {
            thread_id: threadId,
            file_id: fileId,
            user_id: userEmail, // email
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

  // Retrieves the active model of the user
  useEffect(() => {
    const fetchActiveModel = async () => {
      if (!userEmail) return;

      try {
        const res = await axios.get("http://127.0.0.1:8080/get-active-model", {
          params: { user_id: userEmail },
        });

        setModelType(res.data.active_model);
      } catch (err) {
        console.error("Failed to fetch active model:", err);
      }
    };

    fetchActiveModel();
  }, [userEmail]);

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
                <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                  {message.content}
                </ReactMarkdown>
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
            value={modelType || ""}
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
        <textarea
          className="chat-input"
          placeholder="Type a message... (Shift + Enter for a newline)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !loading) {
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
