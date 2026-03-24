# Quick RF Test - Simple Guide

**One-command RF testing with Elite HRV + Whoop**

---

## 🎯 What You Need

1. **Whoop** (on wrist)
2. **Elite HRV app** (on phone, connected to Whoop)
3. **breath.cafe** (on Mac) - use `breath_cafe_research_protocol.html`
4. **15 minutes** of quiet time

---

## 📱 Recording a Session

### Before Session

1. **Open breath.cafe on Mac:**
   - File: `breath_cafe_research_protocol.html`
   - Settings already correct:
     - Duration: 15 minutes ✓
     - Start: 6.75 bpm ✓
     - End: 4.25 bpm ✓
     - Ratio: 1:1 ✓
     - Mode: Per Breath ✓

2. **Open Elite HRV on phone:**
   - Connect to Whoop
   - Verify HR showing

### During Session

1. **Start both at same time** (use screen record if helpful!)
2. **Follow breath.cafe pacer** for 15 minutes
3. **Breathe calmly** - don't stress about perfection
4. **Stop Elite HRV** when session ends

### After Session

1. **Export Elite HRV data:**
   - Format: RR intervals → Text
   - Save to Files/iCloud or AirDrop to Mac
   - Filename: `Elite HRV [timestamp].txt`

2. **You don't need the breath.cafe CSV!**
   - The script generates it automatically
   - Just close breath.cafe

---

## 💻 Converting to HRVisualizer Format

### Simple Method (Recommended)

```bash
# One command!
python3 quick_rf_test.py "Elite HRV [your file].txt"
```

**Example:**
```bash
python3 quick_rf_test.py "Elite HRV 20260213_203000.txt"
```

**Output:**
- Creates: `rf_test_20260213_203045.txt`
- Auto-timestamped
- Ready for Windows!

### What It Does Automatically

✅ Reads your RR intervals
✅ Generates standard Fisher & Lehrer breath schedule
✅ Creates synthetic respiration waveform
✅ Reconstructs ECG waveform
✅ Outputs HRVisualizer-compatible file
✅ Names file with timestamp

### Expected Output

```
======================================================================
QUICK RF TEST - Standard Fisher & Lehrer Protocol
======================================================================

📖 Reading Elite HRV file: Elite HRV 20260213_203000.txt
✅ Loaded 1122 RR intervals
   Duration: 900.0 seconds (15.00 minutes)
   Average HR: 75.0 bpm

🫁 Generating standard Fisher & Lehrer breath schedule...
📐 Standard Fisher & Lehrer Protocol:
   Duration: 15 minutes
   Breathing: 6.75 → 4.25 bpm
   Period change: 66.83 ms/breath
   Estimated breaths: 78

⏱️  Timing check:
   Elite HRV: 900.0 sec
   Protocol: 900.0 sec
   Difference: 0.0 sec
   ✅ Perfect sync!

🫀 Reconstructing ECG from RR intervals...
🫁 Generating synthetic respiration waveform...

💾 Writing HRVisualizer file: rf_test_20260213_203045.txt
✅ Written 230400 samples (15.00 minutes)

======================================================================
✅ CONVERSION COMPLETE!
======================================================================

📁 Output file: rf_test_20260213_203045.txt
```

---

## 📊 Analyzing on Windows

### Transfer File

**Options:**
- USB drive
- Email
- Dropbox/iCloud
- AirDrop (if Windows accessible)

**File to transfer:**
```
rf_test_YYYYMMDD_HHMMSS.txt (usually 3-4 MB)
```

### Import to HRVisualizer

1. Open **HRVisualizer.exe** (or HRVisualizer-orig.exe)
2. Drag and drop `rf_test_*.txt` file
3. Wait ~20 seconds for processing
4. **Your RF is displayed!**

### Expected Results

**RF Range:** 4.0-7.0 bpm (typical)
- 4.0-4.5 bpm: Low RF (slow breathing optimal)
- 4.5-5.5 bpm: Average RF (most common)
- 5.5-6.5 bpm: Higher RF
- 6.5-7.0 bpm: High RF

**Visual Check:**
- Clear waveforms visible ✓
- Peak (thick grey) clearly marked ✓
- RF number displayed in bottom right ✓

---

## 🔄 Advanced: Full Control Method

If you want to customize settings, use the full converter:

```bash
python3 elitehrv_to_hrvisualizer.py \
    --rr "Elite HRV [file].txt" \
    --breath "breath_schedule_per_breath_[timestamp].csv" \
    --start-time "2026-02-13T20:30:00" \
    --output "custom_session.txt"
```

**But for standard RF testing, use `quick_rf_test.py` - it's simpler!**

---

## ❓ Troubleshooting

### "File not found"

```bash
# Check filename
ls -lh "Elite HRV"*.txt

# Use exact filename (with quotes if it has spaces!)
python3 quick_rf_test.py "Elite HRV 20260213_203000.txt"
```

### "Timing difference >30 seconds"

**Cause:** Elite HRV stopped recording early

**Solution:**
- Ensure full 15-minute recording next time
- Check phone didn't sleep/interrupt
- File will still work if >14 minutes

### "HRVisualizer won't import file"

**Checks:**
1. File size ~3-4 MB? (check with `ls -lh`)
2. Transferred completely to Windows?
3. Using HRVisualizer.exe or HRVisualizer-orig.exe?

---

## 📅 Workflow Summary

### One-Time Setup (5 minutes)

1. Install Elite HRV app on phone
2. Connect Elite HRV to Whoop
3. Download `breath_cafe_research_protocol.html` to Mac
4. Ensure HRVisualizer working on Windows PC

### Each RF Test (20 minutes total)

**Recording (15 min):**
1. Start Elite HRV + breath.cafe simultaneously
2. Follow breathing pacer
3. Export Elite HRV data

**Converting (1 min):**
```bash
python3 quick_rf_test.py "Elite HRV [file].txt"
```

**Analyzing (4 min):**
1. Transfer to Windows
2. Import to HRVisualizer
3. Read your RF!

---

## 🎯 Tips for Best Results

### During Recording

✅ Sit comfortably, back supported
✅ Minimize movement (affects Whoop accuracy)
✅ Breathe naturally - don't force
✅ Stay relaxed
✅ Follow pacer smoothly (don't stress about perfection)

### For Consistent Results

✅ Same time of day (morning recommended)
✅ Not after eating/exercise (wait 2+ hours)
✅ Not when stressed/sick
✅ Repeat 2-3 times to verify RF consistency

### Expected Variability

- RF ±0.3 bpm between sessions: Normal ✓
- RF ±0.5+ bpm between sessions: Check conditions
- RF completely different: Data quality issue or true physiological change

---

## 📊 Interpreting Your RF

**Once you know your RF (e.g., 4.5 bpm):**

### For HRV Training

1. **Practice breathing at your RF**
   - Duration: 5-20 minutes daily
   - Use breath.cafe set to your RF (e.g., 4.5 bpm)
   - Benefits: Reduced stress, better autonomic balance

2. **Use Yudemon HRV app**
   - Connects to Whoop
   - Guides breathing near your RF
   - Tracks HRV improvements

3. **Monitor progress**
   - Resting HRV trends upward over weeks/months
   - Better stress resilience
   - Improved emotional regulation

### When to Re-Test RF

- After 6-12 months of HRV training
- If health status changes significantly
- To verify consistency (2-3 tests)

---

## 🎓 Understanding the Data

**What the script does:**

1. **Reads RR intervals** from Elite HRV (your heartbeat timing)
2. **Generates breath schedule** (standard 15-min protocol)
3. **Creates synthetic respiration** (simulates breathing sensor)
4. **Reconstructs ECG** (from RR intervals)
5. **Packages for HRVisualizer** (compatible format)

**Why synthetic respiration works:**

- HRVisualizer needs breathing data to map time → breathing frequency
- We generate a perfect 6.75→4.25 bpm sweep
- Your actual HRV (from real RR intervals) determines the peak
- 0.15 bpm accuracy validated (see test results!)

**The phase lag doesn't matter:**

- Breathing and HR naturally have 2-3 second lag (RSA physiology)
- We're just finding WHICH breathing frequency maximizes HRV
- Not measuring TIMING relationship between breathing and HR
- So synthetic breathing schedule is perfectly fine!

---

## 📚 Files Reference

### Scripts

- **quick_rf_test.py** ← Use this! Simple one-command converter
- **elitehrv_to_hrvisualizer.py** ← Advanced (custom settings)
- **polar_to_hrvisualizer.py** ← For future Polar H10 use

### Breath Pacer

- **breath_cafe_research_protocol.html** ← Use this for sessions

### Documentation

- **QUICK_RF_TEST_GUIDE.md** ← You are here!
- **TONIGHT_TEST_ELITE_HRV.md** ← Detailed full workflow
- **SYNTHETIC_RESPIRATION_TEST_RESULTS.md** ← Validation data

---

## ✅ Quick Command Reference

**Most common:**
```bash
# Convert Elite HRV to HRVisualizer
python3 quick_rf_test.py "Elite HRV [timestamp].txt"
```

**Check files:**
```bash
# List Elite HRV exports
ls -lh "Elite HRV"*.txt

# Check output file
ls -lh rf_test_*.txt
```

**Move to sessions folder:**
```bash
mkdir -p sessions
mv "Elite HRV"*.txt sessions/
mv rf_test_*.txt sessions/
```

---

## 🎉 Success Checklist

After first test:

- [ ] Recorded full 15-minute Elite HRV session
- [ ] Followed breath.cafe pacer
- [ ] Converted with `quick_rf_test.py`
- [ ] Transferred to Windows
- [ ] Imported to HRVisualizer successfully
- [ ] RF detected in 4.0-7.0 bpm range
- [ ] Know my personal RF!

---

**You're all set! Each RF test is now just one simple command.** 🚀
