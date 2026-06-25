import os
import asyncio
import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import get_all_tracks, get_track, get_tracks_count, get_user_favorites
from utils.downloader import search_youtube, download_audio

router = Router()

downloaded_tracks = {}
user_queues = {}
preloaded_tracks = {}
download_tasks = {}

@router.message(Command('playlist'))
async def cmd_playlist(message: Message):
    count = await get_tracks_count()
    
    if count == 0:
        await message.answer("😔 База пуста")
        return
    
    await message.answer(f"📚 <b>Загружаю плейлист...</b>\n\n📊 Всего треков: {count}", parse_mode='HTML')
    
    all_tracks = []
    offset = 0
    limit = 100
    
    while True:
        tracks = await get_all_tracks(limit=limit, offset=offset)
        if not tracks:
            break
        all_tracks.extend(tracks)
        offset += limit
    
    tracks_per_page = 50
    total_pages = (len(all_tracks) + tracks_per_page - 1) // tracks_per_page
    
    await show_playlist_page(message, all_tracks, 1, tracks_per_page, total_pages)

async def show_playlist_page(message: Message, all_tracks: list, page: int, tracks_per_page: int, total_pages: int):
    start_idx = (page - 1) * tracks_per_page
    end_idx = min(start_idx + tracks_per_page, len(all_tracks))
    page_tracks = all_tracks[start_idx:end_idx]
    
    text = f"🎵 <b>Плейлист (страница {page}/{total_pages}):</b>\n\n"
    
    keyboard_buttons = []
    row = []
    
    for i, track in enumerate(page_tracks, start_idx + 1):
        text += f"{i}. <b>{track['artist']}</b> — {track['title']}\n"
        row.append(InlineKeyboardButton(text=f"▶️ {i}", callback_data=f"play_{track['id']}"))
        
        if len(row) == 3:
            keyboard_buttons.append(row)
            row = []
    
    if row:
        keyboard_buttons.append(row)
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"playlist_page_{page-1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"playlist_page_{page+1}"))
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    keyboard_buttons.append([InlineKeyboardButton(text="📥 Скачать пакетом", callback_data="download_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, parse_mode='HTML', reply_markup=keyboard, disable_web_page_preview=True)

@router.callback_query(F.data.startswith('playlist_page_'))
async def callback_playlist_page(callback: CallbackQuery):
    page = int(callback.data.split('_')[2])
    
    all_tracks = []
    offset = 0
    limit = 100
    
    while True:
        tracks = await get_all_tracks(limit=limit, offset=offset)
        if not tracks:
            break
        all_tracks.extend(tracks)
        offset += limit
    
    tracks_per_page = 50
    total_pages = (len(all_tracks) + tracks_per_page - 1) // tracks_per_page
    
    await callback.message.delete()
    await show_playlist_page(callback.message, all_tracks, page, tracks_per_page, total_pages)
    await callback.answer()

@router.callback_query(F.data == 'download_menu')
async def callback_download_menu(callback: CallbackQuery):
    await cmd_download(callback.message)
    await callback.answer()

@router.message(Command('download'))
async def cmd_download(message: Message):
    count = await get_tracks_count()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 10 случайных треков", callback_data="batch_10")],
        [InlineKeyboardButton(text="📦 20 случайных треков", callback_data="batch_20")],
        [InlineKeyboardButton(text="📦 50 случайных треков", callback_data="batch_50")],
        [InlineKeyboardButton(text="❤️ Моё избранное", callback_data="batch_favorites")],
        [InlineKeyboardButton(text=" Hip-Hop", callback_data="genre_hip-hop")],
        [InlineKeyboardButton(text="🎵 Rock", callback_data="genre_rock")],
        [InlineKeyboardButton(text="🎵 Pop", callback_data="genre_pop")],
        [InlineKeyboardButton(text="🎵 Phonk", callback_data="genre_phonk")],
        [InlineKeyboardButton(text="🎵 Patriotic", callback_data="genre_patriotic")],
        [InlineKeyboardButton(text="🔙 Назад к плейлисту", callback_data="show_playlist")],
    ])
    
    text = f"""📥 <b>Меню загрузки</b>

📊 В базе: <b>{count}</b> треков
💾 В кэше: <b>{len(downloaded_tracks)}</b> треков

Выбери пакет для скачивания:
• 10/20/50 — случайные треки
• Избранное — твои любимые
• Жанры — по категориям

⏱️ Каждый трек: 1-3 минуты"""
    
    await message.answer(text, parse_mode='HTML', reply_markup=keyboard)

@router.callback_query(F.data == 'show_playlist')
async def callback_show_playlist(callback: CallbackQuery):
    await cmd_playlist(callback.message)

@router.callback_query(F.data.startswith('batch_'))
async def callback_batch_download(callback: CallbackQuery):
    batch_type = callback.data.split('_')[1]
    
    if batch_type == 'favorites':
        tracks = await get_user_favorites(callback.from_user.id)
        if not tracks:
            await callback.answer("У тебя нет избранных треков", show_alert=True)
            return
    else:
        try:
            count = int(batch_type)
        except:
            count = 10
        
        all_tracks = await get_all_tracks(limit=200)
        tracks = random.sample(all_tracks, min(count, len(all_tracks)))
    
    await start_batch_download(callback.message, tracks, batch_type)
    await callback.answer()

@router.callback_query(F.data.startswith('genre_'))
async def callback_genre_download(callback: CallbackQuery):
    genre = callback.data.split('_')[1]
    
    all_tracks = await get_all_tracks(limit=200)
    genre_tracks = [t for t in all_tracks if t.get('genre', '').lower() == genre.lower()]
    
    if not genre_tracks:
        await callback.answer(f"Жанр {genre} пуст", show_alert=True)
        return
    
    await start_batch_download(callback.message, genre_tracks, f"genre_{genre}")
    await callback.answer()

async def start_batch_download(message: Message, tracks: list, batch_id: str):
    user_id = message.from_user.id
    
    download_tasks[user_id] = {
        'tracks': tracks,
        'current': 0,
        'success': 0,
        'failed': 0,
        'status': 'running'
    }
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏹️ Остановить", callback_data="stop_download")]
    ])
    
    progress_msg = await message.answer(
        f"📥 <b>Начинаю загрузку {len(tracks)} треков...</b>\n\n"
        f"⏳ Это займёт {len(tracks) * 2} - {len(tracks) * 3} минут\n\n"
        f"💡 <i>Совет: можешь закрыть чат, загрузка продолжится</i>",
        parse_mode='HTML',
        reply_markup=keyboard
    )
    
    asyncio.create_task(process_batch_download(message, progress_msg, tracks, user_id))

async def process_batch_download(message: Message, progress_msg: Message, tracks: list, user_id: int):
    task = download_tasks.get(user_id)
    
    for i, track in enumerate(tracks, 1):
        if task and task.get('status') == 'stopped':
            break
        
        if i % 5 == 0 or i == len(tracks):
            progress = int((i / len(tracks)) * 100)
            try:
                await progress_msg.edit_text(
                    f"📥 <b>Загрузка...</b>\n\n"
                    f"📊 Прогресс: {progress}%\n"
                    f"✅ Успешно: {task['success']}\n"
                    f"❌ Ошибок: {task['failed']}\n"
                    f"\n"
                    f"🎵 Сейчас: {track['artist']} — {track['title']}",
                    parse_mode='HTML'
                )
            except:
                pass
        
        try:
            if track['id'] in downloaded_tracks and os.path.exists(downloaded_tracks[track['id']]):
                task['success'] += 1
            else:
                youtube_url = await search_youtube(f"{track['artist']} {track['title']}")
                if youtube_url:
                    audio_path = await download_audio(youtube_url, track_id=track['id'])
                    if audio_path and os.path.exists(audio_path):
                        downloaded_tracks[track['id']] = audio_path
                        task['success'] += 1
                    else:
                        task['failed'] += 1
                else:
                    task['failed'] += 1
        except Exception as e:
            task['failed'] += 1
            print(f"Download error: {e}")
        
        await asyncio.sleep(2)
    
    try:
        await progress_msg.edit_text(
            f"✅ <b>Загрузка завершена!</b>\n\n"
            f"📦 Всего треков: {len(tracks)}\n"
            f"✅ Успешно: {task['success']}\n"
            f"❌ Ошибок: {task['failed']}\n"
            f"💾 В кэше: {len(downloaded_tracks)}",
            parse_mode='HTML'
        )
    except:
        pass
    
    if user_id in download_tasks:
        del download_tasks[user_id]

@router.callback_query(F.data == 'stop_download')
async def callback_stop_download(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in download_tasks:
        download_tasks[user_id]['status'] = 'stopped'
        await callback.answer("⏹️ Остановка загрузки...", show_alert=True)
    else:
        await callback.answer("Нет активной загрузки", show_alert=True)

@router.message(Command('random'))
async def cmd_random(message: Message):
    await play_random(message, message.from_user.id)

@router.callback_query(F.data == 'next_random')
async def callback_next_random(callback: CallbackQuery):
    await play_random(callback.message, callback.from_user.id, callback=callback)

async def play_random(message: Message, user_id: int, callback: CallbackQuery = None):
    tracks = await get_all_tracks(limit=50)
    
    if not tracks:
        await message.answer("😔 Треки не найдены")
        return
    
    random_tracks = random.sample(tracks, min(10, len(tracks)))
    
    user_queues[user_id] = {
        'tracks': random_tracks,
        'current_index': 0
    }
    
    await play_track_from_queue(message, user_id, 0, callback)

async def play_track_from_queue(message: Message, user_id: int, index: int, callback: CallbackQuery = None):
    queue = user_queues.get(user_id)
    
    if not queue or index >= len(queue['tracks']):
        tracks = await get_all_tracks(limit=50)
        if not tracks:
            await message.answer("😔 Треки закончились")
            return
        
        random_tracks = random.sample(tracks, min(10, len(tracks)))
        user_queues[user_id] = {
            'tracks': random_tracks,
            'current_index': 0
        }
        index = 0
    
    track = queue['tracks'][index]
    queue['current_index'] = index
    
    if callback:
        await callback.answer(f"▶️ {track['title']}", show_alert=False)
    
    if user_id in preloaded_tracks and preloaded_tracks[user_id].get('track_id') == track['id']:
        audio_path = preloaded_tracks[user_id]['audio_path']
        loading_msg = await message.answer(f"✅ <b>Воспроизвожу:</b> {track['artist']} — {track['title']}", parse_mode='HTML')
        await asyncio.sleep(1)
        await loading_msg.delete()
        del preloaded_tracks[user_id]
    else:
        loading_msg = await message.answer(f"⏳ <b>Загружаю:</b> {track['artist']} — {track['title']}", parse_mode='HTML')
        
        try:
            if track['id'] in downloaded_tracks and os.path.exists(downloaded_tracks[track['id']]):
                audio_path = downloaded_tracks[track['id']]
                await loading_msg.edit_text(f"✅ <b>Из кэша:</b> {track['artist']} — {track['title']}", parse_mode='HTML')
            else:
                youtube_url = await search_youtube(f"{track['artist']} {track['title']}")
                
                if not youtube_url:
                    await loading_msg.edit_text(f"❌ <b>Не найдено</b>")
                    return
                
                audio_path = await download_audio(youtube_url, track_id=track['id'])
                
                if not audio_path or not os.path.exists(audio_path):
                    await loading_msg.edit_text(f"❌ <b>Ошибка</b>")
                    return
                
                downloaded_tracks[track['id']] = audio_path
            
            await loading_msg.delete()
            
        except Exception as e:
            await loading_msg.edit_text(f"❌ <b>Ошибка:</b> {str(e)[:100]}")
            return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭️ Следующий", callback_data="next_random")]
    ])
    
    await message.answer_audio(
        FSInputFile(audio_path),
        title=track['title'][:30],
        performer=track['artist'][:30],
        caption=f"🎵 <b>{track['artist']}</b>\n{track['title']}",
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    next_index = index + 1
    if next_index < len(queue['tracks']):
        next_track = queue['tracks'][next_index]
        asyncio.create_task(preload_track(user_id, next_track))

async def preload_track(user_id: int, track: dict):
    print(f"🔄 Предзагрузка: {track['artist']} — {track['title']}")
    
    try:
        if track['id'] in downloaded_tracks or (user_id in preloaded_tracks and preloaded_tracks[user_id].get('track_id') == track['id']):
            return
        
        youtube_url = await search_youtube(f"{track['artist']} {track['title']}")
        if not youtube_url:
            return
        
        audio_path = await download_audio(youtube_url, track_id=track['id'])
        if audio_path and os.path.exists(audio_path):
            preloaded_tracks[user_id] = {
                'track_id': track['id'],
                'audio_path': audio_path
            }
            print(f"✅ Предзагружено: {track['title']}")
    except Exception as e:
        print(f"❌ Ошибка предзагрузки: {e}")

@router.callback_query(F.data.startswith('play_'))
async def callback_play(callback: CallbackQuery):
    track_id = int(callback.data.split('_')[1])
    track = await get_track(track_id)
    
    if not track:
        await callback.answer("Трек не найден", show_alert=True)
        return
    
    await callback.answer(f"▶️ {track['title']}", show_alert=False)
    
    loading_msg = await callback.message.answer(f"⏳ <b>Загружаю:</b> {track['artist']} — {track['title']}", parse_mode='HTML')
    
    try:
        if track_id in downloaded_tracks and os.path.exists(downloaded_tracks[track_id]):
            audio_path = downloaded_tracks[track_id]
            await loading_msg.edit_text(f"✅ <b>Из кэша:</b> {track['artist']} — {track['title']}", parse_mode='HTML')
        else:
            youtube_url = await search_youtube(f"{track['artist']} {track['title']}")
            
            if not youtube_url:
                await loading_msg.edit_text(f"❌ <b>Не найдено</b>")
                return
            
            audio_path = await download_audio(youtube_url, track_id=track_id)
            
            if not audio_path or not os.path.exists(audio_path):
                await loading_msg.edit_text(f"❌ <b>Ошибка</b>")
                return
            
            downloaded_tracks[track_id] = audio_path
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭️ Следующий случайный", callback_data="next_random")]
        ])
        
        await loading_msg.delete()
        
        await callback.message.answer_audio(
            FSInputFile(audio_path),
            title=track['title'][:30],
            performer=track['artist'][:30],
            caption=f"🎵 <b>{track['artist']}</b>\n{track['title']}",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await loading_msg.edit_text(f"❌ <b>Ошибка:</b> {str(e)[:100]}")