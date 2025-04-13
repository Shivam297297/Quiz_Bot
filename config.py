# Bot Configuration
TOKEN = "7987706315:AAGth9TFr4prQU6hohy3WAonqy0sJUdMf_0"
ADMIN_IDS = [6512496140]  # Add more admin IDs if needed

# Quiz Settings
DEFAULT_TIME_LIMIT = 30  # seconds
MAX_QUESTIONS_PER_QUIZ = 10

# Difficulty Levels
DIFFICULTY_LEVELS = {
    "easy": {"time_multiplier": 1.5, "score_multiplier": 1},
    "medium": {"time_multiplier": 1.0, "score_multiplier": 1.5},
    "hard": {"time_multiplier": 0.7, "score_multiplier": 2},
    "custom": {"time_multiplier": 1.0, "score_multiplier": 1}  # Custom difficulty
}

# Quiz Categories
CATEGORIES = {
    "python": "Python Programming",
    "web": "Web Development",
    "gk": "General Knowledge",
    "math": "Mathematics",
    "history": "History",  # Nayi category
    "science": "Science",  # Nayi category
    "custom": "Custom Quiz"  # Manual category
}

# Google Sheets Configuration
SHEET_NAME = "Sheet1"
SHEET_ID = "1b5LMrroO_T1FKoD0Y5J65Z1cHmMgD4qxRQDOYkUCWPk"

# Custom Messages
WELCOME_MESSAGE = "Welcome to Quiz Bot! Use /startquiz to begin or /addquestion if you're an admin."