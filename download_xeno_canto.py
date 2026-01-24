import os
import requests
import librosa
import soundfile as sf
import time

# Your Xeno-Canto API key - Get yours from https://xeno-canto.org/account
API_KEY = os.environ.get("XENO_CANTO_API_KEY", "YOUR_API_KEY_HERE")

# IISERB Species
birds = {
    "Asian_Koel": "Eudynamys scolopaceus",
    "Red-vented_Bulbul": "Pycnonotus cafer",
    "Common_Myna": "Acridotheres tristis",
    "Rose-ringed_Parakeet": "Psittacula krameri",
    "Indian_Peafowl": "Pavo cristatus"
}

print("Warming up librosa (first-time compilation, please wait...)...")
try:
    # Pre-compile numba functions
    _ = librosa.load(__file__, sr=16000, duration=0.1)
except:
    pass
print("Ready!\n")

def download_iiserb_data():
    # API v3 with key parameter
    base_url = "https://www.xeno-canto.org/api/3/recordings"
    
    for name, sci_name in birds.items():
        print(f"\n{'='*60}")
        print(f"Fetching {name} ({sci_name})...")
        print('='*60)
        os.makedirs(f"raw_audio/{name}", exist_ok=True)
        
        try:
            # Build query with API key - v3 requires gen: and sp: tags
            genus, species = sci_name.split()[0], sci_name.split()[1]
            query = f"gen:{genus} sp:{species}"
            
            params = {
                'query': query,
                'key': API_KEY
            }
            
            print(f"  Query: {query}")
            r = requests.get(base_url, params=params, timeout=30)
            
            if r.status_code != 200:
                print(f"  X API error (HTTP {r.status_code})")
                print(f"  Response: {r.text[:200]}")
                continue
            
            data = r.json()
            
            # Check if recordings exist
            if 'recordings' not in data:
                print(f"  X No recordings found")
                continue
            
            recordings = data['recordings']
            num_total = data.get('numRecordings', len(recordings))
            
            if not recordings:
                print(f"  ! No recordings available")
                continue
                
            print(f"  Found {num_total} total recordings!")
            print(f"  Downloading first 10...")
            
            # Download first 10
            downloaded = 0
            for i, rec in enumerate(recordings[:10]):
                rec_id = rec.get('id', i)
                file_url = rec.get('file', '')
                
                if not file_url:
                    print(f"  X No file URL for recording {rec_id}")
                    continue
                
                # Ensure URL starts with https
                if not file_url.startswith('http'):
                    file_url = 'https:' + file_url
                
                file_path = f"raw_audio/{name}/{name}_{rec_id}.mp3"
                wav_path = f"iiserb_dataset/{name}/{name}_{rec_id}.wav"
                
                # Skip if already processed
                if os.path.exists(wav_path):
                    print(f"  [{i+1}/10] {rec_id} - Already exists")
                    downloaded += 1
                    continue
                
                # Download MP3
                print(f"[{i+1}/10] Downloading {rec_id}...", end=' ', flush=True)
                try:
                    with requests.get(file_url, stream=True, timeout=60) as audio_r:
                        audio_r.raise_for_status()
                        with open(file_path, 'wb') as f:
                            for chunk in audio_r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    print(f"OK ({os.path.getsize(file_path)//1024}KB)", end=' ')
                    
                    # Convert to TinyML format (16kHz, Mono, 3s)
                    print("Converting...", end=' ', flush=True)
                    y, sr = librosa.load(file_path, sr=16000, mono=True)
                    y = y[:16000*3]  # Keep only 3 seconds
                    os.makedirs(f"iiserb_dataset/{name}", exist_ok=True)
                    sf.write(wav_path, y, 16000)
                    print("WAV")
                    downloaded += 1
                    time.sleep(1)  # Be nice to the server
                    
                except Exception as e:
                    print(f"X ({str(e)[:40]})")
                    
            print(f"\n  Successfully downloaded {downloaded}/10 files for {name}")
                    
        except Exception as e:
            print(f"  X Error: {e}")
            continue
    
    print(f"\n{'='*60}")
    print("Download complete!")
    print('='*60)
    print(f"Raw MP3s: raw_audio/")
    print(f"TinyML WAVs: iiserb_dataset/")

download_iiserb_data()
