from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import create_playlist, add_track_to_playlist, get_user_playlists, get_playlist_tracks, delete_playlist, get_track, search_tracks, get_user_favorites

router = Router()

class PlaylistStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_track = State()

@router.message(Command('createplaylist'))
async def cmd_create_playlist(message: Message, state: FSMContext):
    await message.answer("📝 <b>Введите название плейлиста:</b>\n\nНапример: Для качалки, Для сна", parse_mode='HTML')
    await state.set_state(PlaylistStates.waiting_for_name)

@router.message(Command('cancel'))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Отменено")

@router.message(PlaylistStates.waiting_for_name)
async def process_playlist_name(message: Message, state: FSMContext):
    playlist_name = message.text.strip()
    
    if len(playlist_name) > 50:
        await message.answer("❌ Название слишком длинное (макс. 50 символов)")
        return
    
    playlist_id = await create_playlist(message.from_user.id, playlist_name)
    
    await state.update_data(playlist_id=playlist_id, playlist_name=playlist_name)
    
    await message.answer(
        f"✅ <b>Плейлист '{playlist_name}' создан!</b>\n\n"
        f"🆔 ID: {playlist_id}\n\n"
        "Теперь отправьте ID трека или название, чтобы добавить его.\n"
        "Или напишите /cancel",
        parse_mode='HTML'
    )
    await state.set_state(PlaylistStates.waiting_for_track)

@router.message(PlaylistStates.waiting_for_track)
async def process_add_track(message: Message, state: FSMContext):
    data = await state.get_data()
    playlist_id = data['playlist_id']
    
    if message.text.isdigit():
        track_id = int(message.text)
        track = await get_track(track_id)
        
        if not track:
            await message.answer(f"❌ Трек с ID {track_id} не найден")
            return
        
        await add_track_to_playlist(playlist_id, track_id)
        await message.answer(f"✅ Добавлено: {track['artist']} — {track['title']}")
    else:
        results = await search_tracks(message.text, limit=1)
        
        if not results:
            await message.answer("❌ Трек не найден. Используйте ID.")
            return
        
        track = results[0]
        await add_track_to_playlist(playlist_id, track['id'])
        await message.answer(f"✅ Добавлено: {track['artist']} — {track['title']}")

@router.message(Command('myplaylists'))
async def cmd_my_playlists(message: Message):
    playlists = await get_user_playlists(message.from_user.id)
    
    if not playlists:
        await message.answer("📭 У вас нет плейлистов\n\nСоздайте: /createplaylist")
        return
    
    keyboard = []
    text = "📚 <b>Ваши плейлисты:</b>\n\n"
    
    for playlist in playlists:
        tracks = await get_playlist_tracks(playlist['id'])
        text += f"🎵 <b>{playlist['name']}</b>\n"
        text += f"   Треков: {len(tracks)}\n"
        text += f"   ID: {playlist['id']}\n\n"
        
        keyboard.append([
            InlineKeyboardButton(text=f"▶️ {playlist['name']}", callback_data=f"play_playlist_{playlist['id']}"),
            InlineKeyboardButton(text=f"🗑️ Удалить", callback_data=f"del_playlist_{playlist['id']}")
        ])
    
    await message.answer(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@router.message(Command('favorites'))
async def cmd_favorites(message: Message):
    favorites = await get_user_favorites(message.from_user.id)
    
    if not favorites:
        await message.answer("❤️ У вас пока нет избранных треков")
        return
    
    keyboard = []
    text = f"❤️ <b>Избранное ({len(favorites)}):</b>\n\n"
    
    for i, track in enumerate(favorites[:30], 1):
        text += f"{i}. <b>{track['artist']}</b> — {track['title']}\n"
        keyboard.append([InlineKeyboardButton(text=f"▶️ {track['artist']} - {track['title']}", callback_data=f"play_{track['id']}")])
    
    if len(favorites) > 30:
        text += f"\n... и ещё {len(favorites) - 30} треков"
    
    await message.answer(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

@router.callback_query(F.data.startswith('del_playlist_'))
async def callback_delete_playlist(callback: CallbackQuery):
    playlist_id = int(callback.data.split('_')[2])
    await delete_playlist(playlist_id, callback.from_user.id)
    await callback.answer("🗑️ Плейлист удален", show_alert=True)
    await cmd_my_playlists(callback.message)

@router.callback_query(F.data.startswith('play_playlist_'))
async def callback_play_playlist(callback: CallbackQuery):
    playlist_id = int(callback.data.split('_')[2])
    tracks = await get_playlist_tracks(playlist_id)
    
    if not tracks:
        await callback.answer("Плейлист пуст", show_alert=True)
        return
    
    await callback.message.answer(f"▶️ Воспроизведение плейлиста...\n\nПервый трек: {tracks[0]['artist']} — {tracks[0]['title']}")
    await callback.answer()