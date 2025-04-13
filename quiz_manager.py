from datetime import datetime
from telegram import Update, Poll, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from config import CATEGORIES, DIFFICULTY_LEVELS, DEFAULT_TIME_LIMIT, MAX_QUESTIONS_PER_QUIZ
import random
import logging
import sqlite3
from analytics import Analytics
import json
import os
from telegram.constants import ParseMode
from leaderboard import get_user_rank, get_rank_emoji

logger = logging.getLogger(__name__)

class QuizManager:
    def __init__(self):
        self.active_quizzes = {}
# async def start_quiz(self, update: Update, context: CallbackContext, category: str, difficulty: str = None):
#     user_id = update.effective_user.id
#     username = update.effective_user.username or update.effective_user.full_name or ""

#     # Load all questions (difficulty no longer filtered)
#     questions = self._load_questions(category)

#     if not questions:
#         await update.effective_chat.send_message("❌ No questions available for this category!")
#         return

#     self.active_quizzes[user_id] = {
#         "category": category,
#         "difficulty": "mixed",  # ✅ Fixed to 'mixed' since we are loading all types
#         "current_question": 0,
#         "score": 0,
#         "attempted_questions": 0,
#         "total_questions": len(questions),
#         "start_time": datetime.now(),
#         "questions": questions,
#         "username": username
#     }

#     logger.info(f"🚀 Starting quiz for user {user_id}: {category}")
#     await self._send_question(update, context, user_id)

    async def start_quiz(self, update: Update, context: CallbackContext, category: str, difficulty: str):
        user_id = update.effective_user.id
        username = update.effective_user.username or ""

        questions = self._load_questions(category, difficulty)
        if not questions:
            await update.effective_chat.send_message("No questions available for this category!")
            return

        self.active_quizzes[user_id] = {
            "category": category,
            "difficulty": difficulty,
            "current_question": 0,
            "score": 0,
            "attempted_questions": 0,
            "total_questions": len(questions),
            "start_time": datetime.now(),
            "questions": questions,
            "username": username,
            "chat_id": update.effective_chat.id

            
        }

        logger.info(f"Starting quiz for user {user_id}: {category}, {difficulty}")
        await self._send_question(update, context, user_id)

    def _load_questions(self, category: str, difficulty: str):
        filepath = os.path.join(os.getcwd(), "questions.json")
        with open(filepath, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        # ✅ Fetch all questions of the selected category (no difficulty filter)
        all_questions = all_data.get(category, [])

        # ✅ Shuffle and limit
        random.shuffle(all_questions)
        selected = all_questions[:MAX_QUESTIONS_PER_QUIZ]
        # filtered = [q for q in all_data.get(category, []) if q.get("difficulty") == difficulty]
        # selected = random.sample(filtered, min(len(filtered), MAX_QUESTIONS_PER_QUIZ))
        print(f"📋[JSON] Total questions fetched: {len(selected)}")
        
        # print("Filtered Questions:", filtered)
        print("Selected Questions:", selected)
        
        return selected
    
    def _get_available_difficulties(self, category: str):
        filepath = os.path.join(os.getcwd(), "questions.json")
        if not os.path.exists(filepath):
            print("❌ questions.json not found!")
            return []

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        difficulties = set()
        for q in data.get(category, []):
            if "difficulty" in q:
                difficulties.add(q["difficulty"])

        return list(difficulties)

    async def _save_results(self, user_id: int, session: dict):
        try:
            conn = sqlite3.connect('quiz_bot.db')
            c = conn.cursor()

            c.execute('''INSERT OR IGNORE INTO users (user_id, username) 
                         VALUES (?, ?)''', (user_id, session["username"]))

            percentage = (session["score"] / session["total_questions"]) * 100
            c.execute('''INSERT INTO leaderboard 
                         (user_id, category, score, total, percentage, timestamp)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (user_id, session["category"], session["score"],
                       session["total_questions"], percentage, datetime.now()))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error saving results: {e}")

    async def _send_question(self, update: Update, context: CallbackContext, user_id: int):
        try:
            session = self.active_quizzes.get(user_id)
            if not session:
                logger.error(f"No session found for user {user_id}")
                return

            if session["current_question"] >= session["total_questions"]:
                logger.info(f"Quiz finished for user {user_id}")
                await self._finish_quiz(update, context, user_id)
                return

            question = session["questions"][session["current_question"]]
            time_limit = int(DEFAULT_TIME_LIMIT * DIFFICULTY_LEVELS[session["difficulty"]]["time_multiplier"])

            logger.info(f"Sending question {session['current_question']+1}/{session['total_questions']}")
            chat_id = session["chat_id"]
            message = await context.bot.send_poll(
                chat_id=chat_id,
                #chat_id=update.effective_chat.id,
                question=f"({session['current_question']+1}/{session['total_questions']}) "
                         f"[{session['category'].upper()}] {question['question']}",
                options=question["options"],
                type=Poll.QUIZ,
                correct_option_id=question["correct"],
                is_anonymous=False,
                open_period=time_limit
            )

            session["last_message_id"] = message.message_id

        except Exception as e:
            logger.error(f"Error sending question: {e}")
            await update.effective_chat.send_message("Error sending question.")

    async def _finish_quiz(self, update: Update, context: CallbackContext, user_id: int):
        session = self.active_quizzes.get(user_id)
        if not session:
            logger.error(f"No session found for user {user_id}")
            return

        await self._save_results(user_id, session)

        try:
            analytics = Analytics()
            analytics.save_result(
                update.effective_user,
                {
                    "category": session["category"],
                    "difficulty": session["difficulty"],
                    "score": session["score"],
                    "total": session["total_questions"],
                    "time_taken": (datetime.now() - session["start_time"]).seconds
                }
            )
        except Exception as e:
            logger.error(f"Error saving to Google Sheets: {e}")

        score = session["score"]
        total = session["total_questions"]
        attempted = session["attempted_questions"]
        missed = total - attempted
        time_taken = (datetime.now() - session["start_time"]).seconds

        # 🧠 Get user rank
        try:
            rank, total_users = get_user_rank(user_id, session["category"], session["difficulty"])
            rank_text = f"🏅 You secured <b>{rank}{get_rank_emoji(rank)}</b> place out of <b>{total_users}</b> participants!\n\n"
        except Exception as e:
            logger.error(f"Error fetching rank: {e}")
            rank_text = "🏅 Your rank is being calculated...\n\n"

        keyboard = [
            [InlineKeyboardButton("📊 Show Leaderboard", callback_data="show_leaderboard")]
        ]

        chat_id = session.get("chat_id") or (update.effective_chat.id if update.effective_chat else None)
        print(f"📡 Chat ID in finish_quiz: {chat_id}")

        text = (
            f"🏁 The quiz ‘<b>{session['category']}</b>’ has <i>finished</i>!\n\n"
            f"You answered <b>{total}</b> questions:\n\n"
            f"✅ <b>Correct</b> – {score}\n"
            f"❌ <b>Wrong</b> – {attempted - score}\n"
            f"⏳ <b>Missed</b> – {missed}\n"
            f"🕒 <b>{time_taken} sec</b>\n\n"
            f"{rank_text}"
            f"🥉 <b>Check your position on the leaderboard below 👇</b>\n\n"
            f"<i>You can take this quiz again but it will not change your place on the leaderboard.</i>"
        )

        try:
            if chat_id:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                print("📤 Final message sent to user successfully.")
            else:
                logger.warning("⚠️ Chat ID not found, can't send final message.")
        except Exception as e:
            logger.error(f"Error sending finish message: {e}")

        del self.active_quizzes[user_id]

        # Helper function to add emoji based on rank
        # def get_rank_emoji(rank: int) -> str:
        #     return {
        #         1: "🥇",
        #         2: "🥈",
        #         3: "🥉"
        #     }.get(rank, "")
        # print(f"📡 Chat ID in finish_quiz: {update.effective_chat.id if update.effective_chat else 'None'}")
    async def handle_poll_answer(self, update: Update, context: CallbackContext):
        try:
            answer = update.poll_answer
            user_id = answer.user.id
            session = self.active_quizzes.get(user_id)

            if not session:
                logger.error(f"No active quiz for user {user_id}")
                return

            current_q = session["current_question"]
            question = session["questions"][current_q]

            is_correct = (answer.option_ids[0] == question["correct"]) if answer.option_ids else False
            session["attempted_questions"] += 1
            if is_correct:
                session["score"] += 1

            logger.info(f"User {user_id} answered question {current_q+1}, correct: {is_correct}")

            session["current_question"] += 1

            if session["current_question"] < session["total_questions"]:
                await self._send_question(update, context, user_id)
            else:
                await self._finish_quiz(update, context, user_id)

        except Exception as e:
            logger.error(f"Error handling poll answer: {e}")
            if update.effective_chat:
                await update.effective_chat.send_message("Error processing your answer.")

        #print("📥 Received poll answer ✅")
