"""
This module provides an API for interacting with an assistant, allowing users to create threads, ask questions, and delete threads.

Functions:
- create_thread() -> dict[str, str]: Creates a new conversation thread.
- ask_question(payload: QuestionRequest) -> dict[str, str | list[str]]: Sends a question to the assistant and retrieves the response and cited files.
- delete_thread() -> dict[str, str]: Deletes the current conversation thread.

Usage:
- Use `create_thread` to initialize a conversation.
- Use `ask_question` to send queries and receive responses.
- Use `delete_thread` to remove an active conversation.
"""

from fastapi import FastAPI, HTTPException, Request
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
    allow_origins=["*"],  # Allow all origins (use specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
API_KEY = os.getenv("API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
OKTA_CLIENT_ID = os.getenv("REACT_APP_OKTA_CLIENT")
OKTA_ISSUER= os.getenv("REACT_APP_OKTA_ISSUER")

# Initialize the Assistant API
assistant_api = AssistantAPI(API_KEY, ASSISTANT_ID)

class QuestionRequest(BaseModel):
    """
    Request model for asking a question to the assistant.
    
    Attributes:
        thread_id (str): The ID of the thread where the question is asked.
        question (str): The question to be sent to the assistant.
    """
    thread_id: str
    question: str

@app.post("/create-thread")
async def create_thread() -> dict[str, str]:
    """
    Creates a new thread for conversation.
    
    Returns:
        dict[str, str]: A dictionary containing the message (str) and the created thread ID (str).
    
    Raises:
        HTTPException: Failed to create the thread.
    """
    try:
        thread_id = assistant_api.create_thread()
        return {"message": "Thread created successfully.", "thread_id": thread_id}
    except Exception as e:
        logging.error(f"Error creating thread: {e}")
        raise HTTPException(status_code=500, detail="Failed to create thread.")

@app.post("/ask-question")
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

        # Ensure the thread ID matches the existing session
        if payload.thread_id != assistant_api.thread.id:
            raise HTTPException(status_code=400, detail="Invalid thread ID.")

        # Process the question
        response, citations = assistant_api.ask_question(payload.question)
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
        response = assistant_api.delete_thread()
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
    frontend_origin = request.headers.get("Origin", "http://localhost:3000")
    return {
        "clientId": OKTA_CLIENT_ID,
        "issuer": OKTA_ISSUER,
        "redirectUri": f"{frontend_origin}/login/callback",
    }


if __name__ == "__main__":
    """Starts the FastAPI server on port 8080."""
    logging.info("Starting server on port 8080...")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
