import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
import io

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

    def upload_file(self, file_name, file_stream):
        """Upload a file to the vector store."""
        try:
            logging.info(f"Uploading file: {file_name}")
            response = self.client.beta.vector_stores.files.create(
                vector_store_id=self.vector_store_id,
                file=file_stream,
                file_name=file_name
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
            return response
        except Exception as e:
            logging.error(f"Failed to delete file: {e}")
            raise

    def update_vector_store(self, changes, box_folder_id, box_client, records):
        """
        Updates the vector store with new or modified files detected in the Box folder.

        Args:
            changes (list): List of changes detected by the BoxClient.
            box_folder_id (str): Box folder ID to pull new/modified files.
            box_client (BoxClient): Instance of the BoxClient to interact with Box.
            records (dict): JSON records containing file IDs and timestamps in the vector store.
        """
        if not changes:
            logging.info("No changes detected. Exiting update process.")
            return

        for change in changes:
            file_name = change.split(": ")[1]  # Extract file name from change message
            box_items = box_client.get_folder(box_folder_id).get_items()

            for item in box_items:
                if item.name == file_name and item.type == "file":
                    file_stream = io.BytesIO(item.content())  # Convert file content to byte stream

                    # Check if the file is modified
                    if "Modified" in change:
                        old_file_id, _ = records.get(file_name, (None, None))
                        if old_file_id:
                            self.delete_file(old_file_id)

                        uploaded_file = self.upload_file(file_name, file_stream)
                        records[file_name] = (uploaded_file.id, item.created_at)

                    # Check if the file is new
                    elif "New" in change:
                        uploaded_file = self.upload_file(file_name, file_stream)
                        records[file_name] = (uploaded_file.id, item.created_at)

        # Save the updated records
        with open("file_records.json", "w") as f:
            json.dump(records, f, indent=4)
        logging.info("Vector store updated successfully.")
