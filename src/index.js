require('dotenv').config();
const mongoose = require('mongoose');

// Importa o initHandler do Chester
const { initHandler } = require('./handlers/main.js');

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
.then(() => {
    console.log("✅ Conectado ao MongoDB");
    // Inicia o bot só depois da conexão
    initHandler();
})
.catch(err => {
    console.error("❌ Erro ao conectar no MongoDB:", err);
    process.exit(1);
});

// ================= MANTER SERVIDOR VIVO NO RENDER =================
const http = require('http');
const port = process.env.PORT || 8080;

const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'Bot está rodando!' }));
});

server.listen(port, () => {
    console.log(`🌐 Servidor HTTP rodando na porta ${port}`);
});
