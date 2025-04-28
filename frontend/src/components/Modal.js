import React, { useEffect, useState } from "react";
import "../styles/Modal.css";

const Modal = ({
  visible,
  onClose,
  title,
  children,
  onConfirm,
  showConfirmButtons,
  dontShowAgain,
  setDontShowAgain,
  size = "small",
}) => {
  const [shouldRender, setShouldRender] = useState(visible);
  const [isClosing, setIsClosing] = useState(false);

  useEffect(() => {
    if (visible) {
      setShouldRender(true);
      setIsClosing(false);
    }
  }, [visible]);

  useEffect(() => {
    if (!visible && shouldRender) {
      setIsClosing(true);
      const timeoutId = setTimeout(() => {
        setShouldRender(false);
        setIsClosing(false);
      }, 300);
      return () => clearTimeout(timeoutId);
    }
  }, [visible, shouldRender]);

  if (!shouldRender) return null;

  return (
    <div
      className={`modal-overlay ${isClosing ? "fade-out" : "fade-in"}`}
      onClick={onClose}
    >
      <div
        className={`modal-content ${
          size === "large" ? "modal-content-large" : ""
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        {title && <h1>{title}</h1>}
        <div>{children}</div>

        {typeof dontShowAgain !== "undefined" && setDontShowAgain && (
          <label>
            <input
              type="checkbox"
              checked={dontShowAgain}
              onChange={(e) => {
                const checked = e.target.checked;
                setDontShowAgain(checked);
                localStorage.setItem("hideModelWarning", checked);
              }}
            />
            Don't show this again
          </label>
        )}

        <div className="modal-buttons">
          {showConfirmButtons ? (
            <>
              <button onClick={onConfirm}>Yes, switch</button>
              <button onClick={onClose}>Cancel</button>
            </>
          ) : (
            <button onClick={onClose}>Close</button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Modal;

// const ModelSwitchModal = ({
//   visible,
//   onConfirm,
//   onCancel,
//   dontShowAgain,
//   setDontShowAgain,
// }) => {
//   const [shouldRender, setShouldRender] = useState(visible);
//   const [isClosing, setIsClosing] = useState(false);

//   // When the modal becomes visible, start rendering it
//   useEffect(() => {
//     if (visible) {
//       setShouldRender(true);
//       setIsClosing(false);
//     }
//   }, [visible]);

//   // When the modal becomes invisible, trigger fade-out and unmount after delay
//   useEffect(() => {
//     if (!visible && shouldRender) {
//       setIsClosing(true);
//       const timeoutId = setTimeout(() => {
//         setShouldRender(false);
//         setIsClosing(false);
//       }, 300);
//       return () => clearTimeout(timeoutId); // clean up in case unmounted early
//     }
//   }, [visible, shouldRender]);

//   if (!shouldRender) return null;

//   return (
//     <div
//       className={`modal-overlay ${isClosing ? "fade-out" : "fade-in"}`}
//       onClick={onCancel}
//     >
//       <div className="modal-content" onClick={(e) => e.stopPropagation()}>
//         <h3>Switch Model?</h3>
//         <p>
//           Switching models will end your current conversation thread and start a
//           new one.
//         </p>
//         <label>
//           <input
//             type="checkbox"
//             checked={dontShowAgain}
//             onChange={(e) => {
//               const checked = e.target.checked;
//               setDontShowAgain(checked);
//               localStorage.setItem("hideModelWarning", checked);
//             }}
//           />
//           Don't show this again
//         </label>
//         <div className="modal-buttons">
//           <button onClick={onConfirm}>Yes, switch</button>
//           <button onClick={onCancel}>Cancel</button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default ModelSwitchModal;
