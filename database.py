import aiosqlite
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                duration INTEGER,
                youtube_url TEXT,
                telegram_file_id TEXT,
                genre TEXT,
                mood TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, track_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (track_id) REFERENCES tracks (id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_playlist_tracks (
                playlist_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (playlist_id, track_id),
                FOREIGN KEY (playlist_id) REFERENCES user_playlists (id),
                FOREIGN KEY (track_id) REFERENCES tracks (id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS downloaded_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (track_id) REFERENCES tracks (id)
            )
        ''')
        
        await db.execute('CREATE INDEX IF NOT EXISTS idx_tracks_title ON tracks(title)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks(artist)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_playlists_user ON user_playlists(user_id)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_downloaded_track ON downloaded_tracks(track_id)')
        
        await db.commit()
        print("✅ База данных инициализирована")

async def add_track(title: str, artist: str, genre: str = None, mood: str = None, youtube_url: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'INSERT INTO tracks (title, artist, genre, mood, youtube_url) VALUES (?, ?, ?, ?, ?)',
            (title, artist, genre, mood, youtube_url)
        )
        await db.commit()
        return cursor.lastrowid

async def search_tracks(query: str, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            '''SELECT id, title, artist, genre, mood FROM tracks 
               WHERE title LIKE ? OR artist LIKE ?
               LIMIT ?''',
            (f'%{query}%', f'%{query}%', limit)
        )
        return await cursor.fetchall()

async def get_all_tracks(limit: int = 20, offset: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT id, title, artist, genre, mood FROM tracks ORDER BY artist, title LIMIT ? OFFSET ?',
            (limit, offset)
        )
        return await cursor.fetchall()

async def get_track(track_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM tracks WHERE id = ?', (track_id,))
        return await cursor.fetchone()

async def get_tracks_count():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM tracks')
        result = await cursor.fetchone()
        return result[0]

async def add_user(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            '''INSERT INTO users (id, username, first_name) 
               VALUES (?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET 
               username=excluded.username, first_name=excluded.first_name''',
            (user_id, username, first_name)
        )
        await db.commit()

async def add_to_favorites(user_id: int, track_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR IGNORE INTO favorites (user_id, track_id) VALUES (?, ?)',
            (user_id, track_id)
        )
        await db.commit()

async def get_user_favorites(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            '''SELECT t.id, t.title, t.artist, t.genre, t.mood FROM tracks t
               JOIN favorites f ON t.id = f.track_id
               WHERE f.user_id = ?
               ORDER BY t.artist, t.title''',
            (user_id,)
        )
        return await cursor.fetchall()

async def create_playlist(user_id: int, name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'INSERT INTO user_playlists (user_id, name) VALUES (?, ?)',
            (user_id, name)
        )
        await db.commit()
        return cursor.lastrowid

async def add_track_to_playlist(playlist_id: int, track_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR IGNORE INTO user_playlist_tracks (playlist_id, track_id) VALUES (?, ?)',
            (playlist_id, track_id)
        )
        await db.commit()

async def get_user_playlists(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM user_playlists WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        )
        return await cursor.fetchall()

async def get_playlist_tracks(playlist_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            '''SELECT t.* FROM tracks t
               JOIN user_playlist_tracks upt ON t.id = upt.track_id
               WHERE upt.playlist_id = ?
               ORDER BY upt.added_at''',
            (playlist_id,)
        )
        return await cursor.fetchall()

async def delete_playlist(playlist_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'DELETE FROM user_playlists WHERE id = ? AND user_id = ?',
            (playlist_id, user_id)
        )
        await db.execute(
            'DELETE FROM user_playlist_tracks WHERE playlist_id = ?',
            (playlist_id,)
        )
        await db.commit()

async def add_downloaded_track(track_id: int, file_path: str, file_size: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id FROM downloaded_tracks WHERE track_id = ?',
            (track_id,)
        )
        existing = await cursor.fetchone()
        
        if existing:
            await db.execute(
                'UPDATE downloaded_tracks SET file_path = ?, file_size = ?, downloaded_at = CURRENT_TIMESTAMP WHERE track_id = ?',
                (file_path, file_size, track_id)
            )
        else:
            await db.execute(
                'INSERT INTO downloaded_tracks (track_id, file_path, file_size) VALUES (?, ?, ?)',
                (track_id, file_path, file_size)
            )
        await db.commit()

async def get_downloaded_tracks(limit: int = 50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            '''SELECT t.*, dt.file_path, dt.file_size, dt.downloaded_at 
               FROM downloaded_tracks dt
               JOIN tracks t ON dt.track_id = t.id
               ORDER BY dt.downloaded_at DESC
               LIMIT ?''',
            (limit,)
        )
        return await cursor.fetchall()

async def get_downloaded_count():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM downloaded_tracks')
        result = await cursor.fetchone()
        return result[0]

async def clear_downloaded_tracks():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM downloaded_tracks')
        await db.commit()