# HRV Resonance Frequency Toolkit

A collection of tools for determining your **Resonance Frequency (RF)** — the breathing rate (typically 4.5–7 bpm) at which heart rate variability is maximised. Training at your RF is the basis of HRV biofeedback therapy.

This repo combines:

- **HRVisualizer** — a Windows desktop app (and Python port) for analysing HRV sessions and reading RF from the power spectrum. Developed by Gibson Research Corporation for the Fisher & Lehrer (2021) study; open-source ZIP at [breath.cafe](https://breath.cafe/).
- **Every Breath You Take (EBYT)** — a Python/PySide6 app for live Polar H10 BLE streaming with real-time HRV biofeedback. Forked from [kieranabrennan/every-breath-you-take](https://github.com/kieranabrennan/every-breath-you-take) by Kieran Brennan (MIT license), extended here with the Fisher–Lehrer RF protocol and HRVisualizer-compatible export.
- **Converter scripts** — for importing Elite HRV + breath.cafe data into HRVisualizer when you don't have a computer with you during a session.

---

## Background: What is Resonance Frequency?

At your RF, slow breathing entrains a large RSA (respiratory sinus arrhythmia) — heart rate rises on inhale and falls on exhale in a pronounced sine wave, producing a sharp peak in the HRV power spectrum. Finding this frequency requires testing several rates and observing where HRV amplitude is highest.

The Fisher–Lehrer graduated protocol sweeps from ~6.75 bpm down to ~4.25 bpm over 15 minutes, letting you identify the peak in a single session. Protocol details and supporting software are described in:

> Fisher, S.F. & Lehrer, P.M. (2021). Resonance frequency biofeedback: A sliding scale approach. *Applied Psychophysiology and Biofeedback.* DOI: [10.1007/s10484-021-09524-0](https://doi.org/10.1007/s10484-021-09524-0)

---

## Methods

There are two main routes depending on your equipment:

| Route | Hardware needed | Notes |
|-------|----------------|-------|
| **A – Mobile (EliteHRV + breath.cafe)** | Phone + any chest strap | Simpler setup; synthetic respiration waveform reconstructed from protocol schedule; requires careful manual start-time sync |
| **B – Computer live streaming (EBYT)** | Polar H10 + laptop/desktop with BT | Records real breathing via accelerometer; timing automatic; more accurate |

Both routes produce a HRVisualizer-compatible `.txt` file. RF is read from the resulting HRV frequency plot.

---

## Route A: EliteHRV + breath.cafe → HRVisualizer

Use this route when you want to use your phone and a familiar HRV app, or don't have your laptop available during a session.

> **Note:** Route B (EBYT) is more accurate — it records your actual breathing via the Polar H10 accelerometer, and timing is handled automatically. Route A reconstructs a synthetic respiration waveform from the protocol schedule, which is sufficient for reading your RF peak but less precise.

### Overview

1. Record HRV with the **EliteHRV** app while following the **breath.cafe** pacer
2. Export the RR interval file from EliteHRV
3. Run the converter to produce a HRVisualizer file
4. Open in HRVisualizer to read your RF

### Step 1 — Open the breath.cafe pacer

Open [https://breath.cafe/](https://breath.cafe/) in a browser, or open `breath_cafe_research_protocol.html` locally for the full automated Fisher–Lehrer sweep (6.75 → 4.25 bpm).

Have it ready but **do not start yet**.

### Step 2 — Record with EliteHRV

1. Open the **EliteHRV** app on your phone and start a new session in Free Mode (not their scored protocol).
2. Connect your HRM (Polar H10 recommended — wrist PPG devices are noisier and can shift the apparent RF by 1+ bpm).
3. **Start EliteHRV and the breath.cafe pacer at the same moment.** This synchronisation is the key step — the converter uses the pacer's known protocol schedule to reconstruct the respiration waveform, aligned to your start time.
4. Breathe for 15 minutes following the pacer.
5. Stop both EliteHRV and the pacer at the same time. Note the clock time you started.

### Step 3 — Export RR intervals from EliteHRV

- Go to the session → Share → Export RR Intervals
- This produces a plain text file with one RR interval per line in milliseconds:
  ```
  802
  834
  628
  ```

### Step 4 — Convert to HRVisualizer format

```bash
# No dependencies needed — uses Python standard library only
python3 elitehrv_to_hrvisualizer.py \
    --rr "my_session_rr.txt" \
    --start-time "2026-03-24T20:30:00" \
    --output session_20260324.txt \
    --name "Your Name"
```

The `--start-time` is the clock time when you started both apps. The converter generates the respiration waveform from the Fisher–Lehrer protocol schedule automatically.

Output is a two-column tab-separated file (ECG, Respiration at 256 Hz) in NeXus format, ready for HRVisualizer.

### Step 5 — Open in HRVisualizer

See [Viewing results in HRVisualizer](#viewing-results-in-hrvisualizer) below.

---

## Route B: Live streaming with EBYT (Polar H10 required)

The **Every Breath You Take** app connects directly to a Polar H10 over Bluetooth and streams ECG-grade RR intervals + chest accelerometer (breathing) in real time. It runs the Fisher–Lehrer protocol automatically and exports a HRVisualizer file at the end of the session.

### Prerequisites

- **Polar H10** chest strap (firmware 5.0.0 or later)
- Mac, Linux, or Windows PC with Bluetooth LE
- Python 3.9–3.12

### Installation

```bash
cd every-breath-you-take
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running

```bash
cd every-breath-you-take
source venv/bin/activate
python EBYT.py
```

On macOS you can double-click `EveryBreathYouTake.command` instead.

The app will scan and connect to your Polar H10 automatically. Ensure the strap is fitted snugly around the widest part of the ribcage.

### Doing an RF session

1. **Wear the Polar H10** and wait for it to connect (green indicator in the app).
2. **Select a protocol** from the Protocol dropdown:
   - *Fisher–Lehrer* — graduated sweep 6.75 → 4.25 bpm over 15 minutes (recommended for first RF determination)
   - *Manual* — set the breathing rate yourself
3. **Start the pre-roll**: sit quietly for 1–2 minutes to stabilise. The pacer runs but data is not yet saved.
4. **Click "Start Session"**: this sets the session start time and begins recording. Follow the expanding/contracting gold circle pacer.
5. **Breathe diaphragmatically**: belly expands on inhale, chest stays still. Nose in, nose or pursed-lip out. Passive, relaxed exhale — do not force lungs empty.
6. **After 15 minutes** (or when the protocol ends): click "Stop & Export".
7. The app saves a HRVisualizer-compatible `.txt` file to `every-breath-you-take/exports/`.

### Real-time display

- **Top graph**: raw RR intervals (beat-to-beat HR) and breathing trace
- **Middle graph**: HR oscillation (RSA) — you are looking for a large, smooth sine wave
- **Bottom graph**: HRV frequency spectrum — look for the spectral peak to grow and sharpen as you approach your RF

### Exporting

On "Stop & Export" the app writes two files:
- `exports/YYYY-MM-DD_HH-MM-SS.txt` — HRVisualizer NeXus format
- `exports/YYYY-MM-DD_HH-MM-SS_raw.txt` — raw debug data

---

## Viewing results in HRVisualizer

HRVisualizer analyses the session and displays a frequency spectrum showing where HRV amplitude peaked. Your RF is the frequency of the highest peak in the **RSA band** (roughly 0.05–0.15 Hz / 3–9 bpm).

### Python port (macOS / Linux / Windows)

The file `hrvisualizer.py` is a full Python/PySide6 port of the original VB.NET HRVisualizer, producing the same results.

```bash
# Install (one-time, uses the EBYT venv)
cd every-breath-you-take
source venv/bin/activate
pip install pyqtgraph

# Open a session file
cd ..
python hrvisualizer.py exports/my_session.txt

# Or open without a file (drag-and-drop)
python hrvisualizer.py
```

On macOS you can double-click `HRVisualizer.command`.

**Controls:**
- Mouse wheel: zoom in/out on time axis
- Click and drag scrollbar: pan
- Checkboxes: toggle ECG / respiration traces
- "B&W" button: black and white mode
- "Copy": copy chart to clipboard

### Original Windows app

The original VB.NET source is in `Nexus/`. Open `Nexus/Nexus.sln` in Visual Studio to build. Requires .NET Framework and Microsoft Chart Controls for .NET 3.5 (free download from Microsoft).

---

## Reading your RF

In HRVisualizer, the HRV frequency plot shows power vs. frequency (x-axis in bpm). Look for:

- A **sharp, prominent peak** in the 4–7 bpm region
- The peak should be substantially taller than the noise floor
- If using the Fisher–Lehrer protocol, the peak typically appears 1–2 minutes after the pacer passes through your true RF (physiological entrainment lag)

For the Fisher–Lehrer 15-minute protocol (6.75 → 4.25 bpm):
- The pacer sweeps through the full RF range
- The frequency at the HRV peak is your RF
- Confirm with a second session if the peak is not clear

Round to the nearest 0.25 or 0.5 bpm for training. A typical range is 4.5–6.5 bpm; most people fall between 4.5–5.5 bpm.

---

## Repository structure

```
├── hrvisualizer.py                 Python port of HRVisualizer
├── elitehrv_to_hrvisualizer.py     Convert EliteHRV + breath.cafe → HRVisualizer
├── polar_to_hrvisualizer.py        Convert raw Polar H10 data → HRVisualizer
├── generate_test_data.py           Generate synthetic test sessions
├── quick_rf_test.py                Quick RF determination from RR file
├── convert_session.sh              Shell wrapper for elitehrv_to_hrvisualizer.py
├── HRVisualizer.command            macOS launcher for hrvisualizer.py
├── EveryBreathYouTake.command      macOS launcher for EBYT
│
├── breath_cafe_logger.html         Modified breath.cafe with CSV export logging
├── breath_cafe_research_protocol.html  Fisher–Lehrer automated stepped protocol
│
├── every-breath-you-take/          Polar H10 live streaming app (fork)
│   ├── EBYT.py                     Entry point
│   ├── Model.py                    Sensor callbacks, export orchestration
│   ├── View.py                     PySide6 GUI
│   ├── DataExporter.py             HRVisualizer NeXus format export
│   ├── ProtocolManager.py          Fisher–Lehrer + other protocols
│   ├── Pacer.py                    Visual breathing pacer
│   ├── sensor.py                   Polar H10 BLE interface
│   ├── analysis/
│   │   ├── BreathAnalyser.py       Accelerometer → breathing rate
│   │   ├── HrvAnalyser.py          RR intervals → HRV metrics
│   │   └── HistoryBuffer.py        Circular buffer
│   └── exports/                    Session output files (gitignored)
│
├── Nexus/                          Original VB.NET HRVisualizer source
│
└── test_data/
    └── Alyssa_Synthetic_Respiration.txt   Sample session (from original HRVisualizer)
```

---

## Attribution

### HRVisualizer and Breath Pacer
Developed by **Gibson Research Corporation** (Laguna Beach, CA) for the Fisher & Lehrer (2021) study.
Both tools are open-source. Contact: Lorrie@FisherBehavior.com (Lorrie Fisher, Fisher Behavior).

- Breath Pacer source (well-commented JavaScript): [breath.cafe](https://breath.cafe/) → right-click → View Source
- HRVisualizer source ZIP: [breath.cafe/HRVISUALIZER_WITH_SOURCE_CODE.ZIP](https://breath.cafe/HRVISUALIZER_WITH_SOURCE_CODE.ZIP)
- Digital supplement: [breath.cafe/research.pdf](https://breath.cafe/research.pdf)

The `Nexus/` directory and `hrvisualizer.py` port are based on the HRVisualizer source.

### Every Breath You Take
Original application by **Kieran Brennan**, MIT License.
Original repository: [github.com/kieranabrennan/every-breath-you-take](https://github.com/kieranabrennan/every-breath-you-take)
This fork adds:
- Fisher–Lehrer graduated RF protocol (`ProtocolManager.py`)
- HRVisualizer-compatible NeXus format export (`DataExporter.py`)
- Per-breath discrete rate stepping (as specified in the Fisher–Lehrer paper)

### Fisher–Lehrer RF Protocol
The sliding graduated protocol implemented in this repo is described in:

> Fisher, S.F. & Lehrer, P.M. (2021). Resonance frequency biofeedback: A sliding scale approach. *Applied Psychophysiology and Biofeedback.* DOI: [10.1007/s10484-021-09524-0](https://doi.org/10.1007/s10484-021-09524-0)

The Breath Pacer and HRVisualizer were developed by Gibson Research Corporation specifically for this study. Both programs are open-source (see above).

### breath.cafe
Breathing pacer web app by **Lorrie R. Fisher** — [breath.cafe](https://breath.cafe/).
The modified logger versions (`breath_cafe_logger.html`, `breath_cafe_research_protocol.html`) add CSV export and automated protocol stepping to the original.

---

## License

- `every-breath-you-take/` and this fork's extensions: MIT (see `every-breath-you-take/LICENSE`)
- `Nexus/` (original HRVisualizer source): as distributed by breath.cafe — check with the original author for terms
- Converter scripts and Python port (`hrvisualizer.py`): MIT
