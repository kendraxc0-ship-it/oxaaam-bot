# Made by @X1n0q | Hex
# Crunchyroll Farmer Bot - Pending Lock (NO EXCEPTIONS)

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
                f"🔄 {stage}{dot}\n\n<i>Please wait...</i>",
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        await asyncio.sleep(0.7)
        i += 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # ALWAYS check pending first - NO EXCEPTIONS
    pending_key = f"pending_{user_id}"
    if context.bot_data.get(pending_key, False):
        email = context.bot_data.get(f"pending_email_{user_id}", "Unknown")
        keyboard = [
            [InlineKeyboardButton("✅ Working", callback_data="feedback_working")],
            [InlineKeyboardButton("❌ Not Working", callback_data="feedback_notworking")]
        ]
        await update.message.reply_text(
            f"⚠️ 𝗣𝗲𝗻𝗱𝗶𝗻𝗴 𝗩𝗲𝗿𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻\n\n"
            f"𝗘𝗺𝗮𝗶𝗹: {email}\n\n"
            f"𝗬𝗼𝘂 𝗠𝗨𝗦𝗧 𝗰𝗹𝗶𝗰𝗸 𝗪𝗼𝗿𝗸𝗶𝗻𝗴 𝗼𝗿 𝗡𝗼𝘁 𝗪𝗼𝗿𝗸𝗶𝗻𝗴\n"
            f"𝗯𝗲𝗳𝗼𝗿𝗲 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗶𝗻𝗴 𝗮𝗴𝗮𝗶𝗻.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # ONLY show generate if NO pending
    keyboard = [
        [InlineKeyboardButton("▶ GENERATE", callback_data="gen")],
        [InlineKeyboardButton("📊 STATS", callback_data="stats")],
        [InlineKeyboardButton("❓ HELP", callback_data="help")]
    ]
    
    await update.message.reply_text(
        f"𝗖𝗿𝘂𝗻𝗰𝗵𝘆𝗿𝗼𝗹𝗹 𝗙𝗮𝗿𝗺𝗲𝗿\n\n"
        f"𝟳,𝟱𝟲𝟵 𝘂𝘀𝗲𝗿𝘀 𝗼𝗻𝗹𝗶𝗻𝗲\n"
        f"𝟬.𝟯𝘀 𝗮𝘃𝗴 𝘀𝗽𝗲𝗲𝗱\n\n"
        f"[@X1n0q]",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    if query.data == "gen":
        pending_key = f"pending_{user_id}"
        
        # BLOCK if pending
        if context.bot_data.get(pending_key, False):
            email = context.bot_data.get(f"pending_email_{user_id}", "Unknown")
            keyboard = [
                [InlineKeyboardButton("✅ Working", callback_data="feedback_working")],
                [InlineKeyboardButton("❌ Not Working", callback_data="feedback_notworking")]
            ]
            await query.edit_message_text(
                f"⚠️ 𝗣𝗲𝗻𝗱𝗶𝗻𝗴 𝗩𝗲𝗿𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻\n\n"
                f"𝗘𝗺𝗮𝗶𝗹: {email}\n\n"
                f"𝗬𝗼𝘂 𝗠𝗨𝗦𝗧 𝘃𝗲𝗿𝗶𝗳𝘆 𝗳𝗶𝗿𝘀𝘁!",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # Generate if NO pending
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
            
            # SET PENDING - LOCK THE USER
            context.bot_data[pending_key] = True
            context.bot_data[f"pending_email_{user_id}"] = email

            keyboard = [
                [InlineKeyboardButton("✅ Working", callback_data="feedback_working")],
                [InlineKeyboardButton("❌ Not Working", callback_data="feedback_notworking")]
            ]
            
            await status.edit_text(
                f"✅ 𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗥𝗲𝗮𝗱𝘆\n\n"
                f"𝗘𝗺𝗮𝗶𝗹: {email}\n"
                f"𝗣𝗮𝘀𝘀: {password}\n\n"
                f"⚠️ 𝗦𝗵𝗮𝗿𝗲𝗱 𝗮𝗰𝗰𝗼𝘂𝗻𝘁\n\n"
                f"𝗜𝘀 𝗶𝘁 𝘄𝗼𝗿𝗸𝗶𝗻𝗴?\n\n"
                f"<i>You MUST click Working or Not Working</i>",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await status.edit_text(
                "❌ 𝗙𝗮𝗶𝗹𝗲𝗱\n\n"
                "𝗧𝗿𝘆 𝗮𝗴𝗮𝗶𝗻 𝗶𝗻 𝗮 𝗳𝗲𝘄 𝗺𝗶𝗻𝘂𝘁𝗲𝘀.",
                parse_mode=ParseMode.HTML
            )

    elif query.data == "feedback_working":
        email = context.user_data.get('last_email', 'Unknown')
        password = context.user_data.get('last_password', 'Unknown')
        
        context.user_data['awaiting_screenshot'] = True
        context.user_data['screenshot_email'] = email
        context.user_data['screenshot_password'] = password
        
        # UNLOCK after feedback
        pending_key = f"pending_{user_id}"
        context.bot_data[pending_key] = False
        context.bot_data.pop(f"pending_email_{user_id}", None)
        
        await query.edit_message_text(
            f"📸 𝗦𝗲𝗻𝗱 𝗦𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁\n\n"
            f"𝗦𝗵𝗼𝘄 𝗽𝗿𝗼𝗼𝗳 𝗶𝘁'𝘀 𝘄𝗼𝗿𝗸𝗶𝗻𝗴.\n\n"
            f"𝗘𝗺𝗮𝗶𝗹: {email}",
            parse_mode=ParseMode.HTML
        )

    elif query.data == "feedback_notworking":
        email = context.user_data.get('last_email', 'Unknown')
        password = context.user_data.get('last_password', 'Unknown')
        username = query.from_user.username or "NoUsername"
        
        # UNLOCK after feedback
        pending_key = f"pending_{user_id}"
        context.bot_data[pending_key] = False
        context.bot_data.pop(f"pending_email_{user_id}", None)
        
        # Send to owner
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=f"❌ 𝗡𝗢𝗧 𝗪𝗢𝗥𝗞𝗜𝗡𝗚\n\n𝗨𝘀𝗲𝗿: {user_id} (@{username})\n𝗘𝗺𝗮𝗶𝗹: {email}\n𝗣𝗮𝘀𝘀: {password}",
            parse_mode=ParseMode.HTML
        )
        
        keyboard = [[InlineKeyboardButton("▶ GENERATE", callback_data="gen")]]
        await query.edit_message_text(
            f"❌ 𝗥𝗲𝗽𝗼𝗿𝘁𝗲𝗱\n\n"
            f"𝗬𝗼𝘂 𝗰𝗮𝗻 𝗻𝗼𝘄 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗮𝗴𝗮𝗶𝗻.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "stats":
        stats = context.bot_data.get('stats', {})
        total = stats.get(user_id, {}).get('total', 0)
        working = stats.get(user_id, {}).get('working', 0)
        dead = stats.get(user_id, {}).get('dead', 0)
        
        await query.edit_message_text(
            f"📊 𝗠𝘆 𝗦𝘁𝗮𝘁𝘀\n\n"
            f"𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱: {total}\n"
            f"𝗪𝗼𝗿𝗸𝗶𝗻𝗴: {working}\n"
            f"𝗗𝗲𝗮𝗱: {dead}",
            parse_mode=ParseMode.HTML
        )

    elif query.data == "help":
        await query.edit_message_text(
            f"❓ 𝗛𝗼𝘄 𝘁𝗼 𝗨𝘀𝗲\n\n"
            f"1. 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗮𝗰𝗰𝗼𝘂𝗻𝘁\n"
            f"2. 𝗧𝗲𝘀𝘁 𝗶𝘁\n"
            f"3. 𝗖𝗹𝗶𝗰𝗸 𝗪𝗼𝗿𝗸𝗶𝗻𝗴 𝗼𝗿 𝗡𝗼𝘁 𝗪𝗼𝗿𝗸𝗶𝗻𝗴\n"
            f"4. 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗮𝗴𝗮𝗶𝗻\n\n"
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
            caption=f"✅ 𝗪𝗢𝗥𝗞𝗜𝗡𝗚 (𝗽𝗿𝗼𝗼𝗳)\n\n𝗨𝘀𝗲𝗿: {user_id} (@{username})\n𝗘𝗺𝗮𝗶𝗹: {email}\n𝗣𝗮𝘀𝘀: {password}",
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
        
        keyboard = [[InlineKeyboardButton("▶ GENERATE", callback_data="gen")]]
        await update.message.reply_text(
            f"✅ 𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱\n\n"
            f"𝗬𝗼𝘂 𝗰𝗮𝗻 𝗻𝗼𝘄 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗮𝗴𝗮𝗶𝗻.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            f"⚠️ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝗮 𝘃𝗮𝗹𝗶𝗱 𝗽𝗵𝗼𝘁𝗼 𝗼𝗻𝗹𝘆.\n\n"
            f"𝗬𝗼𝘂𝗿 𝘀𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗮 𝗝𝗣𝗘𝗚 𝗼𝗿 𝗣𝗡𝗚 𝗳𝗶𝗹𝗲.",
            parse_mode=ParseMode.HTML
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if context.user_data.get('awaiting_screenshot', False):
        await update.message.reply_text(
            f"⚠️ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝗮 𝗽𝗵𝗼𝘁𝗼.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # ALWAYS check pending first
    pending_key = f"pending_{user_id}"
    if context.bot_data.get(pending_key, False):
        email = context.bot_data.get(f"pending_email_{user_id}", "Unknown")
        keyboard = [
            [InlineKeyboardButton("✅ Working", callback_data="feedback_working")],
            [InlineKeyboardButton("❌ Not Working", callback_data="feedback_notworking")]
        ]
        await update.message.reply_text(
            f"⚠️ 𝗣𝗲𝗻𝗱𝗶𝗻𝗴 𝗩𝗲𝗿𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻\n\n"
            f"𝗘𝗺𝗮𝗶𝗹: {email}\n\n"
            f"𝗬𝗼𝘂 𝗠𝗨𝗦𝗧 𝗰𝗹𝗶𝗰𝗸 𝗪𝗼𝗿𝗸𝗶𝗻𝗴 𝗼𝗿 𝗡𝗼𝘁 𝗪𝗼𝗿𝗸𝗶𝗻𝗴\n"
            f"𝗯𝗲𝗳𝗼𝗿𝗲 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗶𝗻𝗴 𝗮𝗴𝗮𝗶𝗻.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    await update.message.reply_text(
        f"𝗨𝘀𝗲 /𝘀𝘁𝗮𝗿𝘁 𝘁𝗼 𝗯𝗲𝗴𝗶𝗻.",
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