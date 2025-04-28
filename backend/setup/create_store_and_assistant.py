from openai import OpenAI
from proof_authorize_Box import authorize_box
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)


def get_pdf_file_streams(folder_id='292829099684'):
    """
    Authorizes the Box client, navigates to the specified folder, and extracts all .pdf files as byte streams.

    Parameters:
        folder_id (str): The ID of the Box folder containing the PDF files. Defaults to the MSCHE Box folder.

    Returns:
        list of tuples: A list of (filename, BytesIO stream) tuples for each .pdf file found in the folder.
    """
    box_client = authorize_box()
    user = box_client.user().get()
    print(f"User's name is {user.name}")

    folder = box_client.folder(folder_id).get()
    items = folder.get_items()

    file_streams = []
    for item in items:
        if item.type == 'file' and item.name.endswith('.pdf'):
            try:
                print(f"Converting {item.name} to Byte Stream...")
                stream = io.BytesIO(item.content())
                file_streams.append((item.name, stream))
            except Exception as e:
                print(f'Could not convert {item.name}: {e}')
    return file_streams


def create_assistants(models, instructions_path):
    """
    Creates OpenAI assistants for each model provided in the list, using a shared instruction file.

    Parameters:
        models (list of str): A list of model names to create assistants for (e.g., ["gpt-4o", "gpt-4o-mini"]).
        instructions_path (str): Path to the .txt file containing instruction content for the assistants.

    Returns:
        list: A list of created assistant objects.
    """
    with open(instructions_path, 'r') as file:
        content = file.read()

    assistants = []
    for model in models:
        assistant = client.beta.assistants.create(
            name="Collegiate Document Assistant",
            instructions=content,
            model=model,
            tools=[{"type": "file_search"}],
        )
        assistants.append(assistant)
        print(f"Created assistant for model {model}")
    return assistants


def upload_files_in_batches(file_streams, batch_size=10):
    """
    Uploads the given file streams to a newly created OpenAI vector store in batches.
    Automatically polls each batch until it completes.

    Parameters:
        file_streams (list of tuples): List of (filename, BytesIO) tuples to be uploaded.
        batch_size (int): Number of files to upload per batch. Default is 10.

    Returns:
        object: The created vector store object containing all uploaded files.
    
    Note:
        This function logs the number of completed and failed uploads but does not retry failed files.
    """
    vector_store = client.beta.vector_stores.create(name="Middle States Files")

    num_completed = 0
    num_failed = 0
    cur_index = 0

    while cur_index < len(file_streams):
        batch = file_streams[cur_index: cur_index + batch_size]
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=batch
        )
        num_completed += file_batch.file_counts.completed
        num_failed += file_batch.file_counts.failed
        cur_index += batch_size

    print(f"Upload complete: {num_completed} completed, {num_failed} failed")
    return vector_store


def assign_vector_store_to_assistant(assistant_id, vector_store_id):
    """
    Links the specified vector store to an existing OpenAI assistant by updating its tool resources.

    Parameters:
        assistant_id (str): The ID of the assistant to update.
        vector_store_id (str): The ID of the vector store to associate with the assistant.

    Returns:
        object: The updated assistant object.
    """
    updated_assistant = client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    print(f"Assigned vector store {vector_store_id} to assistant {assistant_id}")
    return updated_assistant


def main():
    """
    Coordinates the full pipeline:
      1. Retrieves .pdf files from Box as byte streams.
      2. Creates assistants for each specified model using a shared instruction file.
      3. Uploads the files in batches to a new vector store.
      4. Associates each assistant with the uploaded vector store.

    Returns:
        None
    """
    file_streams = get_pdf_file_streams()
    models = ["gpt-4o", "gpt-4o-mini"]
    assistants = create_assistants(models, 'MSCHE_Chatbot_Instructions.md')

    for assistant in assistants:
        vector_store = upload_files_in_batches(file_streams)
        assign_vector_store_to_assistant(assistant.id, vector_store.id)
        print("\n")


if __name__ == "__main__":
    main()
