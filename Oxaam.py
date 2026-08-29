#Made By @SajagOG | @KindCoders On Telegram. Site Used : Oxaam.com Auto Sign Up & Auto Service Extractor
# UPGRADED: Full screenshot verification - sends proof to owner

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
        status_msg = await query.message.reply_text("🚀 Starting generation...", parse_mode=ParseMode.HTML)

        animation_task = asyncio.create_task(loading_animation(status_msg))

        service, email, password = await asyncio.to_thread(extract_krunshyrole)

        animation_task.cancel()
        try:
            await animation_task
        except asyncio.CancelledError:
            pass

        if email and password:
            # Store credentials in context for feedback
            context.user_data['last_email'] = email
            context.user_data['last_password'] = password
            context.user_data['last_service'] = service
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
        
        # Set flag that we're awaiting screenshot
        context.user_data['awaiting_screenshot'] = True
        context.user_data['screenshot_email'] = email
        context.user_data['screenshot_password'] = context.user_data.get('last_password', 'Unknown')
        
        await query.edit_message_text(
            f"✅ <b>Great! The account is working.</b>\n\n"
            f"💬 Please send a screenshot of the account working "
            f"(Crunchyroll dashboard, anime playing, or any proof).\n\n"
            f"Just send the image here.\n"
            f"{time.strftime('%I:%M %p')}",
            parse_mode=ParseMode.HTML
        )
        await query.answer("Please send screenshot proof")

    # ===== NOT WORKING: DIRECT FEEDBACK =====
    elif query.data == "feedback_notworking":
        email = context.user_data.get('last_email', 'Unknown')
        password = context.user_data.get('last_password', 'Unknown')
        user_id = query.from_user.id
        username = query.from_user.username or "NoUsername"
        
        feedback_text = (
            f"❌ <b>NOT WORKING</b>\n"
            f"👤 User: {user_id} (@{username})\n"
            f"📧 Email: <code>{email}</code>\n"
            f"🔑 Pass: <code>{password}</code>\n"
            f"🕐 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=feedback_text,
            parse_mode=ParseMode.HTML
        )
        
        await query.edit_message_text(
            "❌ <b>Thank you for your feedback!</b>\n\n"
            "Account marked as NOT WORKING.\n"
            "Use /start to generate another.",
            parse_mode=ParseMode.HTML
        )
        await query.answer("Feedback sent: Not Working ❌")

# ===== PHOTO HANDLER - RECEIVES SCREENSHOT =====
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle screenshot uploads from users"""
    
    # Check if user is in screenshot-awaiting state
    if context.user_data.get('awaiting_screenshot', False):
        email = context.user_data.get('screenshot_email', 'Unknown')
        password = context.user_data.get('screenshot_password', 'Unknown')
        user_id = update.message.from_user.id
        username = update.message.from_user.username or "NoUsername"
        
        # Get the photo (highest quality)
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Send to owner with full details + screenshot
        caption = (
            f"✅ <b>WORKING - WITH PROOF</b>\n"
            f"👤 User: {user_id} (@{username})\n"
            f"📧 Email: <code>{email}</code>\n"
            f"🔑 Pass: <code>{password}</code>\n"
            f"🕐 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"📸 <i>Screenshot proof attached below</i>"
        )
        
        await context.bot.send_photo(
            chat_id=OWNER_CHAT_ID,
            photo=file_id,
            caption=caption,
            parse_mode=ParseMode.HTML
        )
        
        # Clear the flag
        context.user_data['awaiting_screenshot'] = False
        context.user_data.pop('screenshot_email', None)
        context.user_data.pop('screenshot_password', None)
        
        # Confirm to user
        await update.message.reply_text(
            "✅ <b>Screenshot received! Thank you for verifying.</b>\n\n"
            "Account marked as WORKING with proof.\n"
            "Use /start to generate another.",
            parse_mode=ParseMode.HTML
        )
        
    else:
        await update.message.reply_text(
            "⚠️ You don't have any pending verification.\n"
            "Use /start to generate a new account.",
            parse_mode=ParseMode.HTML
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages - remind user to send photo if awaiting screenshot"""
    if context.user_data.get('awaiting_screenshot', False):
        await update.message.reply_text(
            "📸 Please send a <b>photo/screenshot</b> as proof.\n"
            "Text messages are not accepted for verification.",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            "Use /start to generate a Crunchyroll account.",
            parse_mode=ParseMode.HTML
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🤖 Crunchyroll Generator Bot with Screenshot Verification is running...")
    print("All feedback + screenshots will be sent to:", OWNER_CHAT_ID)
    print("Terminal shows full logs. HTML files are saved for debugging.\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()