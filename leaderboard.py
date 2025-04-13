# import matplotlib.pyplot as plt
# import matplotlib.font_manager as fm
# from PIL import Image
# import os
# from telegram import Update
# from telegram.ext import CallbackContext
# from config import SHEET_ID, SHEET_NAME, CATEGORIES
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# class Leaderboard:
#     def __init__(self):
#         scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#         creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
#         self.client = gspread.authorize(creds)
#         self.sheet = self.client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

#     # async def handle_leaderboard_button(self, update: Update, context: CallbackContext):
#     #     query = update.callback_query
#     #     await query.answer()

#     #     category_key = query.data.replace("leaderboard_", "")
#     #     print("➡️ Leaderboard button pressed")
#     #     print("Category Data:", category_key)

#     #     try:
#     #         records = self.sheet.get_all_records()
#     #     except Exception as e:
#     #         await query.message.reply_text(f"⚠️ Failed to fetch leaderboard data: {e}")
#     #         return

#     #     category_data = [row for row in records if str(row.get("category", "")).lower() == category_key.lower()]
#     #     if not category_data:
#     #         await query.message.reply_text("⚠️ No data available for this category.")
#     #         return

#     #     sorted_data = sorted(category_data, key=lambda x: (-float(str(x.get('percentage', '0%')).replace('%', '')), int(x.get('time_taken', 9999))))

#     #     names, percentages = [], []
#     #     emojis = ['🥇', '🥈', '🥉']

#     #     for idx, row in enumerate(sorted_data[:10]):
#     #         rank = emojis[idx] if idx < 3 else f"{idx + 1}."
#     #         name = row.get("name") or row.get("username") or f"User_{row.get('user_id', 'Unknown')}"
#     #         names.append(f"{rank} {name}")
#     #         perc_str = str(row.get("percentage", "0%")).replace('%', '')
#     #         percentages.append(float(perc_str))

#     #     # Emoji font setup
#     #     font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
#     #     emoji_font = None
#     #     for font_path in font_paths:
#     #         if any(word in font_path.lower() for word in ['seguiemj', 'noto', 'symbola']):
#     #             emoji_font = fm.FontProperties(fname=font_path)
#     #             break
#     #     if emoji_font:
#     #         plt.rcParams['font.family'] = emoji_font.get_name()

#     #     # Generate chart
#     #     plt.figure(figsize=(10, 6))
#     #     bars = plt.barh(names[::-1], percentages[::-1], color='cornflowerblue')
#     #     plt.xlabel("Percentage")
#     #     plt.title(f"Leaderboard - {category_key.title()}")
#     #     plt.xlim(0, 100)
#     #     plt.tight_layout()

#     #     image_path = "leaderboard_image.png"
#     #     plt.savefig(image_path)
#     #     plt.close()

#     #     try:
#     #         with open(image_path, "rb") as photo:
#     #             await query.message.reply_photo(photo=photo, caption="📊 Leaderboard by Percentage")
#     #         os.remove(image_path)
#     #     except Exception as e:
#     #         print("❌ Failed to send image:", e)
#     #         await query.message.reply_text("⚠️ Could not generate leaderboard image.")

#     async def handle_leaderboard_button(self, update: Update, context: CallbackContext):
#         query = update.callback_query
#         await query.answer()

#         category_key = query.data.replace("leaderboard_", "")
#         print("➡️ Leaderboard button pressed")
#         print("Category Data:", category_key)

#         try:
#             records = self.sheet.get_all_records()
#         except Exception as e:
#             await query.message.reply_text(f"⚠️ Failed to fetch leaderboard data: {e}")
#             return

#         category_data = [row for row in records if str(row.get("category", "")).lower() == category_key.lower()]
#         if not category_data:
#             await query.message.reply_text("⚠️ No data available for this category.")
#             return

#         sorted_data = sorted(category_data, key=lambda x: (
#             -float(str(x.get('percentage', '0%')).replace('%', '')),
#             int(x.get('time_taken', 9999))
#         ))

#         names, percentages = [], []
#         emojis = ['🥇', '🥈', '🥉']

#         for idx, row in enumerate(sorted_data[:10]):
#             rank = emojis[idx] if idx < 3 else f"{idx + 1}."
#             name = row.get("name") or row.get("username") or f"User_{row.get('user_id', 'Unknown')}"
#             names.append(f"{rank} {name}")
#             perc_str = str(row.get("percentage", "0%")).replace('%', '')
#             percentages.append(float(perc_str))

#         # ✅ Try to support emoji fonts
#         font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
#         emoji_font = None
#         for font_path in font_paths:
#             if any(keyword in font_path.lower() for keyword in ['seguiemj', 'noto', 'symbola']):
#                 emoji_font = fm.FontProperties(fname=font_path)
#                 break
#         if emoji_font:
#             plt.rcParams['font.family'] = emoji_font.get_name()

#         # ✅ Generate Bar Graph
#         try:
#             plt.figure(figsize=(10, 6))
#             bars = plt.barh(names[::-1], percentages[::-1], color='cornflowerblue')
#             plt.xlabel("Percentage")
#             plt.title(f"Leaderboard - {CATEGORIES.get(category_key, category_key).title()}")
#             plt.xlim(0, 100)  # Since it's percentage
#             plt.tight_layout()

#             image_path = "leaderboard_image.png"
#             plt.savefig(image_path)
#             plt.close()

#             with open(image_path, "rb") as photo:
#                 await query.message.reply_photo(photo=photo, caption="📊 Leaderboard by Percentage")
#             os.remove(image_path)
#         except Exception as e:
#             print("❌ Failed to send image:", e)
#             await query.message.reply_text("⚠️ Could not generate leaderboard image.")

#     async def show_leaderboard(self, update: Update, context: CallbackContext):
#         keyboard = [[InlineKeyboardButton(name, callback_data=f"leaderboard_{key}")]
#                     for key, name in CATEGORIES.items()]

#         if update.callback_query:
#             await update.callback_query.edit_message_text(
#                 "📊 Choose category for leaderboard:",
#                 reply_markup=InlineKeyboardMarkup(keyboard)
#             )
#         else:
#             await update.message.reply_text(
#                 "📊 Choose category for leaderboard:",
#                 reply_markup=InlineKeyboardMarkup(keyboard)
#             )

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from PIL import Image
import os
from telegram import Update
from telegram.ext import CallbackContext
from config import SHEET_ID, SHEET_NAME, CATEGORIES
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pandas as pd

class Leaderboard:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

    async def handle_leaderboard_button(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()

        category_key = query.data.replace("leaderboard_", "")
        print("➡️ Leaderboard button pressed")
        print("Category Data:", category_key)

        try:
            records = self.sheet.get_all_records()
        except Exception as e:
            await query.message.reply_text(f"⚠️ Failed to fetch leaderboard data: {e}")
            return

        category_data = [row for row in records if str(row.get("category", "")).lower() == category_key.lower()]
        if not category_data:
            await query.message.reply_text("⚠️ No data available for this category.")
            return

        sorted_data = sorted(category_data, key=lambda x: (
            -float(str(x.get('percentage', '0%')).replace('%', '')),
            int(x.get('time_taken', 9999))
        ))

        names, percentages = [], []
        emojis = ['🥇', '🥈', '🥉']

        for idx, row in enumerate(sorted_data[:10]):
            rank = emojis[idx] if idx < 3 else f"{idx + 1}."
            name = row.get("name") or row.get("username") or f"User_{row.get('user_id', 'Unknown')}"
            names.append(f"{rank} {name}")
            perc_str = str(row.get("percentage", "0%")).replace('%', '')
            percentages.append(float(perc_str))

        font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
        emoji_font = None
        for font_path in font_paths:
            if any(keyword in font_path.lower() for keyword in ['seguiemj', 'noto', 'symbola']):
                emoji_font = fm.FontProperties(fname=font_path)
                break
        if emoji_font:
            plt.rcParams['font.family'] = emoji_font.get_name()

        try:
            plt.figure(figsize=(10, 6))
            bars = plt.barh(names[::-1], percentages[::-1], color='cornflowerblue')
            plt.xlabel("Percentage")
            plt.title(f"Leaderboard - {CATEGORIES.get(category_key, category_key).title()}")
            plt.xlim(0, 100)
            plt.tight_layout()

            image_path = "leaderboard_image.png"
            plt.savefig(image_path)
            plt.close()

            with open(image_path, "rb") as photo:
                await query.message.reply_photo(photo=photo, caption="📊 Leaderboard by Percentage")
            os.remove(image_path)
        except Exception as e:
            print("❌ Failed to send image:", e)
            await query.message.reply_text("⚠️ Could not generate leaderboard image.")

    async def show_leaderboard(self, update: Update, context: CallbackContext):
        keyboard = [[InlineKeyboardButton(name, callback_data=f"leaderboard_{key}")]
                    for key, name in CATEGORIES.items()]

        if update.callback_query:
            await update.callback_query.edit_message_text(
                "📊 Choose category for leaderboard:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                "📊 Choose category for leaderboard:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

def get_user_rank(user_id: int, category: str, difficulty: str) -> tuple[int, int]:
    SHEET_FILE = "quiz_results.csv"
    if not os.path.exists(SHEET_FILE):
        return 0, 0

    df = pd.read_csv(SHEET_FILE)

    filtered = df[
        (df["category"] == category) &
        (df["difficulty"] == difficulty)
    ].copy()

    filtered["percentage"] = (filtered["score"] / filtered["total"]) * 100

    filtered.sort_values(by=["percentage", "time_taken"], ascending=[False, True], inplace=True)

    filtered.reset_index(drop=True, inplace=True)

    filtered["rank"] = filtered.index + 1
    user_row = filtered[filtered["user_id"] == user_id]

    if not user_row.empty:
        rank = int(user_row.iloc[0]["rank"])
        total_users = len(filtered)
        return rank, total_users

    return 0, len(filtered)

def get_rank_emoji(rank: int) -> str:
    return {
        1: "🥇",
        2: "🥈",
        3: "🥉"
    }.get(rank, "")
