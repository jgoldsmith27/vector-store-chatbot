from openai import OpenAI
from proof_authorize_Box import authorize_box
import io
from dotenv import load_dotenv
import os
import json

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
file_mod_dates = {}
for item in items:
    if item.type == 'file' and item.name.endswith('.pdf'):
      print(f'\nFile name: {item.name}, File ID: {item.id}')

      # Fetch the full file object to get `modified_at`
      try:
        file_metadata = box_client.file(item.id).get()
        modified_at= file_metadata.modified_at
        print(f"Last updated at: {modified_at}")
        file_mod_dates[item.name] = modified_at
      except Exception as e:
          print(f"Error fetching file metadata: {e}")
          raise
      
      # Attempt to access file content
      try:
          # Works for box note file
          print("Converting to Byte Stream...\n")
          stream = io.BytesIO(item.content())
          file_streams.append((item.name, stream))
      except Exception as e:
          print(f'Could not convert file to Byte Stream')
          raise

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
vector_store = client.beta.vector_stores.create(name="Updating Middle States Files")

# Creates a dictionary of the file names and ids
print("Creating OpenAI Files...")
file_dict = {}
try:
  for item in file_streams:
    file_name = item[0]
    print(f"Creating files with name: {file_name}")
    response = client.files.create(file=item, purpose="assistants") # returns the created File Object
    file_id = response.id
    file_dict[file_name] = (file_id, file_mod_dates[file_name])
except Exception as e:
   print(f"Couldn't create file with name: {file_name}: {e}")
   raise

# Write dictionary to file to be accessed later
file_path = "file_setup_info.json"
with open(file_path, "w") as file:
    json.dump(file_dict, file, indent=4)

file_ids = [tup[0] for tup in file_dict.values()]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id,
  file_ids=file_ids,
  files=file_streams
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