"""
This module contains functions for interacting with the OpenAI API,
including methods for generating responses and managing threads.

Functions:
- create_thread() -> str: Creates a new thread
-delete_thread() -> dict: Deletes the current thread
- ask_question(question: str) -> tuple[str, list[str]]: Sends a question to the assistant and retrieves the response and cited files.

Usage:
- The `create_thread` method manages thread creation.
The `delete_thread` method manages thread deletion.
- The `ask_question` method can be used to generate responses from the assistant.
"""

import logging
from openai import OpenAI
from dotenv import load_dotenv
import os
from fastapi import HTTPException

class AssistantAPI:
    """
    A client for interacting with the OpenAI APi to perform text generation tasks.

    This class provides methods to create and delete conversation threads, as well as prompt the assistant with questions.

    Attributes:
        api_key (str): The OpenAI API key used for authentication
        assistant_id (str): The ID of the OpenAI assistant
        client (openai.OpenAI): The OpenAI client
        thread: The current conversation thread
    """
    def __init__(self, api_key, assistant_id):
        """
        Initializes access to the existing OpenAI assistant and configures the logging of the file.

        Args:
            api_key (str): The API key for OpenAI
            assistant_id (str): The ID of the assistant
        """
        self.assistant_id = assistant_id
        self.client = OpenAI(api_key=api_key)
        #self.thread = None

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("assistant_api.log"),
                logging.StreamHandler()
            ]
        )

    def create_thread(self) -> str:
        """
        Creates the thread of the current conversation and returns its ID

        Returns:
            str: The id of the thread

        Raises:
            Exception: The thread failed to create

        """
        try:
            thread = self.client.beta.threads.create(messages=[])
            logging.info(f"Thread successfully created with ID: {thread.id}")
            return thread.id
        except Exception as e:
            logging.error(f"Failed to create thread: {e}")
            raise


    def delete_thread(thread_id:str) -> dict:
        """
        Deletes the current conversation thread.
        
        Args:
        	thread_id (str): The id of the current thread

        Returns:
            dict: The response of the API call

        Raises:
            Exception: The thread failed to be deleted
        """
        try:
            if thread_id:
                response = self.client.beta.threads.delete(thread_id)
                logging.info("Thread successfully deleted.")
                return response
            else:
                logging.warning("No active thread to delete.")
        except Exception as e:
            logging.error(f"Failed to delete thread: {e}")
            raise

    def ask_question(self, thread_id, question) -> tuple[str, list[str]]:
        """
        Prompts the assistant with the user question and returns the generated response and cited files

        Args:
        	thread_id (str): The id of the current thread
            question (str): The user prompt

        Returns:
            tuple[str, list[str]]: The generated response and cited files

        Raises:
            ValueError: The thread doesn't exist
            Exception: Failed to process the question
        """
        try:
            if not thread_id:
                raise ValueError("No thread exists. Create a thread first.")

            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=question,
            )
            logging.info("Question added to thread.")

            # Process the response
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread_id, assistant_id=self.assistant_id
            )
            message_list = list(self.client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id))
            message = message_list[-1]
            response_content = message.content[0].text

            # Extract citations if available
            citations = []
            annotations = response_content.annotations
            for annotation in annotations:
                response_content.value = response_content.value.replace(annotation.text, '')
                if file_citation := getattr(annotation, "file_citation", None):
                    cited_file = self.client.files.retrieve(file_citation.file_id)
                    file_name = cited_file.filename.replace('.pdf', '')
                    if file_name not in citations:
                        citations.append(file_name)

            return response_content.value, citations

        except ValueError as e:
            logging.error(f"Thread error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logging.error(f"Failed to process question: {e}")
            raise


if __name__ == "__main__":
    """For testing assistant functionality through the terminal"""
    load_dotenv()
    # API key and assistant details
    API_KEY = os.getenv("API_KEY")
    ASSISTANT_ID = os.getenv("ASSISTANT_ID")

    api = AssistantAPI(API_KEY, ASSISTANT_ID)

    try:
        print("Using Assistant...")
        print("Creating new thread...")
        api.create_thread()
        print("Thread created.")

        while True:
            init = input("Do you want to ask a question? (y|n): ").lower()
            if init == 'n':
                print("Deleting thread...")
                api.delete_thread()
                print("Thread deleted. Have a good day!")
                break
            else:
                question = input("Enter your question for the assistant: ")
                print("Processing your question...")

                response, citations = api.ask_question(question)

                print("Response:")
                print(response)
                print("\nCitations:")
                for citation in citations:
                    print(citation)

    except Exception as e:
        logging.error(f"An error occurred: {e}")

