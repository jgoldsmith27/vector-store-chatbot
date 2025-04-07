import React from "react";
import { Paperclip } from "lucide-react";
import "../styles/FileUpload.css";

const FileUpload = ({ fileName, onFileUpload, disabled }) => {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onFileUpload(file);
      // Reset file name so same file can be uploaded again
      event.target.value = "";
    }
  };

  return (
    <div className="file-upload-container">
      <label
        htmlFor="file-upload"
        className={`file-upload-icon ${disabled ? "disabled" : ""}`}
      >
        <Paperclip size={20} />
        {!disabled && <span className="tooltip">Upload a file</span>}
      </label>

      <input
        id="file-upload"
        type="file"
        onChange={handleFileChange}
        disabled={disabled}
        className="file-upload-input"
      />

      {fileName && (
        <span className="file-upload-tag" title={fileName}>
          📄 {fileName.length > 20 ? fileName.slice(0, 20) + "…" : fileName}
        </span>
      )}
    </div>
  );
};

export default FileUpload;
