import time
import subprocess
from datetime import datetime, time as datetime_time, timedelta

# ==============================================================================
# ECLIPSE PARAMETERS & HARDWARE CONFIGURATIONS
# ==============================================================================
# Path to the digiCamControl executable
CMD_PATH = r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"

# --- REAL TIME CONFIGURATION (Eclipse August 12, 2026 - Northern Spain) ---
P1_START       = datetime_time(19, 30, 0)   # Start of partial phase (C1)
TOTALITY_START = datetime_time(20, 27, 0)   # Start of totality (C2)
TOTALITY_END   = datetime_time(20, 28, 45)  # End of totality (C3)
P3_END         = datetime_time(21, 15, 0)   # Observability limit / Sunset (C4)

# --- PARTIAL PHASE SHOT INTERVALS (in seconds) ---
INTERVAL_INGRESS = 1080  # 18 minutes to distribute 5 equidistant shots during ingress
INTERVAL_EGRESS  = 690   # 11.5 minutes to distribute 5 equidistant shots during egress

# --- EXPOSURE LIST CONFIGURATION ---
# Solar Corona Bracketing (Total Phase)
TOTALITY_EXPOSURES = [
    "1/8000", "1/6400", "1/5000", "1/4000", "1/2000", "1/1000", "1/500", 
    "1/250", "1/125", "1/80", "1/30", "1/20", "1/10", "1/2", "1", "2", "4"
]

# Safety shutter speeds for the Diamond Ring (C2 Burst)
DIAMOND_EXPOSURES = ["1/8000", "1/4000", "1/2000"]

# --- EXECUTION MODES ---
SIM_MODE = False  # Set to False for the actual live event
SIM_SPEED_UP    = 60.0  # Time acceleration factor in simulation (e.g., 60x)

# ==============================================================================
# TIME SIMULATION ENGINE (SimClock)
# ==============================================================================
class SimClock:
    def __init__(self, start_time, speed_up=1.0, active=False):
        self.active = active
        self.speed_up = speed_up
        self.real_start = time.time()
        self.sim_start_dt = datetime.combine(datetime.today(), start_time) - timedelta(minutes=2)

    def now(self):
        if not self.active:
            return datetime.now()
        elapsed_real = time.time() - self.real_start
        elapsed_sim = elapsed_real * self.speed_up
        return self.sim_start_dt + timedelta(seconds=elapsed_sim)

    def sleep(self, seconds, critical=False):
        if not self.active or critical:
            time.sleep(seconds)
        else:
            time.sleep(seconds / self.speed_up)

# System clock initialization
clock = SimClock(P1_START, speed_up=SIM_SPEED_UP, active=SIM_MODE)

# ==============================================================================
# CAMERA INTERFACE FUNCTIONS (digiCamControl)
# ==============================================================================
def set_shutter_speed(speed):
    """Sends the USB command to change the shutter speed."""
    if SIM_MODE:
        return
    try:
        subprocess.run([CMD_PATH, "/c", "set", "shutterspeed", speed], capture_output=True)
    except Exception as e:
        print(f"\n[USB ERROR] Unable to set shutter: {e}")

def capture_image(filename):
    """Sends the USB command to trigger the DSLR."""
    now_str = clock.now().strftime('%H:%M:%S')
    print(f"[{now_str}] [SHOT] -> {filename}")
    if SIM_MODE:
        return
    try:
        subprocess.run([CMD_PATH, "/c", "capture", filename], capture_output=True)
    except Exception as e:
        print(f"\n[USB ERROR] Shot failed for {filename}: {e}")

def play_sound_alert(alert_type):
    """Generates a system audio alert differentiated by event type."""
    import winsound
    if alert_type == "pre_totality":
        winsound.Beep(880, 1000) # High A note for 1 second
    elif alert_type == "start_totality":
        winsound.Beep(1200, 500); winsound.Beep(1200, 500) # Aggressive double beep (Filter off!)
    elif alert_type == "pre_end_totality":
        winsound.Beep(440, 300); winsound.Beep(440, 300) # Warning notice to put filter back on
    elif alert_type == "end_totality":
        winsound.Beep(2000, 1500) # Long, piercing beep (Filter on immediately!)

def calculate_exposure_wait(speed_str):
    """Calculates the physical seconds required for the exposure."""
    if "/" in speed_str:
        num, denom = speed_str.split("/")
        return float(num) / float(denom)
    return float(speed_str)

# ==============================================================================
# CORE ECLIPSE AUTOMATION
# ==============================================================================
def run_eclipse_automation():
    # Time logs for the last executed shots
    last_partial_shot_sim_ts = 0
    
    # Safety Switches (Status flags)
    pre_totality_executed = False  
    pre_end_totality_executed = False 
    totality_executed = False
    filter_remove_warned = False
    diamond_burst_c2_executed = False

    # Dynamic and automatic calculation of critical time windows
    PRE_TOTALITY_TIME     = (datetime.combine(datetime.today(), TOTALITY_START) - timedelta(minutes=1)).time()
    WARN_REMOVE_FILTER    = (datetime.combine(datetime.today(), TOTALITY_START) - timedelta(seconds=12)).time() 
    START_DIAMOND_BURST   = (datetime.combine(datetime.today(), TOTALITY_START) - timedelta(seconds=8)).time()  
    START_CORONA_BRACKET  = (datetime.combine(datetime.today(), TOTALITY_START) + timedelta(seconds=3)).time()  
    PRE_END_TOTALITY_TIME = (datetime.combine(datetime.today(), TOTALITY_END) - timedelta(seconds=20)).time()
    
    print("=" * 70)
    print(f" ECLIPSE AUTOMATION LOGISTICS 2026 - SIMULATION MODE: {SIM_MODE}")
    print("=" * 70)
    print(f" C2 Diamond Window:   From {START_DIAMOND_BURST.strftime('%H:%M:%S')} to {START_CORONA_BRACKET.strftime('%H:%M:%S')}")
    print(f" Corona Bracketing:   From {START_CORONA_BRACKET.strftime('%H:%M:%S')} to {TOTALITY_END.strftime('%H:%M:%S')}")
    print("-" * 70)

    while True:
        now_dt = clock.now()
        now_time = now_dt.time()
        current_sim_ts = now_dt.timestamp()
        
        if SIM_MODE:
            print(f" Simulated Time: {now_dt.strftime('%H:%M:%S')} | Status: Loop monitoring", end="\r")

        # ----------------------------------------------------------------------
        # 1. INITIAL WAIT (Before C1 contact)
        # ----------------------------------------------------------------------
        if now_time < P1_START:
            clock.sleep(0.5)
            continue
            
        # ----------------------------------------------------------------------
        # 2. INCOMING PARTIAL PHASE (C1 -> Diamond Window)
        # ----------------------------------------------------------------------
        elif P1_START <= now_time < START_DIAMOND_BURST:
            
            # Standard pre-alarm voice check (-1 minute to totality)
            if now_time >= PRE_TOTALITY_TIME and not pre_totality_executed:
                print(f"\n\n[!!!] ALERT: -1 MINUTE TO TOTALITY! Get ready.")
                play_sound_alert("pre_totality")
                pre_totality_executed = True 
            
            # Immediate audio warning to remove solar filter (-12 seconds to C2)
            if now_time >= WARN_REMOVE_FILTER and not filter_remove_warned:
                print(f"\n\n[!!!] ACTION: REMOVE SOLAR FILTER NOW! [!!!]")
                play_sound_alert("start_totality")
                filter_remove_warned = True

            # Managed interval shots (Uses INTERVAL_INGRESS = 1080s)
            if current_sim_ts - last_partial_shot_sim_ts >= INTERVAL_INGRESS:
                capture_image("Partial_Ingress")
                last_partial_shot_sim_ts = current_sim_ts
                
        # ----------------------------------------------------------------------
        # 3. INCOMING DIAMOND RING PHASE (C2 Burst - 4 Shots x Exposure)
        # ----------------------------------------------------------------------
        elif START_DIAMOND_BURST <= now_time < START_CORONA_BRACKET and not diamond_burst_c2_executed:
            print(f"\n\n[>>>] ENTERING DIAMOND RING PHASE (C2). Executing fast bursts...")
            
            for speed in DIAMOND_EXPOSURES:
                set_shutter_speed(speed)
                clock.sleep(0.05, critical=True)  # Minimum hardware latency for command reception
                
                # Executes 4 continuous shots at the same stabilized speed
                for shot_num in range(1, 5):
                    capture_image(f"C2_Diamond_{speed.replace('/', '_')}_shot{shot_num}")
                    clock.sleep(0.15, critical=True) # Fast camera buffer clearing
            
            if now_time >= START_CORONA_BRACKET:
                diamond_burst_c2_executed = True

        # ----------------------------------------------------------------------
        # 4. TOTAL PHASE: DEEP SOLAR CORONA BRACKETING
        # ----------------------------------------------------------------------
        elif START_CORONA_BRACKET <= now_time <= TOTALITY_END and not totality_executed:
            print(f"\n\n[!!!] TOTAL PHASE: STARTING DEEP CORONA BRACKETING ({now_time.strftime('%H:%M:%S')})")
            
            sim_seconds_left = (datetime.combine(datetime.today(), TOTALITY_END) - clock.now()).total_seconds()
            real_seconds_left = sim_seconds_left / SIM_SPEED_UP if SIM_MODE else sim_seconds_left
            real_end_time = time.time() + real_seconds_left
            
            # Continuous loop until the very last second of totality
            while time.time() <= real_end_time:
                for speed in TOTALITY_EXPOSURES:
                    if time.time() > real_end_time: 
                        break
                    
                    # Integrated pre-alarm check for end of totality (-20 seconds to C3)
                    sim_now = clock.now().time()
                    if sim_now >= PRE_END_TOTALITY_TIME and not pre_end_totality_executed:
                        print(f"\n\n[!!!] SAFETY WARNING: -20 SECONDS TO THE END OF TOTALITY!")
                        play_sound_alert("pre_end_totality")
                        pre_end_totality_executed = True
                    
                    # Executing bracketing shot
                    set_shutter_speed(speed)
                    clock.sleep(0.1, critical=True)
                    capture_image(f"Totality_Corona_{speed.replace('/', '_')}")
                    
                    # Dynamic calculation of sensor write times to avoid mirror lockups
                    exp_time = calculate_exposure_wait(speed)
                    buffer_time = 2.5 if exp_time >= 1.0 else 1.4
                    wait_time = exp_time + (buffer_time if not SIM_MODE else buffer_time / 2)
                    clock.sleep(wait_time, critical=True) 
            
            # Closing the total window (C3 contact)
            print(f"\n\n[!] END OF TOTALITY ({clock.now().strftime('%H:%M:%S')}). REMOUNT SOLAR FILTER IMMEDIATELY!")
            play_sound_alert("end_totality")
            set_shutter_speed("1/1000") # Safety shutter speed reset for the partial phase
            totality_executed = True
            # Aligns the partial timer with the current time for a clean restart during egress
            last_partial_shot_sim_ts = clock.now().timestamp()
                
        # ----------------------------------------------------------------------
        # 5. OUTGOING PARTIAL PHASE (C3 -> C4 / Sunset)
        # ----------------------------------------------------------------------
        elif TOTALITY_END < now_time <= P3_END:
            # Managed short interval shots (Uses INTERVAL_EGRESS = 690s)
            if current_sim_ts - last_partial_shot_sim_ts >= INTERVAL_EGRESS:
                capture_image("Partial_Egress")
                last_partial_shot_sim_ts = current_sim_ts
                
        # ----------------------------------------------------------------------
        # 6. END OF THE EVENT
        # ----------------------------------------------------------------------
        else:
            print(f"\n\n[+] Automation completed successfully at {now_time.strftime('%H:%M:%S')}.")
            break
            
        clock.sleep(0.1)

if __name__ == "__main__":
    run_eclipse_automation()
