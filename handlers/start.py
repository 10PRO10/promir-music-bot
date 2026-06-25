from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database import add_user, get_tracks_count

router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message):
    await add_user(
        user_id=message.from_user.id,
        username=message.from_user.username or '',
        first_name=message.from_user.first_name or ''
    )
    
    count = await get_tracks_count()
    
    text = f"""🎵 <b>Привет, {message.from_user.first_name}!</b>

📊 В базе: <b>{count}</b> треков

📋 <b>Команды:</b>
/playlist — весь плейлист
/random — случайные треки
/search [запрос] — поиск
/find [запрос] — поиск в интернете
/downloaded — скачанные треки
/download — скачать пакетом
/myplaylists — мои плейлисты
/createplaylist — создать плейлист
/favorites — избранное
/help — помощь

💡 <b>Совет:</b> нажми ▶️ чтобы послушать трек"""
    
    await message.answer(text, parse_mode='HTML')

@router.message(Command('help'))
async def cmd_help(message: Message):
    text = """🆘 <b>Помощь</b>

🎵 <b>Плейлист:</b>
• /playlist — показать все треки (постранично)
• /random — 10 случайных треков
• ⏭️ Автовоспроизведение включено!

🔍 <b>Поиск:</b>
• /search Каспийский Груз (поиск в базе)
• /find Каспийский Груз (поиск в интернете)
• Или просто напиши название

▶️ <b>Воспроизведение:</b>
• Нажми ▶️ рядом с треком
• Следующий трек предзагружается автоматически
• Играет мгновенно!

📚 <b>Плейлисты:</b>
• /createplaylist — создать плейлист
• /myplaylists — мои плейлисты

📥 <b>Скачивание:</b>
• /downloaded — показать скачанные треки
• /download — скачать пакетом (10/20/50 треков)

❤️ <b>Избранное:</b>
• /favorites — твои любимые треки"""
    
    await message.answer(text, parse_mode='HTML')