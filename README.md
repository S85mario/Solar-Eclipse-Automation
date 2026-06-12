# Universal Total Solar Eclipse Automation Script

An advanced Python automation script designed to orchestrate DSLR/Mirrorless camera operations during **any Total Solar Eclipse worldwide**. 

Utilizing the `digiCamControl` CLI interface (`CameraControlRemoteCmd.exe`), this script completely automates tethered shooting across all critical eclipse phases. By accurately calculating and tracking contact times, it eliminates human error and hardware communication latency, allowing photographers to focus entirely on the astronomical event.

## Key Features

* **Universal & Fully Configurable:** Easily adaptable to any eclipse date, time, and geographical location by simply updating the local contact timestamps (C1, C2, C3, and C4).
* **Dual-Phase Partial Tracking:** Independent interval configurations for Ingress (C1 -> C2) and Egress (C3 -> C4) to perfectly handle changing light levels and atmospheric extinction as the Sun changes altitude.
* **Smart Diamond Ring Burst (C2/C3):** Minimizes USB command overhead by locking the shutter speed and firing a rapid 4-shot sequence per exposure level, maximizing the chances of capturing Baily's Beads and the perfect diamond flash.
* **Continuous Corona Bracketing:** Seamless, high-dynamic-range (HDR) looping sequence covering up to 17 exposure values (from ultra-fast speeds like $1/8000s$ down to multi-second long exposures) during the brief totality window.
* **Integrated Simulation Engine (`SimClock`):** Built-in time acceleration clock allows you to thoroughly test and review your entire sequence timeline within seconds at home before hitting the field.
* **Acoustic Warning System:** Uses system-level audio cues to alert you precisely when to remove and reinstall the physical solar ND filter.

---

## Architecture & Logic Flow

1. **Pre-Eclipse Phase:** Monitors the clock until Contact 1 (C1).
2. **Partial Ingress Phase:** Fires a set number of shots spaced out evenly based on the ingress duration.
3. **The C2 Window (Pre-Totality):** Triggers an audio alert to remove the solar filter, changes shutter speed to fast safety margins, and shoots rapid 4-photo cycles to capture the Diamond Ring.
4. **Totality Core (C2 to C3):** Loops through the deep bracketing stack continuously to capture the solar corona. Triggers a safety warning 20 seconds before C3.
5. **Contact 3 (C3):** Sounds a critical alarm to slide the solar filter back on and resets exposure to standard baselines.
6. **Partial Egress Phase:** Fires symmetrically timed shots down to Contact 4 (C4) or sunset.

---

## Installation & Prerequisites

1. **Operating System:** Windows (Required for digiCamControl).
2. **Tethering Software:** Download and install [digiCamControl](http://digicamcontrol.com/). Ensure `CameraControlRemoteCmd.exe` is located in your system path or explicitly configured in the script.
3. **Python:** Python 3.6+ installed.
4. **Camera Setup:** * Connect your camera via USB.
   * Turn off all auto-focus (switch lens to **MF** and lock focus on infinity).
   * Set the camera body to **Manual Mode (M)**.
   * Ensure image saving is set to **RAW** (or RAW+JPEG).

---

## Configuration

To adapt the script to your specific eclipse site, open the file and update the parameters in the top section with your local contact coordinates:

```python
# Path to digiCamControl remote CLI tool
CMD_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"

# Real local contact timings based on your exact observation site
# (Defaults configured for the August 12, 2026 Eclipse in Northern Spain)
P1_START       = datetime_time(19, 30, 0)   # C1: Partial phase starts
TOTALITY_START = datetime_time(20, 27, 0)   # C2: Totality starts
TOTALITY_END   = datetime_time(20, 28, 45)  # C3: Totality ends
P3_END         = datetime_time(21, 15, 0)   # C4: Partial phase ends (or sunset limit)

# Custom interval spacing in seconds
INTERVAL_INGRESS = 1080  # Spacing between partial shots before totality
INTERVAL_EGRESS  = 690   # Spacing between partial shots after totality
