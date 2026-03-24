# 🚀 Quick Start - RF Test with Polar H10

**Status:** ✅ Ready to run!

---

## Super Simple Command

### Quick 2-minute test:

```bash
./run_rf_test.sh 2
```

### Full 15-minute RF test:

```bash
./run_rf_test.sh
```

**That's it!** No venv activation needed - the script handles it!

---

## What Happens:

1. **Connects** to your Polar H10 (make sure it's on and close by!)
2. **Records** for specified duration
3. **Exports** to `exports/rf_test_Fisher-Lehrer_[timestamp].txt`
4. **Ready** for Windows + HRVisualizer!

---

## First Time Setup (Already Done! ✅)

You've already completed setup:
- ✅ Virtual environment created (`venv/`)
- ✅ Dependencies installed (PySide6, blehrm, etc.)
- ✅ Launcher script created (`run_rf_test.sh`)

---

## Test Right Now

Put on your Polar H10 and run:

```bash
cd /Users/oli/Downloads/HRVISUALIZER_WITH_SOURCE_CODE/every-breath-you-take
./run_rf_test.sh 2
```

**2-minute test** - Quick validation that everything works!

---

## Expected Output:

```
🔬 POLAR H10 RF DETERMINATION TEST
   Using Fisher & Lehrer (2022) protocol

======================================================================
POLAR H10 RF TEST - FISHER & LEHRER PROTOCOL
======================================================================

🔍 Scanning for Polar H10...
✅ Found: Polar H10 XXXXXXXX

📡 Connecting to Polar H10 XXXXXXXX...
✅ Connected!

📋 Setting up Fisher_Lehrer protocol...
   Name: Fisher & Lehrer RF Test
   Duration: 2 minutes
   Breathing: 6.75 → 4.25 bpm

🫁 Starting session...
   Follow your breath naturally
   Breathing rate will automatically slide from 6.75 → 4.25 bpm
   Duration: 2 minutes

⏱️  Session in progress... (Press Ctrl+C to stop early)

   [  8%] Time: 00:10 | Breathing: 6.67 bpm | RR intervals:   12 | Breaths:  2560
   [  17%] Time: 00:20 | Breathing: 6.58 bpm | RR intervals:   24 | Breaths:  5120
   ... (continues) ...

✅ Session complete!

======================================================================
SESSION SUMMARY
======================================================================
   RR intervals collected: 143
   Breathing samples collected: 30720
   Duration: 2.00 minutes

======================================================================
EXPORTING TO HRVISUALIZER
======================================================================

📖 Reading Elite HRV file...
✅ Loaded 143 RR intervals
   Duration: 120.0 seconds
   Average HR: 71.8 bpm

🫁 Converting chest acceleration to respiration waveform...

💾 Writing HRVisualizer file: exports/rf_test_Fisher-Lehrer_20260214_203000.txt
✅ Written 30720 samples (2.00 minutes)

======================================================================
✅ EXPORT COMPLETE!
======================================================================

📁 File saved: exports/rf_test_Fisher-Lehrer_20260214_203000.txt

📝 Next steps:
   1. Transfer exports/rf_test_Fisher-Lehrer_20260214_203000.txt to Windows PC
   2. Open HRVisualizer
   3. Import the file
   4. Your RF will be displayed!

📡 Disconnecting from Polar H10...
✅ Disconnected
```

---

## File Output

**Location:** `exports/`

**Format:** `rf_test_Fisher-Lehrer_YYYYMMDD_HHMMSS.txt`

**Example:** `rf_test_Fisher-Lehrer_20260214_203000.txt`

**Size:**
- 2 minutes: ~500 KB
- 15 minutes: ~3-4 MB

---

## Troubleshooting

### "Polar H10 not found"
- **Check:** Polar H10 is powered on (LED should blink)
- **Check:** Electrodes are wet (moisten with water/saliva)
- **Check:** Strap is snug on chest
- **Try:** Move closer to computer

### "Permission denied: ./run_rf_test.sh"
```bash
chmod +x run_rf_test.sh
```

### "ModuleNotFoundError"
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

---

## Tips for Best Results

**For accurate RF measurement:**
- ✅ Morning, fasted (2+ hours after eating)
- ✅ Sit upright, back supported
- ✅ Stay VERY still (accelerometer is sensitive!)
- ✅ Breathe naturally
- ✅ Quiet environment
- ✅ Polar H10 snug but comfortable

---

## Next Steps

### After 2-minute test works:

```bash
# Full 15-minute RF determination
./run_rf_test.sh
```

### Transfer to Windows:

```bash
# Find your export file
ls exports/

# Transfer rf_test_Fisher-Lehrer_*.txt to Windows
# Import to HRVisualizer
# Get your RF!
```

---

**You're ready! Just run `./run_rf_test.sh 2` now!** 🎯
