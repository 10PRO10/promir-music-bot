import os
import glob
import sqlite3
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import get_downloaded_tracks, get_downloaded_count, get_track, clear_downloaded_tracks, DB_PATH

router = Router()

def get_track_by_youtube_id(youtube_id):
    """Найти трек в базе по YouTube ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, title, artist FROM tracks WHERE youtube_url LIKE ?',
            (f'%{youtube_id}%',)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result
    except:
        return None

@router.message(Command('downloaded'))
async def cmd_downloaded(message: Message):
    """Показать ВСЕ файлы из папки downloads с названиями"""
    
    downloads_folder = 'downloads'
    if not os.path.exists(downloads_folder):
        await message.answer("📭 Папка downloads не найдена")
        return
    
    # Получаем все mp3 файлы
    mp3_files = [f for f in os.listdir(downloads_folder) if f.endswith('.mp3')]
    
    if not mp3_files:
        await message.answer("📭 Пока нет скачанных треков\n\nТреки скачиваются когда вы их слушаете")
        return
    
    # Сортируем по дате изменения (новые первые)
    mp3_files.sort(key=lambda f: os.path.getmtime(os.path.join(downloads_folder, f)), reverse=True)
    
    keyboard = []
    text = f"📥 <b>Скачанные файлы ({len(mp3_files)}):</b>\n\n"
    
    for i, filename in enumerate(mp3_files[:50], 1):  # Показываем последние 50
        file_path = os.path.join(downloads_folder, filename)
        file_size = os.path.getsize(file_path)
        size_mb = file_size / (1024 * 1024)
        
        # Извлекаем YouTube ID из имени файла
        youtube_id = filename.replace('.mp3', '')
        
        # Пытаемся найти трек в базе
        track = get_track_by_youtube_id(youtube_id)
        
        if track:
            # Нашли в базе - показываем название
            text += f"{i}. <b>{track['artist']} — {track['title']}</b>\n"
            display_name = f"{track['artist']} - {track['title']}"
        else:
            # Не нашли - показываем имя файла
            text += f"{i}. <b>{filename}</b>\n"
            display_name = filename
        
        text += f"   💾 {size_mb:.1f} MB\n"
        
        # Кнопка отправить
        keyboard.append([
            InlineKeyboardButton(text=f"📤 {i}", callback_data=f"send_file_{filename}")
        ])
    
    keyboard.append([InlineKeyboardButton(text="🗑️ Очистить кэш", callback_data="clear_downloaded")])
    
    await message.answer(
        text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query(F.data == 'clear_downloaded')
async def callback_clear_downloaded(callback: CallbackQuery):
    """Очистить кэш скачанных треков"""
    # Удаляем файлы
    for file in glob.glob('downloads/*.mp3'):
        try:
            os.remove(file)
        except:
            pass
    
    # Очищаем базу
    await clear_downloaded_tracks()
    
    await callback.answer("🗑️ Кэш очищен", show_alert=True)
    await cmd_downloaded(callback.message)

@router.callback_query(F.data.startswith('send_file_'))
async def callback_send_file(callback: CallbackQuery):
    """Отправить файл из downloads"""
    filename = callback.data.replace('send_file_', '')
    file_path = os.path.join('downloads', filename)
    
    if not os.path.exists(file_path):
        await callback.answer("❌ Файл не найден", show_alert=True)
        return
    
    # Пытаемся найти название для отображения
    youtube_id = filename.replace('.mp3', '')
    track = get_track_by_youtube_id(youtube_id)
    
    caption = f"🎵 {track['artist']} - {track['title']}" if track else f"🎵 {filename}"
    
    try:
        await callback.message.answer_audio(
            FSInputFile(file_path),
            caption=caption
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)[:100]}", show_alert=True)