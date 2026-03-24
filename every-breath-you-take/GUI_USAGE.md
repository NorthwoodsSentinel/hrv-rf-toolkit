# 🎯 GUI Usage - Fisher & Lehrer RF Testing

**The GUI now has FULL Fisher & Lehrer protocol with auto-export!**

---

## 🚀 Quick Start

```bash
cd every-breath-you-take
source venv/bin/activate
python EBYT.py
```

---

## 📋 How to Do a Fisher & Lehrer RF Test

### 1. Connect Polar H10

1. **Click "Scan"** button
2. **Wait** for Polar H10 to appear in dropdown
3. **Select** your Polar H10
4. **Click "Connect"**
5. **Wait** for "Connected" message

### 2. Select Fisher & Lehrer Protocol

1. **Find** the "Protocol:" dropdown (below breathing pacer)
2. **Select** "Fisher_Lehrer"
3. *(Hover over dropdown to see description)*

### 3. Start 15-Minute Session

1. **Click "Start Session"** button
2. **Watch** the breathing pacer (gold circle):
   - Expands = Inhale
   - Contracts = Exhale
3. **Follow along** for 15 minutes
4. **Timer shows** elapsed time (00:00 → 15:00)
5. **Breathing rate auto-slides:**
   - Starts at 6.75 bpm
   - Gradually decreases
   - Ends at 4.25 bpm

### 4. Auto-Export When Done

When 15 minutes completes:
- ✅ Session stops automatically
- ✅ **Auto-exports** to HRVisualizer format!
- ✅ Shows popup with file path
- ✅ Ready for Windows transfer!

---

## 🎨 What You'll See

### Main Display:

**🎯 Breathing Pacer (Center Left):**
- Large **gold circle** - Follow this!
- Expands/contracts to pace your breathing
- **Blue circle** - Your actual breathing (from accelerometer)
- **Red dot** - Your heart rate coherence

**📊 Top Graph:**
- **Blue line** - Your chest acceleration (real breathing!)
- **Gold line** - Target breathing pace
- **Red dots** - Your heart rate (bpm)

**📊 Bottom Graph:**
- **Red line** - Your HRV (Heart Rate Variability)
- **Green zone** - High HRV (>150ms) = Good!
- **Yellow zone** - Medium HRV (50-150ms)
- **Red zone** - Low HRV (<50ms)
- **Blue triangles** - Your breathing rate

**⏱️ Timer:**
- Shows elapsed time during session
- Format: MM:SS

---

## 🎚️ Controls

### Protocol Dropdown:
- **Fisher_Lehrer** - 15-min RF test (6.75→4.25 bpm)
- **HeartMath** - Fixed 6 bpm coherence
- **Manual** - Control with slider
- **Custom_5bpm** - Fixed 5 bpm practice

### Session Button:
- **"Start Session"** - Begins protocol + timer
- **"Stop Session"** - Stops early (can still export!)

### Breathing Rate Slider:
- **Manual mode:** Control breathing rate
- **Fisher_Lehrer mode:** Shows current auto-rate (updates automatically)

### Export Button:
- Click anytime after recording to export
- Or wait for auto-export at 15 minutes

---

## 📊 Real-Time Feedback

**Watch your HRV respond to breathing:**

1. **Follow the gold pacer** closely
2. **Blue circle** shows if you're matching it
3. **HRV (red line)** increases when you breathe at resonance!
4. **Aim for green zone** (>150ms)

**This real-time feedback helps you:**
- Stay synchronized with pacer
- See immediate HRV response
- Find what feels comfortable
- Build breathing skill

---

## 🎯 Tips for Best Results

### Before Starting:
- ✅ Polar H10 snug but comfortable
- ✅ Electrodes wet
- ✅ Sit upright, back supported
- ✅ Quiet environment
- ✅ Fasted (2+ hours after eating)

### During Session:
- ✅ **Stay very still** (accelerometer sensitive!)
- ✅ Breathe naturally, don't force
- ✅ Focus on smooth breathing
- ✅ Match the gold circle rhythm
- ✅ Relax - slower breathing is unusual at first!

### What to Ignore:
- ❌ Don't stress about perfect synchronization
- ❌ Don't hold your breath
- ❌ Don't breathe too deeply
- ❌ Don't watch the timer obsessively

---

## 🔬 Fisher & Lehrer Protocol Details

**What happens during 15 minutes:**

| Time | Breathing Rate | What's Happening |
|------|---------------|------------------|
| 0:00 | 6.75 bpm | Starting rate (8.9 sec/breath) |
| 3:45 | 6.00 bpm | Descending through range |
| 7:30 | 5.25 bpm | Middle of protocol |
| 11:15 | 4.50 bpm | Slower breathing |
| 15:00 | 4.25 bpm | Ending rate (14.1 sec/breath) |

**The algorithm finds where your HRV peaks!**

---

## 📁 After Export

### File Location:
```
exports/rf_test_Fisher-Lehrer_YYYYMMDD_HHMMSS.txt
```

### File Size:
~3-4 MB (15 minutes × 256 Hz)

### Contains:
- ✅ Real RR intervals (from Polar H10)
- ✅ **Real breathing data** (from accelerometer!)
- ✅ HRVisualizer-ready format

### Next Steps:
1. Transfer to Windows PC
2. Import to HRVisualizer
3. Your RF will be displayed!

---

## 🎨 Other Protocols

### HeartMath Coherence:
- Fixed 6 bpm breathing
- Good for daily practice
- Builds coherence skill

### Manual Mode:
- Use slider to set any rate
- Good for:
  - Testing different rates
  - Practicing at your known RF
  - Exploring comfort zones

### Custom 5 bpm:
- Fixed 5 bpm practice
- Common RF for many people
- Good default for training

---

## 💡 Pro Tips

**To maximize HRV response:**
1. **Breathe smoothly** - no jerky movements
2. **Equal inhale/exhale** - 1:1 ratio
3. **Use diaphragm** - belly breathing
4. **Stay relaxed** - shoulders down
5. **Match the pacer** - not ahead or behind

**Visual cues you're doing it right:**
- Blue breathing circle matches gold pacer ✓
- HRV line in green zone ✓
- Red HR dots show regular oscillation ✓
- Breathing feels natural (not forced) ✓

---

## ❓ Troubleshooting

### "Blue circle doesn't match gold pacer"
- **Normal!** Takes practice to sync
- Focus on the gold circle
- Don't stress about perfection

### "HRV stays in red/yellow zone"
- Keep breathing calmly
- Takes a few minutes to respond
- Will improve as you find your RF

### "Breathing feels uncomfortable"
- Totally normal at first!
- Slower breathing is unusual
- Gets easier with practice
- Don't force it

### "Graph looks jumpy/noisy"
- Stay more still (movement artifacts)
- Check H10 strap is snug
- Normal variation is okay

---

## 🎉 Success Criteria

**After your 15-minute session:**

✅ Completed full protocol
✅ File auto-exported
✅ Saw HRV respond to breathing
✅ Found comfortable breathing rhythm
✅ Ready to import to HRVisualizer

**Expected RF:** 4-7 bpm (yours will be somewhere in this range!)

---

## 🔄 Daily Practice Workflow

**After you know your RF (e.g., 5.2 bpm):**

1. **Open GUI**
2. **Connect** to Polar H10
3. **Select** "Manual" protocol
4. **Set slider** to your RF (5.2 bpm)
5. **Practice** 10-20 minutes daily
6. **Export** weekly to track progress
7. **Import** to HRVisualizer to see improvements!

---

**You now have a complete research-grade HRV biofeedback system!** 🎯

The real breathing data from the accelerometer + real-time visual feedback + automatic protocol + HRVisualizer export = everything you need for RF determination and daily practice!
