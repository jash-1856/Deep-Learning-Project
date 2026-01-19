# Manual Download Guide for IISERB Bird Sounds

**Important Update:** Xeno-Canto upgraded to API v3 which requires a free API key.

## Quick Solution: Get Your Free API Key

1. **Create a free account**: https://xeno-canto.org/account/register
2. **Get your API key**: https://xeno-canto.org/account
3. **Use the key** in your download script (I'll update it for you)

---

## Option 1: Manual Download from Xeno-Canto Website (No API key needed)

Visit each species page and download recordings:

### 10 IISERB Bird Species Links:

1. **Asian Koel** - *Eudynamys scolopaceus*  
   https://xeno-canto.org/species/Eudynamys-scolopaceus

2. **Red-vented Bulbul** - *Pycnonotus cafer*  
   https://xeno-canto.org/species/Pycnonotus-cafer

3. **Common Myna** - *Acridotheres tristis*  
   https://xeno-canto.org/species/Acridotheres-tristis

4. **Greater Coucal** - *Centropus sinensis*  
   https://xeno-canto.org/species/Centropus-sinensis

5. **Grey Francolin** - *Francolinus pondicerianus*  
   https://xeno-canto.org/species/Francolinus-pondicerianus

6. **Indian Peafowl** - *Pavo cristatus*  
   https://xeno-canto.org/species/Pavo-cristatus

7. **Rose-ringed Parakeet** - *Psittacula krameri*  
   https://xeno-canto.org/species/Psittacula-krameri

8. **Indian Grey Hornbill** - *Ocyceros birostris*  
   https://xeno-canto.org/species/Ocyceros-birostris

9. **Purple Sunbird** - *Cinnyris asiatica*  
   https://xeno-canto.org/species/Cinnyris-asiatica

10. **Coppersmith Barbet** - *Psilopogon haemacephalus*  
    https://xeno-canto.org/species/Psilopogon-haemacephalus

### Download Instructions:

1. Click on each link above
2. Filter by **Country: India** (use the filter panel on the left)
3. Look for **Quality: A** recordings
4. Download **15-20 recordings** per species
5. Save them to: `dataset/audio/[Species_Name]/`

Example structure:
```
dataset/
  audio/
    Asian_Koel/
      recording1.mp3
      recording2.mp3
      ...
    Red-vented_Bulbul/
      recording1.mp3
      ...
```

## Option 2: Use Demo Dataset (For Testing)

If you want to test your model pipeline immediately, run:

```bash
python create_demo_dataset.py
```

This creates synthetic bird-like audio samples that match the TinyML format (16kHz, mono, 3s).

## Option 3: Alternative Sound Sources

- **Macaulay Library** (Cornell Lab): https://www.macaulaylibrary.org/
- **Internet Bird Collection**: https://www.hbw.com/ibc
- **British Library Sounds**: https://sounds.bl.uk/

## After Manual Download

Once you have the MP3 files organized in `dataset/audio/`, run the processing part:

```bash
python iiserb_dataset_automation.py
```

(Comment out the download section and just run `create_iiserb_dataset()`)
