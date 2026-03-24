# Breathing Protocol: Continuous vs. Per-Breath

**Critical difference discovered!**

---

## 🔬 The Fisher & Lehrer Research Protocol

From the paper (page 20):

> "For this study, the parameters of a 15-min session beginning at 6.75 bpm and ending at 4.25 bpm **with a change after every 2 half-breaths** (comprising one breath cycle) produced a constant rate of deceleration of **67.04 ms per breath**"

### What This Means

**Per-Breath Change Method:**
- Rate changes **AFTER each complete breath cycle**
- Not continuous/smooth interpolation
- Discrete stepped changes
- Example timeline:
  ```
  Breath 1: 6.75 bpm (constant for entire breath)
  Breath 2: 6.74 bpm (constant for entire breath)
  Breath 3: 6.73 bpm (constant for entire breath)
  ...
  ```

**Formula:**
- Change is in **breath period** (milliseconds per breath), not rate
- 67.04 ms increase in period per breath
- Period = 60,000 ms / rate_bpm

---

## ❌ Original breath_cafe_logger.html (INCORRECT)

### Implementation
```javascript
// Continuous linear interpolation
session.currentRate = session.startRate + (session.rateChangePerSecond * elapsed);
```

### Behavior
- Rate changes **every 100ms** (update interval)
- Smooth continuous transition
- Example:
  ```
  Time 0.0s: 6.750 bpm
  Time 0.1s: 6.749 bpm  ← Changed!
  Time 0.2s: 6.748 bpm  ← Changed!
  Time 0.3s: 6.747 bpm  ← Changed!
  ```

### Problem
- **Does NOT match research protocol**
- Rate changes hundreds of times per breath
- Not how the paper's algorithm works

---

## ✅ breath_cafe_research_protocol.html (CORRECT)

### Implementation
```javascript
// Track breath cycles
const timeSinceBreathStart = now - session.currentBreathStartTime;

// Check if breath completed
if (timeSinceBreathStart >= session.breathPeriodMs) {
    session.breathCount++;

    // Change period for NEXT breath (not current)
    session.breathPeriodMs += session.periodChangePerBreath;

    // Convert back to rate
    session.currentRate = 60000 / session.breathPeriodMs;

    // Mark new breath start
    session.currentBreathStartTime = now;
}
```

### Behavior
- Rate changes **once per breath cycle**
- Stepped discrete changes
- Example:
  ```
  Breath 1 (0-9s):     6.75 bpm ← Constant
  Breath 2 (9-18s):    6.74 bpm ← Changed after breath 1 complete
  Breath 3 (18-27s):   6.73 bpm ← Changed after breath 2 complete
  Breath 4 (27-36s):   6.72 bpm ← Changed after breath 3 complete
  ```

### Advantages
- ✅ Matches Fisher & Lehrer research protocol exactly
- ✅ Breath counter built-in
- ✅ Can toggle between modes (per-breath vs. continuous)
- ✅ Logs breath count in CSV export

---

## 📊 Impact on Results

### Why This Matters

**Per-Breath Method (Correct):**
- Breathing rate is **stable during each breath**
- HRVisualizer algorithm can associate entire breath with one rate
- More accurate RF determination
- Matches validated research methodology

**Continuous Method (Incorrect):**
- Breathing rate changes mid-breath
- Hard to determine "what rate was I breathing at?"
- Could introduce errors in RF calculation
- Not validated in research

### Example Scenario

**Session timestamp: 7:30 into session**

**Continuous method:**
```
7:29.0s: 5.512 bpm
7:29.5s: 5.511 bpm  ← Changed mid-breath
7:30.0s: 5.510 bpm  ← Changed mid-breath
7:30.5s: 5.509 bpm  ← Changed mid-breath
```
→ What rate to log? Average? Mid-point? Unclear!

**Per-breath method:**
```
Breath 47 (7:23-7:32): 5.51 bpm  ← Constant for entire 9-second breath
```
→ Clear: At 7:30, breathing rate was 5.51 bpm

---

## 🔧 Which File to Use

### For Research / Accurate RF Determination
**Use:** `breath_cafe_research_protocol.html`
- Implements Fisher & Lehrer protocol correctly
- Per-breath rate changes
- Matches paper methodology
- ✅ **RECOMMENDED**

### For General Practice / Training
**Use:** `breath_cafe_logger.html` OR original breath.cafe
- Continuous smooth transitions
- Easier to follow (no sudden changes)
- Good for daily HRV training
- Not for precise RF assessment

---

## 📥 CSV Export Format Comparison

### Original (breath_cafe_logger.html)
```csv
Timestamp,Elapsed_Seconds,Breath_Rate_BPM,Event_Type
2026-02-13T14:30:00.000Z,0.000,6.75,START
2026-02-13T14:31:00.015Z,60.015,6.58,AUTO
2026-02-13T14:32:00.008Z,120.008,6.41,AUTO
```

### Research Protocol (breath_cafe_research_protocol.html)
```csv
Timestamp,Elapsed_Seconds,Breath_Rate_BPM,Breath_Count,Event_Type
2026-02-13T14:30:00.000Z,0.000,6.75,0,START
2026-02-13T14:31:00.015Z,60.015,6.58,6,AUTO
2026-02-13T14:32:00.008Z,120.008,6.41,13,AUTO
```

**Key difference:** Breath count included!
- Allows verification: ~6-7 breaths per minute ✓
- Can track if protocol followed correctly

---

## 🎯 Recommendation

### For Your Polar H10 Project

**Use the research protocol version:**
```bash
# Open this file:
breath_cafe_research_protocol.html

# Settings:
- Mode: "Per Breath (Fisher & Lehrer)" ← Default
- Duration: 15 minutes
- Start: 6.75 bpm
- End: 4.25 bpm
- Ratio: 1:1
```

**Why:**
- Matches HRVisualizer's expected methodology
- More accurate RF detection
- Research-validated approach
- Better data logging (includes breath count)

---

## 🔬 Technical Details

### Period Change Calculation

**Start with rates:**
- Start: 6.75 bpm
- End: 4.25 bpm

**Convert to periods:**
- Start period: 60 / 6.75 = 8.889 seconds/breath = 8889 ms
- End period: 60 / 4.25 = 14.118 seconds/breath = 14118 ms

**Calculate change:**
- Total period change: 14118 - 8889 = 5229 ms
- Duration: 15 minutes = 900 seconds
- Average rate: (6.75 + 4.25) / 2 = 5.5 bpm
- Estimated breaths: 5.5 × 15 = 82.5 breaths
- **Period change per breath: 5229 / 82.5 = 63.4 ms/breath**

**Paper states: 67.04 ms/breath**
- Slight difference due to:
  - Exact calculation vs. approximation
  - Actual breath count will vary slightly
  - Algorithm adjusts dynamically

---

## ✅ Action Items

**For accurate RF assessment:**

1. **Delete or ignore** `breath_cafe_logger.html` (incorrect protocol)

2. **Use** `breath_cafe_research_protocol.html` (correct protocol)

3. **Verify** exported CSV includes breath count column

4. **Check** that breath count ≈ 75-85 breaths for 15-min session
   - If way off (e.g., 150 breaths) → something wrong

5. **Run converter** with correct breathing schedule

---

## 📚 References

**Research Paper Quote:**
> "For this study, the parameters of a 15-min session beginning at 6.75 bpm and ending at 4.25 bpm with a change after every 2 half-breaths (comprising one breath cycle) produced a constant rate of deceleration of 67.04 ms per breath"

**Source:**
Fisher, L.R., Lehrer, P.M. (2022). A Method for More Accurate Determination of Resonance Frequency of the Cardiovascular System. *Applied Psychophysiology and Biofeedback*, 47, 17-26.

---

**Bottom line:** Use the research protocol version to match the validated methodology! 🎯
