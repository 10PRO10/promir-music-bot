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

# Веб-сервер чтобы Render не засыпал
async def health_check(request):
    return web.Response(text="Bot is alive!")

# Страница импорта базы
async def import_database(request):
    """Импорт базы данных из GitHub"""
    
    html_response = """
    <html>
    <head>
        <title>Import Database</title>
        <style>
            body { 
                font-family: Arial; 
                background: #1a1a2e; 
                color: #fff;
                padding: 40px;
                text-align: center;
            }
            .loading { color: #ffd700; }
            .success { color: #00ff00; }
            .error { color: #ff0000; }
        </style>
    </head>
    <body>
        <h1>📥 Импорт базы данных</h1>
        <div id="status" class="loading">⏳ Загружаю треки...</div>
        <div id="progress"></div>
        
        <script>
            setTimeout(function() {
                fetch('/import_do')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('status').className = 'success';
                        document.getElementById('status').innerHTML = '✅ ' + data.message;
                        document.getElementById('progress').innerHTML = '<p>Теперь перезапусти бота:</p><p><a href="https://dashboard.render.com" style="color: #00ff00;">Render Dashboard → Manual Deploy → Redeploy</a></p>';
                    })
                    .catch(error => {
                        document.getElementById('status').className = 'error';
                        document.getElementById('status').innerHTML = '❌ Ошибка: ' + error;
                    });
            }, 100);
        </script>
    </body>
    </html>
    """
    
    return web.Response(text=html_response, content_type='text/html')

async def do_import(request):
    """Фактический импорт данных"""
    try:
        # Скачиваем JSON с GitHub
        async with aiohttp.ClientSession() as session:
            async with session.get('https://github.com/10PRO10/promir-music-bot/raw/main/tracks_export.json') as resp:
                if resp.status != 200:
                    return web.json_response({'message': '❌ Не удалось скачать JSON'})
                tracks = await resp.json()
        
        # Подключаемся к базе
        conn = sqlite3.connect('music_bot.db')
        cursor = conn.cursor()
        
        # Очищаем таблицу
        cursor.execute('DELETE FROM tracks')
        
        # Добавляем треки
        count = 0
        for track in tracks:
            try:
                cursor.execute('''
                    INSERT INTO tracks (id, title, artist, duration, youtube_url, genre, mood)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (track['id'], track['title'], track['artist'], track.get('duration'), 
                      track.get('youtube_url'), track.get('genre'), track.get('mood')))
                count += 1
            except Exception as e:
                print(f"Error adding track: {e}")
        
        conn.commit()
        conn.close()
        
        return web.json_response({'message': f'✅ Импортировано {count} треков! Теперь перезапусти бота на Render (Manual Deploy → Redeploy)'})
        
    except Exception as e:
        return web.json_response({'message': f'❌ Ошибка: {str(e)}'})

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/import', import_database)  # Страница импорта
    app.router.add_get('/import_do', do_import)      # Сам импорт
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌐 Web server started on port 8080")
    print("📥 Import page: /import")

async def main():
    try:
        await init_db()
        
        # Запускаем веб-сервер
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