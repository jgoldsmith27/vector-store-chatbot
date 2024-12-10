from fastapi import FastAPI, HTTPException
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

# Initialize the Assistant API
API_KEY = os.getenv("API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

assistant_api = AssistantAPI(API_KEY, ASSISTANT_ID, VECTOR_STORE_ID)

# Define request models
class QuestionRequest(BaseModel):
    thread_id: str
    question: str

@app.post("/create-thread")
async def create_thread():
    """Create a new thread."""
    try:
        thread_id = assistant_api.create_thread()
        return {"message": "Thread created successfully.", "thread_id": thread_id}
    except Exception as e:
        logging.error(f"Error creating thread: {e}")
        raise HTTPException(status_code=500, detail="Failed to create thread.")

@app.post("/ask-question")
async def ask_question(payload: QuestionRequest):
    """Ask a question to the assistant."""
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
async def delete_thread():
    """Delete the existing thread."""
    try:
        response = assistant_api.delete_thread()
        return {"message": "Thread deleted successfully.", "response": response}
    except Exception as e:
        logging.error(f"Error deleting thread: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete thread.")

if __name__ == "__main__":
    logging.info("Starting server on port 8080...")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
