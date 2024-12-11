# SetUp Folder

To create a new assistant with access to a vector store of Box files, follow this guide.

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
