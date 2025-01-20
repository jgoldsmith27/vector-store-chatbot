# SetUp Folder

To create a new assistant with access to a vector store of Box files, follow this guide.

### Note

Experimenting with new setup with `new_setup.py`
This setup method is necessary for creating an assitant that updates its vector store files.

Main Changes:

- The last modified date of every Box file is retrieved
- File Objects are created after the files are retrieved from Box. The create method (not the beta one for creating vector store files) is used to capture the file id for every file.
- The names, ids, and last modified dates of the file are put in a dictionary. This is important and needs to be referenced later for updating and adding new Box files to the store
- Dictionary is written to `file_setup_info.json` so it can be easily accessed
- File batch upload and poll method takes in a list of the file ids rather than the file names and byte streams, as the files have already been created (which the method was doing internally when given the names and streams)

The non-beta File Object create method must be called instead of the beta Vector Store File create method because the latter doesn't accept the tuples of names and byte streams as a parameter, as defined by the FileTypes Union (check [the SDK](https://github.com/openai/openai-python/blob/main/src/openai/_types.py#L49) for more info)

### For Reference:

- **create_store_and_assistant.py**: Logs the created assistant and vector store ID to the console.
- **proof_authorize_Box**: Method to authenticate the Box account.

### Steps:

1. **Run `create_store_and_assistant.py`:**  
   It will prompt you to provide a Box key in the console. Enter your Box key when prompted.

2. **Accessing Box Files:**  
   The program will access all the files in a specified Box folder and convert them into Byte streams. Currently, the folder ID is hardcoded to access the "Middle States" Box folder, but it can be modified for other purposes.  
   This process is logged to the console for you to observe.

3. **Instantiate OpenAI Client:**  
   The program will instantiate an OpenAI client using an API key stored in a `.env` file. Ensure this file exists and contains your OpenAI API key.

4. **Assistant and Vector Store Creation:**  
   The assistant and vector store are created, the files are uploaded to the store, and the store is attached to the assistant. Both the assistant ID and the vector store ID are logged to the console.  
   Make sure to copy these IDs for later use in the React app or if you want to delete any created instances later.
