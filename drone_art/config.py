# config.py
# All tunable settings live here so the rest of the code stays clean.

# --- Folders ---
INPUT_DIR = "input"
OUTPUT_DIR = "output"

# --- Grid / rendering ---
GRID = 100            # 100 x 100 "drones"
CELL_SIZE = 8         # pixels per cell in the rendered PNG -> 800x800 output
DOT_RATIO = 0.75       # dot diameter as a fraction of the cell (leaves the gap)

# Colours as hex
BACKGROUND_HEX = "#0a101c"   # dark navy, like the example image 

# --- Animation (goal 2) ---
FRAME_DURATION_MS = 100   #ms per frame
MAX_FRAMES = 100         #max frames. Going above 104 will have you hit the excel sheet limit
GIF_LOOP = 0              # 0 = loop forever
GIF_NAME = "animation.gif"

# --- Downsampling quality ---
RESAMPLE = "LANCZOS"   # "LANCZOS" = smooth, "NEAREST" = hard pixel-art look

# --- Input handling ---
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")
VIDEO_EXTENSIONS = (".mp4", ".mov", ".m4v", ".avi", ".mkv")

# Auto center-crop non-square inputs by shaving equal amounts off the
# outer edges (left/right or top/bottom) until it's square.
AUTO_CENTER_CROP = True

# --- Video handling ---
# If a clip has more frames than MAX_FRAMES, how do we pick?
#   "even"  -> evenly spaced samples across the whole clip
#   "first" -> just the first MAX_FRAMES frames
VIDEO_SAMPLING = "even"

# --- CSV export ---
WRITE_CSV = True
CSV_NAME = "symbol_stream.csv"
CSV_EVERY = 1              # write every Nth frame (1 = all frames)
INCLUDE_OFDM_COLUMNS = True  # set False for a lean frame,X,Y,hex file