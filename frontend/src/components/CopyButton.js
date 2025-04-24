import React, { useState } from "react";
import { Copy, Check } from "lucide-react";
import "../styles/CopyButton.css";

const CopyButton = ({ textToCopy, isUser }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy: ", err);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="copy-button"
      aria-label="Copy message"
      style={{ color: isUser ? "#ffffff" : "inherit" }}
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
    </button>
  );
};

export default CopyButton;
