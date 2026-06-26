from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import search_tracks, get_track, add_to_favorites
from utils.downloader import search_youtube, search_soundcloud, search_vk, search_any, download_audio
import os

router = Router()

@router.message(Command('search'))
async def cmd_search(message: Message):
    query = message.text.replace('/search', '').strip()
    if not query:
        await message.answer("❗ Укажи запрос: /search Miyagi")
        return
    
    await do_search(message, query)

@router.message(F.text)
async def text_search(message: Message):
    if message.text.startswith('/'):
        return
    
    await do_search(message, message.text)

async def do_search(message: Message, query: str):
    results = await search_tracks(query, limit=10)
    
    if not results:
        await message.answer(f"😔 По запросу «{query}» ничего не найдено")
        return
    
    builder = InlineKeyboardBuilder()
    text = f"🔍 Найдено по запросу «<b>{query}</b>»:\n\n"
    
    for i, track in enumerate(results, 1):
        text += f"{i}. <b>{track['artist']}</b> — {track['title']}\n"
        builder.button(text=f"▶️", callback_data=f"play_{track['id']}")
        builder.button(text=f"❤️", callback_data=f"fav_{track['id']}")
    
    builder.adjust(2)
    
    await message.answer(text, parse_mode='HTML', reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith('play_'))
async def callback_play(callback: CallbackQuery):
    track_id = int(callback.data.split('_')[1])
    track = await get_track(track_id)
    
    if not track:
        await callback.answer("Трек не найден", show_alert=True)
        return
    
    await callback.answer(f"▶️ {track['title']}", show_alert=False)
    
    try:
        # Ищем на всех сервисах
        youtube_url, platform = await search_any(f"{track['artist']} {track['title']}")
        
        if not youtube_url:
            await callback.message.answer("😔 Ничего не найдено ни на одном сервисе")
            return
        
        await callback.message.answer(f"⏳ Скачиваю с {platform}...", parse_mode='HTML')
        
        audio_path = await download_audio(youtube_url, track_id=track_id)
        
        if not audio_path or not os.path.exists(audio_path):
            await callback.message.answer(" Ошибка скачивания")
            return
        
        await callback.message.answer_audio(
            FSInputFile(audio_path),
            title=track['title'][:30],
            performer=track['artist'][:30],
            caption=f"🎵 {track['artist']}\n{track['title']}\n📡 Источник: {platform}"
        )
        
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)[:100]}")

@router.callback_query(F.data.startswith('fav_'))
async def callback_fav(callback: CallbackQuery):
    track_id = int(callback.data.split('_')[1])
    await add_to_favorites(callback.from_user.id, track_id)
    
    track = await get_track(track_id)
    await callback.answer(f"❤️ Добавлено: {track['artist']} — {track['title']}", show_alert=True)

@router.message(Command('find'))
async def cmd_find(message: Message):
    """Поиск трека на всех сервисах"""
    query = message.text.replace('/find', '').strip()
    
    if not query:
        await message.answer("❗ Укажи запрос: /find Miyagi")
        return
    
    await message.answer(
        f"🔍 <b>Ищу на всех сервисах:</b> {query}\n\n"
        f"📡 SoundCloud → YouTube → VK → Bandcamp",
        parse_mode='HTML'
    )
    
    # Ищем на всех сервисах
    url, platform = await search_any(query)
    
    if not url:
        await message.answer("😔 Ничего не найдено ни на одном сервисе\n\nПопробуй другой запрос")
        return
    
    await message.answer(f"✅ <b>Найдено на {platform}!</b>\n\n⏳ Скачиваю...", parse_mode='HTML')
    
    try:
        audio_path = await download_audio(url)
        
        if not audio_path or not os.path.exists(audio_path):
            await message.answer("❌ Ошибка скачивания")
            return
        
        await message.answer_audio(
            FSInputFile(audio_path),
            caption=f"🎵 Найдено и скачано\n📡 Источник: {platform}"
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)[:100]}")