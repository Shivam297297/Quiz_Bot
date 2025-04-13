import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from config import SHEET_NAME, SHEET_ID, ADMIN_IDS
import os

class Analytics:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json', scope)
        self.client = gspread.authorize(creds)
        try:
            self.sheet = self.client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        except Exception as e:
            print(f"Error accessing Google Sheet: {e}")
            raise

    def save_result(self, user_data, quiz_data):
        try:
            name = user_data.first_name or ""
            username = f"@{user_data.username}" if user_data.username else ""
            display_name = f"{name} {username}".strip()
            new_row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_data.id,
                display_name,
                quiz_data.get('category', 'unknown'),
                quiz_data.get('difficulty', 'unknown'),
                quiz_data.get('score', 0),
                quiz_data.get('total', 1),
                f"{quiz_data.get('score', 0)/max(1, quiz_data.get('total', 1))*100:.2f}%",
                quiz_data.get('time_taken', 0),
                ""  # Rank column (placeholder)
            ]

            print("📤 Saving to sheet:", new_row)
            self.sheet.append_row(new_row)

            # ✅ Recalculate Ranks
            all_records = self.sheet.get_all_values()
            headers = all_records[0]
            rows = all_records[1:]

            if "Rank" not in headers:
                print("⚠️ 'Rank' column missing. Please add 'Rank' as a header in your sheet.")
                return

            score_idx = headers.index("Score")
            time_idx = headers.index("Time Taken")
            rank_idx = headers.index("Rank")

            # Sort by score descending, time ascending
            sorted_rows = sorted(rows, key=lambda x: (-int(x[score_idx]), int(x[time_idx])))

            # Apply new ranks
            for i, row in enumerate(sorted_rows, start=1):
                row[rank_idx] = str(i)

            # Update sheet (excluding header)
            self.sheet.update(f"A2:J{len(sorted_rows)+1}", sorted_rows)

        except Exception as e:
            print(f"❌ Error saving to Google Sheet: {e}")
            try:
                with open("backup_results.txt", "a") as f:
                    f.write(str(new_row) + "\n")
            except Exception as backup_error:
                print(f"❌ Backup failed: {backup_error}")

    def get_category_stats(self, category):
        try:
            worksheet = self.client.open_by_key(SHEET_ID).worksheet(category)
            return worksheet.get_all_records()
        except Exception as e:
            print(f"Error fetching category stats: {e}")
            return []

    async def export_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("Only admins can export results!")
            return
        try:
            records = self.sheet.get_all_records()
            result_text = "Quiz Results:\n\n"
            for record in records:
                result_text += f"User: {record['Name']} | Score: {record['Score']}/{record['Total']} | {record['Percentage']} | Rank: {record.get('Rank', 'N/A')}\n"
            await update.message.reply_text(result_text if records else "No results yet.")
        except Exception as e:
            await update.message.reply_text(f"Error fetching results: {e}")

# Check credentials file on start
print("📁 Checking credentials file path...")
print("Found at:", os.path.exists("credentials.json"))