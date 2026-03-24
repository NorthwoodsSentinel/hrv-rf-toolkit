# Test Data for Polar H10 to HRVisualizer Converter

**Generated:** 2026-02-13 11:32:02

## Overview

This directory contains synthetic test data simulating a real Polar H10 + breath.cafe session.

## Test Data Characteristics

### Session Parameters
- **Duration:** 15 minutes (900 seconds)
- **Start Time:** 2026-02-13 14:30:00
- **Breathing Protocol:** Sliding 6.75 → 4.25 bpm

### Simulated Physiology
- **Base Heart Rate:** 72 bpm
- **RSA Amplitude:** 15 bpm (peak-to-peak)
- **True RF (simulated):** 5.5 bpm
  - HRVisualizer should detect RF near this value!

### Respiratory Sinus Arrhythmia (RSA)
The synthetic data includes realistic RSA:
- HR increases during inhalation (vagal withdrawal)
- HR decreases during exhalation (vagal activation)
- RSA amplitude peaks when breathing near RF (5.5 bpm)
- RSA amplitude decreases when breathing far from RF

## Files

### 1. `test_rr_intervals.csv`
**Format:** EphorPolar CSV export format
```csv
Timestamp,RR_Interval
2026-02-13 14:30:00.000,820.5
2026-02-13 14:30:00.820,835.2
...
```

### 2. `test_rr_intervals.txt`
**Format:** Plain text (one RR interval per line in milliseconds)
```
820.5
835.2
810.3
...
```

### 3. `test_breath_schedule.csv`
**Format:** breath.cafe export format
```csv
Timestamp,Elapsed_Seconds,Breath_Rate_BPM,Event_Type
2026-02-13T14:30:00.000Z,0.000,6.75,START
2026-02-13T14:31:00.015Z,60.015,6.58,AUTO
...
```

## Testing the Converter

Run the converter with test data:

```bash
python polar_to_hrvisualizer.py \
    --rr test_data/test_rr_intervals.csv \
    --breath test_data/test_breath_schedule.csv \
    --output test_data/test_output.txt
```

## Expected Results

When importing `test_output.txt` into HRVisualizer:

### ✅ Success Criteria
- **RF Detection:** Should detect RF near 5.5 bpm (±0.3 bpm acceptable)
- **Max HRV Window:** Should occur around minute 7-8 (when breathing closest to 5.5 bpm)
- **Visual Display:** HR and respiration should show clear phase relationship

### 📊 Why 5.5 bpm?
The test data is generated with maximum RSA amplitude at 5.5 bpm.
This simulates a person whose true resonance frequency is 5.5 bpm.

As breathing rate passes through 5.5 bpm during the sliding protocol:
- Minute 0-7: Approaching RF (increasing HRV amplitude)
- Minute 7-8: At or near RF (maximum HRV amplitude) ← Peak detected here
- Minute 8-15: Moving away from RF (decreasing HRV amplitude)

### 🔍 Validation Checks

1. **Open HRVisualizer display:**
   - Look for 1-minute window marked as max HRV
   - Should be around timestamp 7-8 minutes into session

2. **Check detected RF:**
   - Should report RF ≈ 5.5 bpm
   - Within 0.3-0.5 bpm is excellent
   - Within 0.5-1.0 bpm is acceptable

3. **Visual inspection:**
   - HR oscillations should be largest in middle of session
   - HR and respiration should be in phase (HR↑ on inhale)

## Troubleshooting

### RF detected is way off (>1 bpm error)
- Likely respiration waveform generation issue
- Check synthetic respiration amplitude/frequency
- Verify breath schedule timestamps align with RR timestamps

### No clear HRV peak
- Check if session duration is sufficient
- Verify RSA amplitude is realistic (10-20 bpm typical)
- Ensure breathing rate passes through RF

### Phase relationship inverted
- Timing synchronization error
- RR intervals and breath schedule may be offset
- Check timestamp alignment in converter

## Next Steps

Once test data conversion succeeds:
1. ✅ Converter works end-to-end
2. ✅ HRVisualizer can import the file
3. ✅ RF detection produces reasonable results
4. → Ready for real Polar H10 data!

## Generating New Test Data

To regenerate with different parameters:

```bash
python generate_test_data.py \
    --output test_data/ \
    --duration 15 \
    --base-hr 72 \
    --true-rf 5.5
```

See `python generate_test_data.py --help` for all options.
