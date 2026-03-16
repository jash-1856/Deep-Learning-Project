import os
import librosa
import soundfile as sf
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_DIR = "dataset\wav_clean"
OUTPUT_DIR = "dataset/foregrounds"  # Scaper will use this folder!
SAMPLE_RATE = 32000

# Physics of the cut
TOP_DB = 20        # Cut anything that is 20dB quieter than the loudest peak
MIN_DUR = 0.5      # Minimum length of a chirp (in seconds) to keep
MAX_DUR = 10.0     # Maximum length (prevents keeping giant chunks of noise)

# ==========================================
# THE TRIMMER FUNCTION
# ==========================================
def process_bird_folder(bird_name):
    in_folder = os.path.join(INPUT_DIR, bird_name)
    out_folder = os.path.join(OUTPUT_DIR, bird_name)
    
    if not os.path.isdir(in_folder):
        return
        
    os.makedirs(out_folder, exist_ok=True)
    print(f"\n--- Trimming {bird_name} ---")
    
    total_chunks = 0
    files = [f for f in os.listdir(in_folder) if f.endswith('.wav')]
    
    for i, filename in enumerate(files):
        file_path = os.path.join(in_folder, filename)
        base_name = filename.replace(".wav", "")
        
        try:
            # 1. Load the audio
            y, sr = librosa.load(file_path, sr=SAMPLE_RATE)
            
            # 2. Find the non-silent intervals
            # intervals is a list of [start_index, end_index]
            intervals = librosa.effects.split(y, top_db=TOP_DB)
            
            chunk_count = 0
            for start, end in intervals:
                # Extract the chunk
                chunk = y[start:end]
                duration = len(chunk) / sr
                
                # Filter out tiny clicks or massive blocks of noise
                if MIN_DUR <= duration <= MAX_DUR:
                    save_name = f"{base_name}_chunk{chunk_count}.wav"
                    save_path = os.path.join(out_folder, save_name)
                    
                    sf.write(save_path, chunk, sr)
                    chunk_count += 1
                    total_chunks += 1
            
            if i % 10 == 0:
                print(f"   Processed {i}/{len(files)} files...")
                
        except Exception as e:
            print(f"   [Error] Failed on {filename}: {e}")
            
    print(f"-> Extracted {total_chunks} pure calls for {bird_name}.")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    print("Initializing Silence Trimmer...")
    
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Cannot find {INPUT_DIR}")
    else:
        for folder in os.listdir(INPUT_DIR):
            process_bird_folder(folder)
            
    print("\nTrimming Complete! Your 'dataset/foregrounds' folder is ready for Scaper.")



