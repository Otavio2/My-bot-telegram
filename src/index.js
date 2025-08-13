require('dotenv').config();
const mongoose = require('mongoose');
const http = require('http');

// Garante que o bot seja carregado
require('./bot');

// Importa o initHandler (responsável por configurar eventos)
const { initHandler } = require('./handlers/main');

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
const port = process.env.PORT || 8080;

const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'Bot está rodando!' }));
});

server.listen(port, () => {
    console.log(`🌐 Servidor HTTP rodando na porta ${port}`);
});
