const express = require('express');
const connectDB = require('./db'); // Import the connection logic you wrote in db.js

const app = express();

// 1. Connect to Database
connectDB();

// 2. Basic Route to test server
app.get('/', (req, res) => {
    res.send('API is running...');
});

const PORT = 5000;

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});