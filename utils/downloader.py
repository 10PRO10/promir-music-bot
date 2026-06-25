import os
import asyncio
import yt_dlp
import sqlite3
from database import DB_PATH

async def search_youtube(query: str) -> str:
    """Поиск на YouTube"""
    for attempt in range(3):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'socket_timeout': 30,
                'default_search': 'ytsearch1',
                'no_check_certificate': True,
            }
            
            loop = asyncio.get_event_loop()
            
            def extract():
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(f"ytsearch1:{query} audio", download=False)
                        if info.get('entries'):
                            entries = list(info['entries'])
                            if entries:
                                return entries[0]['url']
                except Exception as e:
                    print(f"Search error: {e}")
                return None
            
            result = await asyncio.wait_for(
                loop.run_in_executor(None, extract),
                timeout=60
            )
            
            if result:
                print(f"✅ Найдено: {result[:50]}...")
                return result
                
        except asyncio.TimeoutError:
            print(f"Search attempt {attempt + 1} timeout")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Search attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2)
    
    return None

def get_youtube_metadata(url):
    """Получить метаданные (название, исполнитель) с YouTube"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info:
                title = info.get('title', '')
                uploader = info.get('uploader', '') or info.get('channel', '')
                video_id = info.get('id', '')
                return title, uploader, video_id
    except Exception as e:
        print(f"⚠️ Ошибка получения метаданных: {e}")
    
    return None, None, None

def update_track_in_db(track_id, title, artist):
    """Обновить трек в базе с правильными названиями"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE tracks SET title = ?, artist = ? WHERE id = ?',
            (title, artist, track_id)
        )
        
        conn.commit()
        conn.close()
        
        print(f"✅ Обновлено в базе: {artist} - {title}")
    except Exception as e:
        print(f"⚠️ Ошибка обновления базы: {e}")

async def download_from_url(url: str, output_path: str = 'downloads', track_id: int = None) -> str:
    """Скачивание аудио с обновлением метаданных"""
    os.makedirs(output_path, exist_ok=True)
    
    # Сначала получаем метаданные
    title, artist, youtube_id = get_youtube_metadata(url)
    
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
            }
            
            loop = asyncio.get_event_loop()
            
            def download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    mp3_file = os.path.splitext(filename)[0] + '.mp3'
                    return mp3_file
            
            result = await asyncio.wait_for(
                loop.run_in_executor(None, download),
                timeout=180
            )
            
            if result and os.path.exists(result):
                print(f"✅ Downloaded: {result}")
                
                # Если получили метаданные и есть track_id
                if title and track_id:
                    # Обновляем в базе
                    update_track_in_db(track_id, title, artist or 'Unknown')
                
                # Сохраняем в базу скачанных
                if track_id:
                    try:
                        from database import add_downloaded_track
                        file_size = os.path.getsize(result)
                        await add_downloaded_track(track_id, result, file_size)
                        print(f"💾 Сохранено в базу: трек {track_id}")
                    except Exception as e:
                        print(f"⚠️ Не удалось сохранить в базу: {e}")
                
                return result
                
        except asyncio.TimeoutError:
            print(f"Download attempt {attempt + 1} timeout")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Download attempt {attempt + 1} error: {e}")
            await asyncio.sleep(3)
    
    print("❌ All download attempts failed")
    return None

async def download_audio(url: str, output_path: str = 'downloads', track_id: int = None) -> str:
    return await download_from_url(url, output_path, track_id)

async def search_multiple_sources(query: str) -> list:
    results = []
    youtube_url = await search_youtube(query)
    if youtube_url:
        results.append({
            'platform': 'YouTube',
            'url': youtube_url,
            'query': query
        })
    return results