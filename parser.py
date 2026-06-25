import re

def parse_track_line(line: str):
    line = line.strip()
    if not line:
        return None
    
    match = re.match(r'^(.+?)\s+-\s+(.+)$', line)
    if match:
        artist = match.group(1).strip()
        title = match.group(2).strip()
        title = re.sub(r'^\d+\.\s*', '', title)
        return artist, title
    return None

def parse_playlist(text: str):
    tracks = []
    for line in text.split('\n'):
        result = parse_track_line(line)
        if result:
            tracks.append(result)
    return tracks

def auto_detect_genre(artist: str, title: str):
    artist_lower = artist.lower()
    
    if 'miyagi' in artist_lower or 'эндшпиль' in artist_lower or 'andy panda' in artist_lower:
        return 'hip-hop', 'vibe'
    
    if 'каспийский груз' in artist_lower:
        return 'hip-hop', 'street'
    
    patriotic = ['radio tapok', 'militaryhub', 'shtil', 'ddoz', 'ксения юхнова', 'r.p.g.']
    if any(p in artist_lower for p in patriotic):
        return 'patriotic', 'military'
    
    rap = ['big baby tape', 'v $ x v', 'guf', 'баста', 'скриптонит', 'рем дигга', 'kizaru', 'брутто']
    if any(r in artist_lower for r in rap):
        return 'hip-hop', 'rap'
    
    pop = ['руки вверх', 'ёлка', 'serebro', 'artik & asti', 'макс корж', 'дима билан']
    if any(p in artist_lower for p in pop):
        return 'pop', 'mainstream'
    
    rock = ['кино', 'король и шут', 'звери', 'алиса', 'сектор газа', 'любэ']
    if any(r in artist_lower for r in rock):
        return 'rock', 'russian'
    
    phonk = ['dvrst', 'kordhell', 'phonk']
    if any(p in artist_lower for p in phonk):
        return 'phonk', 'aggressive'
    
    return 'other', 'unknown'