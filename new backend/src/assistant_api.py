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
    def __init__(self, API_KEY:str) -> None:
        """
        Instantiantes an assistant api object

        client:
            the OpenAI client
        assistant_id:
            the id of the Middle States assistant
        thread:
            the current thread of messages of the user

        Args:
            api_key:
                the API key for the OpenAI client
        """
        self.client = OpenAI(api_key=API_KEY)
        self.assistant_id = 'asst_dJJXxlCA2nIBhqXw6uPgPmhM'
        self.thread = self.create_thread()

    def create_thread(self) -> None:
        """
        Creates the thread for the user's session
        """
        try:
            self.thread = self.client.beta.threads.create(messages=[])
            logging.info(f"Thread created wit id: {self.thread.id}")
        except Exception as e:
            logging.error(f"Unable to create thread: {e}")
            raise

    def delete_thread(self) -> None:
        """
        Deletes the current thread
        """
        try:
            self.client.beta.threads.delete(self.thread.id)
            logging.info(f"Thread deleted with id: {self.thread.id}")
        except Exception as e:
            logging.error(f"Unable to delete thread {self.thread.id}: {e}")

    def prompt_assistant(self, prompt:str) -> tuple[str, list]:
        """
        Runs the assistant on the given thread, returning the assistant response of the inputted prompt

        Args:
            prompt:
                The prompt to the assistant of the user
        """
        # can also handle this case on the front end -> don't allow user to send the prompt unless the prompt is non-empty
        if prompt == "":
            logging.info("User sent empty prompt")
            return "Empty prompt received. Please enter a valid prompt.", []
        try:
            # Adds a new message object to the current thread for the given prompt
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=prompt,
            )
            logging.info(f"Message successfully added to thread with prompt: {prompt}")
            # Creates a new run instance that prompts the assistant on the current thread, generating a response
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id
            )
            logging.info(f"Run instance successfully created and excecuted")
            # Retrieves the most recent message, which holds the answer to the given prompt
            message = list(self.client.beta.threads.messages.list(thread_id=self.thread.id, run_id=run.id))[-1]
            message_content = message.content[0].text
            annotations = message_content.annotations
            citations = []
            # Removes the in-text annotations from the response and ensures every file that is referenced is only included once in the citations list
            for annotation in annotations:
                message_content.value = message_content.value.replace(annotation.text, '')
                if file_citation := getattr(annotation, "file_citation", None):
                    cited_file = self.client.files.retrieve(file_citation.file_id)
                    print(f'Cited file id: {file_citation.file_id}')
                    if cited_file.filename not in citations:
                        citations.append(cited_file.filename)

            logging.info(f"The assistant response: {message_content.value}")
            logging.info(f"The citations of the response: {citations}")
            return message_content.value, citations
        except Exception as e:
            logging.error(f"Unable to prompt the assistant and retrieve the response: {e}")
            return "Error: failed to prompt the assistant", []
    