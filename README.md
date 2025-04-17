# Skidmore MSCHE Chatbot

## Overview

This chatbot application is designed to assist Skidmore College staff and faculty involved in the MSCHE accreditation review process. It connects to an OpenAI assistant with an attached vector store of the review group’s files and documents uploaded from Box.

With this chatbot, members can:

- Search for files containing specific information
- Upload their own files for better context
- Receive quick clarifications on accreditation-related topics
- Gain new insights to drive the review process

The goal is to provide real impact by saving faculty and staff valuable time while streamlining their workflows.

## Cloud Hosting with Reclaim Cloud

This project is cloud-hosted using [Reclaim Cloud](https://reclaim.cloud/), with a fully containerized setup and automatic HTTPS. Below is an overview of the deployment process:

### Dockerized Architecture

The application consists of:

- **Frontend** (React): Built and served using the `serve` package on port 3000.
- **Backend** (FastAPI): Handles API requests on port 8080.
- **Caddy**: Acts as a reverse proxy and automatically manages SSL certificates via Let's Encrypt.

All services are orchestrated via `docker-compose.yml`.

### Domain & HTTPS

- A public domain is mapped to the environment in Reclaim Cloud.
- HTTPS is managed by **Caddy**, which automatically provisions TLS certificates via Let's Encrypt.
- Caddy routes requests:
  - `/api/*` → backend (FastAPI)
  - everything else → frontend (React)

### Key Caddyfile Configuration

```caddyfile
your-domain.com {
  tls your-email@example.com

  handle_path /api/* {
    reverse_proxy backend:8080
  }

  handle {
    reverse_proxy frontend:3000
  }
}
```

## Frontend Design

<div style="display: flex; gap: 10px; justify-content: start;">
  <img src="images/frontend-main-page.png" alt="Frontend Main Picture" style="width: 48%;">
  <img src="images/frontend-modal.png" alt="Frontend Modal Picture" style="width: 48%;">
</div>

The frontend follows a simple, chatbot interface that users will be familiar with and can intuitively work with.

## Technologies

- **Frontend**: React (user interface)
- **Backend**: Python (FastAPI for API handling)
- **SDKs & APIs**:
  - Box (file storage and retrieval)
  - OpenAI Assistant (chatbot processing)
    - The app currently supports a 4o and 4o-mini assistant

## Workflow

![Workflow Diagram](images/MSCHE_Chatbot_FlowChart_v1.png)

This flowchart shows the intended workflow of the project.

1. Users (members of the MSCHE review group) continuously add files to Box
2. Box files are copied to an OpenAI vector store that is attached to an OpenAI assistant
3. Users access the chatbot Okta tile on the Skidmore domain and login using their Skidmore credentials
4. Users prompt the assistant via the frontend UI
5. The assistant generates the response and sends it back to the frontend
6. The UI updates and displays the response to the user
7. Users are free to repeatdely prompt and receive responses from the assistant

## Usage

- Open the chatbot application and enter your query.
- The chatbot will retrieve relevant accreditation documents and provide responses based on uploaded files.

## App Management

### `manage_app.sh` Script for Local Use

This script helps manage the chatbot application locally.

**First-time setup:**
Grant execute permissions by running:

```bash
chmod +x manage_app.sh
```

**Setup the virtual environment (venv)**
If running on a non-externally managed system (Macbook, desktop, etc.), use this:

```bash
source manage_app.sh venv
```

If running on an externally managed system (like a podium computer), use this:

```bash
source manage_app.sh venv podium
```

**Start the application**

```bash
./manage_app.sh start
```

**Stop the application**

```bash
./manage_app.sh stop
```

**End venv**

```bash
deactivate
```

**Notes**

The `venv` function is used to activate the virtual environment, which modifies the current shell session (by adjusting environment variables like `PATH` to point to the virtual environment's Python binaries). This can only be done in the current shell, which is why it must be run using `source`.

On the other hand, `start` and `stop` are functions that can be run as standalone commands (e.g., `./manage_app.sh start`) because they do not modify the shell environment and can be executed in a subshell without affecting the current shell session.

### Containerizing with Docker

This project includes multiple files for containerization using Docker:

- **Two Dockerfiles (`Dockerfile`)**:
  - One for containerizing the frontend
  - One for containerizing the backend
- **One Docker Compose file (`docker-compose.yml`)** located at the root of the project

#### Running the Project in Docker

To build and run the full project using Docker Compose, execute:

```bash
docker compose up --build
```

If you are using an older version of Docker or Docker Compose, use:

```bash
docker-compose up --build
```

#### Prerequisites

- Ensure that [Docker](https://www.docker.com/get-started) is installed and running on your device.
- If using Docker Compose, ensure that you have [Docker Compose](https://docs.docker.com/compose/install/) installed.
  - Docker Compose may already be installed on your machine if you download Docker Desktop, as it is included in the .dmg

#### Additional Notes

- If you need to rebuild images without using the cache, add the `--no-cache` flag:

  ```bash
  docker compose up --build --no-cache
  ```

- To run the containers in detached mode (background):

  ```bash
  docker compose up --build -d
  ```

- To stop and remove the containers, run:

  ```bash
  docker compose down
  ```

  The containers can also be stopped gracefully by typing `Ctrl + C` while they are running

- Logs for each container can be viewed with:

  ```bash
  docker compose logs -f
  ```

## .env File

The `.env` file for this project stores sensitive keys and configuration values required for integrating **Okta Authentication** and **OpenAI API**. It ensures that your application functions securely by keeping your environment variables separate from the codebase.

Make sure to create a `.env` file in the root of your project with the following variables set:

```env
REACT_APP_OKTA_ISSUER=your-okta-issuer-url
REACT_APP_OKTA_CLIENT=your-okta-client-id
API_KEY=your-openai-api-key
ASSISTANT_ID_4O_MINI=your-openai-assistant-4o-mini-id
ASSISTANT_ID_4O=our-openai-assistant-4o-id
```

### Explanation of Variables:

- **REACT_APP_OKTA_ISSUER**: This is the issuer URL for your Okta authorization server. You can find this value in the Okta Developer Console under "API" > "Authorization Servers".
- **REACT_APP_OKTA_CLIENT**: This is your Okta client ID, which identifies your application for authentication requests. You can find this in the Okta Developer Console under "Applications" > "Your App".

- **API_KEY**: This is the API key for the OpenAI service. You can obtain this key by signing up for access to the OpenAI API at [OpenAI API](https://beta.openai.com/signup/).

- **ASSISTANT_ID_4O/4O_MINI**: These are the IDs of the specific OpenAI Assistants you want to use. You can configure these through the OpenAI platform to link your assistant or create the assistant via the API.

## Future Work

The goal is to make the chatbot accessible as a **tile on Skidmore’s Okta platform**, allowing review group members to log in through Okta authentication.

Next steps include:

- **Enhanced AI capabilities**: Improve document retrieval accuracy and chatbot responses.
- **User feedback**: Collect feedback from faculty/staff to refine usability.
- **Improve UX**: Enhance the design and functionality of the chatbot to maximize the user experience

Check the **GitHub Issues** page to see new features planned for the application and what is currently being worked on.
