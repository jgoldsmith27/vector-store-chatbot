const OpenAI = require("openai");
const dotenv = require("dotenv");

dotenv.config();
const openai = new OpenAI(process.env.OPENAI_API_KEY);
