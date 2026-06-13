# Universal Total Solar Eclipse Automation Script

An advanced, robust Python automation script designed to orchestrate split-second camera triggering and exposure bracketing during a Total Solar Eclipse. Operating via **digiCamControl**, this engine supports **Canon, Nikon, and Sony** camera systems, automating high-speed Diamond Ring bursts, multi-exposure Corona HDR sequences, and automated local voice alerts.

---

## 🌟 Key Features

* **Multi-Brand Shutter Profiles:** Seamlessly handles firmware-specific command line formats across Canon (decimal notations like `0.5`), Nikon, and Sony (fractional notations like `1/2`).
* **Anti-Freeze Connection Protocol:** Built-in interactive "Phase 0" startup checklist enforcing the exact hardware initialization sequence to prevent USB handshake lockups.
* **Corona HDR Bracketing Engine:** Executes an expanded 14-stop exposure ladder with an automated double-exposure safety buffer per stop to neutralize accidental camera shake.
* **Diamond Ring & Baily's Beads Burst:** Captures highly volatile contact points (C2 and C3) with rapid 20-shot continuous brackets covering a 4-stop range.
* **Integrated Time Simulation:** Features a `SIM_MODE` clock simulator to perform full-speed or accelerated dry-runs from the comfort of your desk without firing physical shutters.
* **Emergency Local Logging:** Simultaneous terminal and text-file logging to preserve operational diagnostic history on the field.

---

## 🛠️ Hardware & Software Prerequisites

### 1. Operating System & Software
* **Windows OS:** Required natively due to reliance on `winsound` audio architecture and the digiCamControl backend.
* **digiCamControl:** Must be installed in its default directory: `C:\Program Files (x86)\digiCamControl\`.

### 2. Camera Body Configurations
Before launching the automation script, configure your camera body exactly as follows:

* ⚠️ **CRITICAL: Exposure Parameters (ISO & Aperture):** Manually dial in your chosen ISO (e.g., ISO 100 or 400) and Aperture (e.g., f/8) *permanently* before the script starts. **The automation engine strictly changes the Shutter Speed only.** It will NOT alter your ISO or Aperture during the sequence.
* **Exposure Mode:** Set the physical mode dial strictly to **M (Manual)**.
* **Focusing:** Achieve perfect focus on the sun/stars beforehand, then switch the lens/body to **MF (Manual Focus)**. Secure the focus ring with tape.
* **Storage Routing:** Ensure the camera is configured to write files **ONLY to the internal SD card**. Saving files over USB to the laptop will overflow the interface buffer during high-speed brackets.
* **Brand Specific Connections:**
    * *Nikon / Canon:* Standard PTP communication protocol.
    * *Sony:* The camera's USB Connection setting **must** be set to **PC Remote** or **MTP** depending on the specific mirrorless model.

---

## ⚙️ Configuration & Customization

Open the script in your preferred editor and adjust the **Global Configuration** block at the top:

### 1. Select Your Camera Brand
```python
# Options: "CANON", "NIKON", or "SONY"
CAMERA_BRAND = "CANON" 

2. Input Your Coordinates' Exact Contact Times

Calculate the precise contact times for your specific observation path and modify the variables accordingly:
Python

P1_START       = datetime_time(19, 30, 0)   # Partial Phase Ingress Begins
TOTALITY_START = datetime_time(20, 27, 0)   # Totality Begins (C2 Contact)
TOTALITY_END   = datetime_time(20, 28, 45)  # Totality Ends (C3 Contact)
P3_END         = datetime_time(21, 15, 0)   # Partial Phase Egress Ends (C4)

3. Audio Triggers (User-Provided)

To keep the engine flexible and international-friendly, no audio files are provided in this repository. You are encouraged to record or generate your own countdown voice alerts in your native language (hearing a familiar voice or language helps reduce stress during critical live phases).

Save them as .wav files on your local drive and map their absolute paths in the configuration block:
Python

AUDIO_1_MIN        = r"C:\Eclipse\Audio\one_minute_left.wav"
AUDIO_TOGLI_FILTRO = r"C:\Eclipse\Audio\remove_filter.wav"
AUDIO_20_SEC       = r"C:\Eclipse\Audio\20_seconds_left.wav"
AUDIO_METTI_FILTRO = r"C:\Eclipse\Audio\replace_filter.wav"

🚀 Step-by-Step Field Operation Workflow

To prevent Windows or the camera firmware from freezing the USB stack, follow this exact physical connection sequence enforced by the script's interactive Preflight Checklist:

    Mount everything: Secure your setup on your tripod or tracker, mount the Solar Filter, and acquire perfect focus.

    Power On Camera: Turn on your camera body before plugging in any data links. Ensure it is in Manual mode with ISO and Aperture locked.

    Connect Interface Link: Plug the USB cable into the camera body and then into the laptop.

    Execute Script: Launch the automation engine terminal:
    Bash

    python eclipse_automation_en.py

    Interactive Validation: The script will open digiCamControl automatically and pause at "Phase 0". Read the screen, confirm the connection protocol, and hit ENTER.

    Physical Safety Checklist: Go through the 5-point safety questionnaire on the terminal pressing ENTER for each step to ensure your solar filter is on and settings are locked.

    Engine Takeover: The countdown engine takes control. You can safely step away from the equipment and enjoy the celestial event.

🧪 Testing with Simulation Mode

Do not wait until eclipse day to test your setup. You can dry-run the entire script at home safely:

    Set SIM_MODE = True in the configuration.

    Set SIM_SPEED_UP = 1.0 to run the timeline in real-time, or increase it (e.g., 5.0) to accelerate the partial phases during testing.

    The engine will warp its internal clock to 1 minute before C1 and cycle through all phases, playing your local audio alerts and printing virtual shutter actions without checking hardware endpoints.

⚠️ Disclaimer

This software is provided "as is", without warranty of any kind. Solar eclipse events are unforgiving and non-repeatable. Perform extensive dry-runs with your specific camera body model, laptop power banks, and data cables under varying conditions before the live event.