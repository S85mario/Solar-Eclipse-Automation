
# SolarEclipse2026 📸 🌒

Automated hybrid control system for Canon/Nikon cameras via **digiCamControl** for high-precision bracketing during the **Total Solar Eclipse of August 12, 2026**.

This script combines the bulletproof reliability of the digiCamControl CLI (`CameraControlRemoteCmd.exe`) for camera parameter changes with the sub-millisecond speed of Web Server HTTP triggers for immediate shutter release. Optimized for astromodified cameras and designed to save files **strictly to the camera's SD card** to maximize buffer clearing speed and prevent PC storage overhead.

---

# 🚀 Key Features

* **Hybrid Engine:** Parameter setting via native CLI (~1s overhead between long intervals) + fast HTTP capture trigger (~22ms latency for exact synchronization).
* **Forced SD-Only Storage:** Automatically overrides digiCamControl session defaults to enforce file saving directly on the camera's memory card (`CameraMemoryOnly`), keeping the PC clean.
* **Interactive Debug Mode:** Easily toggle detailed colored console logging and precise URL requests at startup.
* **Telegram Notifications:** Real-time updates, error logging, and critical filter alerts sent directly to your phone.
* **Astromodification Optimized:** Tailored timeline exposure mapping to exploit increased H-alpha sensitivity (656.3 nm) for stunning solar prominences and chromosphere capture.

---

# 🛠️ Prerequisites & Configuration

# 1. Requirements
* Windows OS with digiCamControl installed.
* Python 3.x.
* A compatible DSLR/Mirrorless camera (e.g., Canon EOS R series) connected via high-speed USB-C.

# 2. File Structure
Ensure your project folder contains:
```text
├── SolarEclipse2026.py   # The main script
└── secrets.json          # Telegram bot configuration (Optional)

# 3. Telegram Setup (secrets.json)

If you want real-time phone alerts on the field, create a secrets.json file:

{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "chat_id": "YOUR_CHAT_ID_HERE"
  }
}

📈 The August 12, 2026 Shooting Timeline

The script executes a hardcoded, chronological event sequence calibrated around C2 (Second Contact) and C3 (Third Contact).

| Phase / Event | Timing Relative to Totality | Settings (ISO | Shutter | Aperture) | Target Target |
| :--- | :--- | :--- | :--- |
| Partial Phase C1 | C2 - 58 min | ISO 100 | 1/250s | f/8.0 | First Contact tracking |
| Partial Phases | C2 -40m / -20m / -10m / -5m | ISO 100 | 1/250s | f/8.0 | Solar disk tracking |
| Diamond Ring C2 | C2 - 5 sec | ISO 400 | 1/100s | f/8.0 | Baily's beads blend |
| Baily's Beads C2 | C2 - 2 sec | ISO 200 | 1/3200s | f/16.0 | Sharp lunar valleys peaks |
| HDR 1 | C2 + 0 sec | ISO 200 | 1/4000s | f/8.0 | Prominences (H-alpha) |
| HDR 2 & 3 | C2 + 2 sec / + 4 sec | ISO 200 | 1/1000s, 1/250s | f/8.0| Inner & Mid Corona |
| HDR 4 & 5 | C2 + 6 sec / + 8 sec | ISO 200 | 1/60s, 1/15s | f/8.0 | Extended & Outer Corona |
| HDR 6 & 7 | C2 + 10 sec / + 12 sec | ISO 200 | 1/4s, 1.0s | f/8.0 | Deep Structure & Earthshine |
| Baily's Beads C3| C3 + 2 sec | ISO 200 | 1/3200s | f/16.0 | Third Contact diamond prep |
| Diamond Ring C3 | C3 + 5 sec | ISO 400 | 1/100s | f/8.0 | Totality exit |
| Partial Phases | C3 +5m to +30m | ISO 100 | 1/250s | f/8.0 | Final egress tracking |

📋 Field Deployment Checklist (Pre-Flight)

When you launch the script, an interactive checklist will prompt you to confirm every crucial step before activation:

    [ ] POWER: PC connected to stable power bank/inverter; Camera battery at 100%.

    [ ] CABLE: High-speed USB-C tethering cable securely locked.

    [ ] DIGICAMCONTROL: Software active, camera detected, LIVE VIEW CLOSED (Crucial to avoid lag).

    [ ] WEB SERVER: Web Server active in digiCamControl settings (default port 2727).

    [ ] MANUAL FOCUS (MF): Focus locked on infinity via Live View beforehand, lens switched to MF and taped down.

    [ ] IMAGE REVIEW: "Image Review" set to OFF in the Camera internal menus (Crucial to prevent BUSY locks).

    [ ] SOLAR FILTER: ND 3.8/5.0 Solar Filter securely attached for partial phases.

💻 Usage

  1  Run digiCamControl and ensure your camera is fully recognized.

  2  Open a terminal/command prompt in the script directory and run:

    python SolarEclipse2026.py

  3  Debug Selection: The script will ask: Vuoi attivare la modalità DEBUG  avanzata? (s/N):.

   - Press S for testing (displays full ANSI color-coded logs and active web endpoints).

   - Press Enter (No) on the eclipse day for clean, standard execution.

  4 Complete the on-screen checklist by pressing ENTER at each step.

  5 Hands-Off: Once initiated, do NOT touch the camera body or press the Play   button to preview images. Let the script manage the buffer.

  ⚠️ Critical Safety Reminders during Totality

  -  Filter Removal: The script will issue a loud console flash and a Telegram prompt at C2 - 4min 50s stating: ⚠️ RIMUOVERE FILTRO ND 3.8 ORA!. Remove your solar filter immediately to capture the Diamond Ring and Totality.

  -  Filter Re-insertion: Right after the Diamond Ring C3, the script will prompt: 🚨 REINSERIRE FILTRO ND 3.8 IMMEDIATAMENTE!. Put the solar filter back on to protect your camera sensor and optics from focused sunlight during the egress partial phases.

  ⚙️ Astromodification Notes

This sequence is heavily optimized for sensors with removed or replaced IR-cut filters. The rapid 1/4000s exposures (HDR 1) will natively resolve a staggering amount of structural contrast within the hydrogen-alpha solar loops, while the overall spectrum will exhibit an enhanced pink/magenta saturation near the inner corona boundary. Ensure your White Balance is adjusted in post-production from the native RAW data.

Clear skies for August 12, 2026! 🌌

