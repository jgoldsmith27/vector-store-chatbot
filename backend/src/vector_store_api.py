import logging
import os
from dotenv import load_dotenv
from openai import OpenAI

class OpenAIVectorStoreAPI:
    def __init__(self, api_key, vector_store_id):
        self.api_key = api_key
        self.vector_store_id = vector_store_id
        self.client = OpenAI(api_key=api_key)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("vector_store_api.log"),
                logging.StreamHandler()
            ]
        )

        logging.info("OpenAI client initialized.")
        logging.info(f"Loaded VECTOR_STORE_ID: {self.vector_store_id}")

    def get_file_ids(self):
        """Get the IDs of files in the vector store."""
        try:
            logging.info("Fetching file IDs from vector store.")
            response = self.client.beta.vector_stores.files.list(vector_store_id=self.vector_store_id)
            file_ids = [file["id"] for file in response.get("data", [])]
            logging.info(f"Fetched file IDs: {file_ids}")
            return file_ids
        except Exception as e:
            logging.error(f"Failed to fetch file IDs: {e}")
            raise

    def upload_file(self, file_path):
        """Upload a file to the vector store."""
        try:
            logging.info(f"Uploading file: {file_path}")
            with open(file_path, "rb") as file:
                response = self.client.beta.vector_stores.files.create(
                    vector_store_id=self.vector_store_id,
                    file=file
                )
            logging.info(f"File uploaded successfully: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to upload file: {e}")
            raise

    def delete_file(self, file_id):
        """Delete a file from the vector store."""
        try:
            logging.info(f"Deleting file with ID: {file_id}")
            response = self.client.beta.vector_stores.files.delete(
                vector_store_id=self.vector_store_id,
                file_id=file_id
            )
            logging.info(f"File with ID {file_id} deleted successfully.")
            return {"status": "success", "file_id": file_id}
        except Exception as e:
            logging.error(f"Failed to delete file: {e}")
            raise

    def delete_vector_store(self):
        """Delete the vector store associated with the client."""
        try:
            logging.info("Deleting vector store.")
            deleted_vector_store = self.client.beta.vector_stores.delete(vector_store_id=self.vector_store_id)
            logging.info(f"Vector store ({self.vector_store_id}) successfully deleted.")
            logging.info(deleted_vector_store)
        except Exception as e:
            logging.error(f"Failed to delete vector store: {e}")
            raise

    def create_vector_store(self, name):
        """Create a new vector store."""
        try:
            logging.info(f"Creating new vector store with name: {name}")
            vector_store = self.client.beta.vector_stores.create(name=name)
            logging.info(f"Created vector store with ID: {vector_store.id}")
            return vector_store
        except Exception as e:
            logging.error(f"Failed to create vector store: {e}")
            raise

if __name__ == "__main__":
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

    if not API_KEY or not VECTOR_STORE_ID:
        raise ValueError("API_KEY or VECTOR_STORE_ID not set in the environment variables.")

    api = OpenAIVectorStoreAPI(api_key=API_KEY, vector_store_id=VECTOR_STORE_ID)

    try:
        logging.info("Starting API usage example.")
        file_ids = api.get_file_ids()
        print("File IDs:", file_ids)

        # Example file upload 
        # response = api.upload_file("")
        # print("Upload Response:", response)

        # Example file deletion 
        # delete_response = api.delete_file("")
        # print("Delete Response:", delete_response)

        # Create a new vector store example
        # vector_store = api.create_vector_store(name="New Vector Store")
        # print("Created Vector Store ID:", vector_store.id)

        # Delete the vector store example
        # api.delete_vector_store()

    except Exception as e:
        logging.error(f"An error occurred during API usage: {e}")
