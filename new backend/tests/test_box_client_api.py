import os
import sys

# Add the `src` directory to the Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from box_client_api import BoxClient

# Test logic
def delete_all_files(api, folder_id='0'):
    """
    Deletes all files in the specified Box folder for testing purposes.

    Args:
        api (BoxAPI): The BoxAPI instance.
        folder_id (str): Box folder ID to delete files from (default: root folder).
    """
    print("Deleting all files from Box folder...")
    try:
        folder = api.client.folder(folder_id).get_items()
        for item in folder:
            if item.type == 'file':
                api.client.file(item.id).delete()
                print(f"Deleted file: {item.name}")
    except Exception as e:
        print(f"Error deleting files: {e}")
        raise

def test_box_api(api):
    # Clean up Box folder
    delete_all_files(api)

    # Detect changes in the cleaned folder
    print("Detecting changes in the cleaned folder...")
    changes = api.detect_changes()
    print("Detected changes:", changes)

    # Upload a test file
    test_file = "test_file.txt"
    with open(test_file, "w") as f:
        f.write("This is a test file.")
    print("Uploading the test file...")
    api.upload_file(test_file)

    print("Detecting changes after upload...")
    changes = api.detect_changes()
    print("Detected changes:", changes)

    # Delete the file from Box
    print("Deleting the test file from Box...")
    api.delete_file("test_file.txt")

    # Reupload the same file
    print("Reuploading the test file...")
    api.upload_file(test_file)

    print("Detecting changes after re-upload...")
    changes = api.detect_changes()
    print("Detected changes:", changes)

    # Clean up local test file
    os.remove(test_file)

if __name__ == "__main__":
    # Initialize the BoxAPI
    api = BoxClient(config_path='/Users/jacob/Desktop/vector-store-chatbot/new backend/168895_g0v9h4sy_config.json')


    # Run the test
    test_box_api(api)
