import json import os from dotenv import load_dotenv from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup from telegram.ext import ( ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes )

load_dotenv() TOKEN = os.getenv("BOT_TOKEN")

DATA_FILE = "tasks.json"

def load_data(): if not os.path.exists(DATA_FILE): return {} with open(DATA_FILE, "r") as f: return json.load(f)

def save_data(data): with open(DATA_FILE, "w") as f: json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "✅ Welcome to Task Manager Bot!\n\n" "Commands:\n" "/add <task> - Add new task\n" "/list - List your tasks\n" "You can also mark tasks done or delete them using buttons." )

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = str(update.message.chat_id) data = load_data()

task_text = " ".join(context.args)
if not task_text:
    await update.message.reply_text("⚠️ Please provide a task description. Example:\n/add Buy groceries")
    return

if user_id not in data:
    data[user_id] = []

data[user_id].append({"task": task_text, "done": False})
save_data(data)

await update.message.reply_text(f"✅ Task added: {task_text}")

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE): user_id = str(update.message.chat_id) data = load_data()

if user_id not in data or not data[user_id]:
    await update.message.reply_text("📭 No tasks found. Use /add to create one.")
    return

for i, task in enumerate(data[user_id]):
    status = "✅" if task["done"] else "❌"
    text = f"{status} {task['task']}"

    keyboard = [
        [
            InlineKeyboardButton("Mark Done ✅", callback_data=f"done_{i}"),
            InlineKeyboardButton("Delete 🗑️", callback_data=f"del_{i}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query user_id = str(query.message.chat_id) data = load_data()

await query.answer()

if user_id not in data:
    await query.edit_message_text("⚠️ No tasks found.")
    return

if query.data.startswith("done_"):
    idx = int(query.data.split("_")[1])
    if idx < len(data[user_id]):
        data[user_id][idx]["done"] = True
        save_data(data)
        await query.edit_message_text(f"✅ Marked as done: {data[user_id][idx]['task']}")
    else:
        await query.edit_message_text("⚠️ Task not found.")

elif query.data.startswith("del_"):
    idx = int(query.data.split("_")[1])
    if idx < len(data[user_id]):
        removed_task = data[user_id].pop(idx)
        save_data(data)
        await query.edit_message_text(f"🗑️ Deleted: {removed_task['task']}")
    else:
        await query.edit_message_text("⚠️ Task not found.")

if name == 'main': app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_task))
app.add_handler(CommandHandler("list", list_tasks))
app.add_handler(CallbackQueryHandler(button_handler))

print("🤖 Task Manager Bot is running...")
app.run_polling()

