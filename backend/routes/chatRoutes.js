const express = require("express");
const router = express.Router();
const { handleMessage } = require("../controllers/chatController");

// POST route to receive user messages
router.post("/", handleMessage);

module.exports = router;