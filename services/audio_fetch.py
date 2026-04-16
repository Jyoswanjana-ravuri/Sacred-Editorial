import os
import sys
import sys
from datasets import load_dataset, Audio
from dotenv import load_dotenv

# Load environment variables (including HF_TOKEN)
load_dotenv()

# Add parent directory to python path so it can find the DB module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DB.db import SessionLocal, Shloka

AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "DB", "audio"))

def fetch_and_save_audio():
    print(f"Ensuring audio directory exists: {AUDIO_DIR}")
    os.makedirs(AUDIO_DIR, exist_ok=True)
    
    print("Loading JDhruv14/Bhagavad-Gita_Audio dataset from Hugging Face...")
    # Using the HF_TOKEN to authenticate with Hub
    dataset = load_dataset("JDhruv14/Bhagavad-Gita_Audio", split="train", token=os.getenv("HF_TOKEN"))
    
    # Crucial Fix: Disable internal ML audio decoding to avoid torchcodec DLL crashes on Windows
    # Instead, we just retrieve the raw WAV bytes directly!
    dataset = dataset.cast_column("audio", Audio(decode=False))
    
    db = SessionLocal()
    
    count = 0
    print(f"Dataset loaded with {len(dataset)} items.")
    for item in dataset:
        try:
            # Let's inspect keys briefly if it's the first item
            if count == 0:
                print("First item keys: ", item.keys())
                
            # typical keys: 'chapter', 'verse', 'audio'
            # adjust these if the dataset has different column names like 'chapter_id', 'verse_id' or 'id'
            # For JDhruv14 dataset, they often use 'chapter' and 'verse'
            chapter = int(item.get('chapter', item.get('Chapter', 1)))
            verse = int(item.get('verse', item.get('Verse', 1)))
            
            audio_data = item.get('audio')
            if not audio_data or 'bytes' not in audio_data:
                continue
                
            audio_bytes = audio_data['bytes']
            
            # create chapter directory
            chap_dir = os.path.join(AUDIO_DIR, str(chapter))
            os.makedirs(chap_dir, exist_ok=True)
            
            file_path = os.path.join(chap_dir, f"{verse}.wav")
            
            # Write raw bytes directly if it doesn't exist
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(audio_bytes)
            
            count += 1
            if count % 100 == 0:
                print(f"Processed {count} audio files...")
                
        except Exception as e:
            print(f"Error processing item: {e}")
            
    print(f"Successfully processed {count} audio files.")
    db.close()

if __name__ == "__main__":
    fetch_and_save_audio()
