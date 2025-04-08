import React from "react";
import { Paperclip } from "lucide-react";
import "../styles/FileUpload.css";

const FileUpload = ({ fileNames, onFileUpload, disabled }) => {
  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    if (files.length > 0) {
      onFileUpload(files);
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
        multiple
        onChange={handleFileChange}
        disabled={disabled}
        className="file-upload-input"
      />

      <div className="file-upload-tag-list">
        {fileNames.map((name, index) => (
          <span key={index} className="file-upload-tag" title={name}>
            📄 {name.length > 20 ? name.slice(0, 20) + "…" : name}
          </span>
        ))}
      </div>
    </div>
  );
};

export default FileUpload;
