import os
import shutil
import librosa
import soundfile as sf
from sklearn.model_selection import train_test_split
import requests
import time
from urllib.parse import quote

# 1. Species list from your IISERB hotspot (Scientific Names for Xeno-Canto)
# I've selected the 10 most distinct and common vocalizers on the IISERB list
iiserb_birds = {
    "Asian_Koel": "Eudynamys scolopaceus",
    "Red-vented_Bulbul": "Pycnonotus cafer",
    "Common_Myna": "Acridotheres tristis",
    "Greater_Coucal": "Centropus sinensis",
    "Grey_Francolin": "Francolinus pondicerianus",
    "Indian_Peafowl": "Pavo cristatus",
    "Rose-ringed_Parakeet": "Psittacula krameri",
    "Indian_Grey_Hornbill": "Ocyceros birostris",
    "Purple_Sunbird": "Cinnyris asiatica",
    "Coppersmith_Barbet": "Psilopogon haemacephalus"
}

# Test API connection first
def test_api():
    print("Testing Xeno-Canto API connection...")
    # Try different possible API endpoints
    test_urls = [
        "https://www.xeno-canto.org/api/2/recordings?query=gen:passer",
        "https://xeno-canto.org/api/2/recordings?query=Passer",
    ]
    
    for test_url in test_urls:
        try:
            print(f"  Trying: {test_url}")
            response = requests.get(test_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                num_recs = data.get('numRecordings', 0)
                if num_recs > 0:
                    print(f"✓ API working! Found {num_recs} test recordings\n")
                    return True
                print(f"  Response: {list(data.keys())}")
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")
    
    print("✗ Could not connect to API\n")
    return False

# 2. Download high-quality recordings from India using Xeno-Canto API
def download_xeno_canto_recordings():
    raw_dir = "dataset/audio"
    os.makedirs(raw_dir, exist_ok=True)
    
    for name, sci_name in iiserb_birds.items():
        print(f"--- Downloading {name} ({sci_name}) ---")
        
        # Create species folder
        species_folder = os.path.join(raw_dir, name)
        os.makedirs(species_folder, exist_ok=True)
        
        # Try different query formats
        queries_to_try = [
            sci_name,  # Simple species name
            f"gen:{sci_name.split()[0]} sp:{sci_name.split()[1]}",  # Genus:species format
        ]
        
        recordings = []
        for query in queries_to_try:
            url = f"https://www.xeno-canto.org/api/2/recordings?query={quote(query)}"
            print(f"  Query: {query}")
            
            try:
                response = requests.get(url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code == 200:
                    data = response.json()
                    recordings = data.get('recordings', [])
                    num_recordings = data.get('numRecordings', 0)
                    
                    if recordings:
                        print(f"  ✓ Found {num_recordings} total recordings")
                        break
                    else:
                        print(f"  No recordings (status {response.status_code})")
                else:
                    print(f"  Failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ✗ Error: {str(e)[:80]}")
                continue
        
        if not recordings:
            print(f"  ⚠ Skipping {name} - no recordings available\n")
            continue
        
        # Filter for quality recordings
        quality_recs = [r for r in recordings if r.get('q', '') in ['A', 'B']]
        if quality_recs:
            recordings = quality_recs[:30]
            print(f"  ✓ Using {len(recordings)} quality A/B recordings")
        else:
            recordings = recordings[:30]
        
        # Download up to 15 recordings per species
        count = 0
        for rec in recordings:
            if count >= 15:
                break
            
            # Get download URL
            file_url = rec.get('file')
            if not file_url:
                continue
                
            if not file_url.startswith('http'):
                file_url = 'https:' + file_url
            
            # Download file
            rec_id = rec.get('id', count)
            filename = f"{name}_{rec_id}.mp3"
            filepath = os.path.join(species_folder, filename)
            
            try:
                print(f"  [{count+1}/15] Downloading {rec_id}...", end=' ', flush=True)
                audio_response = requests.get(file_url, timeout=60, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                audio_response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(audio_response.content)
                print("✓")
                count += 1
                time.sleep(1)  # Be respectful to the server
            except Exception as e:
                print(f"✗ ({str(e)[:40]})")
                
        print(f"  ✅ Downloaded {count} files for {name}\n")
        time.sleep(2)  # Longer pause between species

# Test API first
if test_api():
    download_xeno_canto_recordings()
else:
    print("⚠ Skipping download due to API issues. Please check your internet connection.")

# 3. Process into TinyML format (16kHz, Mono, 3s clips) & Train/Test Split
def create_iiserb_dataset():
    raw_dir = "dataset/audio"
    final_dir = "iiserb_tinyml_dataset"
    
    print("\n--- Processing audio files to TinyML format ---")
    
    for label in iiserb_birds.keys():
        # Use the folder name we created
        full_path = os.path.join(raw_dir, label)
        
        if not os.path.exists(full_path):
            print(f"Skipping {label} - no folder found")
            continue
            
        files = [f for f in os.listdir(full_path) if f.endswith('.mp3')]
        
        if len(files) == 0:
            print(f"Skipping {label} - no audio files")
            continue
        
        print(f"Processing {len(files)} files for {label}...")
        
        # Split 80% Train, 20% Test
        train_f, test_f = train_test_split(files, test_size=0.2, random_state=42)
        
        for split, split_files in [('train', train_f), ('test', test_f)]:
            target_path = os.path.join(final_dir, split, label)
            os.makedirs(target_path, exist_ok=True)
            
            for f in split_files:
                try:
                    # Load, resample to 16kHz (TinyML standard), convert to Mono
                    y, sr = librosa.load(os.path.join(full_path, f), sr=16000, mono=True)
                    # Use a 3-second window for the model
                    y_clipped = y[:16000*3] 
                    sf.write(os.path.join(target_path, f.replace(".mp3", ".wav")), y_clipped, 16000)
                except Exception as e:
                    print(f"  Error processing {f}: {e}")
        
        print(f"  ✓ {len(train_f)} train + {len(test_f)} test files")

create_iiserb_dataset()
print("\n✅ Done! Your dataset is ready in 'iiserb_tinyml_dataset/'")
