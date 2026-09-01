#Made By @SajagOG | @KindCoders On Telegram.
#UPGRADED v11: MULTI-SERVICE EXTRACTOR - Fetches ALL free services from Oxaam

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
CHANNEL_ID = -1004253692032
CHANNEL_LINK = "https://t.me/Hexmaincuh"

# ===== SERVICE LIST =====
SERVICES = [
    "DAZN Ultimate",
    "Beautiful.ai",
    "Perplexity Pro",
    "Rakuten Viki",
    "Hoichoi TV",
    "SonyLIV",
    "The Economist Premium",
    "Jasper AI",
    "Figma AI",
    "Brilliant Premium",
    "YouTube Premium",
    "Prime Video",
    "Gemini Enterprise",
    "Tidal Premium",
    "Adobe Pro",
    "Crunchyroll Premium",
    "TradingView Premium",
    "Grammarly Pro",
    "Pluralsight",
    "Skillshare Premium",
    "Scribd Premium",
    "Super Duolingo"
]

def generate_user():
    names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Neha", "Arjun", "Kiran"]
    domains = ["gmail.com", "outlook.com", "yahoo.com", "protonmail.com"]
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

def extract_all_services():
    """
    Extract ALL free services from Oxaam.
    Returns a dict of {service_name: (email, password)}
    """
    logger.info("=== Oxaam Multi-Service Extractor ===")
    
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
        return {}

    html = r.text
    logger.info("✅ Page loaded. Extracting ALL services...")

    # ─── METHOD 1: Parse JS Array ──────────────────────────────────────────
    all_services = {}
    
    js_match = re.search(r'const CREDENTIALS\s*=\s*(\[.*?\]);', html, re.DOTALL | re.IGNORECASE)
    
    if js_match:
        try:
            creds_json = js_match.group(1)
            creds_json = re.sub(r'(\w+):', r'"\1":', creds_json)
            credentials = json.loads(creds_json)
            
            for cred in credentials:
                service = cred.get("service", "").strip()
                email = cred.get("email", "").strip()
                password = cred.get("password", "").strip()
                if service and email and password:
                    # Clean up service name
                    service = re.sub(r'<[^>]+>', '', service)
                    service = service.replace("&nbsp;", " ").strip()
                    all_services[service] = (email, password)
                    logger.info(f"✅ {service}: {email} | {password}")
        except Exception as e:
            logger.warning(f"JS parsing failed: {e}")

    # ─── METHOD 2: Fallback Regex ──────────────────────────────────────────
    if not all_services:
        # Pattern for service blocks
        pattern = r'<div[^>]*class="[^"]*service[^"]*"[^>]*>.*?<h[23][^>]*>(.*?)</h[23]>.*?(?:Email|email)[^:➜]*[:➜]\s*([\w\.-]+@[\w\.-]+\.\w+).*?(?:Password|password|Pass)[^:➜]*[:➜]\s*([^<"\n]+)'
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            service = match[0].strip()
            email = match[1].strip()
            password = match[2].strip()
            service = re.sub(r'<[^>]+>', '', service)
            service = service.replace("&nbsp;", " ").strip()
            if service and email and password:
                all_services[service] = (email, password)
                logger.info(f"✅ {service}: {email} | {password}")

    # ─── METHOD 3: Direct text parsing ─────────────────────────────────────
    if not all_services:
        # Find all service blocks in the HTML
        blocks = re.split(r'<div[^>]*class="[^"]*col[^"]*"[^>]*>', html)
        
        current_service = None
        current_email = None
        current_password = None
        
        for block in blocks:
            # Look for service name
            service_match = re.search(r'<h[23][^>]*>(.*?)</h[23]>', block, re.DOTALL | re.IGNORECASE)
            if service_match:
                current_service = service_match.group(1).strip()
                current_service = re.sub(r'<[^>]+>', '', current_service)
                current_service = current_service.replace("&nbsp;", " ").strip()
            
            # Look for email
            email_match = re.search(r'(?:Email|email)[^:➜]*[:➜]\s*([\w\.-]+@[\w\.-]+\.\w+)', block, re.IGNORECASE)
            if email_match:
                current_email = email_match.group(1).strip()
            
            # Look for password
            pass_match = re.search(r'(?:Password|password|Pass)[^:➜]*[:➜]\s*([^<"\n]+)', block, re.IGNORECASE)
            if pass_match:
                current_password = pass_match.group(1).strip()
            
            # If we have all three, save it
            if current_service and current_email and current_password:
                all_services[current_service] = (current_email, current_password)
                logger.info(f"✅ {current_service}: {current_email} | {current_password}")
                current_service = None
                current_email = None
                current_password = None

    logger.info(f"✅ Extracted {len(all_services)} services total")
    return all_services

def extract_single_service(service_name):
    """Extract credentials for a specific service."""
    all_services = extract_all_services()
    
    # Try exact match
    if service_name in all_services:
        return service_name, all_services[service_name][0], all_services[service_name][1]
    
    # Try partial match
    for key in all_services:
        if service_name.lower() in key.lower() or key.lower() in service_name.lower():
            return key, all_services[key][0], all_services[key][1]
    
    # Try to find by keywords
    keywords = service_name.lower().split()
    for key in all_services:
        key_lower = key.lower()
        if all(kw in key_lower for kw in keywords):
            return key, all_services[key][0], all_services[key][1]
    
    return None, None, None

def extract_krunshyrole():
    """Legacy function for Crunchyroll only."""
    service, email, password = extract_single_service("Crunchyroll Premium")
    if email and password:
        return service or "Crunchyroll Premium", email, password
    return None, None, None

async def loading_animation(status_msg, service_name="Crunchyroll Premium"):
    stages = [
        "Creating fresh Oxaam account...",
        "Logging into Oxaam...",
        "Fetching free services page...",
        f"Extracting {service_name} credentials..."
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

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"START command from user {user_id}")
    
    if await is_user_in_channel(context, user_id):
        context.user_data['channel_verified'] = True
        await show_main_menu(update, context)
    else:
        context.user_data['channel_verified'] = False
        await show_join_prompt(update, context)

# ===== MAIN MENU =====
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, message=None):
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
    
    # ─── Build service buttons ─────────────────────────────────────────────
    keyboard = []
    row = []
    for i, service in enumerate(SERVICES):
        # Shorten service names for buttons
        short_name = service.replace(" Premium", "").replace(" Pro", "").replace(" Ultimate", "")
        if len(short_name) > 20:
            short_name = short_name[:18] + "…"
        
        row.append(InlineKeyboardButton(f"🎬 {short_name}", callback_data=f"gen_{i}"))
        
        # 2 buttons per row
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Add a "Fetch All" button
    keyboard.append([InlineKeyboardButton("📦 Get ALL Services", callback_data="gen_all")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    main_text = (
        "👋 <b>Premium Account Generator Bot</b>\n\n"
        "Select a service below to get free premium credentials:\n\n"
        f"<i>✅ {len(SERVICES)} services available</i>\n"
        "<i>⚠️ Shared accounts • Can get logged out anytime.</i>"
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
    
    # ─── VERIFY CHANNEL ──────────────────────────────────────────────────────
    if query.data == "verify_channel":
        if await is_user_in_channel(context, user_id):
            context.user_data['channel_verified'] = True
            await query.edit_message_text(
                "✅ <b>Verification Successful!</b>\n\nLoading main menu...",
                parse_mode=ParseMode.HTML
            )
            await asyncio.sleep(0.5)
            await show_main_menu(update, context, query.message)
        else:
            await query.edit_message_text(
                "❌ <b>Not Verified Yet</b>\n\n"
                "Please click the 'Click Here' button below to join.",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 Click Here to Join Channel", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ Verify Now", callback_data="verify_channel")]
                ])
            )
        return
    
    # ─── CHECK VERIFICATION FOR ALL OTHER ACTIONS ──────────────────────────
    if not await is_user_in_channel(context, user_id):
        context.user_data['channel_verified'] = False
        await show_join_prompt(update, context, query.message)
        return
    else:
        context.user_data['channel_verified'] = True
    
    # ─── FETCH ALL SERVICES ─────────────────────────────────────────────────
    if query.data == "gen_all":
        if context.user_data.get('pending_feedback', False):
            await query.edit_message_text("⛔ PENDING FEEDBACK - Send a photo to unlock.", parse_mode=ParseMode.HTML)
            return
        
        status_msg = await query.message.reply_text("🚀 Fetching ALL services...", parse_mode=ParseMode.HTML)
        
        animation_task = asyncio.create_task(loading_animation(status_msg, "ALL SERVICES"))
        
        all_services = await asyncio.to_thread(extract_all_services)
        
        animation_task.cancel()
        try:
            await animation_task
        except asyncio.CancelledError:
            pass
        
        if all_services:
            result_text = "✅ <b>ALL SERVICES EXTRACTED!</b>\n\n"
            for i, (service, (email, password)) in enumerate(all_services.items(), 1):
                result_text += f"{i}. <b>{service}</b>\n"
                result_text += f"   📧 <code>{email}</code>\n"
                result_text += f"   🔑 <code>{password}</code>\n\n"
            
            # Truncate if too long
            if len(result_text) > 4000:
                result_text = result_text[:3900] + "\n\n<i>... truncated</i>"
            
            await status_msg.edit_text(
                result_text,
                parse_mode=ParseMode.HTML
            )
        else:
            await status_msg.edit_text(
                "❌ Could not extract any services.\n\n"
                "The site may have updated. Try again in a few minutes.",
                parse_mode=ParseMode.HTML
            )
        return
    
    # ─── GENERATE SINGLE SERVICE ───────────────────────────────────────────
    if query.data.startswith("gen_"):
        if context.user_data.get('pending_feedback', False):
            await query.edit_message_text("⛔ PENDING FEEDBACK - Send a photo to unlock.", parse_mode=ParseMode.HTML)
            return
        
        # Get service name from index
        try:
            idx = int(query.data.split("_")[1])
            service_name = SERVICES[idx]
        except:
            service_name = "Crunchyroll Premium"
        
        status_msg = await query.message.reply_text(f"🚀 Generating {service_name}...", parse_mode=ParseMode.HTML)
        
        animation_task = asyncio.create_task(loading_animation(status_msg, service_name))
        
        service, email, password = await asyncio.to_thread(extract_single_service, service_name)
        
        animation_task.cancel()
        try:
            await animation_task
        except asyncio.CancelledError:
            pass
        
        if email and password:
            context.user_data['last_email'] = email
            context.user_data['last_password'] = password
            context.user_data['last_service'] = service or service_name
            context.user_data['pending_feedback'] = True
            
            result_text = (
                f"✅ <b>{service or service_name}</b>\n\n"
                f"<b>Service :</b> {service or service_name}\n"
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
                f"❌ <b>Could not extract {service_name} credentials.</b>\n\n"
                "The site may have updated. Try again in a few minutes.",
                parse_mode=ParseMode.HTML
            )
    
    # ─── FEEDBACK BUTTONS ──────────────────────────────────────────────────
    elif query.data == "feedback_working":
        if not context.user_data.get('pending_feedback', False):
            await query.edit_message_text("⚠️ No pending feedback to submit.", parse_mode=ParseMode.HTML)
            return
        
        context.user_data['feedback_type'] = 'working'
        
        await query.edit_message_text(
            f"✅ <b>Great! The account is working.</b>\n\n"
            f"📸 <b>Send a screenshot</b> of the account working.\n\n"
            f"<i>Only photos will be accepted.</i>",
            parse_mode=ParseMode.HTML
        )
        
    elif query.data == "feedback_notworking":
        if not context.user_data.get('pending_feedback', False):
            await query.edit_message_text("⚠️ No pending feedback to submit.", parse_mode=ParseMode.HTML)
            return
        
        context.user_data['feedback_type'] = 'not_working'
        
        await query.edit_message_text(
            f"❌ <b>Account not working?</b>\n\n"
            f"📸 <b>Send a screenshot</b> showing the issue.\n\n"
            f"<i>Only photos will be accepted.</i>",
            parse_mode=ParseMode.HTML
        )

# ===== PHOTO HANDLER =====
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await is_user_in_channel(context, user_id):
        context.user_data['channel_verified'] = False
        await show_join_prompt(update, context)
        return
    else:
        context.user_data['channel_verified'] = True
    
    if context.user_data.get('pending_feedback', False):
        email = context.user_data.get('last_email', 'Unknown')
        password = context.user_data.get('last_password', 'Unknown')
        service = context.user_data.get('last_service', 'Unknown')
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
            f"🎬 Service: {service}\n"
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
    user_id = update.effective_user.id
    
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
            "Use /start to generate a premium account.",
            parse_mode=ParseMode.HTML
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("=" * 60)
    print("🤖 Premium Account Generator Bot v11 - MULTI-SERVICE")
    print("=" * 60)
    print(f"📢 Channel ID: {CHANNEL_ID}")
    print(f"📢 Channel Link: {CHANNEL_LINK}")
    print(f"👤 Owner: {OWNER_CHAT_ID}")
    print(f"📦 Services: {len(SERVICES)} available")
    print("=" * 60)
    print("\n✅ Services available:")
    for i, s in enumerate(SERVICES, 1):
        print(f"   {i:2}. {s}")
    print("=" * 60)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()