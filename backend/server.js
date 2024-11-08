const express = require("express");
const cors = require("cors");
const chatRoutes = require("./routes/chatRoutes");

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use("/api", chatRoutes); // Ensure the /api prefix is here

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
