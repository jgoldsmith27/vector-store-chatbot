import OpenAI from "openai";
import dotenv from "dotenv";
import fs from "fs";

dotenv.config();

const openai = new OpenAI(process.env.OPENAI_API_KEY);

// Step 1

async function main() {
  const assistant = await openai.beta.assistants.create({
    name: "Story Summarizer",
    instructions:
      "You provide summaries and answer any questions about the stories and essays you have been provided.",
    model: "gpt-4o",
    tools: [{ type: "file_search" }],
  });
}

main();

// Step 2

const fileStreams = [
  "/Users/ericdeon/Desktop/Vector Store Test Documents/Copy_Dear_Rose.pdf",
  "/Users/ericdeon/Desktop/Vector Store Test Documents/Copy_Summer_Burning.pdf",
].map((path) => fs.createReadStream(path));

// Create a vector store including our two files.
let vectorStore = await openai.beta.vectorStores.create({
  name: "Test Stories",
});

await openai.beta.vectorStores.fileBatches.uploadAndPoll(
  vectorStore.id,
  fileStreams
);
