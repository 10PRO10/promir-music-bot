import asyncio
import logging
import sqlite3
import json
import os
from aiogram import Bot, Dispatcher
from aiohttp import web
import aiohttp

from config import BOT_TOKEN
from database import init_db
from handlers import start, search, playlists, play, downloaded

logging.basicConfig(level=logging.INFO)

# ==================== АВТОИМПОРТ БАЗЫ ====================
async def auto_import_database():
    """Автоматически загружает базу из GitHub при старте"""
    try:
        print("\n" + "="*60)
        print("📥 АВТОИМПОРТ БАЗЫ ДАННЫХ...")
        print("="*60)
        
        github_url = 'https://raw.githubusercontent.com/10PRO10/promir-music-bot/main/tracks_export.json'
        
        async with aiohttp.ClientSession() as session:
            print(f"🔗 Подключаюсь к GitHub...")
            async with session.get(github_url, timeout=120) as resp:
                if resp.status != 200:
                    print(f"❌ Файл не найден на GitHub (ошибка {resp.status})")
                    return False
                
                print(f"⬇️ Скачиваю файл...")
                text_data = await resp.text()
                
                if not text_data.strip():
                    print("❌ Файл пустой!")
                    return False
                
                try:
                    tracks = json.loads(text_data)
                    print(f"✅ Распаршено {len(tracks)} треков")
                except json.JSONDecodeError as e:
                    print(f"❌ Ошибка JSON: {e}")
                    return False
        
        print("🔌 Подключаюсь к базе данных...")
        conn = sqlite3.connect('music_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM tracks')
        old_count = cursor.fetchone()[0]
        print(f"📊 В базе сейчас: {old_count} треков")
        
        print("🗑️ Очищаю таблицу...")
        cursor.execute('DELETE FROM tracks')
        
        print("📝 Импортирую треки...")
        success_count = 0
        
        for i, track in enumerate(tracks, 1):
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO tracks 
                    (id, title, artist, duration, youtube_url, genre, mood)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    track.get('id'),
                    track.get('title', ''),
                    track.get('artist', ''),
                    track.get('duration'),
                    track.get('youtube_url'),
                    track.get('genre'),
                    track.get('mood')
                ))
                success_count += 1
                
                if success_count % 200 == 0:
                    print(f"  ➕ {success_count}/{len(tracks)}...")
                    
            except Exception as e:
                print(f"  ⚠️ Ошибка трека {i}: {e}")
        
        conn.commit()
        
        cursor.execute('SELECT COUNT(*) FROM tracks')
        new_count = cursor.fetchone()[0]
        
        conn.close()
        
        print("="*60)
        print(f"✅ АВТОИМПОРТ ЗАВЕРШЁН!")
        print(f"   Добавлено: {new_count} треков")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка автоимпорта: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== ВЕБ-СЕРВЕР ====================
async def health_check(request):
    return web.Response(
        text="<h1>🎵 Бот работает!</h1><p>База загружается автоматически при старте</p>",
        content_type='text/html'
    )

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌐 Web server started on port 8080")

# ==================== ОСНОВНАЯ ФУНКЦИЯ ====================
async def main():
    try:
        print("\n" + "="*60)
        print("🚀 ЗАПУСК МУЗЫКАЛЬНОГО БОТА")
        print("="*60)
        
        print("📂 Инициализация базы данных...")
        await init_db()
        
        # АВТОМАТИЧЕСКИЙ ИМПОРТ!
        print("\n🔄 Запускаю автоимпорт...")
        import_success = await auto_import_database()
        
        if not import_success:
            print("⚠️ Автоимпорт не удался")
        
        await start_web_server()
        
        print("🤖 Запуск Telegram бота...")
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher()
        
        dp.include_router(start.router)
        dp.include_router(play.router)
        dp.include_router(playlists.router)
        dp.include_router(downloaded.router)
        dp.include_router(search.router)
        
        logging.info("✅ Все роутеры подключены")
        
        me = await bot.me()
        
        conn = sqlite3.connect('music_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tracks')
        count = cursor.fetchone()[0]
        conn.close()
        
        print("\n" + "="*60)
        print("✅ БОТ УСПЕШНО ЗАПУЩЕН!")
        print(f"📱 Username: @{me.username}")
        print(f"📊 Треков в базе: {count}")
        print("="*60 + "\n")
        
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")
    finally:
        if 'bot' in locals():
            await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())