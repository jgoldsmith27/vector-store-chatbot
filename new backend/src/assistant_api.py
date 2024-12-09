from openai import OpenAI
import logging

# Setup logging
logging.basicConfig(
    filename='box_client.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AssistantAPI:
    def __init__(self, API_KEY: str) -> None:
        """
        Instantiates an assistant API object.

        Args:
            API_KEY: The API key for the OpenAI client.
        """
        self.client = OpenAI(api_key=API_KEY)
        self.assistant_id = 'asst_dJJXxlCA2nIBhqXw6uPgPmhM'
        self.thread = None  # Initially, no thread is created.

    def create_thread(self) -> str:
        """
        Creates a new thread for the user's session and returns the thread ID.
        """
        try:
            self.thread = self.client.beta.threads.create(messages=[])
            logging.info(f"Thread created with ID: {self.thread.id}")
            return self.thread.id
        except Exception as e:
            logging.error(f"Unable to create thread: {e}")
            raise

    def delete_thread(self) -> None:
        """
        Deletes the current thread.
        """
        if not self.thread:
            logging.warning("No thread to delete.")
            return

        try:
            self.client.beta.threads.delete(self.thread.id)
            logging.info(f"Thread deleted with ID: {self.thread.id}")
            self.thread = None
        except Exception as e:
            logging.error(f"Unable to delete thread {self.thread.id}: {e}")

    def prompt_assistant(self, prompt: str, thread_id: str) -> tuple[str, list]:
        """
        Runs the assistant on the given thread and returns the assistant response of the inputted prompt.

        Args:
            prompt: The prompt for the assistant.
            thread_id: The ID of the thread for this session.

        Returns:
            A tuple containing the response content and a list of citations.
        """
        if prompt == "":
            logging.info("User sent an empty prompt.")
            return "Empty prompt received. Please enter a valid prompt.", []

        try:
            # Attach the thread ID to the session
            self.thread = self.client.beta.threads.retrieve(thread_id=thread_id)

            # Add the user's message to the thread
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=prompt,
            )
            logging.info(f"Message added to thread {self.thread.id} with prompt: {prompt}")

            # Generate a response
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id
            )
            logging.info("Run instance successfully created and executed.")

            # Retrieve the most recent response
            message = list(self.client.beta.threads.messages.list(thread_id=self.thread.id, run_id=run.id))[-1]
            message_content = message.content[0].text
            annotations = message_content.annotations
            citations = []

            # Process annotations and citations
            for annotation in annotations:
                message_content = message_content.replace(annotation.text, '')
                if file_citation := getattr(annotation, "file_citation", None):
                    cited_file = self.client.files.retrieve(file_citation.file_id)
                    logging.info(f"Cited file ID: {file_citation.file_id}")
                    if cited_file.filename not in citations:
                        citations.append(cited_file.filename)

            logging.info(f"Assistant response: {message_content}")
            logging.info(f"Citations: {citations}")
            return message_content.strip(), citations
        except Exception as e:
            logging.error(f"Error prompting assistant: {e}")
            return "Error: Failed to prompt the assistant.", []
