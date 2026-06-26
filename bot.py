import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiohttp import web
import sqlite3
import json
import aiohttp

from config import BOT_TOKEN
from database import init_db
from handlers import start, search, playlists, play, downloaded

logging.basicConfig(level=logging.INFO)

# Веб-сервер (health check)
async def health_check(request):
    return web.Response(text="Bot is alive!")

# Страница импорта
async def import_page(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Import Database - Music Bot</title>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #fff;
                padding: 40px;
                text-align: center;
                min-height: 100vh;
                margin: 0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.05);
                padding: 40px;
                border-radius: 20px;
            }
            h1 { margin-bottom: 30px; }
            .btn {
                display: inline-block;
                padding: 15px 30px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 10px;
                margin: 10px;
                font-weight: bold;
            }
            .btn:hover { background: #45a049; }
            #status {
                margin: 20px 0;
                padding: 20px;
                border-radius: 10px;
                font-size: 1.2em;
            }
            .loading { background: rgba(255, 215, 0, 0.2); border: 2px solid #ffd700; color: #ffd700; }
            .success { background: rgba(0, 255, 0, 0.2); border: 2px solid #00ff00; color: #00ff00; }
            .error { background: rgba(255, 0, 0, 0.2); border: 2px solid #ff0000; color: #ff6666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📥 Импорт базы данных</h1>
            <div id="status" class="loading">⏳ Нажми кнопку для импорта...</div>
            <button onclick="startImport()" class="btn">🚀 Начать импорт</button>
            <div id="result"></div>
        </div>
        <script>
            async function startImport() {
                document.getElementById('status').className = 'loading';
                document.getElementById('status').innerHTML = '⏳ Импортирую... Подожди 1-2 минуты...';
                
                try {
                    const response = await fetch('/import_do');
                    const data = await response.json();
                    
                    if (data.success) {
                        document.getElementById('status').className = 'success';
                        document.getElementById('status').innerHTML = '✅ ' + data.message;
                        document.getElementById('result').innerHTML = '<p style="margin-top:20px;"><a href="https://dashboard.render.com" class="btn" target="_blank">Перезапустить бота на Render</a></p>';
                    } else {
                        document.getElementById('status').className = 'error';
                        document.getElementById('status').innerHTML = '❌ ' + data.message;
                    }
                } catch (error) {
                    document.getElementById('status').className = 'error';
                    document.getElementById('status').innerHTML = '❌ Ошибка: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

# Импорт данных из GitHub
async def do_import(request):
    try:
        github_url = 'https://raw.githubusercontent.com/10PRO10/promir-music-bot/main/tracks_export.json'
        
        print("📥 Скачиваю базу с GitHub...")
        
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
        
        print(f"✅ Импортировано {count} треков")
        
        return web.json_response({
            'success': True,
            'message': f'Успешно импортировано {count} треков! Теперь нажми Manual Deploy → Redeploy на Render'
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
    app.router.add_get('/import_do', do_import)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌐 Web server started on port 8080")
    print("📥 Import page: https://promir-music-bot.onrender.com/import")

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
        logging.error(f"❌ Ошибка: {e}")
        print("\n💡 Проверь токен и интернет!")
    finally:
        if 'bot' in locals():
            await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())