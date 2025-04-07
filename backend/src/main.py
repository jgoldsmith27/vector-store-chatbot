"""
This module provides an API for interacting with an assistant, allowing users handle thread logic, prompt the assistant, and upload and attach files.

Functions:
- attach_file (payload: AttachFileRequest) -> dict[str, str]: Attaches a OpenAI file object to a thread given the ID of both.
- upload (file: UploadFile = File(...)) -> -> dict[str, str]: Creates an OpenAI file object given a file.
- set_model(payload: ModelSelectRequest) -> dict[str, str]: Sets the active assistant based on the string alias.
- create_thread() -> dict[str, str]: Creates a new conversation thread.
- ask_question(payload: QuestionRequest) -> dict[str, str | list[str]]: Sends a question to the assistant and retrieves the response and cited files.
- delete_thread() -> dict[str, str]: Deletes the current conversation thread.

Usage:
- Use `upload` to create an OpenAI file object.
- Use `attach_file` to attach a file to a thread.
- Use `set_model` to change the model.
- Use `create_thread` to initialize a conversation.
- Use `ask_question` to send queries and receive responses.
- Use `delete_thread` to remove an active conversation.
"""

from fastapi import FastAPI, HTTPException, Request, File, UploadFile
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

# Set default Assistant to 4o
#assistant_api = assistant_api_4o
app.state.active_assistant = assistant_api_4o

class QuestionRequest(BaseModel):
    """
    Request model for asking a question to the assistant.
    
    Attributes:
        thread_id (str): The ID of the thread where the question is asked.
        question (str): The question to be sent to the assistant.
    """
    thread_id: str
    question: str

class ModelSelectRequest(BaseModel):
    """
    Request model for changing the active assistant

    Attributes:
        model_type (str): The string identifier for the model type
    """
    model_type: str

class AttachFileRequest(BaseModel):
    """
    Request model for attaching a file to a thread

    Attributes:
        thread_id (str): The ID of the thread to attach the file to.
        file_id (str): The ID of the file object to attach
    """
    thread_id: str
    file_id: str

@app.post("/attach-file")
@app.post("/attach-file/")
async def attach_file(payload: AttachFileRequest) -> dict[str, str]:
    """
    Attaches an uploaded file to an existing thread as a user message.

    This endpoint takes an OpenAI file ID and a thread ID, 
    and creates a new message within that thread that includes the file. 
    This makes the file accessible to the assistant in future runs.

    Args:
        payload (AttachFileRequest): An object containing `thread_id` and `file_id`.

    Returns:
        dict[str, str]: A dictionary indicating success.

    Raises:
        HTTPException: If the attachment fails due to invalid thread or file.
    """
    try:
        return app.state.active_assistant.attach_file_to_thread(
            thread_id=payload.thread_id,
            file_id=payload.file_id
        )
    except Exception as e:
        logging.error(f"Attach failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to attach file.")
    
@app.post("/upload")
@app.post("/upload/")
async def upload(file: UploadFile = File(...)) -> dict[str, str]:
    """
    Uploads a file to OpenAI and returns its unique file ID.

    This endpoint receives a file from the user, uploads it to OpenAI 
    using the Assistants API, and returns the corresponding file ID. 
    The file must be uploaded before it can be attached to a thread.

    Args:
        file (UploadFile): The file uploaded by the client.

    Returns:
        dict[str, str]: A dictionary containing the generated file ID.

    Raises:
        HTTPException: If the file upload fails.
    """
    try:
        file_id = app.state.active_assistant.upload_file(file)
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
        payload (ModelSelectRequest): The request payload containing the model identifier.

    Returns:
        dict[str, str]: A dictionary containing a success message and the active model type

    Raises:
        HTTPException
    """
    if payload.model_type == "4o":
        app.state.active_assistant = assistant_api_4o
    elif payload.model_type == "4o-mini":
        app.state.active_assistant = assistant_api_4o_mini
    else:
        logging.error(f"Error changing assistant to unknown model {payload.model_type}")
        raise HTTPException(status_code=500, detail=f"Failed to change the assistant to unknown model {payload.model_type}.")
    
    return {"status": "successfully changed the model", "active_model": payload.model_type}

@app.post("/create-thread")
@app.post("/create-thread/")
async def create_thread() -> dict[str, str]:
    """
    Creates a new thread for conversation.
    
    Returns:
        dict[str, str]: A dictionary containing the message (str) and the created thread ID (str).
    
    Raises:
        HTTPException: Failed to create the thread.
    """
    try:
        thread_id = app.state.active_assistant.create_thread()
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
        payload (QuestionRequest): The request payload containing thread ID and question.
    
    Returns:
        dict[str, str]: A dictionary containing the assistant's response (str) and citations (list[str]).
    
    Raises:
        HTTPException: The thread ID is invalid.
        HTTPException: Failed to process the question.
    """
    try:
        # Log the incoming request
        logging.info(f"Received payload: {payload}")

        # Process the question
        response, citations = app.state.active_assistant.ask_question(payload.thread_id, payload.question)
        return {
            "response": response,
            "citations": citations,
        }
    except HTTPException as e:
        logging.error(f"Error: {e.detail}")
        raise
    except Exception as e:
        logging.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail="Failed to process question.")

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
async def get_okta_config(request:Request) -> dict[str, str]:
    """
    Retrieves the okta issuer and client id for configuration

    Returns:
        dict[str, str]: A dictionary containing the client id and issuer

    """
    frontend_origin = request.headers.get("Origin", "https://skid-msche-chatbot.us.reclaim.cloud")
    return {
        "clientId": OKTA_CLIENT_ID,
        "issuer": OKTA_ISSUER,
        "redirectUri": f"{frontend_origin}/login/callback",
    }


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






