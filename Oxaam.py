#Made By @SajagOG | @KindCoders On Telegram. Site Used : Oxaam.com Auto Sign Up & Auto Service Extractor
# UPGRADED v10: FORCED VERIFICATION ON EVERY START - No cached sessions

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
from telegram.error import BadRequest

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== CONFIG =====
BOT_TOKEN = "8516833981:AAGfsgG0vDzOzLNC9viruXa9l3wCz53LDOQ"
OWNER_CHAT_ID = 7305141058
CHANNEL_ID = -1004253692032  # ✅ CORRECT CHANNEL ID
CHANNEL_LINK = "https://t.me/Hexmaincuh"

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

# ===== CHANNEL MEMBERSHIP CHECK =====
async def is_user_in_channel(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """Check if user is a member of the required channel"""
    try:
        logger.info(f"Checking membership for user {user_id} in channel {CHANNEL_ID}")
        chat_member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id
        )
        logger.info(f"User {user_id} status: {chat_member.status}")
        
        if chat_member.status in ['creator', 'administrator', 'member']:
            logger.info(f"✅ User {user_id} IS in channel")
            return True
        else:
            logger.warning(f"❌ User {user_id} is NOT in channel (status: {chat_member.status})")
            return False
            
    except BadRequest as e:
        logger.error(f"BadRequest: {e}")
        if "bot is not a member" in str(e).lower():
            await context.bot.send_message(
                chat_id=OWNER_CHAT_ID,
                text="⚠️ <b>URGENT: Bot is not a member of the channel!</b>\n\n"
                     "Please add the bot to the channel first, then make it an admin.\n"
                     f"Channel ID: {CHANNEL_ID}\n"
                     f"Channel: {CHANNEL_LINK}",
                parse_mode=ParseMode.HTML
            )
        return False
    except Exception as e:
        logger.error(f"Channel check failed: {e}")
        return False

# ===== JOIN PROMPT =====
async def show_join_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, message=None):
    """Display the mandatory join prompt with buttons"""
    keyboard = [
        [InlineKeyboardButton("📢 Click Here to Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Verify Now", callback_data="verify_channel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🔐 <b>Channel Verification Required</b>\n\n"
        "You must join our channel before you can use this bot.\n\n"
        "📌 <b>Why?</b>\n"
        "• Get exclusive updates\n"
        "• Access to premium content\n"
        "• Support the developer\n\n"
        "👇 <b>Click the button below to join, then press Verify Now.</b>"
    )
    
    if message:
        try:
            await message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        except:
            await message.reply_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

# ===== START COMMAND - ALWAYS CHECK VERIFICATION =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"START command from user {user_id}")
    
    # ALWAYS check membership - don't trust cached flag
    if await is_user_in_channel(context, user_id):
        logger.info(f"User {user_id} is verified, showing main menu")
        context.user_data['channel_verified'] = True
        await show_main_menu(update, context)
    else:
        logger.info(f"User {user_id} not verified, showing join prompt")
        # Clear any cached verification
        context.user_data['channel_verified'] = False
        await show_join_prompt(update, context)

# ===== MAIN MENU =====
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, message=None):
    """Show the main generation menu"""
    # Check pending feedback lock
    if context.user_data.get('pending_feedback', False):
        lock_msg = (
            "⛔ <b>PENDING FEEDBACK REQUIRED</b>\n\n"
            "You must submit feedback for the last generated account before you can generate a new one.\n\n"
            "📸 Please send a <b>PHOTO</b> as proof:\n"
            "• ✅ Working → screenshot of working account\n"
            "• ❌ Not Working → screenshot showing the issue\n\n"
            "<i>No text messages accepted. Only photos.</i>"
        )
        if message:
            await message.edit_text(lock_msg, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(lock_msg, parse_mode=ParseMode.HTML)
        return
    
    keyboard = [[InlineKeyboardButton("🔥 Gen Crunchyroll", callback_data="gen_krunshy")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    main_text = (
        "👋 <b>Crunchyroll Farmer Bot</b>\n\n"
        "Click the button to generate fresh <b>Crunchy Premium</b> credentials.\n\n"
        "<i>Shared accounts may expire quickly.</i>"
    )
    
    if message:
        try:
            await message.edit_text(
                main_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        except:
            await message.reply_text(
                main_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_text(
            main_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

# ===== BUTTON HANDLER =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    # ===== VERIFY CHANNEL BUTTON =====
    if query.data == "verify_channel":
        # Check membership
        if await is_user_in_channel(context, user_id):
            context.user_data['channel_verified'] = True
            
            # Show success and immediately show main menu
            await query.edit_message_text(
                "✅ <b>Verification Successful!</b>\n\n"
                "You are now verified. Loading main menu...",
                parse_mode=ParseMode.HTML
            )
            
            # Show main menu after a brief delay
            await asyncio.sleep(0.5)
            await show_main_menu(update, context, query.message)
        else:
            # Not verified - show prompt again
            await query.edit_message_text(
                "❌ <b>Not Verified Yet</b>\n\n"
                "You haven't joined the channel yet.\n"
                "Please click the 'Click Here' button below to join, then press 'Verify Now' again.",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Click Here to Join Channel", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ Verify Now", callback_data="verify_channel")]
                ])
            )
        return
    
    # ===== ALL OTHER ACTIONS REQUIRE CHANNEL VERIFICATION =====
    # ALWAYS re-check - don't trust cached flag
    if not await is_user_in_channel(context, user_id):
        context.user_data['channel_verified'] = False
        await show_join_prompt(update, context, query.message)
        return
    else:
        context.user_data['channel_verified'] = True
    
    # ===== GENERATE BUTTON =====
    if query.data == "gen_krunshy":
        if context.user_data.get('pending_feedback', False):
            await query.edit_message_text(
                "⛔ PENDING FEEDBACK - Send a photo to unlock.",
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
            context.user_data['last_email'] = email
            context.user_data['last_password'] = password
            context.user_data['last_service'] = service
            context.user_data['pending_feedback'] = True
            
            result_text = (
                f"✅ <b>Crunchyroll Premium Generated!</b>\n\n"
                f"<b>Service :</b> <b> CrunchiefarmV6.6</b>\n"
                f"<b>Email   :</b> <code>{email}</code>\n"
                f"<b>Password:</b> <code>{password}</code>\n\n"
                f"⚠️ <b>Shared account • Can get logged out anytime.</b>\n\n"
                f"👇 <b>Is the account working?</b>"
            )
            
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
    
    # ===== FEEDBACK BUTTONS =====
    elif query.data == "feedback_working":
        if not context.user_data.get('pending_feedback', False):
            await query.edit_message_text(
                "⚠️ No pending feedback to submit.",
                parse_mode=ParseMode.HTML
            )
            return
        
        context.user_data['feedback_type'] = 'working'
        
        await query.edit_message_text(
            f"✅ <b>Great! The account is working.</b>\n\n"
            f"📸 <b>Send a screenshot</b> of the account working "
            f"(Crunchyroll dashboard, anime playing, or any proof).\n\n"
            f"<i>Only photos will be accepted.</i>\n"
            f"{time.strftime('%I:%M %p')}",
            parse_mode=ParseMode.HTML
        )
        
    elif query.data == "feedback_notworking":
        if not context.user_data.get('pending_feedback', False):
            await query.edit_message_text(
                "⚠️ No pending feedback to submit.",
                parse_mode=ParseMode.HTML
            )
            return
        
        context.user_data['feedback_type'] = 'not_working'
        
        await query.edit_message_text(
            f"❌ <b>Account not working?</b>\n\n"
            f"📸 <b>Send a screenshot</b> showing the issue (login error, expired, etc.).\n\n"
            f"<i>Only photos will be accepted.</i>",
            parse_mode=ParseMode.HTML
        )

# ===== PHOTO HANDLER =====
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Only photos can clear pending feedback - but MUST be verified first"""
    user_id = update.effective_user.id
    
    # ALWAYS re-check verification
    if not await is_user_in_channel(context, user_id):
        context.user_data['channel_verified'] = False
        await show_join_prompt(update, context)
        return
    else:
        context.user_data['channel_verified'] = True
    
    if context.user_data.get('pending_feedback', False):
        email = context.user_data.get('last_email', 'Unknown')
        password = context.user_data.get('last_password', 'Unknown')
        feedback_type = context.user_data.get('feedback_type', 'unknown')
        username = update.message.from_user.username or "NoUsername"
        
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        if feedback_type == 'working':
            status_emoji = "✅"
            status_text = "WORKING - WITH PROOF"
        elif feedback_type == 'not_working':
            status_emoji = "❌"
            status_text = "NOT WORKING - WITH PROOF"
        else:
            status_emoji = "⚠️"
            status_text = "FEEDBACK RECEIVED"
        
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
        
        context.user_data['pending_feedback'] = False
        context.user_data.pop('feedback_type', None)
        
        await update.message.reply_text(
            f"{status_emoji} <b>Feedback received! Thank you.</b>\n\n"
            "You can now generate a new account using /start.",
            parse_mode=ParseMode.HTML
        )
        
    else:
        await update.message.reply_text(
            "⚠️ You don't have any pending feedback.\n"
            "Use /start to generate a new account.",
            parse_mode=ParseMode.HTML
        )

# ===== TEXT HANDLER =====
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Text is NEVER accepted - only photos"""
    user_id = update.effective_user.id
    
    # ALWAYS re-check verification
    if not await is_user_in_channel(context, user_id):
        context.user_data['channel_verified'] = False
        await show_join_prompt(update, context)
        return
    else:
        context.user_data['channel_verified'] = True
    
    if context.user_data.get('pending_feedback', False):
        await update.message.reply_text(
            "⛔ <b>ONLY PHOTOS ACCEPTED</b>\n\n"
            "Please send a <b>screenshot/photo</b> as feedback.\n"
            "Text messages are not accepted for verification.\n\n"
            "Send a photo to unlock.",
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
    
    print("=" * 60)
    print("🤖 Crunchyroll Generator Bot v10 - FORCED VERIFICATION")
    print("=" * 60)
    print(f"📢 Channel ID: {CHANNEL_ID}")
    print(f"📢 Channel Link: {CHANNEL_LINK}")
    print(f"👤 Owner: {OWNER_CHAT_ID}")
    print("\n✅ EVERY /start checks channel membership - no cached sessions")
    print("=" * 60)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()