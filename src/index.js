require('dotenv').config();
const mongoose = require('mongoose');
const TelegramBot = require('node-telegram-bot-api');

// ================= VARIÁVEIS DE AMBIENTE =================
const token = process.env.TELEGRAM_API;
const dbString = process.env.DB_STRING;

if (!token) {
    console.error("❌ ERRO: TELEGRAM_API não configurado!");
    process.exit(1);
}

if (!dbString) {
    console.error("❌ ERRO: DB_STRING não configurado!");
    process.exit(1);
}

// ================= CONEXÃO AO MONGODB =================
mongoose.connect(dbString, {
    useNewUrlParser: true,
    useUnifiedTopology: true
})
.then(() => console.log("✅ Conectado ao MongoDB"))
.catch(err => {
    console.error("❌ Erro ao conectar no MongoDB:", err);
    process.exit(1);
});

// ================= INICIAR BOT =================
const bot = new TelegramBot(token, { polling: true });

bot.on('message', (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, `Olá ${msg.from.first_name}, seu bot está funcionando no Render!`);
});
