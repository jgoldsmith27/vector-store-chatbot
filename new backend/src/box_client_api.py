import os
import json
import logging
from datetime import datetime
from boxsdk import JWTAuth, Client

# Setup logging
logging.basicConfig(
    filename='box_client.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class BoxClient:
    RECORDS_FILE = 'file_records.json'

    def __init__(self, config_path: str):
        """
        Initializes the BoxAPI with the configuration file path.
        
        Args:
            config_path (str): Path to the Box configuration file.
        """
        self.config_path = config_path
        self.client = self.authenticate()
        self.records = self.load_records()

    def authenticate(self) -> Client:
        """Authenticates with the Box API."""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            config = JWTAuth.from_settings_file(self.config_path)
            logging.info("Authenticated successfully.")
            return Client(config)
        except Exception as e:
            logging.error(f"Failed to authenticate: {e}")
            raise

    def load_records(self) -> dict:
        """
        Loads the file records from the JSON file.

        Returns:
            dict: The file records. Returns an empty dictionary if the file is empty or missing.
        """
        try:
            if os.path.exists(self.RECORDS_FILE):
                with open(self.RECORDS_FILE, 'r') as f:
                    content = f.read().strip()
                    if not content:  # Handle empty file
                        logging.warning("File records JSON is empty. Initializing new records.")
                        return {}
                    return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading file records: {e}")
            return {}

        return {}

    def save_records(self):
        """Saves file records to the local JSON file."""
        with open(self.RECORDS_FILE, 'w') as f:
            json.dump(self.records, f, indent=4)
        logging.info("File records saved.")

    def get_folder(self, folder_id):
        """
        Gets the specified Box folder.

        Args:
            folder_id (str): Box folder ID.

        Returns:
            The specified Box folder object.
        """
        try:
            folder = self.client.folder(folder_id=folder_id).get()
            logging.info(f"Accessed folder with ID: {folder_id}")
            return folder
        except Exception as e:
            logging.error(f"Failed to access folder with ID {folder_id}: {e}")
            raise

    def upload_file(self, local_file_path: str, folder_id='0'):
        """Uploads a file to the specified Box folder."""
        try:
            with open(local_file_path, 'rb') as file_stream:
                uploaded_file = self.client.folder(folder_id).upload_stream(file_stream, os.path.basename(local_file_path))
            logging.info(f"File uploaded: {uploaded_file.name}")
            return uploaded_file
        except Exception as e:
            logging.error(f"Failed to upload file: {e}")
            raise

    def delete_file(self, file_name: str, folder_id='0'):
        """
        Deletes a file with the given name from the specified Box folder.

        Args:
            file_name (str): The name of the file to delete.
            folder_id (str): Box folder ID to search for the file (default: root folder).
        """
        try:
            folder = self.client.folder(folder_id).get_items()
            for item in folder:
                if item.name == file_name and item.type == 'file':
                    self.client.file(item.id).delete()
                    logging.info(f"File deleted from Box: {file_name}")
                    return
            logging.warning(f"File not found in Box: {file_name}")
        except Exception as e:
            logging.error(f"Failed to delete file: {e}")
            raise

    def detect_changes(self, folder_id):
        """
        Detects new or modified files in the specified Box folder.

        Args:
            folder_id (str): Box folder ID to detect changes in.

        Returns:
            list: A list of changes detected (new or modified files).
        """
        changes = []
        folder = self.get_folder(folder_id)

        try:
            for item in folder.get_items():
                if item.type == 'file':
                    file_info = self.client.file(item.id).get()
                    created_at = file_info.created_at  # ISO 8601 string

                    if item.name not in self.records:
                        # New file detected
                        changes.append(f"New file: {item.name}")
                        self.records[item.name] = created_at
                    elif self.records[item.name] != created_at:
                        # Modified file detected
                        changes.append(f"Modified file: {item.name}")
                        self.records[item.name] = created_at

            self.save_records()
        except Exception as e:
            logging.error(f"Failed to detect changes in folder {folder_id}: {e}")
            raise

        return changes

