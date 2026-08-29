#Made By @X1n0q | Hex · Upgraded from @SajagOG
#Oxaam.com Auto Sign Up & Auto Service Extractor with Pending System

import requests
import random
import string
import re
import asyncio
import time
import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ── CONFIG ────────────────────────────────────────────────────────────────────
TOKEN = "8516833981:AAGfsgG0vDzOzLNC9viruXa9l3wCz53LDOQ"
ADMIN_CHAT_ID = "7305141058"  # Where feedback will be sent
FEEDBACK_CHANNEL = "@https://t.me/sixsevenmaster0101"  # Optional: send to channel too

# ── DATA STORAGE ─────────────────────────────────────────────────────────────
class FeedbackStorage:
    def __init__(self):
        self.pending_feedback = {}  # user_id -> {email, password, service, timestamp}
        self.feedback_log = []      # List of all feedback
    
    def add_pending(self, user_id, email, password, service):
        self.pending_feedback[user_id] = {
            'email': email,
            'password': password,
            'service': service,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_pending(self, user_id):
        return self.pending_feedback.get(user_id)
    
    def clear_pending(self, user_id):
        if user_id in self.pending_feedback:
            del self.pending_feedback[user_id]
    
    def has_pending(self, user_id):
        return user_id in self.pending_feedback

feedback_db = FeedbackStorage()

# ── ORIGINAL FUNCTIONS ──────────────────────────────────────────────────────
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

# ── BOT HANDLERS ─────────────────────────────────────────────────────────────
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # Check if user has pending feedback
    if feedback_db.has_pending(user_id):
        pending_data = feedback_db.get_pending(user_id)
        email = pending_data.get('email', 'Unknown')
        
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
            f"Please click the button below to verify if the account is working.\n\n"
            f"After verification, you can generate a new account using the button below.",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        return
    
    # Normal start menu
    keyboard = [[InlineKeyboardButton("🔥 Generate Crunchyroll", callback_data="gen_krunshy")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 <b>Crunchyroll Farmer Bot</b>\n\n"
        "Click the button below to generate fresh <b>Crunchyroll Premium</b> credentials.\n\n"
        "After generation, you'll be asked to verify if the account is working.\n\n"
        "<i>Shared accounts may expire quickly.</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # ── GENERATE ──────────────────────────────────────────────────────────────
    if query.data == "gen_krunshy":
        # Check if user has pending feedback
        if feedback_db.has_pending(user_id):
            pending_data = feedback_db.get_pending(user_id)
            email = pending_data.get('email', 'Unknown')
            
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
            # Store for feedback
            feedback_db.add_pending(user_id, email, password, service)
            
            # Create feedback buttons
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
            result_text = (
                "❌ <b>Could not extract credentials this time.</b>\n\n"
                "The site may have updated. Try again in a few minutes.\n"
                "Check the saved HTML file for details."
            )
            await status_msg.edit_text(result_text, parse_mode=ParseMode.HTML)

    # ── FEEDBACK: WORKING ──────────────────────────────────────────────────
    elif query.data.startswith("fb_working_"):
        target_user_id = int(query.data.split("_")[2])
        
        # Allow the original user OR admin
        if query.from_user.id != target_user_id and query.from_user.id != int(ADMIN_CHAT_ID):
            await query.answer("This feedback is for the original requester only.", show_alert=True)
            return
        
        data = feedback_db.get_pending(target_user_id)
        if data:
            feedback_db.clear_pending(target_user_id)
            
            context.user_data['feedback_user'] = target_user_id
            context.user_data['feedback_data'] = data
            context.user_data['feedback_status'] = 'working'
            
            await query.message.reply_text(
                f"✅ Great! The account is working.\n\n"
                f"📸 <b>Please send a screenshot</b> of the account working\n"
                f"(Crunchyroll dashboard, anime playing, or any proof).\n\n"
                f"Just send the image here.",
                parse_mode=ParseMode.HTML
            )
            await query.message.delete()
        else:
            await query.answer("Feedback session expired. Generate a new account.", show_alert=True)

    # ── FEEDBACK: NOT WORKING ──────────────────────────────────────────────
    elif query.data.startswith("fb_notworking_"):
        target_user_id = int(query.data.split("_")[2])
        
        if query.from_user.id != target_user_id and query.from_user.id != int(ADMIN_CHAT_ID):
            await query.answer("This feedback is for the original requester only.", show_alert=True)
            return
        
        data = feedback_db.get_pending(target_user_id)
        if data:
            feedback_db.clear_pending(target_user_id)
            
            context.user_data['feedback_user'] = target_user_id
            context.user_data['feedback_data'] = data
            context.user_data['feedback_status'] = 'notworking'
            
            # Ask why
            keyboard = [
                [InlineKeyboardButton("❌ Wrong Password", callback_data=f"reason_wrongpass_{target_user_id}")],
                [InlineKeyboardButton("⏳ Account Expired", callback_data=f"reason_expired_{target_user_id}")],
                [InlineKeyboardButton("🚫 Already Used", callback_data=f"reason_used_{target_user_id}")],
                [InlineKeyboardButton("📸 Send Screenshot", callback_data=f"reason_ss_{target_user_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                f"❌ Sorry the account isn't working.\n\n"
                f"<b>Why is it not working?</b>\n"
                f"Select a reason or send a screenshot:",
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
            await query.message.delete()
        else:
            await query.answer("Feedback session expired. Generate a new account.", show_alert=True)

    # ── REASON SELECTION ──────────────────────────────────────────────────
    elif query.data.startswith("reason_"):
        parts = query.data.split("_")
        reason = parts[1]
        target_user_id = int(parts[2]) if len(parts) > 2 else query.from_user.id
        
        if query.from_user.id != target_user_id and query.from_user.id != int(ADMIN_CHAT_ID):
            await query.answer("This is for the original requester.", show_alert=True)
            return
        
        data = context.user_data.get('feedback_data')
        if not data:
            await query.answer("Session expired. Generate a new account.", show_alert=True)
            return
        
        if reason == "ss":
            await query.message.reply_text(
                f"📸 <b>Please send a screenshot</b> showing why it's not working.\n\n"
                f"Just send the image here.",
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
        
        # Send feedback without screenshot
        await send_feedback(query.message, data, 'notworking', reason_text, None)
        
        await query.message.reply_text(
            f"✅ <b>Feedback sent!</b> Thank you for helping us improve.\n\n"
            f"<b>Reason:</b> {reason_text}\n\n"
            f"🔄 You can now generate a new account using /start",
            parse_mode=ParseMode.HTML
        )
        await query.message.delete()
        context.user_data.pop('feedback_data', None)

# ── SCREENSHOT HANDLER ──────────────────────────────────────────────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = context.user_data.get('feedback_data')
    
    if not data:
        await update.message.reply_text("❌ No pending feedback session. Use /start to generate a new account.")
        return
    
    status = context.user_data.get('feedback_status', 'unknown')
    photo = update.message.photo[-1]
    file = await photo.get_file()
    
    # Download the photo
    photo_path = f"feedback_{user_id}_{int(time.time())}.jpg"
    await file.download_to_drive(photo_path)
    
    # Send feedback with image
    await send_feedback(update.message, data, status, "See screenshot", photo_path)
    
    # Clean up
    context.user_data.pop('feedback_data', None)
    context.user_data.pop('feedback_status', None)
    
    await update.message.reply_text(
        f"✅ <b>Feedback sent!</b> Thank you for the screenshot! 📸\n\n"
        f"🔄 You can now generate a new account using /start",
        parse_mode=ParseMode.HTML
    )

async def send_feedback(message, data, status, reason, photo_path=None):
    """Send feedback to admin/channel"""
    if not data:
        return
    
    email = data.get('email', 'Unknown')
    password = data.get('password', 'Unknown')
    service = data.get('service', 'Crunchyroll')
    timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    status_emoji = "✅" if status == "working" else "❌"
    status_text = "WORKING" if status == "working" else "NOT WORKING"
    
    feedback_text = (
        f"📊 <b>NEW FEEDBACK</b>\n"
        f"{'─' * 30}\n"
        f"<b>User:</b> {message.from_user.first_name} (ID: {message.from_user.id})\n"
        f"<b>Username:</b> @{message.from_user.username or 'N/A'}\n"
        f"<b>Service:</b> {service}\n"
        f"<b>Email:</b> <code>{email}</code>\n"
        f"<b>Password:</b> <code>{password}</code>\n"
        f"<b>Status:</b> {status_emoji} {status_text}\n"
        f"<b>Reason:</b> {reason}\n"
        f"<b>Time:</b> {timestamp}\n"
    )
    
    # Send to admin
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo_file:
                await message.bot.send_photo(
                    chat_id=ADMIN_CHAT_ID,
                    photo=photo_file,
                    caption=feedback_text,
                    parse_mode=ParseMode.HTML
                )
            # Also send to channel if configured
            if FEEDBACK_CHANNEL and FEEDBACK_CHANNEL.startswith('@'):
                with open(photo_path, 'rb') as photo_file:
                    await message.bot.send_photo(
                        chat_id=FEEDBACK_CHANNEL,
                        photo=photo_file,
                        caption=feedback_text,
                        parse_mode=ParseMode.HTML
                    )
        else:
            await message.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=feedback_text,
                parse_mode=ParseMode.HTML
            )
            if FEEDBACK_CHANNEL and FEEDBACK_CHANNEL.startswith('@'):
                await message.bot.send_message(
                    chat_id=FEEDBACK_CHANNEL,
                    text=feedback_text,
                    parse_mode=ParseMode.HTML
                )
    except Exception as e:
        logger.error(f"Failed to send feedback: {e}")
    
    # Clean up photo
    if photo_path and os.path.exists(photo_path):
        try:
            os.remove(photo_path)
        except:
            pass

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 Crunchyroll Generator Bot with Pending System is running...")
    print(f"📊 Feedback will be sent to Admin ID: {ADMIN_CHAT_ID}")
    if FEEDBACK_CHANNEL:
        print(f"📢 Feedback will also be sent to: {FEEDBACK_CHANNEL}")
    print("\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()