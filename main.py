import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    PollAnswerHandler
)
from config import TOKEN
from leaderboard import Leaderboard
from quiz_manager import QuizManager
import random


# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Start Python Quiz", callback_data="start_python")],
        [InlineKeyboardButton("Start Web Dev Quiz", callback_data="start_web")],
        [InlineKeyboardButton("Start Science Quiz", callback_data="start_science")],
        [InlineKeyboardButton("Show Leaderboard", callback_data="show_leaderboard")],
        [InlineKeyboardButton("Help", callback_data="show_help")]
    ]
    await update.message.reply_text(
        "📚 Welcome to Quiz Bot! Choose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ✅ Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("start_"):
        category = query.data.replace("start_", "")

        available_difficulties = context.application.quiz_manager._get_available_difficulties(category)

        if not available_difficulties:
            await query.edit_message_text("⚠️ No questions found for this category.")
            return

        difficulty = random.choice(available_difficulties)
        await context.application.quiz_manager.start_quiz(update, context, category, difficulty)

    elif query.data == "show_leaderboard":
        leaderboard = Leaderboard()
        await leaderboard.show_leaderboard(update, context)

    elif query.data == "show_help":
        await query.edit_message_text(
            "Available Commands:\n"
            "/start - Start the bot\n"
            "/python - Start Python quiz\n"
            "/web - Start Web Dev quiz\n"
            "/science - Start Science quiz\n"
            "/leaderboard - Show leaderboard\n"
            "/help - Show this help message"
        )

# ✅ Main Function
def main():
    application = Application.builder().token(TOKEN).build()

    # ✅ Attach QuizManager instance (used everywhere)
    application.quiz_manager = QuizManager()

    leaderboard = Leaderboard()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("python",
        lambda update, context: context.application.quiz_manager.start_quiz(update, context, "python", "medium")))
    application.add_handler(CommandHandler("web",
        lambda update, context: context.application.quiz_manager.start_quiz(update, context, "web", "medium")))
    application.add_handler(CommandHandler("science",
        lambda update, context: context.application.quiz_manager.start_quiz(update, context, "science", "medium")))
    application.add_handler(CommandHandler("leaderboard",
        lambda update, context: leaderboard.show_leaderboard(update, context)))
    application.add_handler(CommandHandler("help",
        lambda update, context: update.message.reply_text(
            "Available Commands:\n/start - Start the bot\n"
            "/python - Start Python quiz\n/web - Web quiz\n"
            "/science - Science quiz\n/leaderboard - Show leaderboard\n/help - Show this help"
        )))
    application.add_handler(CallbackQueryHandler(
    leaderboard.handle_leaderboard_button,
    pattern="^leaderboard_"
    ))

    # Button Clicks
    application.add_handler(CallbackQueryHandler(button_handler))

    # ✅ Poll Answer Handler (no new QuizManager instance)
    application.add_handler(PollAnswerHandler(application.quiz_manager.handle_poll_answer))

    # ✅ Leaderboard category selector
    application.add_handler(CallbackQueryHandler(
        leaderboard.handle_leaderboard_button,
        pattern="^leaderboard_"
    ))

    logger.info("✅ Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
