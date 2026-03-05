import os
import requests
import time
import librosa
import soundfile as sf

# ==========================================
# 1. PASTE YOUR API KEY HERE
# ==========================================
# Get this from xeno-canto.org -> My Account -> Developer
API_KEY = "29703358651515765b6d498860ce2b2c96dd5980"

# ==========================================
# CONFIGURATION
# ==========================================
TARGET_BIRDS = [
    "Pavo cristatus", "Vanellus indicus", "Corvus splendens", 
    "Columba livia", "Ptyonoprogne concolor", "Merops orientalis",
    "Apus affinis", "Psittacula krameria", "Ploceus philippinus",
    "Pycnonotus cafer", "Psittacula cyanocephala", "Dendrocygna javanica",
    "Cinnyris asiaticus", "Acridotheres tristis", "Eudynamys scolopaceus"
]

MAX_FILES = 100
DATASET_PATH = "dataset"
SAMPLE_RATE = 32000

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def convert_to_wav(mp3_path, wav_path):
    try:
        y, sr = librosa.load(mp3_path, sr=SAMPLE_RATE)
        sf.write(wav_path, y, sr)
        return True
    except:
        return False

def get_recordings(query_str):
    """Fetches list of recordings using the strict V3 format"""
    # Note: Even though it says V3, the endpoint URL often remains /api/2/ 
    # but the backend rules (tags required) are V3.
    url = "https://xeno-canto.org/api/3/recordings"
    
    params = {
        'query': query_str,
        'key': API_KEY
    }
    
    try:
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            print(f"   [API Error] {resp.status_code}: {resp.text}")
            return []
            
        data = resp.json()
        return data.get('recordings', [])
    except Exception as e:
        print(f"   [Connection Error] {e}")
        return []

# ==========================================
# THE PRIORITY SORTING SCRAPER
# ==========================================
def download_priority(species, max_count):
    safe_name = species.replace(" ", "_")
    mp3_dir = os.path.join(DATASET_PATH, "mp3_raw", safe_name)
    wav_dir = os.path.join(DATASET_PATH, "wav_clean", safe_name)
    os.makedirs(mp3_dir, exist_ok=True)
    os.makedirs(wav_dir, exist_ok=True)
    
    print(f"\n--- Processing: {species} ---")
    
    # 1. Build Strict V3 Query (Gen/Sp tags)
    parts = species.split(" ")
    if len(parts) == 2:
        base_query = f'gen:{parts[0]} sp:{parts[1]} len:5-30'
    else:
        base_query = f'en:"{species}" len:5-30'
    
    # 2. Fetch Lists separately
    print("Fetching Quality A...")
    list_a = get_recordings(f'{base_query} q:A')
    
    print("Fetching Quality B...")
    list_b = get_recordings(f'{base_query} q:B')
    
    # 3. ASSIGN PRIORITIES (The "Score" Logic)
    # Score 1: Quality A + Clean
    # Score 2: Quality B + Clean
    # Score 3: Quality A + Dirty
    # Score 4: Quality B + Dirty (REJECT)
    
    candidates = []
    
    # Process A Files
    for rec in list_a:
        is_clean = len(rec['also']) == 0
        if is_clean:
            rec['priority'] = 1 # GOLD
        else:
            rec['priority'] = 3 # BRONZE
        candidates.append(rec)
        
    # Process B Files
    for rec in list_b:
        is_clean = len(rec['also']) == 0
        if is_clean:
            rec['priority'] = 2 # SILVER
        else:
            continue # Don't even add to list
        candidates.append(rec)
        
    # 4. SORT BY PRIORITY
    # This ensures Priority 1 downloads first, then 2, then 3.
    candidates.sort(key=lambda x: x['priority'])
    
    print(f"Found {len(candidates)} valid candidates (Scores 1, 2, 3).")
    
    # 5. DOWNLOAD LOOP
    count = 0
    for rec in candidates:
        if count >= max_count: break
        
        file_id = rec['id']
        prio = rec['priority']
        mp3_path = os.path.join(mp3_dir, f"{file_id}.mp3")
        wav_path = os.path.join(wav_dir, f"{file_id}.wav")
        
        if os.path.exists(wav_path):
            count += 1
            continue
            
        try:
            # Helper text for console
            prio_labels = {1: "A-Clean", 2: "B-Clean", 3: "A-Dirty"}
            
            # Download
            mp3_data = requests.get(rec['file'])
            with open(mp3_path, 'wb') as f:
                f.write(mp3_data.content)
            
            # Convert
            if convert_to_wav(mp3_path, wav_path):
                print(f"Downloaded {count+1}/{max_count}: ID {file_id} [{prio_labels[prio]}]")
                count += 1
                
            time.sleep(1) # Be polite
            
        except Exception as e:
            print(f"      Failed ID {file_id}: {e}")

if __name__ == "__main__":
    if "PASTE" in API_KEY:
        print("ERROR: Please paste your API Key in line 11.")
    else:
        for bird in TARGET_BIRDS:
            download_priority(bird, MAX_FILES)
        print("\nAll downloads complete.")