import os
import random
import librosa
import librosa.display
import matplotlib.pyplot as plt

# ==========================================
# 1. THE TWEAKED DIALS
# ==========================================
DATA_DIR = "dataset/wav_clean"
NUM_FILES = 10           # How many random files to check
TOP_DB = 20              # Tweak 1: Forgiving decibel drop (keeps quieter sounds)
PAD_SECONDS = 0.1        # Tweak 2: 100ms padding on cuts (prevents choppy audio)

# ==========================================
# 2. BATCH VISUALIZER LOGIC
# ==========================================
def get_random_files(base_dir, num):
    """Crawls the directory and picks random .wav files"""
    all_wavs = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.wav'):
                all_wavs.append(os.path.join(root, f))
    
    if not all_wavs:
        return []
    return random.sample(all_wavs, min(num, len(all_wavs)))

def plot_waveform(ax, file_path):
    """Processes a single file and draws it on the grid subplot"""
    try:
        # Load audio
        y, sr = librosa.load(file_path, sr=32000)
        
        # 1. Apply the tweaked math
        intervals = librosa.effects.split(y, top_db=TOP_DB)
        
        # 2. Apply the padding
        pad_samples = int(PAD_SECONDS * sr)
        padded_intervals = []
        
        for start, end in intervals:
            p_start = max(0, start - pad_samples)
            p_end = min(len(y), end + pad_samples)
            padded_intervals.append((p_start, p_end))

        # 3. Draw the Blue Waveform
        librosa.display.waveshow(y, sr=sr, alpha=0.5, color='#1f77b4', ax=ax)
        
        # 4. Draw the Green "Keep" Boxes
        for start, end in padded_intervals:
            ax.axvspan(start/sr, end/sr, color='#2ca02c', alpha=0.4)
            
        # Formatting
        bird_name = file_path.split(os.sep)[-2]
        file_name = os.path.basename(file_path)
        ax.set_title(f"{bird_name} | {file_name}", fontsize=9, fontweight='bold')
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.label_outer() # Hides redundant axis labels
        
    except Exception as e:
        ax.set_title(f"Error loading {os.path.basename(file_path)}", color='red')

# ==========================================
# 3. EXECUTION (SAVES AS PNG)
# ==========================================
if __name__ == "__main__":
    print(f"Locating files in {DATA_DIR}...")
    
    # Quick path check
    if not os.path.exists(DATA_DIR):
        print(f"CRITICAL ERROR: The folder '{DATA_DIR}' does not exist.")
        print("Make sure you are running this script from the main project folder.")
        exit()
        
    files_to_check = get_random_files(DATA_DIR, NUM_FILES)
    
    if not files_to_check:
        print(f"CRITICAL ERROR: No .wav files found inside '{DATA_DIR}'.")
        exit()

    print(f"Found files! Testing TOP_DB={TOP_DB} and PADDING={PAD_SECONDS}s...")
    print("Please wait, librosa takes a minute to load the audio...")
    
    # Create the visual grid (5 rows, 2 columns)
    fig, axes = plt.subplots(5, 2, figsize=(16, 12))
    axes = axes.flatten()

    for i, file_path in enumerate(files_to_check):
        plot_waveform(axes[i], file_path)
        print(f"   -> Processed {i+1}/{len(files_to_check)}")

    # Adjust layout and save the image
    plt.suptitle(f"Silence Trimming X-Ray (TOP_DB={TOP_DB}, PADDING={PAD_SECONDS}s)", fontsize=16)
    plt.tight_layout()
    plt.subplots_adjust(top=0.92) # Leave room for the main title
    
    save_path = "trim_check_result.png"
    plt.savefig(save_path, dpi=150)
    print(f"\n✅ SUCCESS! The grid has been saved as '{save_path}'")
    print("Go open that image file in your folder to see the results!")