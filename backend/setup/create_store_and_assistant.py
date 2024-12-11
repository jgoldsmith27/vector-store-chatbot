from openai import OpenAI
from proof_authorize_Box import authorize_box
import io
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

#################
# Step 0: Authorize the Box client and download the files from the test folder

box_client = authorize_box() #default inDev is True

# Access your Box account details
box_user = box_client.user().get()
print(f"User's name is {box_user.name}")

# Access folder
folder_id = '292829099684'
folder = box_client.folder(folder_id).get()
items = folder.get_items()

file_streams = [] #List of file text byte streams
for item in items:
    if item.type == 'file' and item.name.endswith('.pdf'):
      print(f'\nFile name: {item.name}, File ID: {item.id}')
      # Attempt to access file content
      try:
          # Works for box note file
          print("Converting to Byte Stream...\n")
          stream = io.BytesIO(item.content())
          file_streams.append((item.name, stream))

      except Exception as e:
          print(f'Could not convert file to Byte Stream')

#################

# Step 1: Creates an assitant with the File Search tool
api_key = os.getenv("API_KEY")

client = OpenAI(api_key=api_key)
 
assistant = client.beta.assistants.create(
  name=" Collegiate Document Assistant",
  instructions="You summarize the documents, pertaining to college and academic information, that have been given to you and answer any questions about them.",
  model="gpt-4o-mini",
  tools=[{"type": "file_search"}],
)

# Step 2: Create and add files to the Vector Store
# Create the  vector store
vector_store = client.beta.vector_stores.create(name="Test Middle States Files")

 
# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams #from Step 0
)
 
# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)

print(f'\nFiles in vector store: {vector_store.file_counts}')

#Step 3: Update assistant to use the new Vector Store

assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

print(f'Created vector store id: {vector_store.id}')
print(f'Created assistant id: {assistant.id}')