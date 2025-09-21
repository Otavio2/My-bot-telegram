import os
import random
import requests
import html
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    PollAnswerHandler,
    ContextTypes,
)
from dotenv import load_dotenv

# =====================
# Config
# =====================
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")

if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN não definido!")

application = Application.builder().token(TOKEN).build()

# =====================
# Traduções
# =====================
TRANSLATIONS = {
    "pt": {
        "welcome": "🎮 Bem-vindo ao Quiz Bot!\n\nUse /quiz para começar.\nUse /score para ver sua pontuação.",
        "correct": "✅ Correto! (+10 pontos)\nPontuação: {score}",
        "wrong": "❌ Errado! Resposta: {resposta}\n(-5 pontos)\nPontuação: {score}",
        "score": "📊 Sua pontuação: {score}\n🎯 Nível atual: {nivel}",
        "jservice_label": "Pergunta aberta (Jeopardy!)"
    },
    "en": {
        "welcome": "🎮 Welcome to Quiz Bot!\n\nUse /quiz to start.\nUse /score to check your points.",
        "correct": "✅ Correct! (+10 points)\nScore: {score}",
        "wrong": "❌ Wrong! Correct answer: {resposta}\n(-5 points)\nScore: {score}",
        "score": "📊 Your score: {score}\n🎯 Current level: {nivel}",
        "jservice_label": "Open question (Jeopardy!)"
    }
}

def t(user_lang, key, **kwargs):
    lang = user_lang if user_lang in TRANSLATIONS else "pt"
    return TRANSLATIONS[lang][key].format(**kwargs)

# =====================
# Funções auxiliares
# =====================
def get_question_otdb(category=None, difficulty="easy"):
    url = f"https://opentdb.com/api.php?amount=1&type=multiple&difficulty={difficulty}"
    if category:
        url += f"&category={category}"
    res = requests.get(url).json()
    q = res["results"][0]
    pergunta = html.unescape(q["question"])
    resposta = html.unescape(q["correct_answer"])
    opcoes = [html.unescape(x) for x in q["incorrect_answers"]] + [resposta]
    random.shuffle(opcoes)
    return pergunta, opcoes, resposta, q["category"]

def get_question_jservice():
    url = "https://jservice.io/api/random?count=1"
    res = requests.get(url).json()[0]
    pergunta = res["question"]
    resposta = res["answer"]
    categoria = res.get("category", {}).get("title", "Unknown")
    return pergunta, [resposta], resposta, categoria

def get_difficulty(score):
    if score <= 30:
        return "easy"
    elif score <= 60:
        return "medium"
    return "hard"

# =====================
# Estado do jogo
# =====================
user_scores = {}
active_quizzes = {}

# =====================
# Handlers
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code or "pt"
    await update.message.reply_text(t(lang, "welcome"))

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = update.effective_user.language_code or "pt"
    score = user_scores.get(user_id, 0)
    difficulty = get_difficulty(score)

    category = context.args[0] if context.args else None

    if category == "jservice":
        pergunta, opcoes, resposta, categoria = get_question_jservice()
        opcoes = [resposta, "Não sei", "Talvez", "Outra opção"]
        correct_index = 0
        categoria = t(lang, "jservice_label")
    else:
        pergunta, opcoes, resposta, categoria = get_question_otdb(category, difficulty)
        correct_index = opcoes.index(resposta)

    poll = await update.message.reply_poll(
        question=f"❓ ({categoria}, {difficulty})\n\n{pergunta}",
        options=opcoes,
        type="quiz",
        correct_option_id=correct_index,
        is_anonymous=False
    )

    active_quizzes[poll.poll.id] = {
        "resposta": resposta,
        "user_id": user_id,
        "lang": lang,
        "correct_index": correct_index
    }

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.poll_answer
    poll_id = answer.poll_id
    user_id = answer.user.id
    data = active_quizzes.get(poll_id)

    if not data or data["user_id"] != user_id:
        return

    lang = data["lang"]
    resposta_correta = data["resposta"]
    correct_index = data["correct_index"]
    score = user_scores.get(user_id, 0)

    if answer.option_ids and answer.option_ids[0] == correct_index:
        score += 10
        await context.bot.send_message(user_id, t(lang, "correct", score=score))
    else:
        score = max(score - 5, 0)
        await context.bot.send_message(user_id, t(lang, "wrong", resposta=resposta_correta, score=score))

    user_scores[user_id] = score
    del active_quizzes[poll_id]

async def score_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = update.effective_user.language_code or "pt"
    score = user_scores.get(user_id, 0)
    difficulty = get_difficulty(score)
    await update.message.reply_text(t(lang, "score", score=score, nivel=difficulty))

# =====================
# Registra handlers
# =====================
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("quiz", quiz))
application.add_handler(CommandHandler("score", score_cmd))
application.add_handler(PollAnswerHandler(handle_poll_answer))

# =====================
# Inicialização com Render (webhook ou polling)
# =====================
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    if BASE_URL:
        # Render
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{BASE_URL}/{TOKEN}",
        )
    else:
        # Local
        application.run_polling()
