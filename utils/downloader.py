import os
import asyncio
import yt_dlp
import sqlite3
from database import DB_PATH

# ==================== ПОИСК НА РАЗНЫХ СЕРВИСАХ ====================

async def search_youtube(query: str) -> str:
    """Поиск на YouTube"""
    print(f"🔍 Ищу на YouTube: {query}")
    for attempt in range(2):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'socket_timeout': 30,
                'default_search': 'ytsearch1',
                'no_check_certificate': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            }
            
            loop = asyncio.get_event_loop()
            
            def extract():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch1:{query} audio", download=False)
                    if info.get('entries'):
                        entries = list(info['entries'])
                        if entries:
                            return entries[0]['url']
                return None
            
            result = await asyncio.wait_for(loop.run_in_executor(None, extract), timeout=60)
            
            if result:
                print(f"✅ YouTube: {result[:50]}...")
                return result
                
        except Exception as e:
            print(f"⚠️ YouTube ошибка: {e}")
            await asyncio.sleep(1)
    
    print("❌ YouTube не нашёл")
    return None

async def search_soundcloud(query: str) -> str:
    """Поиск на SoundCloud - НЕ БЛОКИРУЕТ!"""
    print(f"🔍 Ищу на SoundCloud: {query}")
    for attempt in range(2):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'socket_timeout': 30,
                'default_search': 'scsearch1',
                'no_check_certificate': True,
            }
            
            loop = asyncio.get_event_loop()
            
            def extract():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"scsearch1:{query}", download=False)
                    if info.get('entries'):
                        entries = list(info['entries'])
                        if entries:
                            return entries[0]['url']
                return None
            
            result = await asyncio.wait_for(loop.run_in_executor(None, extract), timeout=60)
            
            if result:
                print(f"✅ SoundCloud: {result[:50]}...")
                return result
                
        except Exception as e:
            print(f"⚠️ SoundCloud ошибка: {e}")
            await asyncio.sleep(1)
    
    print("❌ SoundCloud не нашёл")
    return None

async def search_vk(query: str) -> str:
    """Поиск на VK"""
    print(f"🔍 Ищу на VK: {query}")
    for attempt in range(2):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'socket_timeout': 30,
                'default_search': 'vksearch1',
                'no_check_certificate': True,
            }
            
            loop = asyncio.get_event_loop()
            
            def extract():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"vksearch1:{query}", download=False)
                    if info.get('entries'):
                        entries = list(info['entries'])
                        if entries:
                            return entries[0]['url']
                return None
            
            result = await asyncio.wait_for(loop.run_in_executor(None, extract), timeout=60)
            
            if result:
                print(f"✅ VK: {result[:50]}...")
                return result
                
        except Exception as e:
            print(f"⚠️ VK ошибка: {e}")
            await asyncio.sleep(1)
    
    print("❌ VK не нашёл")
    return None

async def search_bandcamp(query: str) -> str:
    """Поиск на Bandcamp"""
    print(f"🔍 Ищу на Bandcamp: {query}")
    for attempt in range(2):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'socket_timeout': 30,
                'default_search': 'bcsearch1',
                'no_check_certificate': True,
            }
            
            loop = asyncio.get_event_loop()
            
            def extract():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"bcsearch1:{query}", download=False)
                    if info.get('entries'):
                        entries = list(info['entries'])
                        if entries:
                            return entries[0]['url']
                return None
            
            result = await asyncio.wait_for(loop.run_in_executor(None, extract), timeout=60)
            
            if result:
                print(f"✅ Bandcamp: {result[:50]}...")
                return result
                
        except Exception as e:
            print(f"⚠️ Bandcamp ошибка: {e}")
            await asyncio.sleep(1)
    
    print("❌ Bandcamp не нашёл")
    return None

# ==================== УНИВЕРСАЛЬНЫЙ ПОИСК ====================
# ПОРЯДОК: SoundCloud → Bandcamp → YouTube → VK

async def search_any(query: str) -> tuple:
    """Ищет на всех сервисах - SoundCloud ПЕРВЫМ (не блокирует)!"""
    print(f"\n🎵 Поиск трека: {query}")
    print("="*50)
    
    # 1. SoundCloud - НЕ БЛОКИРУЕТ!
    print("📡 Пробую SoundCloud...")
    url = await search_soundcloud(query)
    if url:
        print("="*50)
        print(f"✅ Найдено на SoundCloud!")
        return url, 'SoundCloud'
    
    # 2. Bandcamp - тоже хороший
    print("📡 Пробую Bandcamp...")
    url = await search_bandcamp(query)
    if url:
        print("="*50)
        print(f"✅ Найдено на Bandcamp!")
        return url, 'Bandcamp'
    
    # 3. YouTube - может блокировать
    print("📡 Пробую YouTube...")
    url = await search_youtube(query)
    if url:
        print("="*50)
        print(f"✅ Найдено на YouTube!")
        return url, 'YouTube'
    
    # 4. VK
    print("📡 Пробую VK...")
    url = await search_vk(query)
    if url:
        print("="*50)
        print(f"✅ Найдено на VK!")
        return url, 'VK'
    
    print("="*50)
    print("❌ Ничего не найдено ни на одном сервисе")
    return None, None

# ==================== СКАЧИВАНИЕ ====================

def get_metadata(url):
    """Получить метаданные трека"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info:
                return info.get('title', ''), info.get('uploader', ''), info.get('id', '')
    except Exception as e:
        print(f"⚠️ Ошибка метаданных: {e}")
    
    return None, None, None

def update_track_in_db(track_id, title, artist):
    """Обновить трек в базе"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE tracks SET title = ?, artist = ? WHERE id = ?', (title, artist, track_id))
        conn.commit()
        conn.close()
        print(f"✅ Обновлено в базе: {artist} - {title}")
    except Exception as e:
        print(f"⚠️ Ошибка обновления: {e}")

async def download_from_url(url: str, output_path: str = 'downloads', track_id: int = None) -> str:
    """Скачивание с любого сервиса"""
    os.makedirs(output_path, exist_ok=True)
    
    # Получаем метаданные
    title, artist, media_id = get_metadata(url)
    
    for attempt in range(3):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
                'outtmpl': f'{output_path}/%(id)s.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'socket_timeout': 60,
                'retries': 3,
                'fragment_retries': 3,
                'no_check_certificate': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                'extractor_args': {
                    'youtube': {
                        'skip': ['hls', 'dash'],
                        'player_client': ['ios', 'web']
                    }
                }
            }
            
            loop = asyncio.get_event_loop()
            
            def download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    mp3_file = os.path.splitext(filename)[0] + '.mp3'
                    return mp3_file
            
            result = await asyncio.wait_for(loop.run_in_executor(None, download), timeout=180)
            
            if result and os.path.exists(result):
                print(f"✅ Downloaded: {result}")
                
                if title and track_id:
                    update_track_in_db(track_id, title, artist or 'Unknown')
                
                if track_id:
                    try:
                        from database import add_downloaded_track
                        file_size = os.path.getsize(result)
                        await add_downloaded_track(track_id, result, file_size)
                        print(f"💾 Сохранено в базу: трек {track_id}")
                    except Exception as e:
                        print(f"⚠️ Не удалось сохранить: {e}")
                
                return result
                
        except asyncio.TimeoutError:
            print(f"Download attempt {attempt + 1} timeout")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Download attempt {attempt + 1} error: {e}")
            await asyncio.sleep(3)
    
    print("❌ Все попытки скачивания не удались")
    return None

async def download_audio(url: str, output_path: str = 'downloads', track_id: int = None) -> str:
    return await download_from_url(url, output_path, track_id)

async def search_multiple_sources(query: str) -> list:
    """Ищет на всех сервисах и возвращает список результатов"""
    results = []
    
    # SoundCloud
    url = await search_soundcloud(query)
    if url:
        results.append({'platform': 'SoundCloud', 'url': url, 'query': query})
    
    # Bandcamp
    url = await search_bandcamp(query)
    if url:
        results.append({'platform': 'Bandcamp', 'url': url, 'query': query})
    
    # YouTube
    url = await search_youtube(query)
    if url:
        results.append({'platform': 'YouTube', 'url': url, 'query': query})
    
    # VK
    url = await search_vk(query)
    if url:
        results.append({'platform': 'VK', 'url': url, 'query': query})
    
    return results