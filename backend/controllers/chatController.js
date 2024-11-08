require('dotenv').config();
const OpenAI = require('openai');
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const assistantId = process.env.ASSISTANT_ID;
const vectorStoreId = process.env.VECTOR_STORE_ID;

/**
 * Summarize documents in the vector store using the assistant.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 */
async function handleChatRequest(req, res) {
  const userMessage = req.body.message;

  try {
    // Step 1: Create a thread with the user’s query
    const thread = await openai.beta.threads.create({
      messages: [
        {
          role: "user",
          content: userMessage,
        },
      ],
      tool_resources: {
        file_search: { vector_store_ids: [vectorStoreId] },
      },
    });

    // Step 2: Create a run and wait for the assistant’s response
    const run = await openai.beta.threads.runs.createAndPoll(thread.id, {
      assistant_id: assistantId,
    });

    // Step 3: Retrieve the assistant's response
    const messages = await openai.beta.threads.messages.list(thread.id, {
      run_id: run.id,
    });

    // Find the assistant’s response in the messages
    const response = messages.data.find(msg => msg.role === "assistant");

    if (response) {
      res.json({ response: response.content });
    } else {
      res.json({ response: "No response generated." });
    }
  } catch (error) {
    console.error("Error handling chat request:", error.message || error.response?.data);
    res.status(500).json({ error: "An error occurred while processing your request." });
  }
}

module.exports = { handleChatRequest };
