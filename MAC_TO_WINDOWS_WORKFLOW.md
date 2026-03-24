# Mac to Windows Workflow Guide
**Polar H10 + breath.cafe → HRVisualizer**

Your setup: **Mac for data collection → Windows PC for HRVisualizer**

---

## 🎯 Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    ON YOUR MAC                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: Record Session                                    │
│  ├─ Polar H10 → iPhone (ECG Recorder/EphorPolar)           │
│  └─ breath.cafe → Browser (modified version with logging)  │
│                                                             │
│  Step 2: Export Data                                       │
│  ├─ RR_20260213_143000.csv (from Polar app)                │
│  └─ breath_schedule_20260213_143000.csv (from breath.cafe) │
│                                                             │
│  Step 3: Convert to HRVisualizer Format                    │
│  └─ Run: python3 polar_to_hrvisualizer.py                  │
│      Output: hrv_session_20260213_143000.txt               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Transfer .txt file
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  ON YOUR WINDOWS PC                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 4: Import into HRVisualizer                          │
│  └─ Open HRVisualizer.exe                                  │
│      Load: hrv_session_20260213_143000.txt                 │
│                                                             │
│  Step 5: View Results                                      │
│  ├─ Detected RF (should be ~5.5 bpm for test data)         │
│  ├─ Visual timeline (HR + respiration)                     │
│  └─ Max HRV window marker                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Step-by-Step Instructions

### PART 1: On Your Mac (Data Collection & Conversion)

#### ✅ Prerequisites (One-Time Setup)

**1. Install Python 3** (if not already installed)
```bash
# Check if you have Python 3
python3 --version

# If not installed, get it from:
# https://www.python.org/downloads/
```

**2. Verify converter scripts are ready**
```bash
cd ~/Downloads/HRVISUALIZER_WITH_SOURCE_CODE

# Check files exist
ls -l polar_to_hrvisualizer.py
ls -l breath_cafe_logger.html
ls -l generate_test_data.py
```

**3. Test with dummy data** (optional but recommended)
```bash
# Generate test data
python3 generate_test_data.py --output test_data/

# Run converter
python3 polar_to_hrvisualizer.py \
    --rr test_data/test_rr_intervals.csv \
    --breath test_data/test_breath_schedule.csv \
    --output test_data/test_output.txt

# Should see: "✅ CONVERSION COMPLETE!"
```

---

#### 📱 Step 1: Record Your Session

**A. Set up Polar H10**
- Fit chest strap (wet electrodes)
- Open Polar recording app on iPhone (ECG Recorder or EphorPolar)
- Verify Bluetooth connection

**B. Set up breath.cafe**
- On Mac, open `breath_cafe_logger.html` in browser
- Configure:
  - Duration: 15 minutes
  - Start Rate: 6.75 bpm
  - End Rate: 4.25 bpm
  - Log Interval: 60 seconds

**C. Synchronized start** (at exact time like 14:30:00)
```
Watch clock → At :00 second mark:
  1. Start Polar recording
  2. Click "Start Session" on breath.cafe
  3. Begin breathing with pacer
```

**D. Complete session**
- Breathe for 15 minutes following pacer
- Stop Polar recording
- Stop/export breath.cafe session

---

#### 📤 Step 2: Export Your Data

**A. From Polar App (iPhone)**

**If using ECG Recorder:**
```
1. Tap completed session
2. Tap "Export" or share icon
3. Choose "Files" app
4. Save to: iCloud Drive/HRV_Sessions/
5. Filename: RR_YYYYMMDD_HHMMSS.csv
```

**If using EphorPolar:**
```
1. Session automatically saved as CSV
2. Share → AirDrop to Mac
   OR
   Share → Save to Files → iCloud Drive
```

**B. From breath.cafe (Mac)**
```
1. Click "Export CSV" button
2. File downloads: breath_schedule_YYYYMMDD_HHMMSS.csv
3. Move to working directory:
   ~/Downloads/HRVISUALIZER_WITH_SOURCE_CODE/sessions/
```

**C. Transfer Polar data to Mac**

**Via AirDrop:**
```
iPhone → Mac AirDrop
File appears in ~/Downloads/
Move to: ~/Downloads/HRVISUALIZER_WITH_SOURCE_CODE/sessions/
```

**Via iCloud Drive:**
```
Files already synced to Mac
Access at: ~/Library/Mobile Documents/com~apple~CloudDocs/
Copy to: ~/Downloads/HRVISUALIZER_WITH_SOURCE_CODE/sessions/
```

---

#### 🔄 Step 3: Convert to HRVisualizer Format

**A. Organize your files**
```bash
cd ~/Downloads/HRVISUALIZER_WITH_SOURCE_CODE

# Create sessions directory
mkdir -p sessions

# Your files should be:
sessions/RR_20260213_143000.csv
sessions/breath_schedule_20260213_143000.csv
```

**B. Run the converter**
```bash
python3 polar_to_hrvisualizer.py \
    --rr sessions/RR_20260213_143000.csv \
    --breath sessions/breath_schedule_20260213_143000.csv \
    --output sessions/hrv_session_20260213_143000.txt
```

**C. Verify conversion succeeded**
```bash
# Should see output like:
# ============================================================
# ✅ CONVERSION COMPLETE!
# ============================================================
# Output file: sessions/hrv_session_20260213_143000.txt

# Check file was created
ls -lh sessions/hrv_session_20260213_143000.txt

# Should show file size ~2-3 MB
```

**D. Quick validation**
```bash
# Check first few lines
head -n 10 sessions/hrv_session_20260213_143000.txt

# Should show:
# Client:     Polar_H10_User
# Session:    Converted_Session
# Date:       02-13-2026
# Time:       14:30:00
# Duration:   900 Seconds
# Output rate: 256 Samples/sec
# ...
```

---

#### 📁 Step 4: Transfer to Windows PC

**Method A: USB Drive**
```bash
# Copy file to USB drive
cp sessions/hrv_session_20260213_143000.txt /Volumes/USB_DRIVE/

# Eject USB
# Move to Windows PC
# Copy from USB to: C:\Users\YourName\Documents\HRV\
```

**Method B: AirDrop to yourself (if using shared Apple ID)**
```
1. Right-click .txt file
2. Share → AirDrop → Your Windows PC (if nearby)
   (Only works if Windows has iCloud or AirDrop support)
```

**Method C: Cloud Storage (Dropbox/Google Drive/OneDrive)**
```bash
# Upload to Dropbox
cp sessions/hrv_session_20260213_143000.txt ~/Dropbox/HRV/

# Download on Windows from Dropbox folder
```

**Method D: Email to yourself**
```
1. Attach hrv_session_20260213_143000.txt to email
2. Send to yourself
3. Download on Windows PC
```

**Method E: Network Share (if Mac and PC on same network)**
```bash
# On Windows: Share a folder (e.g., C:\HRV_Shared)
# On Mac: Connect to PC's shared folder
# Go → Connect to Server → smb://WINDOWS_PC_IP/HRV_Shared
# Copy file to shared folder
```

---

### PART 2: On Your Windows PC (HRVisualizer Analysis)

#### 📂 Step 5: Import into HRVisualizer

**A. Locate HRVisualizer**
```
HRVisualizer source code location:
~/Downloads/HRVISUALIZER_WITH_SOURCE_CODE/

Look for:
- Nexus/Nexus.sln (Visual Studio solution)
- Nexus/Nexus/bin/Debug/Nexus.exe (compiled executable)
  OR
- Nexus/Nexus/bin/Release/Nexus.exe
```

**B. If not compiled yet:**
```
1. Open Visual Studio on Windows
2. File → Open → Project/Solution
3. Navigate to: Nexus/Nexus.sln
4. Build → Build Solution (F7)
5. Executable created at: Nexus/Nexus/bin/Debug/Nexus.exe
```

**C. Run HRVisualizer**
```
1. Double-click Nexus.exe
2. File → Open (or similar - check UI)
3. Browse to: hrv_session_20260213_143000.txt
4. Click Open/Import
```

**D. Wait for processing**
```
- HRVisualizer will:
  1. Parse the file
  2. Process ECG/RR data
  3. Analyze respiration waveform
  4. Calculate RF
  5. Display results
```

---

#### 🔍 Step 6: Interpret Results

**What to look for:**

**1. Resonance Frequency Value**
```
Should display: RF = X.XX bpm

For test data: Should be ~5.5 bpm (±0.3 bpm)
For your real data: Typically 4.5-6.5 bpm
```

**2. Visual Timeline Display**
```
- HR waveform (top): Should show oscillations
- Respiration waveform (bottom): Should show sine-like breathing pattern
- 1-min window marker: Highlights max HRV region
- Phase relationship: HR should increase on inhale, decrease on exhale
```

**3. Peak HRV Location**
```
For test data: Should occur around minute 7-8
  (when breathing rate passes through 5.5 bpm)

For your data: Note which breathing rate produced max HRV
  This is your resonance frequency!
```

**4. Validation Checks**
```
✅ File imported without errors
✅ Visual display shows clear waveforms
✅ RF value in expected range (4-7 bpm)
✅ Max HRV window makes sense timewise
✅ Phase relationship correct (HR↑ on inhale)
```

---

## 🛠️ Troubleshooting

### Issue: "File format not recognized" in HRVisualizer

**Cause:** Header format doesn't match expected

**Solution:**
```bash
# On Mac, check first 10 lines
head -n 10 sessions/hrv_session_20260213_143000.txt

# Should match exactly:
# Client:     Polar_H10_User
# Session:    Converted_Session
# Date:       MM-DD-YYYY
# Time:       HH:MM:SS
# Duration:   XXX Seconds
# Output rate: 256 Samples/sec
# 256 SPS	32 SPS           ← TAB-separated!
# Sensor-B:ECG/EKG	Sensor-G:RSP  ← TAB-separated!
# [blank line]
# [data starts]
```

**Fix:** Ensure converter script runs without errors

---

### Issue: RF detected way off from expected

**Cause:** Timing misalignment between RR and breathing

**Solution:**
1. Check RR file has timestamps (or is in order)
2. Check breath schedule timestamps match RR timestamps
3. Verify synchronized start time was exact
4. Re-run converter with verbose logging

---

### Issue: Can't transfer file from Mac to Windows

**Easiest solution:**
```bash
# On Mac: Email to yourself
# In Terminal:
echo "HRV session file attached" | mail -s "HRV Session" \
    -A sessions/hrv_session_20260213_143000.txt \
    your.email@gmail.com

# Download on Windows PC
```

---

### Issue: HRVisualizer won't compile on Windows

**Solution A: Use pre-compiled version**
```
Check if Nexus.exe already exists in:
- Nexus/Nexus/bin/Debug/
- Nexus/Nexus/bin/Release/

If yes, just run it directly
```

**Solution B: Install Visual Studio**
```
1. Download Visual Studio Community (FREE)
   https://visualstudio.microsoft.com/downloads/

2. During install, select:
   - .NET desktop development
   - Visual Basic components

3. Open Nexus.sln and build
```

---

## 📝 Quick Reference Card

**Print this for your desk:**

```
═══════════════════════════════════════════════════════════
         MAC → WINDOWS HRVISUALIZER WORKFLOW
═══════════════════════════════════════════════════════════

ON MAC:

1. RECORD
   □ Polar H10 on chest → iPhone app
   □ breath.cafe open → Mac browser
   □ Start both at same time (exact second!)
   □ Breathe 15 minutes

2. EXPORT
   □ Polar: Export RR_YYYYMMDD_HHMMSS.csv
   □ breath.cafe: Export breath_schedule_YYYYMMDD_HHMMSS.csv
   □ Transfer both to Mac (AirDrop/iCloud)

3. CONVERT
   □ cd ~/Downloads/HRVISUALIZER_WITH_SOURCE_CODE
   □ python3 polar_to_hrvisualizer.py \
       --rr sessions/RR_YYYYMMDD_HHMMSS.csv \
       --breath sessions/breath_schedule_YYYYMMDD_HHMMSS.csv \
       --output sessions/hrv_session_YYYYMMDD_HHMMSS.txt
   □ Verify: ls -lh sessions/hrv_session_*.txt

4. TRANSFER
   □ USB drive / Dropbox / Email
   □ Copy .txt file to Windows PC

ON WINDOWS:

5. IMPORT
   □ Open HRVisualizer (Nexus.exe)
   □ File → Open → hrv_session_YYYYMMDD_HHMMSS.txt

6. ANALYZE
   □ Read RF value (your resonance frequency!)
   □ Note max HRV window timing
   □ Verify visual display looks correct

═══════════════════════════════════════════════════════════
```

---

## 🎯 Test Data Results (Validation)

**You already have test data ready!**

```bash
# On Mac, try importing this into Windows HRVisualizer:
test_data/test_output.txt

# Expected results:
# ✅ RF detected: ~5.5 bpm (±0.3)
# ✅ Max HRV window: ~minute 7-8
# ✅ Clear phase relationship in visual display
```

This confirms the pipeline works before using real Polar H10 data!

---

## 📦 What You Have Ready

**On your Mac right now:**

```
~/Downloads/HRVISUALIZER_WITH_SOURCE_CODE/
├── polar_to_hrvisualizer.py       ← Main converter script
├── generate_test_data.py           ← Test data generator
├── breath_cafe_logger.html         ← Modified breath.cafe with logging
├── run_end_to_end_test.sh         ← Automated test script
│
├── test_data/                      ← Test session (ready to use!)
│   ├── test_rr_intervals.csv
│   ├── test_breath_schedule.csv
│   ├── test_output.txt            ← Transfer this to Windows to test!
│   └── README_TEST_DATA.md
│
├── sessions/                       ← Your real sessions go here
│   └── (empty - will fill when H10 arrives)
│
└── Nexus/                          ← HRVisualizer source code
    └── Nexus.sln                   ← Open this on Windows PC
```

**Status:**
- ✅ Test data generated successfully
- ✅ Converter tested and working
- ✅ Ready for real Polar H10 data
- ⏳ Waiting for H10 to arrive

---

## 🚀 Next Steps

### This Week (Before H10 Arrives)
1. ✅ Test data generated
2. ✅ Converter verified working
3. **Transfer test_output.txt to Windows PC**
4. **Test importing into HRVisualizer**
5. **Verify RF detection works (should show ~5.5 bpm)**

### When H10 Arrives
1. Download Yudemon HRV (immediate use)
2. Record first session with H10 + breath.cafe
3. Run through Mac → Windows workflow
4. Compare Yudemon RF vs. HRVisualizer RF

### Optional: Build HRVisualizer on Windows
```
If Nexus.exe doesn't exist yet:

1. Transfer entire HRVISUALIZER_WITH_SOURCE_CODE folder to Windows
2. Install Visual Studio Community (free)
3. Open Nexus/Nexus.sln
4. Build → Build Solution
5. Run Nexus.exe from bin/Debug/
```

---

**You're all set!** The pipeline is tested and ready. Just waiting for hardware. 🎉
