# configuration.py

# --- From Table 1 in Ubi_Comp_TermProject.pdf ---

# [cite_start]3 TX, 4 RX [cite: 159, 163]
NUM_TX = 3
NUM_RX = 4

# [cite_start]Number of Chirps per frame [cite: 163]
# (The table calls this "Number of Chirps", but it means loops)
LOOPS_PER_FRAME = 182

# [cite_start]ADC samples per chirp [cite: 163]
ADC_SAMPLES = 256

# [cite_start]Range Resolution in meters [cite: 163]
RANGE_RESOLUTION = 0.0414  # 4.14 cm

# [cite_start]Velocity Resolution in m/s [cite: 163]
DOPPLER_RESOLUTION = 0.028 # 0.028 m/s

# --- From the 'naive_xyz' function in your script ---
NUM_ANGLE_BINS = 64