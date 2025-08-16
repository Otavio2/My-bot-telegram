const mongoose = require('mongoose');

// ================= SCHEMA =================
const MessageSchema = new mongoose.Schema({
    message: { type: String, required: true },
    reply: { type: [String], required: true } // array de respostas (stickers ou texto)
});

// ================= MODEL =================
const MessageModel = mongoose.model('Message', MessageSchema);

module.exports = { MessageModel };
