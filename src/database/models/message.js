const { Schema, model } = require('mongoose');

const MessageSchema = new Schema({
  message: {
    type: String,
    unique: true,
    required: true,
  },
  reply: {
    type: [String], // array de strings
    trim: true
  }
});

const MessageModel = model('Message', MessageSchema);

module.exports = { MessageModel };
