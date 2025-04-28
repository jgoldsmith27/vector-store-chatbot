import React, { useState } from "react";
import { Info } from "lucide-react";
import Modal from "./Modal";
import { useOktaAuth } from "@okta/okta-react";
import "../styles/Header.css";
import "../styles/Chat.css"; // To reuse your .logout-button class

const Header = () => {
  const [showInfoModal, setShowInfoModal] = useState(false);
  const { oktaAuth } = useOktaAuth();

  return (
    <>
      <div className="header-container">
        {/* Empty flex space to push title center */}
        <div className="header-spacer"></div>{" "}
        <h1 className="header-title">MSCHE Chatbot</h1>
        <div className="header-actions">
          <button
            className="header-icon-button"
            onClick={() => setShowInfoModal(true)}
            aria-label="Information"
          >
            <Info size={20} />
          </button>
          {/* Logout button */}
          <button
            className="logout-button"
            onClick={() => oktaAuth.signOut()}
            aria-label="Log Out"
          >
            Log Out
          </button>
        </div>
      </div>

      {/* Info Modal */}
      <Modal
        visible={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        title="About the MSCHE Chatbot"
        size="large"
      >
        <h2>Welcome to the MSCHE Chatbot</h2>

        <p>
          The MSCHE Chatbot is a collaborative assistant designed to support
          Skidmore College's self-study process for the Middle States Commission
          on Higher Education (MSCHE) accreditation. Its mission is to help
          working groups, committees, and staff navigate MSCHE Standards I–VII
          by suggesting evidence, clarifying expectations, and keeping track of
          major milestones—all while promoting Skidmore’s mission, values, and
          goals.
        </p>

        <h3>Purpose and Approach</h3>
        <ul>
          <li>
            Provide clear, accessible explanations of each MSCHE Standard.
          </li>
          <li>Suggest documentation types and where they may be found.</li>
          <li>
            Encourage thoughtful, collaborative progress through questions and
            guidance—not decisions.
          </li>
          <li>
            Tailor support to reflect Skidmore’s commitment to creativity,
            holistic education, and inclusive excellence.
          </li>
        </ul>

        <h3>Key Features</h3>
        <ul>
          <li>
            <strong>Conversational Assistance:</strong> Engage
            incrementally—clarify intent, suggest next steps, and collaborate
            through the accreditation process.
          </li>
          <li>
            <strong>Model Switching:</strong> Choose between different AI model
            options based on your needs for responsiveness or depth.
          </li>
          <li>
            <strong>Document Uploads:</strong> Attach relevant documents to
            threads for more tailored support (e.g., self-study drafts, data
            reports).
          </li>
          <li>
            <strong>Context Awareness:</strong> The chatbot can suggest likely
            evidence types without displaying confidential content.
          </li>
          <li>
            <strong>Alignment Prompts:</strong> Receive guidance to help align
            evidence, actions, and reporting to MSCHE Standards.
          </li>
        </ul>

        <h3>How to Use the Chatbot</h3>
        <ol>
          <li>
            <strong>Create a New Thread:</strong> Click the "New Chat" button to
            start a fresh conversation.
          </li>
          <li>
            <strong>Select a Model (Optional):</strong> Choose between model
            types if you prefer faster or more detailed responses.
          </li>
          <li>
            <strong>Upload Documents (Optional):</strong> Attach files that the
            chatbot can reference to better guide your work.
          </li>
          <li>
            <strong>Ask a Question:</strong> Pose a clear question about an
            MSCHE Standard, self-study draft, documentation need, or workflow
            process.
          </li>
          <li>
            <strong>Engage Collaboratively:</strong> Expect the chatbot to ask
            clarifying questions, suggest next steps, and guide you
            incrementally.
          </li>
        </ol>

        <h3>Important Reminders</h3>
        <ul>
          <li>
            The chatbot is a guide and thought partner—it does not make
            decisions for your committee.
          </li>
          <li>
            All final interpretations and conclusions rest with the human teams
            leading Skidmore’s accreditation efforts.
          </li>
          <li>
            The chatbot respects confidentiality and institutional privacy at
            all times.
          </li>
        </ul>

        <p>
          We hope the MSCHE Chatbot helps make your self-study process more
          thoughtful and productive.
          <strong> Any feedback is greatly appreciated!!!</strong>
        </p>
      </Modal>
    </>
  );
};

export default Header;
