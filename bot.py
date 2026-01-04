import asyncio
import time
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ───── НАСТРОЙКИ ─────
BOT_TOKEN = "TOKEN_ОТ_BOTFATHER"

ADMINS = [123456789]  # ID админов
allowed_group_id = None  # разрешённая группа

# антифлуд
FLOOD_LIMIT = 5
FLOOD_TIME = 7
flood = {}

# реакции
REACTION_CHANCE = 0.15
REACTIONS = ["👍", "😂", "🔥", "😎", "🤖", "💯", "👀"]

# ───── 30 ТРИГГЕРОВ С РАНДОМОМ ─────
TRIGGERS = {
    "Фокс": ["давай гуляй", "ало ало", "чеши отсюда"],
    "как дела": ["все плохо", "я на похоронах, хороню твоего папу", "плачу и грущу"],
    "бот": ["я быстрее твоего ириса", "нахуй иди", "чё надо"],
    "помоги": ["помощи здесь нет", "напиши дами или фоксу что-ли"],
    "спам": ["я твоего отца спермой заспамил"],
    "админ": ["хуй тебе"],
    "работаешь": ["я вот 24/7 без выходных"],
    "кто ты": ["я лично твой ебырь"],
    "правила": ["чувак всем похуй на правила, их владелец даже не знает"],
    "ссылка": ["хуесос ссылки запрещены"],
    "докс": ["я задоксил своим членом твою парализованную бабушку"],
    "мут": ["в хуй твой мут"],
    "бан": ["в хуй твой бан"],
    "чат": ["спасите помогите, я в рабстве"],
    "группа": ["это ниихуя не защищённая группа"],
    "мама": ["у тебя мать сдохла"],
    "лол": ["ахахахаха ржака мем 2026", "посмеялся от души товарищ, не шути больше"],
    "б": ["лудики ебучие блять"],
    "ок": ["👌", "Принято"],
    "да": ["пизда"],
    "нет": ["минет"],
    "что": ["хуй в ебло"],
    "почему": ["по качеришке"],
    "зачем": ["так надо"],
    "ботик": ["твоя мать шлюха"],
    "помоги": ["напиши админам"],
    "шлюха": ["твоя мать"],
    "гуляй": ["сорри не могу, твой отец мешает"],
    "admin": ["Admin mode on"],
    "рейдить": ["я тебе по ебалу постучу"],
}

# ───── ИНИЦИАЛИЗАЦИЯ ─────
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ───── КНОПКИ ─────
def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Разрешить группу", callback_data="allow_group")],
        [InlineKeyboardButton(text="➖ Запретить группу", callback_data="disallow_group")],
        [InlineKeyboardButton(text="📊 Статус", callback_data="status")]
    ])

def user_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")]
    ])

# ───── АНТИФЛУД ─────
def is_flood(user_id):
    now = time.time()
    flood.setdefault(user_id, [])
    flood[user_id] = [t for t in flood[user_id] if now - t < FLOOD_TIME]
    flood[user_id].append(now)
    return len(flood[user_id]) > FLOOD_LIMIT

# ───── ОСНОВНОЙ ОБРАБОТЧИК ГРУПП ─────
@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def group_guard(message: Message):
    global allowed_group_id

    # доступ к группе
    if allowed_group_id is None or message.chat.id != allowed_group_id:
        await bot.leave_chat(message.chat.id)
        return

    # игнор сообщений от ботов
    if message.from_user.is_bot:
        return

    # рандомная реакция
    if random.random() < REACTION_CHANCE:
        try:
            await bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[{"type": "emoji", "emoji": random.choice(REACTIONS)}]
            )
        except:
            pass

    # антифлуд
    if is_flood(message.from_user.id):
        await message.delete()
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            permissions={}
        )
        return

    # триггеры (reply-сообщения ТЕПЕРЬ ОБРАБАТЫВАЮТСЯ)
    if message.text:
        text = message.text.lower()
        for trigger, responses in TRIGGERS.items():
            if trigger in text:
                await message.reply(random.choice(responses))
                break

# ───── /start В ЛС ─────
@dp.message(F.text == "/start", F.chat.type == "private")
async def start_private(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer(
            "👑 **Админ-панель**",
            reply_markup=admin_menu(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "👋 Привет!\n\n"
            "Я — бот для защиты группы.\n\n"
            "🛡 Возможности:\n"
            "• антиспам\n"
            "• антифлуд\n"
            "• триггеры с рандомом\n"
            "• реакции\n"
            "• контроль доступа\n\n"
            "Работаю 24/7 🤖",
            reply_markup=user_menu()
        )

# ───── КНОПКИ ─────
@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ **О боте**\n\n"
        "Бот реагирует на фразы участников,\n"
        "ставит реакции и автоматически следит за порядком.",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "allow_group")
async def allow_group(callback: CallbackQuery):
    global allowed_group_id
    if callback.from_user.id not in ADMINS:
        return
    allowed_group_id = callback.message.chat.id
    await callback.message.edit_text(
        f"✅ **Группа разрешена**\nID: `{allowed_group_id}`",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "disallow_group")
async def disallow_group(callback: CallbackQuery):
    global allowed_group_id
    if callback.from_user.id not in ADMINS:
        return
    allowed_group_id = None
    await callback.message.edit_text(
        "❌ **Доступ ко всем группам отключён**",
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "status")
async def status(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        return
    await callback.message.edit_text(
        f"📊 **Статус бота**\n\n"
        f"Группа: `{allowed_group_id}`\n"
        f"Антифлуд: ✅\n"
        f"Триггеров: {len(TRIGGERS)}\n"
        f"Реакции: ✅",
        parse_mode="Markdown"
    )

# ───── ЗАПУСК ─────
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
