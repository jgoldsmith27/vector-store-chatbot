# Skidmore MSCHE Chatbot

## Overview

This chatbot application is designed to assist Skidmore College staff and faculty involved in the MSCHE accreditation review process. It connects to an OpenAI assistant with an attached vector store of the review group’s files and documents uploaded from Box.

With this chatbot, members can:

- Search for files containing specific information
- Receive quick clarifications on accreditation-related topics
- Gain new insights to drive the review process

The goal is to provide real impact by saving faculty and staff valuable time while streamlining their workflows.

## Technologies

- **Frontend**: React (user interface)
- **Backend**: Python (FastAPI for API handling)
- **SDKs & APIs**:
  - Box (file storage and retrieval)
  - OpenAI Assistants (chatbot processing)

## Usage

- Open the chatbot application and enter your query.
- The chatbot will retrieve relevant accreditation documents and provide responses based on uploaded files.

## App Management

### `manage_app.sh` Script for Local Use

This script helps manage the chatbot application locally.

**First-time setup:**  
Convert the script into an executable by running:

```bash
chmod +x manage_app.sh
```

**Start the application**

```bash
./manage_app.sh start
```

**Stop the application**

```bash
./manage_app.sh stop
```

## Future Work

The goal is to make the chatbot accessible as a **tile on Skidmore’s Okta platform**, allowing review group members to log in through Okta authentication.

Next steps include:

- **Okta integration**: Implement single sign-on (SSO) for user authentication.
- **Enhanced AI capabilities**: Improve document retrieval accuracy and chatbot responses.
- **User feedback**: Collect feedback from faculty/staff to refine usability.

Check the **GitHub Issues** page to see new features planned for the application and what is currently being worked on
