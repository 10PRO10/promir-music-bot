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
        
        # Подключаемся к базе
        print("🔌 Подключаюсь к базе данных...")
        conn = sqlite3.connect('music_bot.db')
        cursor = conn.cursor()
        
        # Проверяем текущее количество
        cursor.execute('SELECT COUNT(*) FROM tracks')
        old_count = cursor.fetchone()[0]
        print(f"📊 В базе сейчас: {old_count} треков")
        
        # Очищаем таблицу
        print("🗑️ Очищаю таблицу...")
        cursor.execute('DELETE FROM tracks')
        
        # Добавляем треки
        print("📝 Импортирую треки...")
        success_count = 0
        error_count = 0
        
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
                error_count += 1
                if error_count <= 5:  # Показываем первые 5 ошибок
                    print(f"  ⚠️ Ошибка трека {i}: {e}")
        
        conn.commit()
        
        # Проверяем итоговое количество
        cursor.execute('SELECT COUNT(*) FROM tracks')
        new_count = cursor.fetchone()[0]
        
        conn.close()
        
        print("="*60)
        print(f"✅ АВТОИМПОРТ ЗАВЕРШЁН!")
        print(f"   Добавлено: {new_count} треков")
        print(f"   Ошибок: {error_count}")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка автоимпорта: {e}")
        return False

# ==================== ВЕБ-СЕРВЕР ====================
async def health_check(request):
    """Проверка работоспособности"""
    return web.Response(
        text="<h1>🎵 Бот работает!</h1><p>Открой /import для ручного импорта</p>",
        content_type='text/html'
    )

async def import_page(request):
    """Страница ручного импорта"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Импорт базы</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial; background: #1a1a2e; color: #fff; padding: 40px; text-align: center; }
            .box { max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; }
            .btn { display: inline-block; padding: 15px 30px; background: #4CAF50; color: white; text-decoration: none; border-radius: 10px; margin: 10px; cursor: pointer; border: none; font-size: 16px; }
            .btn:hover { background: #45a049; }
            #result { margin-top: 20px; padding: 15px; border-radius: 10px; }
            .success { background: rgba(0,255,0,0.2); color: #0f0; }
            .error { background: rgba(255,0,0,0.2); color: #f66; }
            .loading { background: rgba(255,215,0,0.2); color: #ffd700; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>📥 Импорт базы данных</h1>
            <p>Загрузить 1520 треков с GitHub</p>
            <button class="btn" onclick="doImport()">🚀 Начать импорт</button>
            <div id="result"></div>
        </div>
        <script>
            async function doImport() {
                const result = document.getElementById('result');
                result.className = 'loading';
                result.innerHTML = '⏳ Импортирую...';
                
                try {
                    const response = await fetch('/api_import');
                    const data = await response.json();
                    
                    if (data.success) {
                        result.className = 'success';
                        result.innerHTML = '✅ ' + data.message;
                    } else {
                        result.className = 'error';
                        result.innerHTML = '❌ ' + data.message;
                    }
                } catch (e) {
                    result.className = 'error';
                    result.innerHTML = '❌ Ошибка: ' + e.message;
                }
            }
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def api_import(request):
    """API для ручного импорта"""
    try:
        github_url = 'https://raw.githubusercontent.com/10PRO10/promir-music-bot/main/tracks_export.json'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(github_url, timeout=120) as resp:
                if resp.status != 200:
                    return web.json_response({
                        'success': False,
                        'message': f'Файл не найден на GitHub'
                    })
                
                text_data = await resp.text()
                tracks = json.loads(text_data)
        
        conn = sqlite3.connect('music_bot.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tracks')
        
        count = 0
        for track in tracks:
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
                count += 1
            except:
                pass
        
        conn.commit()
        conn.close()
        
        return web.json_response({
            'success': True,
            'message': f'Импортировано {count} треков! Перезагрузи страницу Telegram'
        })
        
    except Exception as e:
        return web.json_response({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/import', import_page)
    app.router.add_get('/api_import', api_import)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌐 Web server started on port 8080")
    print("📥 Import page: https://promir-music-bot.onrender.com/import")

# ==================== ОСНОВНАЯ ФУНКЦИЯ ====================
async def main():
    try:
        print("\n" + "="*60)
        print("🚀 ЗАПУСК МУЗЫКАЛЬНОГО БОТА")
        print("="*60)
        
        # Инициализация базы
        print("📂 Инициализация базы данных...")
        await init_db()
        
        # АВТОМАТИЧЕСКИЙ ИМПОРТ (ГЛАВНОЕ!)
        print("\n🔄 Запускаю автоимпорт...")
        import_success = await auto_import_database()
        
        if not import_success:
            print("⚠️ Автоимпорт не удался, но бот продолжит работу")
        
        # Запуск веб-сервера
        await start_web_server()
        
        # Запуск бота
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
        print("\n" + "="*60)
        print("✅ БОТ УСПЕШНО ЗАПУЩЕН!")
        print(f"📱 Username: @{me.username}")
        print(f"📊 Треков в базе: ", end="")
        
        # Показываем количество треков
        conn = sqlite3.connect('music_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tracks')
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"{count}")
        print("="*60 + "\n")
        
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")
        print("\n💡 Проверь токен и интернет!")
    finally:
        if 'bot' in locals():
            await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())