import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiohttp import web

from config import BOT_TOKEN
from database import init_db
from handlers import start, search, playlists, play, downloaded

logging.basicConfig(level=logging.INFO)

# Веб-сервер чтобы Render не засыпал
async def health_check(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("🌐 Web server started on port 8080")

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