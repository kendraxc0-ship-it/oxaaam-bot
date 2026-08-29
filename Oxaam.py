#Made By @SajagOG | @KindCoders On Telegram. Site Used : Oxaam.com Auto Sign Up & Auto Service Extractor
# UPGRADED v2: Mandatory feedback for BOTH outcomes + /start lock until feedback submitted

import requests
import random
import string
import re
import asyncio
import time
import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CONFIG =====
BOT_TOKEN = "8516833981:AAGfsgG0vDzOzLNC9viruXa9l3wCz53LDOQ"
OWNER_CHAT_ID = 7305141058

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
    logger.info("=== Oxaam Free Services Credential Extractor (Bot Mode) ===")
    
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
    user_id = update.effective_user.id
    
    # ===== FEEDBACK LOCK: If pending feedback exists, block new generation =====
    if context.user_data.get('pending_feedback', False):
        await update.message.reply_text(
            "⛔ <b>You have pending feedback for the last generated account.</b>\n\n"
            "Please complete the feedback process first:\n"
            "• If it worked → send a screenshot proof\n"
            "• If it didn't work → send a screenshot or reason\n\n"
            "Use /cancel_feedback if you want to discard and start fresh.",
            parse_mode=ParseMode.HTML
        )
        return

    keyboard = [[InlineKeyboardButton("🔥 Gen Crunchyroll", callback_data="gen_krunshy")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 <b>Crunchyroll Farmer Bot</b>\n\n"
        "Click the button to generate fresh <b>Crunchy Premium</b> credentials.\n\n"
        "<i>Shared accounts may expire quickly.</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "gen_krunshy":
        # Double-check lock
        if context.user_data.get('pending_feedback', False):
            await query.edit_message_text(
                "⛔ You have pending feedback. Complete it first or use /cancel_feedback.",
                parse_mode=ParseMode.HTML
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
            # Store credentials and set pending feedback flag
            context.user_data['last_email'] = email
            context.user_data['last_password'] = password
            context.user_data['last_service'] = service
            context.user_data['pending_feedback'] = True
            context.user_data['awaiting_screenshot'] = False  # reset flag

            result_text = (
                f"✅ <b>Crunchyroll Premium Generated!</b>\n\n"
                f"<b>Service :</b> <b> CrunchiefarmV6.6</b>\n"
                f"<b>Email   :</b> <code>{email}</code>\n"
                f"<b>Password:</b> <code>{password}</code>\n\n"
                f"⚠️ <b>Shared account • Can get logged out anytime.</b>\n\n"
                f"👇 <b>Is the account working?</b>"
            )
            
            # Add feedback buttons
            keyboard = [
                [
                    InlineKeyboardButton("✅ Working", callback_data="feedback_working"),
                    InlineKeyboardButton("❌ Not Working", callback_data="feedback_notworking")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await status_msg.edit_text(
                result_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        else:
            await status_msg.edit_text(
                "❌ <b>Could not extract Krunshyrole credentials this time.</b>\n\n"
                "The site may have updated. Try again in a few minutes.\n"
                "Check the saved HTML file for details.",
                parse_mode=ParseMode.HTML
            )

    # ===== WORKING: ASK FOR SCREENSHOT =====
    elif query.data == "feedback_working":
        email = context.user_data.get('last_email', 'Unknown')
        
        context.user_data['awaiting_screenshot'] = True
        context.user_data['screenshot_email'] = email
        context.user_data['screenshot_password'] = context.user_data.get('last_password', 'Unknown')
        context.user_data['feedback_type'] = 'working'  # track type
        
        await query.edit_message_text(
            f"✅ <b>Great! The account is working.</b>\n\n"
            f"💬 Please send a screenshot of the account working "
            f"(Crunchyroll dashboard, anime playing, or any proof).\n\n"
            f"Just send the image here.\n"
            f"{time.strftime('%I:%M %p')}",
            parse_mode=ParseMode.HTML
        )
        await query.answer("Please send screenshot proof")

    # ===== NOT WORKING: NOW ALSO ASKS FOR SCREENSHOT (mandatory) =====
    elif query.data == "feedback_notworking":
        email = context.user_data.get('last_email', 'Unknown')
        
        context.user_data['awaiting_screenshot'] = True
        context.user_data['screenshot_email'] = email
        context.user_data['screenshot_password'] = context.user_data.get('last_password', 'Unknown')
        context.user_data['feedback_type'] = 'not_working'  # track type
        
        await query.edit_message_text(
            f"❌ <b>Account not working? Please confirm.</b>\n\n"
            f"💬 Send a screenshot showing the issue (login error, expired, etc.) "
            f"or a text reason if you cannot screenshot.\n\n"
            f"Just send the image or type your reason here.",
            parse_mode=ParseMode.HTML
        )
        await query.answer("Please send proof or reason")

# ===== PHOTO HANDLER - RECEIVES SCREENSHOT (for BOTH outcomes) =====
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle screenshot uploads for both working and not working"""
    
    if context.user_data.get('awaiting_screenshot', False):
        email = context.user_data.get('screenshot_email', 'Unknown')
        password = context.user_data.get('screenshot_password', 'Unknown')
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "NoUsername"
        feedback_type = context.user_data.get('feedback_type', 'unknown')
        
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Build caption based on feedback type
        if feedback_type == 'working':
            status_emoji = "✅"
            status_text = "WORKING - WITH PROOF"
        elif feedback_type == 'not_working':
            status_emoji = "❌"
            status_text = "NOT WORKING - WITH PROOF"
        else:
            status_emoji = "⚠️"
            status_text = "FEEDBACK (unknown type)"
        
        caption = (
            f"{status_emoji} <b>{status_text}</b>\n"
            f"👤 User: {user_id} (@{username})\n"
            f"📧 Email: <code>{email}</code>\n"
            f"🔑 Pass: <code>{password}</code>\n"
            f"🕐 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"📸 <i>Screenshot attached</i>"
        )
        
        await context.bot.send_photo(
            chat_id=OWNER_CHAT_ID,
            photo=file_id,
            caption=caption,
            parse_mode=ParseMode.HTML
        )
        
        # Clear all feedback flags
        context.user_data['awaiting_screenshot'] = False
        context.user_data['pending_feedback'] = False
        context.user_data.pop('screenshot_email', None)
        context.user_data.pop('screenshot_password', None)
        context.user_data.pop('feedback_type', None)
        
        # Confirm to user
        await update.message.reply_text(
            f"{status_emoji} <b>Screenshot received! Thank you for your feedback.</b>\n\n"
            "You can now generate a new account using /start.",
            parse_mode=ParseMode.HTML
        )
        
    else:
        await update.message.reply_text(
            "⚠️ You don't have any pending verification.\n"
            "Use /start to generate a new account.",
            parse_mode=ParseMode.HTML
        )

# ===== TEXT HANDLER - ALLOWS TEXT REASON FOR "NOT WORKING" =====
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages - for not working, accept reason text; otherwise remind"""
    
    if context.user_data.get('awaiting_screenshot', False):
        feedback_type = context.user_data.get('feedback_type', 'unknown')
        
        # If feedback is "not_working", accept text reason
        if feedback_type == 'not_working':
            email = context.user_data.get('screenshot_email', 'Unknown')
            password = context.user_data.get('screenshot_password', 'Unknown')
            user_id = update.message.from_user.id
            username = update.message.from_user.username or "NoUsername"
            reason = update.message.text
            
            caption = (
                f"❌ <b>NOT WORKING - TEXT REASON</b>\n"
                f"👤 User: {user_id} (@{username})\n"
                f"📧 Email: <code>{email}</code>\n"
                f"🔑 Pass: <code>{password}</code>\n"
                f"🕐 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"📝 <i>Reason:</i> {reason}"
            )
            
            await context.bot.send_message(
                chat_id=OWNER_CHAT_ID,
                text=caption,
                parse_mode=ParseMode.HTML
            )
            
            # Clear flags
            context.user_data['awaiting_screenshot'] = False
            context.user_data['pending_feedback'] = False
            context.user_data.pop('screenshot_email', None)
            context.user_data.pop('screenshot_password', None)
            context.user_data.pop('feedback_type', None)
            
            await update.message.reply_text(
                "❌ <b>Reason received. Thank you for your feedback!</b>\n\n"
                "You can now generate a new account using /start.",
                parse_mode=ParseMode.HTML
            )
        else:
            # If working, force screenshot
            await update.message.reply_text(
                "📸 For 'Working' feedback, please send a <b>photo/screenshot</b> as proof.\n"
                "Text is only accepted for 'Not Working' reports.",
                parse_mode=ParseMode.HTML
            )
    else:
        await update.message.reply_text(
            "Use /start to generate a Crunchyroll account.",
            parse_mode=ParseMode.HTML
        )

# ===== CANCEL COMMAND TO RESET PENDING FEEDBACK =====
async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow user to cancel pending feedback and unlock /start"""
    if context.user_data.get('pending_feedback', False):
        context.user_data['pending_feedback'] = False
        context.user_data['awaiting_screenshot'] = False
        context.user_data.pop('screenshot_email', None)
        context.user_data.pop('screenshot_password', None)
        context.user_data.pop('feedback_type', None)
        
        await update.message.reply_text(
            "🗑️ <b>Pending feedback cancelled.</b>\n\n"
            "You can now generate a new account using /start.",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            "You have no pending feedback to cancel.",
            parse_mode=ParseMode.HTML
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel_feedback", cancel_feedback))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🤖 Crunchyroll Generator Bot v2 with MANDATORY feedback for BOTH outcomes...")
    print("All feedback + screenshots will be sent to:", OWNER_CHAT_ID)
    print("Users are LOCKED from /start until feedback is submitted.\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()