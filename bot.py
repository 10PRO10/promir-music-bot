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

# Веб-сервер
async def health_check(request):
    return web.Response(text="Bot is alive!")

# Страница импорта
async def import_page(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Import Database</title>
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
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 {
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .status {
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                font-size: 1.2em;
            }
            .loading {
                background: rgba(255, 215, 0, 0.2);
                border: 2px solid #ffd700;
                color: #ffd700;
            }
            .success {
                background: rgba(0, 255, 0, 0.2);
                border: 2px solid #00ff00;
                color: #00ff00;
            }
            .error {
                background: rgba(255, 0, 0, 0.2);
                border: 2px solid #ff0000;
                color: #ff6666;
            }
            .btn {
                display: inline-block;
                padding: 15px 30px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 10px;
                margin: 10px;
                font-weight: bold;
                transition: all 0.3s;
            }
            .btn:hover {
                background: #45a049;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📥 Импорт базы данных</h1>
            <div id="status" class="loading">
                ⏳ Загружаю треки из GitHub...
            </div>
            <div id="progress"></div>
        </div>
        
        <script>
            async function startImport() {
                try {
                    const response = await fetch('/import_do');
                    const data = await response.json();
                    
                    const statusDiv = document.getElementById('status');
                    const progressDiv = document.getElementById('progress');
                    
                    if (data.success) {
                        statusDiv.className = 'success';
                        statusDiv.innerHTML = '✅ ' + data.message;
                        progressDiv.innerHTML = `
                            <p style="margin-top: 30px;">
                                <strong>Теперь перезапусти бота:</strong>
                            </p>
                            <a href="https://dashboard.render.com" class="btn" target="_blank">
                                Render Dashboard → Manual Deploy → Redeploy
                            </a>
                        `;
                    } else {
                        statusDiv.className = 'error';
                        statusDiv.innerHTML = '❌ ' + data.message;
                    }
                } catch (error) {
                    document.getElementById('status').className = 'error';
                    document.getElementById('status').innerHTML = '❌ Ошибка соединения: ' + error.message;
                }
            }
            
            // Запускаем импорт при загрузке страницы
            setTimeout(startImport, 500);
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def do_import(request):
    """Импорт данных из GitHub"""
    try:
        # URL для raw GitHub
        github_url = 'https://raw.githubusercontent.com/10PRO10/promir-music-bot/main/tracks_export.json'
        
        print("📥 Начинаю загрузку с GitHub...")
        
        async with aiohttp.ClientSession() as session:
            # Скачиваем файл
            async with session.get(github_url, timeout=120) as resp:
                print(f"📊 Статус ответа: {resp.status}")
                
                if resp.status != 200:
                    return web.json_response({
                        'success': False,
                        'message': f'Файл не найден на GitHub (ошибка {resp.status}). Убедись что tracks_export.json загружен в репозиторий!'
                    })
                
                # Читаем как текст
                text_data = await resp.text()
                print(f"📄 Размер файла: {len(text_data)} байт")
                
                if not text_data.strip():
                    return web.json_response({
                        'success': False,
                        'message': 'Файл пустой!'
                    })
                
                # Парсим JSON вручную
                try:
                    tracks = json.loads(text_data)
                    print(f"✅ Распаршено {len(tracks)} треков")
                except json.JSONDecodeError as e:
                    print(f"❌ Ошибка JSON: {e}")
                    print(f"Первые 200 символов: {text_data[:200]}")
                    return web.json_response({
                        'success': False,
                        'message': f'Неверный формат JSON: {e}. Проверь что файл tracks_export.json валидный!'
                    })
        
        # Подключаемся к базе
        print("🔌 Подключаюсь к базе данных...")
        conn = sqlite3.connect('music_bot.db')
        cursor = conn.cursor()
        
        # Очищаем таблицу
        print("🗑️ Очищаю таблицу tracks...")
        cursor.execute('DELETE FROM tracks')
        
        # Считаем сколько было
        cursor.execute('SELECT COUNT(*) FROM tracks')
        before_count = cursor.fetchone()[0]
        print(f"📊 Треков до очистки: {before_count}")
        
        # Добавляем треки
        print("📝 Добавляю треки...")
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
                
                if success_count % 100 == 0:
                    print(f"  ➕ Добавлено {success_count} треков...")
                    
            except Exception as e:
                error_count += 1
                print(f"  ⚠️ Ошибка трека {i}: {e}")
        
        # Сохраняем
        conn.commit()
        
        # Считаем итоговое количество
        cursor.execute('SELECT COUNT(*) FROM tracks')
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Готово! Добавлено {total_count} треков")
        
        return web.json_response({
            'success': True,
            'message': f'Успешно импортировано {total_count} треков! (Ошибок: {error_count})'
        })
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        
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