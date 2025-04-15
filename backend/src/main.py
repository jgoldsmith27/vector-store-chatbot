"""
This module provides an API for interacting with a per-user assistant, allowing users to handle thread logic, prompt the assistant, upload and attach files, switch assistant models, and retrieve authentication configuration.

Functions:
- attach_file(payload: AttachFileRequest) -> dict[str, str]: Attaches an OpenAI file object to a thread for a specific user.
- upload(file: UploadFile = File(...), user_id: str = Form(...)) -> dict[str, str]: Uploads a file to OpenAI for a specific user's assistant and returns the file ID.
- set_model(payload: ModelSelectRequest) -> dict[str, str]: Sets the active assistant model for a specific user.
- create_thread(payload: CreateThreadRequest) -> dict[str, str]: Creates a new conversation thread for a specific user.
- ask_question(payload: QuestionRequest) -> dict[str, str | list[str]]: Sends a question to the assistant for a specific user and retrieves the response and cited files.
- delete_thread(payload: DeleteThreadRequest) -> dict[str, str]: Deletes a specific user's active conversation thread.
- get_active_model(user_id: str) -> dict[str, str]: Retrieves the currently active model type for a specific user.
- get_okta_config(request: Request) -> dict[str, str]: Returns Okta configuration details required by the frontend for authentication setup.

Usage:
- Use `upload` to upload a file to OpenAI for a user.
- Use `attach_file` to attach an uploaded file to a user's thread.
- Use `set_model` to set or switch the assistant model for a user.
- Use `create_thread` to start a new conversation thread for a user.
- Use `ask_question` to send a question and get a response from a user's assistant.
- Use `delete_thread` to remove a user's active conversation thread.
- Use `get_active_model` to synchronize frontend display with the backend's stored model for a user.
- Use `get_okta_config` to retrieve Okta authentication configuration for initializing the frontend login flow.
"""

from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from pydantic import BaseModel
import uvicorn
import logging
from assistant_api import AssistantAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("server.log"), logging.StreamHandler()],
)

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://skid-msche-chatbot.us.reclaim.cloud"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
API_KEY = os.getenv("API_KEY")
ASSISTANT_ID_4O = os.getenv("ASSISTANT_ID_4O")
ASSISTANT_ID_4O_MINI = os.getenv("ASSISTANT_ID_4O_MINI")
OKTA_CLIENT_ID = os.getenv("REACT_APP_OKTA_CLIENT")
OKTA_ISSUER= os.getenv("REACT_APP_OKTA_ISSUER")

# Initialize the Assistant API
assistant_api_4o = AssistantAPI(API_KEY, ASSISTANT_ID_4O)
assistant_api_4o_mini = AssistantAPI(API_KEY, ASSISTANT_ID_4O_MINI)

# Maps user_id -> AssistantAPI instance
app.state.user_assistants = {}

class QuestionRequest(BaseModel):
    """
    Request model for asking a question to the assistant.
    
    Attributes:
        thread_id (str): The ID of the thread where the question is asked.
        question (str): The question to be sent to the assistant.
        user_id (str): The ID of the user (their email)
    """
    thread_id: str
    question: str
    user_id: str

class ModelSelectRequest(BaseModel):
    """
    Request model for changing the active assistant

    Attributes:
        model_type (str): The string identifier for the model type.
        user_id (str): The ID of the user (their email)
    """
    model_type: str
    user_id: str

class AttachFileRequest(BaseModel):
    """
    Request model for attaching a file to a thread

    Attributes:
        thread_id (str): The ID of the thread to attach the file to.
        file_id (str): The ID of the file object to attach
        user_id (str): The ID of the user (their email)
    """
    thread_id: str
    file_id: str
    user_id: str

class CreateThreadRequest(BaseModel):
    """
    Request model for creating a thread

    Attributes:
        user_id (str): The ID of the user (their email)
    """
    user_id: str


@app.post("/attach-file")
@app.post("/attach-file/")
async def attach_file(payload: AttachFileRequest) -> dict[str, str]:
    """
    Attaches an uploaded file to an existing thread as a user message.

    This endpoint takes an OpenAI file ID and a thread ID, 
    and creates a new message within that thread that includes the file. 
    This makes the file accessible to the assistant in future runs.

    Args:
        payload (AttachFileRequest): An object containing `thread_id`, `file_id`, and `user_id`.

    Returns:
        dict[str, str]: A dictionary indicating success.

    Raises:
        HTTPException: If the attachment fails due to invalid thread or file.
    """
    try:
        assistant = app.state.user_assistants.get(payload.user_id, assistant_api_4o)
        return assistant.attach_file_to_thread(
            thread_id=payload.thread_id,
            file_id=payload.file_id
        )
    except Exception as e:
        logging.error(f"Attach failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to attach file.")
    
@app.post("/upload")
@app.post("/upload/")
async def upload(file: UploadFile = File(...), user_id: str = Form(...)) -> dict[str, str]:
    """
    Uploads a file to OpenAI and returns its unique file ID.

    This endpoint receives a file from the user, uploads it to OpenAI 
    using the Assistants API, and returns the corresponding file ID. 
    The file must be uploaded before it can be attached to a thread.

    Args:
        file (UploadFile): The file uploaded by the client.
        user_id (str): The ID of the user

    Returns:
        dict[str, str]: A dictionary containing the generated file ID.

    Raises:
        HTTPException: If the file upload fails.
    """
    try:
        assistant = app.state.user_assistants.get(user_id, assistant_api_4o)
        file_id = assistant.upload_file(file)
        return {"file_id": file_id}
    except Exception as e:
        logging.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload failed.")

@app.post("/set-model")
@app.post("/set-model/")
async def set_model(payload: ModelSelectRequest) -> dict[str, str]:
    """
    Changes the active assistant based on the model type

    Args:
        payload (ModelSelectRequest): The request payload containing the model identifier and user ID.

    Returns:
        dict[str, str]: A dictionary containing a success message and the active model type

    Raises:
        HTTPException
    """
    if payload.model_type == "4o":
        assistant = assistant_api_4o
    elif payload.model_type == "4o-mini":
        assistant = assistant_api_4o_mini
    else:
        logging.error(f"Unknown model type: {payload.model_type}")
        raise HTTPException(status_code=400, detail="Invalid model type")

    app.state.user_assistants[payload.user_id] = assistant

    logging.info(f"Set model '{payload.model_type}' for user '{payload.user_id}'")
    return {"status": "successfully changed the model", "active_model": payload.model_type}

@app.post("/create-thread")
@app.post("/create-thread/")
async def create_thread(payload: CreateThreadRequest) -> dict[str, str]:
    """
    Creates a new thread for conversation.

    Args:
        payload (CreateThreadRequest): The request payload containing the user ID.

    Returns:
        dict[str, str]: A dictionary containing the message (str) and the created thread ID (str).
    
    Raises:
        HTTPException: Failed to create the thread.
    """
    try:
        assistant = app.state.user_assistants.get(payload.user_id, assistant_api_4o)
        thread_id = assistant.create_thread()
        return {"message": "Thread created successfully.", "thread_id": thread_id}
    except Exception as e:
        logging.error(f"Error creating thread: {e}")
        raise HTTPException(status_code=500, detail="Failed to create thread.")

@app.post("/ask-question")
@app.post("/ask-question/")
async def ask_question(payload: QuestionRequest) -> dict[str, str | list[str]]:
    """
    Prompts the assistant with the user question and returns the generated response and cited files.
    
    Args:
        payload (QuestionRequest): The request payload containing thread ID, question, and user ID.
    
    Returns:
        dict[str, str]: A dictionary containing the assistant's response (str) and citations (list[str]).
    
    Raises:
        HTTPException: The thread ID is invalid.
        HTTPException: Failed to process the question.
    """
    try:
        user_id = payload.user_id 
        assistant = app.state.user_assistants.get(user_id, assistant_api_4o)

        response, citations = assistant.ask_question(payload.thread_id, payload.question)
        return {
            "response": response,
            "citations": citations,
        }
    except Exception as e:
        logging.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail="Failed to process question.")

# NOT CURRENTLY USED
@app.delete("/delete-thread")
async def delete_thread() -> dict[str, str]:
    """
    Deletes the existing conversation thread.
    
    Returns:
        dict[str, str]: A dictionary containing a success message and the response from the assistant API.
    
    Raises:
        HTTPException: Failed to delete the thread.
    """
    try:
        response = app.state.active_assistant.delete_thread()
        return {"message": "Thread deleted successfully.", "response": response}
    except Exception as e:
        logging.error(f"Error deleting thread: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete thread.")
    
@app.get("/auth-config")
async def get_okta_config(request:Request) -> dict[str, str | list[str]]:
    """
    Retrieves the okta issuer and client id for configuration

    Returns:
        dict[str, str | list[str]]: A dictionary containing the client id and issuer

    """
    frontend_origin = request.headers.get("Origin", "https://skid-msche-chatbot.us.reclaim.cloud")
    return {
        "clientId": OKTA_CLIENT_ID,
        "issuer": OKTA_ISSUER,
        "redirectUri": f"{frontend_origin}/login/callback",
        "scopes": ["openid", "profile", "email"],
    }

@app.get("/get-active-model")
async def get_active_model(user_id: str) -> dict[str, str]:
    """
    Retrieves the active model for a given user.

    Args:
        user_id (str): The ID of the user.

    Returns:
        dict[str, str]: Contains the active model of a user.
    """
    logging.info(f"")
    assistant = app.state.user_assistants.get(user_id, assistant_api_4o)  # fallback to 4o
    active_model = None
    if assistant == assistant_api_4o:
        active_model = "4o"
    else: 
        active_model = "4o-mini"
    logging.info(f"Active model of user {user_id} is: {active_model}")
    return {"active_model": active_model}


if __name__ == "__main__":
    """Starts the FastAPI server on port 8080."""
    logging.info("Starting server on port 8080...")
    #uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        proxy_headers=True,             
        forwarded_allow_ips="*"     
    )






