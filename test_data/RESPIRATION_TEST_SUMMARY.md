# Synthetic Respiration Impact Test

## Test Files

1. **Original:** `Nexus/Nexus/Alyssa-Short.txt`
   - Real NeXus-32 respiration hardware data
   - Piezo-electric strain belt

2. **Modified:** `Alyssa_Synthetic_Respiration.txt`
   - Same ECG data (unchanged)
   - Synthetic respiration (simulated from breath.cafe rates)

## Purpose

Determine how much RF detection accuracy we lose by using:
- Polar H10 (no respiration hardware)
- breath.cafe visual pacer (no amplitude measurement)
- Synthetic respiration waveform (generated from breathing rates)

## Hypothesis

Synthetic respiration may cause RF detection errors because:
1. **No real amplitude data**: We don't know how DEEP the person breathed
2. **Perfect sine wave**: Real breathing has irregularities
3. **Estimated amplitude**: We guessed ±15 units based on Alyssa's data

## How to Test

### On Windows PC:

1. Open HRVisualizer (Nexus.exe)

2. Import original file:
   - File → Open → Alyssa-Short.txt
   - Note detected RF: ________ bpm

3. Import modified file:
   - File → Open → Alyssa_Synthetic_Respiration.txt
   - Note detected RF: ________ bpm

4. Calculate difference:
   - Difference: |Original RF - Modified RF| = ________ bpm

## Expected Results

**If difference < 0.3 bpm:**
- ✅ Synthetic respiration is GOOD ENOUGH
- Polar H10 + breath.cafe approach will work
- No need for respiration hardware

**If difference 0.3-0.5 bpm:**
- ⚠️ Synthetic respiration has moderate impact
- Results still usable for personal RF assessment
- Consider respiration hardware for research-grade accuracy

**If difference > 0.5 bpm:**
- ❌ Synthetic respiration significantly affects accuracy
- Need real respiration hardware (piezo belt)
- Current approach not suitable for precise RF detection

## Results

*Fill this in after testing on Windows:*

- **Original RF:** ________ bpm
- **Modified RF:** ________ bpm
- **Difference:** ________ bpm
- **Conclusion:** _______________________
