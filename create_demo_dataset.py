"""
Demo Dataset Creator for IISERB Bird Sound Classification
Creates synthetic audio samples for testing your TinyML pipeline
"""
import os
import numpy as np
import soundfile as sf
from sklearn.model_selection import train_test_split

# Species to create demo samples for
iiserb_birds = [
    "Asian_Koel",
    "Red-vented_Bulbul",
    "Common_Myna",
    "Greater_Coucal",
    "Grey_Francolin",
    "Indian_Peafowl",
    "Rose-ringed_Parakeet",
    "Indian_Grey_Hornbill",
    "Purple_Sunbird",
    "Coppersmith_Barbet"
]

def generate_bird_like_audio(duration=3, sr=16000, freq_range=(1000, 8000)):
    """Generate synthetic bird-like audio with varying frequency patterns"""
    t = np.linspace(0, duration, int(sr * duration))
    
    # Create multiple frequency components (simulating bird calls)
    audio = np.zeros_like(t)
    
    for _ in range(np.random.randint(3, 7)):  # 3-6 frequency components
        freq = np.random.uniform(*freq_range)
        phase = np.random.uniform(0, 2 * np.pi)
        amplitude = np.random.uniform(0.1, 0.3)
        
        # Add frequency modulation (warbling effect)
        mod_freq = np.random.uniform(2, 10)
        mod_depth = np.random.uniform(50, 200)
        modulated_freq = freq + mod_depth * np.sin(2 * np.pi * mod_freq * t)
        
        audio += amplitude * np.sin(2 * np.pi * modulated_freq * t + phase)
    
    # Add envelope (attack-decay)
    envelope = np.exp(-3 * t)
    audio *= envelope
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    return audio.astype(np.float32)

def create_demo_dataset(num_samples_per_species=20, test_split=0.2):
    """Create demo dataset with train/test split"""
    print("Creating IISERB Demo Dataset for TinyML...\n")
    
    final_dir = "iiserb_tinyml_dataset"
    
    for bird in iiserb_birds:
        print(f"Generating samples for {bird}...")
        
        samples = []
        for i in range(num_samples_per_species):
            audio = generate_bird_like_audio()
            samples.append((f"{bird}_{i:03d}.wav", audio))
        
        # Split into train and test
        train_samples, test_samples = train_test_split(
            samples, test_size=test_split, random_state=42
        )
        
        # Save training samples
        train_dir = os.path.join(final_dir, "train", bird)
        os.makedirs(train_dir, exist_ok=True)
        
        for filename, audio in train_samples:
            sf.write(os.path.join(train_dir, filename), audio, 16000)
        
        # Save test samples
        test_dir = os.path.join(final_dir, "test", bird)
        os.makedirs(test_dir, exist_ok=True)
        
        for filename, audio in test_samples:
            sf.write(os.path.join(test_dir, filename), audio, 16000)
        
        print(f" Created {len(train_samples)} train + {len(test_samples)} test samples")
    
    print(f"\n Demo dataset ready in '{final_dir}/'")
    print(f"\n Dataset structure:")
    print(f"   - 10 bird species")
    print(f"   - {num_samples_per_species} samples per species")
    print(f"   - {int(num_samples_per_species * (1-test_split))} training samples per class")
    print(f"   - {int(num_samples_per_species * test_split)} test samples per class")
    print(f"   - 16kHz sampling rate, 3-second clips")

if __name__ == "__main__":
    create_demo_dataset(num_samples_per_species=20, test_split=0.2)
