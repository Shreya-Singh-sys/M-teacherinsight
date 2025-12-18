const mongoose = require('mongoose');

// Replace with your actual connection string from Atlas
const uri = "mongodb+srv://vishwa177_db_user:Vishwa177@tiesquad.tvlhzmz.mongodb.net/teacherDB";

const connectDB = async () => {
    try {
        const conn = await mongoose.connect(uri);
        
        // THIS IS THE SUCCESS MESSAGE
        console.log(`✅ MongoDB Connected: ${conn.connection.host}`);
    } catch (error) {
        // THIS IS THE ERROR MESSAGE
        console.error(`❌ Error: ${error.message}`);
        process.exit(1);
    }
};

module.exports = connectDB;