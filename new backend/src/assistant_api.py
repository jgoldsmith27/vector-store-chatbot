import logging
from openai import OpenAI

class AssistantAPI:
    def __init__(self, api_key, assistant_id, vector_store_id):
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.vector_store_id = vector_store_id
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
            if hasattr(message.content[0], "annotations"):
                for annotation in message.content[0].annotations:
                    response_content = response_content.replace(annotation.text, '')
                    if file_citation := getattr(annotation, "file_citation", None):
                        cited_file = self.client.files.retrieve(file_citation.file_id)
                        citations.append(cited_file.filename)
            else:
                logging.warning("No annotations found in the response.")

            return response_content, citations

        except ValueError as e:
            logging.error(f"Thread error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logging.error(f"Failed to process question: {e}")
            raise


if __name__ == "__main__":
    # API key and assistant details
    API_KEY = "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"
    ASSISTANT_ID = "asst_dJJXxlCA2nIBhqXw6uPgPmhM"
    VECTOR_STORE_ID = "vs_ax9QXMrGoYaHz6drqWnvuORr"

    api = AssistantAPI(API_KEY, ASSISTANT_ID, VECTOR_STORE_ID)

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
