import React, { useEffect } from "react";
import "../styles/Notification.css";

function Notification({ message, type, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return <div className={`notification ${type}`}>{message}</div>;
}

export default Notification;
