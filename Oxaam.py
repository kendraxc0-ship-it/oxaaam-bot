#Made By @X1n0q | Hex · Oxaam Auto Sign Up + Feedback Bot
#ONE FILE - TWO BOTS RUNNING TOGETHER

import asyncio
import requests
import random
import string
import re
import time
import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

# ── CONFIG ────────────────────────────────────────────────────────────────────
MAIN_TOKEN = "8516833981:AAGfsgG0vDzOzLNC9viruXa9l3wCz53LDOQ"
FEEDBACK_TOKEN = "8815684366:AAGuiGnto1SvfwAZNuFUtzt2yWMNLZJZ_X8" @BotFather
ADMIN_CHAT_ID = "7305141058"  # YOUR TELEGRAM ID

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ── DATA STORAGE ─────────────────────────────────────────────────────────────
class FeedbackDB:
    def __init__(self):
        self.file = "feedback_data.json"
        self.data = self._load()
    
    def _load(self):
        try:
            with open(self.file, 'r') as f:
                return json.load(f)
        except:
            return {"pending": {}}
    
    def _save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_pending(self, user_id, email, password, service):
        self.data["pending"][str(user_id)] = {
            "email": email,
            "password": password,
            "service": service,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self._save()
    
    def get_pending(self, user_id):
        return self.data["pending"].get(str(user_id))
    
    def clear_pending(self, user_id):
        if str(user_id) in self.data["pending"]:
            del self.data["pending"][str(user_id)]
            self._save()
    
    def has_pending(self, user_id):
        return str(user_id) in self.data["pending"]

db = FeedbackDB()

# ── MAIN BOT FUNCTIONS ──────────────────────────────────────────────────────
def generate_user():
    names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Neha"]
    domains = ["gmail.com", "outlook.com", "yahoo.com"]
    name = random.choice(names) + "".join(random.choices(string.ascii_lowercase, k=4))
    email = name.lower() + str(random.randint(100, 999)) + "@" + random.choice(domains)
    phone = "9" + "".join(random.choices(string.digits, k=9))
    password = "Pass@" + "".join(random.choices(string.ascii_letters + string.digits, k=8))
    return {"name": name, "email": email, "phone": phone, "password": password, "country": "India"}

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def extract_krunshyrole():
    logger.info("=== Oxaam Free Services Credential Extractor ===")
    session = requests.Session()
    user = generate_user()
    logger.info(f"Creating Oxaam account...")
    logger.info(f"Email    : {user['email']}")
    logger.info(f"Password : {user['password']}\n")

    signup_data = f"name={user['name']}&email={user['email']}&phone={user['phone']}&password={user['password']}&country={user['country']}"
    session.post("https://www.oxaam.com/", 
                 headers={**headers, "Content-Type": "application/x-www-form-urlencoded", "Referer": "https://www.oxaam.com/"}, 
                 data=signup_data, timeout=15)

    login_data = f"email={user['email']}&password={user['password']}"
    session.post("https://www.oxaam.com/login.php", 
                 headers={**headers, "Content-Type": "application/x-www-form-urlencoded", "Referer": "https://www.oxaam.com/"}, 
                 data=login_data, timeout=15)

    logger.info("Fetching free services page...")
    r = session.get("https://www.oxaam.com/freeservice.php", 
                    headers={**headers, "Referer": "https://www.oxaam.com/dashboard.php"}, timeout=15)

    if r.status_code != 200:
        logger.error(f"❌ Failed (Status: {r.status_code})")
        return None, None, None

    html = r.text
    logger.info("✅ Page loaded. Extracting credentials...")

    filename = f"oxaam_freeservices_{int(time.time())}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"✅ Full page saved as '{filename}'")

    js_match = re.search(r'const CREDENTIALS\s*=\s*(\[.*?\]);', html, re.DOTALL | re.IGNORECASE)
    
    if js_match:
        try:
            creds_json = js_match.group(1)
            creds_json = re.sub(r'(\w+):', r'"\1":', creds_json)  
            credentials = json.loads(creds_json)
            if credentials and isinstance(credentials, list) and len(credentials) > 0:
                pick = random.choice(credentials)  
                email = pick.get("email", "").strip()
                password = pick.get("password", "").strip()
                if email and password:
                    logger.info(f"Server - Krunshyrole Premium")
                    logger.info(f"Email - {email}")
                    logger.info(f"Pass  - {password}")
                    logger.info("-" * 45)
                    return "Krunshyrole Premium", email, password
        except Exception as e:
            logger.warning(f"JS parsing failed: {e}")

    fallback = re.findall(
        r'(Krunshyrole[^<]*?Premium).*?Email[^:➜]*[:➜]\s*([\w\.-]+@[\w\.-]+\.\w+).*?Password[^:➜]*[:➜]\s*([^<"\n]+)',
        html, re.DOTALL | re.IGNORECASE
    )

    for block in fallback:
        if len(block) >= 3:
            service = block[0].replace("&nbsp;", " ").strip().title()
            email = block[1].strip()
            password = block[2].strip()
            logger.info(f"Server - {service}")
            logger.info(f"Email - {email}")
            logger.info(f"Pass  - {password}")
            logger.info("-" * 45)
            return service, email, password

    logger.warning("❌ Could not extract Krunshyrole credentials")
    return None, None, None

# ── MAIN BOT HANDLERS ──────────────────────────────────────────────────────
async def loading_animation(status_msg):
    stages = [
        "Creating fresh Oxaam account...",
        "Logging into Oxaam...",
        "Fetching free services page...",
        "Extracting Krunshyrole Premium credentials..."
    ]
    dots = ["", ".", "..", "..."]
    i = 0
    start_time = time.time()
    while time.time() - start_time < 20:
        stage = stages[i % len(stages)]
        dot = dots[i % len(dots)]
        try:
            await status_msg.edit_text(
                f"🔄 {stage}{dot}\n\n<i>Please wait • Usually takes 8-18 seconds...</i>",
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        await asyncio.sleep(0.7)
        i += 1

async def main_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if db.has_pending(user_id):
        pending = db.get_pending(user_id)
        email = pending.get('email', 'Unknown')
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Working", callback_data=f"fb_working_{user_id}"),
                InlineKeyboardButton("❌ Not Working", callback_data=f"fb_notworking_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚠️ <b>You have a pending account that needs verification!</b>\n\n"
            f"📧 Email: <code>{email}</code>\n\n"
            f"Please click the button below to verify if the account is working.",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        return
    
    keyboard = [[InlineKeyboardButton("🔥 Generate Crunchyroll", callback_data="gen_krunshy")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 <b>Crunchyroll Farmer Bot</b>\n\n"
        "Click the button below to generate fresh <b>Crunchyroll Premium</b> credentials.\n\n"
        "After generation, you'll be asked to verify if the account is working.",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def main_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "gen_krunshy":
        if db.has_pending(user_id):
            pending = db.get_pending(user_id)
            email = pending.get('email', 'Unknown')
            keyboard = [
                [
                    InlineKeyboardButton("✅ Working", callback_data=f"fb_working_{user_id}"),
                    InlineKeyboardButton("❌ Not Working", callback_data=f"fb_notworking_{user_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                f"⚠️ <b>You have a pending account that needs verification!</b>\n\n"
                f"📧 Email: <code>{email}</code>\n\n"
                f"Please verify this account first before generating a new one.",
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
            return
        
        status_msg = await query.message.reply_text("🚀 Starting generation...", parse_mode=ParseMode.HTML)
        animation_task = asyncio.create_task(loading_animation(status_msg))
        service, email, password = await asyncio.to_thread(extract_krunshyrole)
        animation_task.cancel()
        try:
            await animation_task
        except asyncio.CancelledError:
            pass

        if email and password:
            db.add_pending(user_id, email, password, service)
            keyboard = [
                [
                    InlineKeyboardButton("✅ Working", callback_data=f"fb_working_{user_id}"),
                    InlineKeyboardButton("❌ Not Working", callback_data=f"fb_notworking_{user_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            result_text = (
                f"✅ <b>Crunchyroll Premium Generated!</b>\n\n"
                f"<b>Service :</b> CrunchiefarmV6.6\n"
                f"<b>Email   :</b> <code>{email}</code>\n"
                f"<b>Password:</b> <code>{password}</code>\n\n"
                f"<b>📝 Please verify if this account is working:</b>"
            )
            await status_msg.edit_text(result_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            await status_msg.edit_text(
                "❌ <b>Could not extract credentials this time.</b>\n\n"
                "The site may have updated. Try again in a few minutes.",
                parse_mode=ParseMode.HTML
            )

# ── FEEDBACK HANDLERS (SAME BOT) ──────────────────────────────────────────
async def fb_working(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    target_id = int(query.data.split("_")[2])
    
    if str(user_id) != str(target_id) and str(user_id) != ADMIN_CHAT_ID:
        await query.answer("This is for the original requester only.", show_alert=True)
        return
    
    data = db.get_pending(target_id)
    if not data:
        await query.answer("No pending feedback.", show_alert=True)
        return
    
    db.clear_pending(target_id)
    context.user_data['feedback_data'] = data
    context.user_data['feedback_status'] = 'working'
    
    await query.message.reply_text(
        f"✅ Great! The account is working.\n\n"
        f"📸 Please send a screenshot as proof.\n\n"
        f"Just send the image here.",
        parse_mode=ParseMode.HTML
    )
    await query.message.delete()

async def fb_notworking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    target_id = int(query.data.split("_")[2])
    
    if str(user_id) != str(target_id) and str(user_id) != ADMIN_CHAT_ID:
        await query.answer("This is for the original requester only.", show_alert=True)
        return
    
    data = db.get_pending(target_id)
    if not data:
        await query.answer("No pending feedback.", show_alert=True)
        return
    
    db.clear_pending(target_id)
    context.user_data['feedback_data'] = data
    context.user_data['feedback_status'] = 'notworking'
    
    keyboard = [
        [InlineKeyboardButton("❌ Wrong Password", callback_data=f"reason_wrongpass_{target_id}")],
        [InlineKeyboardButton("⏳ Account Expired", callback_data=f"reason_expired_{target_id}")],
        [InlineKeyboardButton("🚫 Already Used", callback_data=f"reason_used_{target_id}")],
        [InlineKeyboardButton("📸 Send Screenshot", callback_data=f"reason_ss_{target_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"❌ Why isn't the account working?",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    await query.message.delete()

async def reason_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    parts = query.data.split("_")
    reason = parts[1]
    target_id = int(parts[2]) if len(parts) > 2 else user_id
    
    if str(user_id) != str(target_id) and str(user_id) != ADMIN_CHAT_ID:
        await query.answer("Not yours!", show_alert=True)
        return
    
    data = context.user_data.get('feedback_data')
    if not data:
        await query.answer("Session expired.", show_alert=True)
        return
    
    if reason == "ss":
        await query.message.reply_text(
            f"📸 Please send a screenshot showing why it's not working.",
            parse_mode=ParseMode.HTML
        )
        await query.message.delete()
        return
    
    reason_map = {
        'wrongpass': '❌ Wrong Password',
        'expired': '⏳ Account Expired',
        'used': '🚫 Already Used',
    }
    reason_text = reason_map.get(reason, reason)
    
    await send_feedback_to_admin(query.message, data, 'notworking', reason_text, None)
    context.user_data.pop('feedback_data', None)
    
    await query.message.reply_text(
        f"✅ Feedback sent! Thank you!",
        parse_mode=ParseMode.HTML
    )
    await query.message.delete()

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = context.user_data.get('feedback_data')
    
    if not data:
        await update.message.reply_text("❌ No pending session. Use /start to generate.")
        return
    
    status = context.user_data.get('feedback_status', 'unknown')
    photo = update.message.photo[-1]
    file = await photo.get_file()
    
    photo_path = f"feedback_{user_id}_{int(time.time())}.jpg"
    await file.download_to_drive(photo_path)
    
    await send_feedback_to_admin(update.message, data, status, "Screenshot sent", photo_path)
    
    context.user_data.pop('feedback_data', None)
    context.user_data.pop('feedback_status', None)
    
    await update.message.reply_text(
        f"✅ Feedback sent! Thank you! 📸\n\n"
        f"Use /start to generate more.",
        parse_mode=ParseMode.HTML
    )

async def send_feedback_to_admin(message, data, status, reason, photo_path=None):
    email = data.get('email', 'Unknown')
    password = data.get('password', 'Unknown')
    service = data.get('service', 'Unknown')
    timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    status_emoji = "✅" if status == "working" else "❌"
    status_text = "WORKING" if status == "working" else "NOT WORKING"
    
    text = (
        f"📊 NEW FEEDBACK\n"
        f"{'─' * 30}\n"
        f"User: {message.from_user.first_name} (ID: {message.from_user.id})\n"
        f"Username: @{message.from_user.username or 'N/A'}\n"
        f"Service: {service}\n"
        f"Email: {email}\n"
        f"Password: {password}\n"
        f"Status: {status_emoji} {status_text}\n"
        f"Reason: {reason}\n"
        f"Time: {timestamp}\n"
    )
    
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as f:
                await message.bot.send_photo(
                    chat_id=ADMIN_CHAT_ID,
                    photo=f,
                    caption=text,
                    parse_mode=ParseMode.HTML
                )
        else:
            await message.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=text,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Failed to send: {e}")
    
    if photo_path and os.path.exists(photo_path):
        try:
            os.remove(photo_path)
        except:
            pass

# ── RUN BOTH BOTS ──────────────────────────────────────────────────────────
def run_bot(token, handlers):
    app = Application.builder().token(token).build()
    for handler in handlers:
        app.add_handler(handler)
    app.run_polling(allowed_updates=Update.ALL_TYPES)

async def run_main_bot():
    handlers = [
        CommandHandler("start", main_start),
        CallbackQueryHandler(main_button, pattern="^gen_krunshy$"),
        CallbackQueryHandler(fb_working, pattern="^fb_working_"),
        CallbackQueryHandler(fb_notworking, pattern="^fb_notworking_"),
        CallbackQueryHandler(reason_handler, pattern="^reason_"),
        MessageHandler(filters.PHOTO, photo_handler),
    ]
    
    app = Application.builder().token(MAIN_TOKEN).build()
    for handler in handlers:
        app.add_handler(handler)
    
    print("🤖 Main Bot is running...")
    await app.initialize()
    await app.start()
    await app.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    print("🚀 Starting both bots...")
    print(f"📊 Admin ID: {ADMIN_CHAT_ID}")
    print("\n")
    
    try:
        asyncio.run(run_main_bot())
    except KeyboardInterrupt:
        print("\n🛑 Bots stopped.")

if __name__ == "__main__":
    main()