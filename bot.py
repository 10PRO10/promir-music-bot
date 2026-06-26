import asyncio
import logging
import sqlite3
import json
from aiogram import Bot, Dispatcher
from aiohttp import web
import aiohttp

from config import BOT_TOKEN
from database import init_db
from handlers import start, search, playlists, play, downloaded

logging.basicConfig(level=logging.INFO)

# Главная страница
async def health_check(request):
    return web.Response(
        text="<h1>🎵 Бот работает!</h1><p>Открой /import для импорта базы</p>",
        content_type='text/html'
    )

# Страница импорта
async def import_page(request):
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
            <p>Нажми кнопку чтобы импортировать 1520 треков с GitHub</p>
            <button class="btn" onclick="doImport()">🚀 Начать импорт</button>
            <div id="result"></div>
        </div>
        <script>
            async function doImport() {
                const result = document.getElementById('result');
                result.className = 'loading';
                result.innerHTML = '⏳ Импортирую... Подожди 10-30 секунд...';
                
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

# API импорта
async def api_import(request):
    try:
        print("📥 Начинаю импорт...")
        
        # Скачиваем JSON с GitHub
        github_url = 'https://raw.githubusercontent.com/10PRO10/promir-music-bot/main/tracks_export.json'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(github_url, timeout=120) as resp:
                if resp.status != 200:
                    return web.json_response({
                        'success': False,
                        'message': f'Файл не найден на GitHub (ошибка {resp.status}). Загрузи tracks_export.json в репозиторий!'
                    })
                
                text_data = await resp.text()
                
                if not text_data.strip():
                    return web.json_response({
                        'success': False,
                        'message': 'Файл пустой!'
                    })
                
                try:
                    tracks = json.loads(text_data)
                except json.JSONDecodeError as e:
                    return web.json_response({
                        'success': False,
                        'message': f'Ошибка JSON: {e}'
                    })
        
        print(f"✅ Загружено {len(tracks)} треков")
        
        # Импорт в базу
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
            except Exception as e:
                print(f"⚠️ Ошибка: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Импортировано {count} треков!")
        
        return web.json_response({
            'success': True,
            'message': f'Импортировано {count} треков! Теперь нажми Manual Deploy → Redeploy на Render чтобы перезапустить бота.'
        })
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
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
    print("📥 Import: https://promir-music-bot.onrender.com/import")

async def main():
    try:
        await init_db()
        await start_web_server()
        
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher()
        
        dp.include_router(start.router)
        dp.include_router(play.router)
        dp.include_router(playlists.router)
        dp.include_router(downloaded.router)
        dp.include_router(search.router)
        
        logging.info("✅ Все роутеры подключены")
        
        me = await bot.me()
        print("✅ База данных инициализирована")
        print("🚀 Бот запущен!")
        print(f"📱 Бот: @{me.username}")
        
        await dp.start_polling(bot, skip_updates=True)
        
    except Exception as e:
        logging.error(f" Ошибка: {e}")
    finally:
        if 'bot' in locals():
            await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())