import sys
import os
import io

# Add project root to sys.path to find the DB package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure UTF-8 output for Sanskrit characters
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from DB.db import SessionLocal, Shloka

def query_sloka(chapter, verse):
    db = SessionLocal()
    try:
        shloka = db.query(Shloka).filter(
            Shloka.chapter == chapter,
            Shloka.verse == verse
        ).first()

        if not shloka:
            print(f"Error: Sloka not found for Chapter {chapter}, Verse {verse}")
            return

        print("-" * 50)
        print(f"CHAPTER {shloka.chapter}, VERSE {shloka.verse}")
        print("-" * 50)
        print("\n[ SANSKRIT ]\n")
        print(shloka.sanskrit_text.strip())
        print("\n[ TRANSLITERATION ]\n")
        print(shloka.transliteration.strip())
        print("\n[ ENGLISH MEANING ]\n")
        print(shloka.english_meaning.strip())
        print("-" * 50)

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python services/shloka_fetch.py <chapter_id> <shloka_id>")
        print("Example: python services/shloka_fetch.py 1 1")
    else:
        try:
            ch = int(sys.argv[1])
            vs = int(sys.argv[2])
            query_sloka(ch, vs)
        except ValueError:
            print("Error: Chapter and Shloka IDs must be integers.")
