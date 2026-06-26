import sqlite3
import json

# Подключаемся к локальной базе
conn = sqlite3.connect('music_bot.db')
cursor = conn.cursor()

# Получаем все треки
cursor.execute('SELECT * FROM tracks')
tracks = cursor.fetchall()

print(f"📊 Найдено {len(tracks)} треков")

# Экспортируем в JSON
tracks_data = []
for track in tracks:
    tracks_data.append({
        'id': track[0],
        'title': track[1],
        'artist': track[2],
        'duration': track[3],
        'youtube_url': track[4],
        'telegram_file_id': track[5] if len(track) > 5 else None,
        'genre': track[6] if len(track) > 6 else None,
        'mood': track[7] if len(track) > 7 else None
    })

# Сохраняем
with open('tracks_export.json', 'w', encoding='utf-8') as f:
    json.dump(tracks_data, f, ensure_ascii=False, indent=2)

print(f"✅ Экспортировано в tracks_export.json")
print(f"📁 Размер файла: {len(json.dumps(tracks_data, ensure_ascii=False))} байт")

conn.close()