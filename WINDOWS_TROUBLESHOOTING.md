# HRVisualizer Hangs at "Determining breath pace"

## Problem

HRVisualizer gets stuck with a loading circle at the "Determining breath pace" step when processing files.

## Root Cause

The `SineWaveFit()` function (CodeFile.vb, line 821) has an infinite loop:

```vb
SearchPhase:
    ' ... iterative optimization ...
    If Corrections Then GoTo SearchPhase   ' Loops back if ANY corrections made
```

This iterative optimization algorithm can fail to converge on certain data, causing infinite loops.

---

## Solutions (Try in Order)

### ✅ Solution 1: Try Older Executable (QUICKEST FIX)

The x86/Release folder has multiple executables. Try them in this order:

**On Windows PC:**

1. **First try:** `HRVisualizer-orig.exe` (88 KB, Sept 2018)
   ```
   Location: Nexus\Nexus\bin\x86\Release\HRVisualizer-orig.exe
   ```
   - Older version, may have simpler/more robust fitting algorithm
   - Open this executable
   - Load your Alyssa.txt or test_output.txt file

2. **If that fails, try:** `HRVisualizer-orid2.exe` (89 KB, Jan 2020)
   ```
   Location: Nexus\Nexus\bin\x86\Release\HRVisualizer-orid2.exe
   ```

3. **If that fails, try:** Debug build
   ```
   Location: Nexus\Nexus\bin\Debug\Nexus.exe
   ```
   - Debug builds often have better error handling

---

### ✅ Solution 2: Fix the Source Code (PERMANENT FIX)

If all executables hang, we need to add a safety timeout to the sine fit algorithm.

**Required:** Visual Studio on Windows (any edition, including free Community edition)

#### Files to Modify

**File:** `Nexus/Nexus/CodeFile.vb`

**Line 647:** Add iteration counter to `SineWaveFit()` function

**Original code:**
```vb
Sub SineWaveFit()
    ' ... setup code ...

SearchPhase:
    Dim Corrections = 0

    ' ... Phase adjustment ...
    ' ... Frequency adjustment ...
    ' ... Offset adjustment ...
    ' ... Amplitude adjustment ...

    If Corrections Then GoTo SearchPhase    ' ← INFINITE LOOP RISK
End Sub
```

**Fixed code:**
```vb
Sub SineWaveFit()
    ' ... setup code ...

    Dim IterationCount = 0              ' ← ADD THIS
    Const MaxIterations = 100           ' ← ADD THIS (safety limit)

SearchPhase:
    Dim Corrections = 0

    IterationCount = IterationCount + 1 ' ← ADD THIS

    ' ... Phase adjustment ...
    ' ... Frequency adjustment ...
    ' ... Offset adjustment ...
    ' ... Amplitude adjustment ...

    ' ← REPLACE THIS LINE:
    ' If Corrections Then GoTo SearchPhase

    ' ← WITH THIS:
    If Corrections And IterationCount < MaxIterations Then
        Processing.Label25.Text = "Iter: " & IterationCount  ' Show progress
        Application.DoEvents()
        GoTo SearchPhase
    ElseIf IterationCount >= MaxIterations Then
        Console.WriteLine("Warning: Sine fit reached max iterations")
    End If
End Sub
```

#### Steps to Rebuild

1. **Open solution in Visual Studio:**
   ```
   Open: Nexus\Nexus.sln
   ```

2. **Edit CodeFile.vb:**
   - Find `Sub SineWaveFit()` (line 647)
   - Add the three changes marked above

3. **Rebuild:**
   - Menu: Build → Rebuild Solution
   - OR: Press Ctrl+Shift+B

4. **Test:**
   - Run: Nexus\Nexus\bin\Debug\Nexus.exe (or x86\Release\HRVisualizer.exe)
   - Load test file
   - Should complete within ~10-20 seconds now

---

### ✅ Solution 3: Alternative - Use Pre-compiled Working Version

If you don't have Visual Studio:

**Transfer the Debug build from Mac to Windows:**

The Debug build (compiled Feb 23, 2020) may work better than the Release build:

```bash
# On Mac:
Location: Nexus/Nexus/bin/Debug/Nexus.exe
Size: Should exist if previously compiled

# Copy to Windows and try running
```

---

## Understanding the Hang

### What the Algorithm Does

The `SineWaveFit()` function fits a sine wave to the breathing data to determine the exact resonance frequency. It:

1. **Initial coarse search:** Tests frequencies from 3.5-7.0 bpm (lines 689-707)
2. **Iterative refinement:** Repeatedly adjusts 4 parameters until convergence:
   - Phase (up to 200 steps per pass)
   - Frequency (up to 400 steps per pass)
   - DC Offset (up to 200 steps per pass)
   - Amplitude (up to 999 steps per pass)

3. **Convergence check:** If ANY corrections were made, loop back and try again

### Why It Hangs

**Convergence failure:** The algorithm may oscillate between states without reaching a stable solution:
- Example: Adjusting phase improves fit, then adjusting frequency undoes it, then phase needs adjustment again...
- Without a maximum iteration counter, it loops forever

### Visual Indicators

When stuck, you'll see:
- Four green squares (Label21-24) cycling through
- Counter (Label25) showing iteration numbers
- Loading circle spinning
- **No progress** - stays at this stage indefinitely

---

## Validation After Fix

Once you get HRVisualizer working:

### Test with Known Good Data

1. **Load original Alyssa.txt:**
   - Should complete in ~10-20 seconds
   - Expected RF: ~5.5 bpm (check against paper results)

2. **Load test_output.txt:**
   - Our generated test data
   - Expected RF: ~5.5 bpm (simulated)
   - If this works → Polar H10 pipeline validated!

3. **Load Alyssa_Synthetic_Respiration.txt:**
   - Compare RF with original Alyssa.txt
   - Difference < 0.3 bpm → synthetic respiration is accurate enough

---

## Quick Reference

| Executable | Location | Date | Size | Try Order |
|------------|----------|------|------|-----------|
| HRVisualizer-orig.exe | x86/Release | Sept 2018 | 88 KB | ⭐ Try 1st |
| HRVisualizer-orid2.exe | x86/Release | Jan 2020 | 89 KB | Try 2nd |
| Nexus.exe | Debug | Feb 2020 | - | Try 3rd |
| HRVisualizer.exe | x86/Release | Feb 2020 | 89 KB | Currently hanging |

---

## If Nothing Works

### Option A: Skip Sine Fit (Workaround)

You could modify the code to skip sine fitting and just report the peak location:

```vb
' In ProcessData() at line 124:
' Comment out: SineWaveFit()
' Add: ResonanceBpm = 5.5  ' Manual estimate from peak location
```

### Option B: Use Different Algorithm

Consider alternative RF detection methods:
- FFT-based frequency analysis
- Peak detection in HRV vs breathing rate plot
- Cross-correlation between HR and breathing

### Option C: Use Yudemon Instead

For immediate RF assessment while debugging HRVisualizer:
- Yudemon HRV app works with Polar H10
- Proprietary algorithm but well-validated
- Get results immediately while fixing HRVisualizer

---

## Expected Timeline

**Solution 1 (Try different executable):** 5 minutes
- Just run different .exe files

**Solution 2 (Fix source code):** 30-60 minutes
- Requires Visual Studio installation
- Edit one file, rebuild
- Most robust solution

**Solution 3 (Use Debug build):** 10 minutes
- Transfer and test

---

## Success Criteria

✅ HRVisualizer completes processing without hanging
✅ RF is detected and displayed (3-7 bpm range expected)
✅ Visual timeline shows clear waveforms
✅ Processing completes in <30 seconds for 15-min session

---

## Next Steps After Fix

Once HRVisualizer works:

1. ✅ **Validate test data:** Import test_output.txt → Should show RF ~5.5 bpm
2. ✅ **Test synthetic respiration:** Compare Alyssa.txt vs Alyssa_Synthetic_Respiration.txt
3. ✅ **Wait for Polar H10:** Record real session
4. ✅ **Convert and analyze:** Use polar_to_hrvisualizer.py → Import to HRVisualizer
5. ✅ **Determine your RF:** Get your personal resonance frequency!

---

**Bottom line:** Try the older HRVisualizer-orig.exe first - it may just work! If not, the code fix is straightforward and takes <30 minutes with Visual Studio.
