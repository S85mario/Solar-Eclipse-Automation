readme_content = """# Solar Eclipse HDR Automation Script (August 12, 2026)

[English](#english) | [Italiano](#italiano) | [Source Code / Codice Sorgente](#source-code)

---

## English

An automated Python script designed to orchestrate high-dynamic-range (HDR) bracketing sequences during solar eclipses. It automates camera settings (Shutter Speed, Aperture, ISO) and handles precise timing constraints relative to the contact points **C2** (Start of Totality) and **C3** (End of Totality). 

The script interfaces directly with **digiCamControl** via its Command Line Interface (CLI) to guarantee stable communication, especially during rapid setting changes like the Diamond Ring and Baily's Beads phases.

### Features
* ⏱️ **Astronomical Event Synchronization:** Automates shots based on fixed time offsets from C2 and C3.
* 📷 **Hardware-Stabilized Aperture Control:** Implements clean formatting (e.g., `f/X.0`) and electronic settling delays to prevent lens firmware locks.
* 🤖 **Telegram Integration:** Sends real-time status, execution confirmation, and error logging directly to a Telegram channel/bot.
* ⚙️ **Configurable Scripts:** Uses standard `TAKEPIC` command strings for easy sequence adjustments.

### Prerequisites
* **OS:** Windows 10 / 11
* **Python:** 3.x
* **Software:** [digiCamControl](http://digicamcontrol.com/) installed at its default path (`C:\\Program Files (x86)\\digiCamControl\\`).
* **Camera Setup:** Camera set to **Manual (M)** mode, Lens switched to **Manual Focus (MF)**, and Live View **closed** inside the digiCamControl GUI.

### Configuration
1. **Telegram Credentials:** Create a file named `secrets.json` in the same directory as the script:
'''json
   {
       "telegram": {
           "bot_token": "YOUR_BOT_TOKEN",
           "chat_id": "YOUR_CHAT_ID"
       }
   }

   Eclipse Contacts: Edit the C2_TIME and C3_TIME variables inside the script with the exact astronomical contact coordinates for your specific shooting location.