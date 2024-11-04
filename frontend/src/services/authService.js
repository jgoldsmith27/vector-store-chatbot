const correctPassword = "123456";

/**
 * Simulate user authentication by password.
 * @param {string} password - Input password to check.
 * @returns {boolean} - Returns true if authentication is successful, otherwise false.
 */
export const authenticateUser = async (password) => {
    return new Promise((resolve, reject) => {
        try {
            if (password === correctPassword) {
                resolve(true);
            } else {
                resolve(false);
            }
        } catch (error) {
            reject("Authentication error");
        }
    });
};