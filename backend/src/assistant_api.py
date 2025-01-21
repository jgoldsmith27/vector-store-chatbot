import logging
from openai import OpenAI
from dotenv import load_dotenv
import os
from fastapi import HTTPException

class AssistantAPI:
    def __init__(self, api_key, assistant_id):
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.client = OpenAI(api_key=api_key)
        self.thread = None

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("assistant_api.log"),
                logging.StreamHandler()
            ]
        )

    def create_thread(self):
        try:
            self.thread = self.client.beta.threads.create(messages=[])
            logging.info(f"Thread successfully created with ID: {self.thread.id}")
            return self.thread.id
        except Exception as e:
            logging.error(f"Failed to create thread: {e}")
            raise


    def delete_thread(self):
        try:
            if self.thread:
                response = self.client.beta.threads.delete(self.thread.id)
                logging.info("Thread successfully deleted.")
                return response
            else:
                logging.warning("No active thread to delete.")
        except Exception as e:
            logging.error(f"Failed to delete thread: {e}")
            raise

    def ask_question(self, question):
        try:
            if not self.thread:
                raise ValueError("No thread exists. Create a thread first.")

            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=question,
            )
            logging.info("Question added to thread.")

            # Process the response
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id, assistant_id=self.assistant_id
            )
            message_list = list(self.client.beta.threads.messages.list(thread_id=self.thread.id, run_id=run.id))
            message = message_list[-1]
            response_content = message.content[0].text

            # Extract citations if available
            citations = []
            annotations = response_content.annotations
            for annotation in annotations:
                response_content.value = response_content.value.replace(annotation.text, '')
                if file_citation := getattr(annotation, "file_citation", None):
                    cited_file = self.client.files.retrieve(file_citation.file_id)
                    if cited_file.filename not in citations:
                        citations.append(cited_file.filename)

            return response_content.value, citations

        except ValueError as e:
            logging.error(f"Thread error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logging.error(f"Failed to process question: {e}")
            raise


if __name__ == "__main__":
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
