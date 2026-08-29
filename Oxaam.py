# Made by @X1n0q | Hex
# Crunchyroll Farmer Bot - Simple & Clean

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
    session = requests.Session()
    user = generate_user()

    signup_data = f"name={user['name']}&email={user['email']}&phone={user['phone']}&password={user['password']}&country={user['country']}"
    session.post("https://www.oxaam.com/", 
                 headers={**headers, "Content-Type": "application/x-www-form-urlencoded", "Referer": "https://www.oxaam.com/"}, 
                 data=signup_data, timeout=15)

    login_data = f"email={user['email']}&password={user['password']}"
    session.post("https://www.oxaam.com/login.php", 
                 headers={**headers, "Content-Type": "application/x-www-form-urlencoded", "Referer": "https://www.oxaam.com/"}, 
                 data=login_data, timeout=15)

    r = session.get("https://www.oxaam.com/freeservice.php", 
                    headers={**headers, "Referer": "https://www.oxaam.com/dashboard.php"}, timeout=15)

    if r.status_code != 200:
        return None, None, None

    html = r.text
    
    with open(f"oxaam_{int(time.time())}.html", "w", encoding="utf-8") as f:
        f.write(html)

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
                    return "Krunshyrole Premium", email, password
        except:
            pass

    fallback = re.findall(
        r'(Krunshyrole[^<]*?Premium).*?Email[^:➜]*[:➜]\s*([\w\.-]+@[\w\.-]+\.\w+).*?Password[^:➜]*[:➜]\s*([^<"\n]+)',
        html, re.DOTALL | re.IGNORECASE
    )

    for block in fallback:
        if len(block) >= 3:
            service = block[0].replace("&nbsp;", " ").strip().title()
            email = block[1].strip()
            password = block[2].strip()
            return service, email, password

    return None, None, None

async def loading_animation(status_msg):
    stages = [
        "Creating Oxaam account...",
        "Logging in...",
        "Fetching credentials...",
        "Extracting premium..."
    ]
    dots = ["", ".", "..", "..."]
    i = 0
    start = time.time()
    while time.time() - start < 20:
        stage = stages[i % len(stages)]
        dot = dots[i % len(dots)]
        try:
            await status_msg.edit_text(
                f"⚡ {stage}{dot}\n\n<i>Please wait...</i>",
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        await asyncio.sleep(0.7)
        i += 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    pending_key = f"pending_{user_id}"
    if context.bot_data.get(pending_key, False):
        email = context.bot_data.get(f"pending_email_{user_id}", "Unknown")
        keyboard = [
            [InlineKeyboardButton("✅ Working", callback_data="feedback_working")],
            [InlineKeyboardButton("❌ Not Working", callback_data="feedback_notworking")]
        ]
        await update.message.reply_text(
            f"🔒 <b>Pending Verification</b>\n\n"
            f"Account: <code>{email}</code>\n\n"
            f"Please verify before generating another account.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    keyboard = [
        [InlineKeyboardButton("▶ Generate Account", callback_data="gen")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    
    await update.message.reply_text(
        f"🎬 <b>Crunchyroll Farmer</b>\n\n"
        f"• {random.randint(7000, 8000):,} users online\n"
        f"• 0.3s avg speed\n\n"
        f"<i>Made by @X1n0q | Hex</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    if query.data == "gen":
        pending_key = f"pending_{user_id}"
        if context.bot_data.get(pending_key, False):
            email = context.bot_data.get(f"pending_email_{user_id}", "Unknown")
            keyboard = [
                [InlineKeyboardButton("✅ Working", callback_data="feedback_working")],
                [InlineKeyboardButton("❌ Not Working", callback_data="feedback_notworking")]
            ]
            await query.edit_message_text(
                f"🔒 <b>Pending Verification</b>\n\n"
                f"Account: <code>{email}</code>\n\n"
                f"Please verify first.",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        status = await query.message.reply_text("⚡ Generating...", parse_mode=ParseMode.HTML)
        anim = asyncio.create_task(loading_animation(status))
        
        service, email, password = await asyncio.to_thread(extract_krunshyrole)
        
        anim.cancel()
        try:
            await anim
        except:
            pass

        if email and password:
            context.user_data['last_email'] = email
            context.user_data['last_password'] = password
            
            context.bot_data[pending_key] = True
            context.bot_data[f"pending_email_{user_id}"] = email

            keyboard = [
                [InlineKeyboardButton("✅ Working", callback_data="feedback_working")],
                [InlineKeyboardButton("❌ Not Working", callback_data="feedback_notworking")]
            ]
            
            await status.edit_text(
                f"✅ <b>Account Ready</b>\n\n"
                f"📧 <code>{email}</code>\n"
                f"🔑 <code>{password}</code>\n\n"
                f"⚠️ Shared account\n\n"
                f"<i>Is it working?</i>",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await status.edit_text(
                "❌ <b>Failed</b>\n\n"
                "Could not generate account.\n"
                "Please try again in a few minutes.",
                parse_mode=ParseMode.HTML
            )

    elif query.data == "feedback_working":
        email = context.user_data.get('last_email', 'Unknown')
        password = context.user_data.get('last_password', 'Unknown')
        
        context.user_data['awaiting_screenshot'] = True
        context.user_data['screenshot_email'] = email
        context.user_data['screenshot_password'] = password
        
        pending_key = f"pending_{user_id}"
        context.bot_data[pending_key] = False
        context.bot_data.pop(f"pending_email_{user_id}", None)
        
        await query.edit_message_text(
            f"📸 <b>Send Screenshot</b>\n\n"
            f"Show proof it's working.\n\n"
            f"📩 {email}",
            parse_mode=ParseMode.HTML
        )

    elif query.data == "feedback_notworking":
        email = context.user_data.get('last_email', 'Unknown')
        password = context.user_data.get('last_password', 'Unknown')
        username = query.from_user.username or "NoUsername"
        
        pending_key = f"pending_{user_id}"
        context.bot_data[pending_key] = False
        context.bot_data.pop(f"pending_email_{user_id}", None)
        
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=f"❌ NOT WORKING\nUser: {user_id} (@{username})\nEmail: {email}\nPass: {password}",
            parse_mode=ParseMode.HTML
        )
        
        keyboard = [[InlineKeyboardButton("▶ Generate Again", callback_data="gen")]]
        await query.edit_message_text(
            f"❌ <b>Reported</b>\n\n"
            f"Account marked as not working.\n\n"
            f"<i>You can generate again.</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "stats":
        stats = context.bot_data.get('stats', {})
        total = stats.get(user_id, {}).get('total', 0)
        working = stats.get(user_id, {}).get('working', 0)
        dead = stats.get(user_id, {}).get('dead', 0)
        
        await query.edit_message_text(
            f"📊 <b>Your Stats</b>\n\n"
            f"Generated: {total}\n"
            f"Working: {working}\n"
            f"Dead: {dead}\n",
            parse_mode=ParseMode.HTML
        )

    elif query.data == "help":
        await query.edit_message_text(
            f"❓ <b>How to Use</b>\n\n"
            f"1. Generate account\n"
            f"2. Test it\n"
            f"3. Click Working or Not Working\n"
            f"4. Generate again\n\n"
            f"<i>Must verify before generating again.</i>\n\n"
            f"✦ @X1n0q | Hex",
            parse_mode=ParseMode.HTML
        )

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if context.user_data.get('awaiting_screenshot', False):
        email = context.user_data.get('screenshot_email', 'Unknown')
        password = context.user_data.get('screenshot_password', 'Unknown')
        username = update.message.from_user.username or "NoUsername"
        
        photo = update.message.photo[-1]
        
        await context.bot.send_photo(
            chat_id=OWNER_CHAT_ID,
            photo=photo.file_id,
            caption=f"✅ WORKING (with proof)\nUser: {user_id} (@{username})\nEmail: {email}\nPass: {password}",
            parse_mode=ParseMode.HTML
        )
        
        context.user_data['awaiting_screenshot'] = False
        context.user_data.pop('screenshot_email', None)
        context.user_data.pop('screenshot_password', None)
        
        # Update stats
        stats = context.bot_data.get('stats', {})
        if user_id not in stats:
            stats[user_id] = {'total': 0, 'working': 0, 'dead': 0}
        stats[user_id]['total'] = stats[user_id].get('total', 0) + 1
        stats[user_id]['working'] = stats[user_id].get('working', 0) + 1
        context.bot_data['stats'] = stats
        
        keyboard = [[InlineKeyboardButton("▶ Generate Again", callback_data="gen")]]
        await update.message.reply_text(
            f"✅ <b>Verified</b>\n\n"
            f"Thank you!\n\n"
            f"<i>You can generate again.</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "⚠️ No pending verification.",
            parse_mode=ParseMode.HTML
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_screenshot', False):
        await update.message.reply_text(
            "📸 Please send a photo.",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(
            "Use /start to begin.",
            parse_mode=ParseMode.HTML
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("🤖 Bot running...")
    print("📤 Owner:", OWNER_CHAT_ID)
    print("✦ Made by @X1n0q | Hex\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()