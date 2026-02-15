# IISERB Bird Sound Dataset - TinyML Project

This project automates the download and processing of bird sound recordings from the IISERB (Indian Institute of Science Education and Research Bhopal) hotspot for TinyML applications.

##  Features

- Downloads bird sound recordings from Xeno-Canto database
- Converts audio to TinyML-compatible format (16kHz, mono, 3-second clips)
- Creates train/test splits for model training
- Supports 10 common bird species from IISERB region

##  Bird Species Included

1. Asian Koel (*Eudynamys scolopaceus*)
2. Red-vented Bulbul (*Pycnonotus cafer*)
3. Common Myna (*Acridotheres tristis*)
4. Greater Coucal (*Centropus sinensis*)
5. Grey Francolin (*Francolinus pondicerianus*)
6. Indian Peafowl (*Pavo cristatus*)
7. Rose-ringed Parakeet (*Psittacula krameri*)
8. Indian Grey Hornbill (*Ocyceros birostris*)
9. Purple Sunbird (*Cinnyris asiatica*)
10. Coppersmith Barbet (*Psilopogon haemacephalus*)

##  Quick Start

### Prerequisites

```bash
pip install librosa scikit-learn soundfile requests
```

### Option 1: Generate Demo Dataset (No API key needed)

```bash
python create_demo_dataset.py
```

This creates synthetic bird-like sounds perfect for testing your TinyML pipeline.

### Option 2: Download Real Bird Sounds

1. Get a free API key from [Xeno-Canto](https://xeno-canto.org/account)
2. Set your API key as an environment variable:
   ```bash
   # Windows PowerShell
   $env:XENO_CANTO_API_KEY="your_api_key_here"
   
   # Linux/Mac
   export XENO_CANTO_API_KEY="your_api_key_here"
   ```
3. Run the download script:
   ```bash
   python download_xeno_canto.py
   ```

### Option 3: Manual Download

Follow the instructions in [MANUAL_DOWNLOAD_GUIDE.md](MANUAL_DOWNLOAD_GUIDE.md)

##  Project Structure

```
├── create_demo_dataset.py          # Generate synthetic demo data
├── download_xeno_canto.py          # Download real bird sounds
├── iiserb_dataset_automation.py    # Full automation script
├── MANUAL_DOWNLOAD_GUIDE.md        # Manual download instructions
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

##  Output Format

The scripts generate a dataset in the following structure:

```
iiserb_tinyml_dataset/
├── train/
│   ├── Asian_Koel/
│   │   ├── Asian_Koel_001.wav
│   │   └── ...
│   ├── Red-vented_Bulbul/
│   └── ...
└── test/
    ├── Asian_Koel/
    └── ...
```

**Audio Specifications:**
- Format: WAV
- Sample Rate: 16kHz
- Channels: Mono
- Duration: 3 seconds
- Split: 80% train, 20% test

##  Resources

- [Xeno-Canto](https://xeno-canto.org/) - Bird sound database
- [IISERB eBird Hotspot](https://ebird.org/hotspot/L2217455) - Source of species list
- [TinyML Book](https://www.oreilly.com/library/view/tinyml/9781492052036/)

##  License

This project is for educational purposes. Bird recordings are from Xeno-Canto and are subject to their individual licenses.

##  Acknowledgments

- Xeno-Canto community for the bird sound recordings
- IISERB for the species reference data ESIC
