/**
 * Handles incoming chat messages from the frontend.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 */
const handleMessage = (req, res) => {
    const { message } = req.body;
    console.log("User message:", message);

    // Simulate a delay
    setTimeout(() => {
        res.json({ response: "Test example" });
    }, 3000);
};

module.exports = { handleMessage };