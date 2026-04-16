import urllib.request
import json
from db import SessionLocal, engine, Base, Shloka

# Author ID for Swami Adidevananda (English)
TARGET_AUTHOR_ID = 18

def fetch_json(url):
    print(f"Downloading {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    return json.loads(response.read())

def seed_db():
    print("Creating tables (Remote Schema)...")
    Base.metadata.create_all(bind=engine)
    
    # 1. Fetch Verse data (Sanskrit + Transliteration)
    verses = fetch_json('https://raw.githubusercontent.com/gita/gita/main/data/verse.json')
    
    # 2. Fetch Translation data (English meanings)
    translations = fetch_json('https://raw.githubusercontent.com/gita/gita/main/data/translation.json')
    
    # 3. Create a lookup for English translation by verse_id
    # We pick author 18 (Swami Adidevananda)
    translation_map = {}
    for t in translations:
        if t['author_id'] == TARGET_AUTHOR_ID:
            translation_map[t['verse_id']] = t.get('description', '')

    db = SessionLocal()
    try:
        count = db.query(Shloka).count()
        if count > 0:
            print(f"Database contains {count} slokas. Clearing for fresh seed...")
            db.query(Shloka).delete()
            db.commit()

        print("Seeding database with 700 verses (Merged Data)...")
        for v in verses:
            verse_id = v['id']
            english_meaning = translation_map.get(verse_id, "Meaning not found")
            
            shloka = Shloka(
                chapter=v['chapter_number'],
                verse=v['verse_number'],
                sanskrit_text=v.get('text', ''),
                transliteration=v.get('transliteration', ''),
                english_meaning=english_meaning
            )
            db.add(shloka)
            
        db.commit()
        print("Successfully seeded all 700 Slokas with Transliteration and English Meaning!")
    except Exception as e:
        print(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
