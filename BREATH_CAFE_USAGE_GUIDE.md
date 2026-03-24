# breath.cafe Usage Guide for Polar H10 Testing

**Goal:** Use breath.cafe as breathing pacer while maintaining perfect timing sync with Polar H10 RR data

---

## 🌐 What is breath.cafe?

**Official Site:** https://breath.cafe/
**Created by:** Lorrie R. Fisher (Fisher Behavior) - same author as HRVisualizer
**License:** Open source (view source code: right-click → View Source)

**Features:**
- ✅ Visual breathing pacer with triangular waveform
- ✅ Adjustable breathing rate (bpm)
- ✅ Smooth rate transitions (sliding protocol)
- ✅ 1:1 inhale/exhale ratio
- ✅ Runs in any web browser (no install)
- ❌ Does NOT record or export data (it's just a pacer)

**Key Insight:** breath.cafe shows you *when* to breathe, but you need to log *what* rate and *when* you changed it.

---

## 🎯 Three Ways to Use breath.cafe

### Option 1: Manual Logging (Simplest)
### Option 2: Screen Recording (Most Practical)
### Option 3: Modified Version with Auto-Logging (Most Accurate)

---

## 📝 Option 1: Manual Logging with breath.cafe

### Setup

**Equipment:**
- Computer/tablet: breath.cafe open in browser
- Phone #1: Polar H10 recording app (ECG Recorder/EphorPolar)
- Phone #2: Clock display (time.is) + notepad for logging
- Printout: Timing log template (below)

### Timing Log Template

**Print this and fill out with pen during test:**

```
POLAR H10 + BREATH.CAFE TIMING LOG
Date: __________  Session: __________

Start Time (exact): ___:___:___
Polar Recording Started: ___:___:___

Breath Rate Changes:
┌──────────────┬────────────┬───────────┬────────────────┐
│  Clock Time  │  Elapsed   │  Rate Set │     Notes      │
│   (HH:MM:SS) │   (min)    │   (bpm)   │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │    0:00    │   6.75    │ START          │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │    1:00    │   6.58    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │    2:00    │   6.41    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │    3:00    │   6.25    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │    4:00    │   6.08    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │    5:00    │   5.92    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │    6:00    │   5.75    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │    7:00    │   5.58    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │    8:00    │   5.42    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │    9:00    │   5.25    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │   10:00    │   5.08    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │   11:00    │   4.92    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │   12:00    │   4.75    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │   13:00    │   4.58    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │   14:00    │   4.42    │                │
├──────────────┼────────────┼───────────┼────────────────┤
│ ___:___:___  │   15:00    │   4.25    │ END            │
└──────────────┴────────────┴───────────┴────────────────┘

Stop Time: ___:___:___
Polar Recording Stopped: ___:___:___

Notes/Issues:
_________________________________________________
_________________________________________________
```

### Step-by-Step Protocol

**Pre-Session (5 minutes before):**

1. **Set up devices:**
   ```
   Left side:   Computer with breath.cafe
   Center:      You sitting comfortably
   Right side:  Phone with time.is + printed log sheet
   On chest:    Polar H10 strap (snug fit)
   ```

2. **Configure breath.cafe:**
   - Open https://breath.cafe/
   - Initial rate: 6.75 bpm
   - Verify pacer is visible and moving smoothly
   - Practice following for 30 seconds

3. **Start Polar recording:**
   - Open ECG Recorder or EphorPolar
   - Verify H10 connection (green/connected)
   - Position finger on "Start" button
   - Don't press yet!

**Session Start (T=0):**

```
Watch clock on phone (time.is)
When second hand hits :00 (e.g., 14:30:00):

1. Press START on Polar app
2. Write exact time on log sheet
3. Say aloud: "Starting NOW at [time]"
4. Immediately begin breathing with pacer
```

**During Session (every 1 minute):**

```
breath.cafe sliding protocol (15 minutes):
- Automatically decreases from 6.75 → 4.25 bpm
- Rate changes smoothly, not in steps

YOUR JOB:
Every 1 minute, note the current rate and time:
  - Glance at clock: "14:31:00"
  - Look at breath.cafe: "6.58 bpm"
  - Write both on log sheet
  - Continue breathing (don't lose rhythm!)

Pro tip: Do this during EXHALATION (easier)
```

**Session End (T=15 min):**

```
1. Stop Polar recording
2. Write exact stop time
3. Save Polar export with matching filename
   Example: RR_20260213_143000.csv
            (matching start time)
```

**Post-Session:**

4. Type up handwritten log into CSV:

**File:** `breath_schedule_20260213_143000.csv`
```csv
Timestamp,Elapsed_Seconds,Breath_Rate_BPM,Notes
2026-02-13 14:30:00,0,6.75,Start
2026-02-13 14:31:00,60,6.58,
2026-02-13 14:32:00,120,6.41,
2026-02-13 14:33:00,180,6.25,
2026-02-13 14:34:00,240,6.08,
2026-02-13 14:35:00,300,5.92,
2026-02-13 14:36:00,360,5.75,
2026-02-13 14:37:00,420,5.58,
2026-02-13 14:38:00,480,5.42,
2026-02-13 14:39:00,540,5.25,
2026-02-13 14:40:00,600,5.08,
2026-02-13 14:41:00,660,4.92,
2026-02-13 14:42:00,720,4.75,
2026-02-13 14:43:00,780,4.58,
2026-02-13 14:44:00,840,4.42,
2026-02-13 14:45:00,900,4.25,End
```

**Now you have:**
- ✅ Polar RR intervals with timestamps
- ✅ Breathing schedule with timestamps
- ✅ Both aligned to same time reference
- ✅ Ready for Python converter script!

---

## 📹 Option 2: Screen Recording (Recommended!)

### Why This is Better

**Advantages:**
- Don't need to write during breathing
- Can verify timing later if needed
- Visual proof of what happened
- Easier to stay focused on breathing

### Setup

**Single Screen Method:**

```
Computer/Tablet Screen Layout:
┌─────────────────────────────────────────┐
│  breath.cafe           time.is          │
│  (left 2/3)            (top right)      │
│                                         │
│  [Pacer animation]     14:30:15         │
│  Rate: 6.58 bpm        Feb 13, 2026     │
│                                         │
│                        Notepad          │
│                        (bottom right)   │
│                        Currently:       │
│                        6.58 bpm         │
└─────────────────────────────────────────┘
         ↓
   Screen Recording Active
```

**Multi-Screen Method:**

```
Screen 1 (laptop):      Screen 2 (phone):
┌──────────────────┐    ┌──────────────┐
│  breath.cafe     │    │ Polar App    │
│                  │    │ Recording... │
│  [Pacer]         │    │              │
│  6.58 bpm        │    │ HR: 72 bpm   │
│                  │    │ Time: 5:23   │
└──────────────────┘    └──────────────┘
         ↓                      ↑
   Record this          Don't need to record
```

### Step-by-Step

**1. Prepare Screen Layout:**

Open in browser:
- **Tab 1:** https://breath.cafe/ (full screen or left side)
- **Tab 2:** https://time.is/ (small window, top right corner)
- **Optional:** Notepad/TextEdit window (for manual rate notes)

**2. Start Screen Recording:**

**macOS:**
```
CMD + Shift + 5
→ Select "Record Entire Screen" or "Record Selected Window"
→ Click "Record"
→ Small recording icon appears in menu bar
```

**Windows:**
```
Xbox Game Bar: Win + G
→ Click camera icon "Capture"
→ Click record button
```

**Chromebook:**
```
Shift + Ctrl + Show Windows (⊞)
→ Select screen recording
```

**iPad/Tablet:**
```
Control Center → Screen Recording button
(Add to Control Center in Settings if not visible)
```

**3. Configure breath.cafe:**

Click on the page, look for controls (usually top or bottom):
- **Duration:** 15 minutes
- **Start Rate:** 6.75 bpm
- **End Rate:** 4.25 bpm
- **Ratio:** 1:1 (inhale:exhale)

*(Note: breath.cafe may auto-calculate rate change per breath)*

**4. Synchronized Start:**

```
Watch time.is clock
At exact minute boundary (e.g., 14:30:00):

  1. Start Polar recording (on phone)
  2. Click "Start" on breath.cafe
  3. Say aloud: "Starting at 14:30:00"
     (audio captured in screen recording if enabled)
  4. Begin breathing
```

**5. During Session:**

- Just breathe and follow the pacer!
- No need to write anything
- Screen recording captures:
  - breath.cafe rate display
  - time.is clock in corner
  - Any manual notes you type

**Optional:** Type rate changes in notepad window:
```
[You type while breathing]
14:31 - 6.58
14:32 - 6.41
14:33 - 6.25
...
```

**6. Session End:**

```
At 15 minutes:
  1. breath.cafe pacer completes (shows 4.25 bpm)
  2. Stop Polar recording
  3. Stop screen recording
  4. Say aloud: "Ending at 14:45:00"
```

**7. Post-Processing:**

Watch the screen recording:
- Open video in player (VLC, QuickTime, etc.)
- Step through at key moments (every minute)
- Note what breath.cafe rate shows at each clock time
- Create CSV from video evidence

**Example workflow:**
```
Open screen_recording.mov
Scrub to timestamp 14:31:00 (on time.is display)
Pause
Look at breath.cafe: shows 6.58 bpm
Write in CSV: 2026-02-13 14:31:00,60,6.58

Repeat for each minute mark
```

**Tools to help:**
- **VLC Media Player:** Frame-by-frame stepping (E key)
- **QuickTime:** Arrow keys for frame stepping
- **Screenshot:** Capture each minute for reference

---

## 🔧 Option 3: Modified breath.cafe with Auto-Logging

### The Ultimate Solution

**What:** Modified version of breath.cafe that automatically logs timing data
**Complexity:** Medium (need to edit HTML/JavaScript)
**Benefit:** Perfect millisecond-precision timestamps, zero manual effort

### Download and Modify breath.cafe

**Step 1: Download Source Code**

```bash
# Open browser to https://breath.cafe/
# Right-click anywhere on page
# Select "View Page Source" or "View Source"
# Browser opens new tab with HTML/JavaScript code
# File → Save Page As → "breath_pacer_original.html"
```

**Step 2: Create Modified Version**

I'll create the modified version for you:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>breath.cafe - Modified with Data Logging</title>
    <style>
        /* [Include original breath.cafe styles here] */
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #1a1a2e;
            color: #eee;
        }
        #pacer-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        #controls {
            margin-bottom: 20px;
            padding: 20px;
            background: #16213e;
            border-radius: 8px;
        }
        #pacer {
            width: 100%;
            height: 200px;
            background: #0f3460;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
        }
        #log-display {
            margin-top: 20px;
            padding: 10px;
            background: #16213e;
            border-radius: 8px;
            max-height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .log-entry {
            color: #4ecca3;
            margin: 2px 0;
        }
        button {
            background: #4ecca3;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
            color: #1a1a2e;
            font-weight: bold;
        }
        button:hover {
            background: #45b393;
        }
        input, select {
            padding: 8px;
            margin: 5px;
            border-radius: 5px;
            border: 1px solid #4ecca3;
            background: #0f3460;
            color: #eee;
        }
        #current-rate {
            font-size: 24px;
            font-weight: bold;
            color: #4ecca3;
            text-align: center;
            margin: 10px 0;
        }
        #timer {
            font-size: 18px;
            text-align: center;
            color: #eee;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div id="pacer-container">
        <h1>breath.cafe - Data Logging Edition</h1>
        <p>Enhanced version with automatic timestamp logging for HRV research</p>

        <div id="controls">
            <h3>Session Settings</h3>
            <label>Duration (minutes): <input type="number" id="duration" value="15" min="1" max="60"></label><br>
            <label>Start Rate (bpm): <input type="number" id="start-rate" value="6.75" step="0.25" min="3" max="10"></label><br>
            <label>End Rate (bpm): <input type="number" id="end-rate" value="4.25" step="0.25" min="3" max="10"></label><br>
            <label>Inhale:Exhale Ratio:
                <select id="ratio">
                    <option value="1:1" selected>1:1</option>
                    <option value="1:2">1:2</option>
                </select>
            </label><br>
            <label>Log Interval (seconds): <input type="number" id="log-interval" value="60" min="1" max="300"></label>
            <small>(How often to log breathing rate)</small><br><br>

            <button id="start-btn" onclick="startSession()">Start Session</button>
            <button id="stop-btn" onclick="stopSession()" disabled>Stop Session</button>
            <button id="export-btn" onclick="exportLog()">Export CSV</button>
        </div>

        <div id="timer">Ready to start...</div>
        <div id="current-rate">-- bpm</div>

        <div id="pacer">
            <canvas id="pacer-canvas"></canvas>
        </div>

        <div id="log-display">
            <div class="log-entry">Log will appear here during session...</div>
        </div>
    </div>

    <script>
        // Session state
        let session = {
            active: false,
            startTime: null,
            startRate: 6.75,
            endRate: 4.25,
            duration: 900, // seconds
            currentRate: 6.75,
            logInterval: 60, // seconds
            breathLog: [],
            intervalId: null,
            logIntervalId: null
        };

        // Initialize
        function startSession() {
            // Get settings
            session.duration = parseInt(document.getElementById('duration').value) * 60;
            session.startRate = parseFloat(document.getElementById('start-rate').value);
            session.endRate = parseFloat(document.getElementById('end-rate').value);
            session.currentRate = session.startRate;
            session.logInterval = parseInt(document.getElementById('log-interval').value);

            // Calculate rate change per second (linear interpolation)
            session.rateChangePerSecond = (session.endRate - session.startRate) / session.duration;

            // Mark session start
            session.startTime = new Date();
            session.active = true;
            session.breathLog = [];

            // Log start event
            logBreathRate('START');

            // Update UI
            document.getElementById('start-btn').disabled = true;
            document.getElementById('stop-btn').disabled = false;
            document.getElementById('log-display').innerHTML = '';
            addLogEntry(`Session started at ${session.startTime.toISOString()}`);
            addLogEntry(`Duration: ${session.duration}s, Rate: ${session.startRate} → ${session.endRate} bpm`);

            // Start update loops
            session.intervalId = setInterval(updateSession, 100); // Update 10x per second
            session.logIntervalId = setInterval(() => logBreathRate('AUTO'), session.logInterval * 1000);

            // Start pacer animation
            startPacerAnimation();
        }

        function stopSession() {
            if (!session.active) return;

            // Log end event
            logBreathRate('END');

            // Stop loops
            clearInterval(session.intervalId);
            clearInterval(session.logIntervalId);

            // Mark session end
            session.active = false;

            // Update UI
            document.getElementById('start-btn').disabled = false;
            document.getElementById('stop-btn').disabled = true;
            addLogEntry(`Session ended at ${new Date().toISOString()}`);
            addLogEntry(`Total duration: ${getElapsedSeconds().toFixed(1)}s`);
            addLogEntry('Click "Export CSV" to download data');

            // Stop animation
            stopPacerAnimation();
        }

        function updateSession() {
            if (!session.active) return;

            const elapsed = getElapsedSeconds();

            // Update current rate (linear interpolation)
            session.currentRate = session.startRate + (session.rateChangePerSecond * elapsed);

            // Clamp to end rate if past duration
            if (elapsed >= session.duration) {
                session.currentRate = session.endRate;
                stopSession();
                return;
            }

            // Update display
            document.getElementById('current-rate').textContent = session.currentRate.toFixed(2) + ' bpm';
            document.getElementById('timer').textContent =
                `${formatTime(elapsed)} / ${formatTime(session.duration)}`;
        }

        function logBreathRate(eventType = 'AUTO') {
            const now = new Date();
            const elapsed = getElapsedSeconds();

            const entry = {
                timestamp: now.toISOString(),
                elapsed: elapsed.toFixed(3),
                breathRate: session.currentRate.toFixed(2),
                eventType: eventType
            };

            session.breathLog.push(entry);

            // Display in log window
            addLogEntry(`[${formatTime(elapsed)}] ${entry.breathRate} bpm (${eventType})`);
        }

        function addLogEntry(text) {
            const logDiv = document.getElementById('log-display');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.textContent = text;
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight; // Auto-scroll to bottom
        }

        function exportLog() {
            if (session.breathLog.length === 0) {
                alert('No data to export. Run a session first!');
                return;
            }

            // Generate CSV
            let csv = 'Timestamp,Elapsed_Seconds,Breath_Rate_BPM,Event_Type\n';
            session.breathLog.forEach(entry => {
                csv += `${entry.timestamp},${entry.elapsed},${entry.breathRate},${entry.eventType}\n`;
            });

            // Create download
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            // Filename with timestamp
            const filename = `breath_schedule_${formatDateForFilename(session.startTime)}.csv`;
            a.download = filename;

            a.click();
            URL.revokeObjectURL(url);

            addLogEntry(`Exported to: ${filename}`);
        }

        function getElapsedSeconds() {
            if (!session.startTime) return 0;
            return (new Date() - session.startTime) / 1000;
        }

        function formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        }

        function formatDateForFilename(date) {
            const year = date.getFullYear();
            const month = (date.getMonth() + 1).toString().padStart(2, '0');
            const day = date.getDate().toString().padStart(2, '0');
            const hour = date.getHours().toString().padStart(2, '0');
            const min = date.getMinutes().toString().padStart(2, '0');
            const sec = date.getSeconds().toString().padStart(2, '0');
            return `${year}${month}${day}_${hour}${min}${sec}`;
        }

        // Pacer animation (simplified)
        let animationFrameId = null;
        const canvas = document.getElementById('pacer-canvas');
        const ctx = canvas ? canvas.getContext('2d') : null;

        function startPacerAnimation() {
            if (!canvas) return;

            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;

            animatePacer();
        }

        function stopPacerAnimation() {
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
            }
        }

        function animatePacer() {
            if (!session.active || !ctx) return;

            const elapsed = getElapsedSeconds();
            const breathPeriod = 60 / session.currentRate; // seconds per breath
            const phase = (elapsed % breathPeriod) / breathPeriod; // 0 to 1

            // Clear canvas
            ctx.fillStyle = '#0f3460';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw breathing indicator (simple circle that grows/shrinks)
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const minRadius = 20;
            const maxRadius = 80;

            // Sine wave for smooth breathing (0=exhale, 0.5=inhale, 1=exhale)
            const radius = minRadius + (maxRadius - minRadius) * (0.5 + 0.5 * Math.sin(phase * 2 * Math.PI));

            ctx.fillStyle = phase < 0.5 ? '#4ecca3' : '#45b393'; // Inhale vs exhale color
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            ctx.fill();

            // Text
            ctx.fillStyle = '#1a1a2e';
            ctx.font = 'bold 20px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(phase < 0.5 ? 'INHALE' : 'EXHALE', centerX, centerY);

            animationFrameId = requestAnimationFrame(animatePacer);
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !session.active) {
                e.preventDefault();
                startSession();
            } else if (e.code === 'Escape' && session.active) {
                e.preventDefault();
                stopSession();
            } else if (e.code === 'KeyL' && session.active) {
                e.preventDefault();
                logBreathRate('MANUAL');
            }
        });

        // Initialize canvas
        window.addEventListener('resize', () => {
            if (canvas) {
                canvas.width = canvas.offsetWidth;
                canvas.height = canvas.offsetHeight;
            }
        });
    </script>
</body>
</html>
```

**Step 3: Save and Use**

Save the above code as: `breath_cafe_logger.html`

**Step 4: How to Use**

```
1. Double-click breath_cafe_logger.html
   → Opens in your browser

2. Configure settings:
   - Duration: 15 minutes
   - Start Rate: 6.75 bpm
   - End Rate: 4.25 bpm
   - Log Interval: 60 seconds (logs rate every minute)

3. Click "Start Session" (or press Spacebar)
   → Automatic logging begins!

4. During session:
   - Follow the visual pacer (growing/shrinking circle)
   - Automatic logs every 60 seconds
   - Press 'L' key to manually log at any time

5. At end (or press Escape to stop early):
   - Click "Export CSV"
   - File downloads automatically
   - Filename: breath_schedule_YYYYMMDD_HHMMSS.csv
```

**Output CSV Example:**

```csv
Timestamp,Elapsed_Seconds,Breath_Rate_BPM,Event_Type
2026-02-13T14:30:00.000Z,0.000,6.75,START
2026-02-13T14:31:00.015Z,60.015,6.58,AUTO
2026-02-13T14:32:00.008Z,120.008,6.41,AUTO
2026-02-13T14:33:00.012Z,180.012,6.25,AUTO
2026-02-13T14:34:00.019Z,240.019,6.08,AUTO
2026-02-13T14:35:00.005Z,300.005,5.92,AUTO
2026-02-13T14:36:00.011Z,360.011,5.75,AUTO
2026-02-13T14:37:00.014Z,420.014,5.58,AUTO
2026-02-13T14:38:00.003Z,480.003,5.42,AUTO
2026-02-13T14:39:00.018Z,540.018,5.25,AUTO
2026-02-13T14:40:00.009Z,600.009,5.08,AUTO
2026-02-13T14:41:00.016Z,660.016,4.92,AUTO
2026-02-13T14:42:00.007Z,720.007,4.75,AUTO
2026-02-13T14:43:00.013Z,780.013,4.58,AUTO
2026-02-13T14:44:00.010Z,840.010,4.42,AUTO
2026-02-13T14:45:00.004Z,900.004,4.25,END
```

**Perfect millisecond-precision timestamps!**

---

## 🎯 Which Option Should You Use?

| Option | Effort | Accuracy | Best For |
|--------|--------|----------|----------|
| **1. Manual Logging** | High (writing during test) | ±10 sec | First quick test |
| **2. Screen Recording** | Low (set and forget) | ±2 sec | Most practical |
| **3. Modified breath.cafe** | Medium (one-time setup) | ±0.01 sec | Repeated testing |

**My Recommendation:**

### For Your First Test:
→ **Option 2: Screen Recording**
- Easy setup (5 minutes)
- Focus on breathing, not logging
- Can verify timing later
- Good enough accuracy (±2-5 seconds)

### After Proof-of-Concept Works:
→ **Option 3: Modified breath.cafe**
- One-time setup (save the HTML file)
- Perfect accuracy forever
- Automatic CSV export
- Professional-grade timing

---

## 📋 Complete Testing Protocol with breath.cafe

### Equipment Checklist

```
□ Polar H10 chest strap (charged, on chest)
□ Phone #1: Polar recording app (ECG Recorder/EphorPolar)
□ Computer: breath.cafe (or modified version)
□ Phone #2 or tablet: time.is open
□ If Option 1: Printed timing log + pen
□ If Option 2: Screen recording software ready
□ If Option 3: breath_cafe_logger.html file saved locally
```

### Step-by-Step

**15 Minutes Before:**
1. Fit Polar H10 (wet electrodes slightly, snug fit)
2. Verify Bluetooth connection
3. Open breath.cafe (or modified version)
4. Set up screen recording (if Option 2)
5. Have clock visible (time.is)

**5 Minutes Before:**
6. Practice breathing with pacer (30 seconds)
7. Position pen and log sheet (if Option 1)
8. Get comfortable in chair
9. Turn off phone notifications
10. Close unnecessary apps

**At Start Time (e.g., 14:30:00 exactly):**
11. Start Polar recording
12. Start breath.cafe / press Start Session
13. Start screen recording (if Option 2)
14. Note exact start time
15. **BEGIN BREATHING**

**During 15-Minute Session:**
16. Follow visual pacer smoothly
17. If Option 1: Write times every minute
18. If Option 2/3: Just breathe!
19. Stay relaxed, don't force breaths

**At End (15:00 elapsed):**
20. Stop Polar recording
21. breath.cafe completes / Stop Session
22. Stop screen recording (if Option 2)
23. Export CSV (if Option 3)
24. Note exact end time

**Post-Session:**
25. Export Polar RR data
26. Create/verify breathing schedule CSV
27. Match filenames (same timestamp)
28. Ready for Python converter!

---

## 💾 File Naming Convention

**Keep everything matched by timestamp:**

```
Session from Feb 13, 2026, 14:30:00

Polar Export:
  RR_20260213_143000.csv

Breathing Schedule:
  breath_schedule_20260213_143000.csv

Screen Recording (if used):
  screen_20260213_143000.mov

Final Output (after conversion):
  hrv_session_20260213_143000.txt  (HRVisualizer format)
```

**This makes it easy to match files later!**

---

## 🔍 Troubleshooting breath.cafe

### Issue: Can't Adjust Rate

**Problem:** breath.cafe uses automatic sliding rate
**Solution:** Modified version (Option 3) lets you set start/end rates

### Issue: Pacer Jumps/Stutters

**Problem:** Browser performance or background tabs
**Solution:**
- Close other browser tabs
- Use Chrome/Firefox (better performance than Safari)
- Don't screen record at 4K (use 1080p)

### Issue: Lost Track of What Rate I Was At

**Problem:** Didn't log during session
**Solution:**
- Use Option 3 (automatic logging)
- OR use Option 2 (screen recording captures rate display)

### Issue: Started Polar and breath.cafe at Different Times

**Problem:** Not synchronized
**Solution:**
- Note BOTH start times
- Calculate offset: `breath_cafe_start - polar_start`
- Adjust timestamps in CSV: Add offset to all breath.cafe times

### Issue: Don't Know Exact breath.cafe Rate at Each Timestamp

**Problem:** Sliding protocol = continuous change
**Solution:** Calculate it!

```python
# breath.cafe sliding formula
start_rate = 6.75  # bpm
end_rate = 4.25    # bpm
duration = 900     # seconds (15 min)

rate_change_per_second = (end_rate - start_rate) / duration
# = (4.25 - 6.75) / 900 = -0.00278 bpm/sec

# At any time t:
rate_at_t = start_rate + (rate_change_per_second * t)

# Example: At 5 minutes (300 sec)
rate_at_300 = 6.75 + (-0.00278 * 300)
            = 6.75 - 0.834
            = 5.916 bpm
```

**Use this formula if you only know start/end times!**

---

## ✅ Success Checklist

Before moving to data conversion, verify you have:

- ✅ Polar RR export file (CSV or TXT)
- ✅ Timestamps in Polar file (absolute or relative)
- ✅ Breathing schedule CSV (with timestamps)
- ✅ Start time exactly known (HH:MM:SS)
- ✅ Both files match time reference
- ✅ Session duration = expected (±10 sec for 15-min session)
- ✅ No major gaps in Polar data (<5% dropout)
- ✅ breath.cafe rate progression makes sense (6.75 → 4.25)

**If all checked → Ready for Python converter!**

---

## 📞 Quick Reference Card

**Print this and tape to your desk:**

```
═══════════════════════════════════════════════════════
        POLAR H10 + BREATH.CAFE QUICK START
═══════════════════════════════════════════════════════

PRE-TEST:
  □ Polar H10 on chest, connected to app
  □ breath.cafe open (6.75→4.25 bpm, 15 min)
  □ Clock visible (time.is)
  □ Screen recording ON (if Option 2)

START (at exact :00 second):
  1. START Polar recording
  2. START breath.cafe
  3. NOTE time: ___:___:___
  4. BEGIN breathing

DURING:
  - Follow pacer smoothly
  - Stay relaxed
  - (If manual logging: note rate every 1 min)

END (at 15:00):
  1. STOP Polar recording
  2. breath.cafe finishes
  3. STOP screen recording
  4. EXPORT CSV

POST-TEST:
  □ Export Polar RR data
  □ Create breathing schedule CSV
  □ Match filenames by timestamp
  □ Run Python converter
  □ Load into HRVisualizer

═══════════════════════════════════════════════════════
```

---

**Next Steps:**

Ready to create the **Python converter script** that will:
1. Read your Polar RR export
2. Read your breathing schedule CSV
3. Generate synthetic respiration waveform
4. Output HRVisualizer-compatible file

Want me to build that now?
