require('dotenv').config();
const OpenAI = require('openai');
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const assistantId = process.env.ASSISTANT_ID;
const vectorStoreId = process.env.VECTOR_STORE_ID;

async function summarizeDocument() {
    // const files = await openai.beta.vectorStores.files.list(vectorStoreId);
    // console.log(files);

  try {
    // Create a new thread for the query
    const thread = await openai.beta.threads.create({
      messages: [
        {
          role: "user",
          content: "Summarize the files",
        },
      ],
      tool_resources: {
        file_search: { vector_store_ids: [vectorStoreId] },
      },
    });

    // Create a run and poll until completion
    const run = await openai.beta.threads.runs.createAndPoll(thread.id, {
      assistant_id: assistantId,
    });

    // Retrieve and display the assistant's response
    const messages = await openai.beta.threads.messages.list(thread.id, {
      run_id: run.id,
    });

    const response = messages.data.find(msg => msg.role === "assistant");
    if (response) {
      console.log("Document Summary:");
      console.log(response.content);
    } else {
      console.log("No summary was generated.");
    }
  } catch (error) {
    console.error("Error:", error.message || error.response?.data);
  }
}

summarizeDocument();
