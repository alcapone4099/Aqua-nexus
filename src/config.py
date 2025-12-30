import os

# --- 1. Project Navigation ---
# Get the absolute path of the project root (D:\AquaQ_MARL)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 2. Bay of Bengal Coordinates ---
LAT_MIN = 5.0
LAT_MAX = 22.0
LON_MIN = 80.0
LON_MAX = 96.0

# --- 3. Simulation Grid Size ---
GRID_WIDTH = 50
GRID_HEIGHT = 50

# --- 4. Data Paths ---
# We use os.path.join to ensure it works on Windows and Linux
RAW_CHL_PATH  = os.path.join(BASE_DIR, "data", "raw", "copernicus_data_chl.nc")
RAW_O2_PATH   = os.path.join(BASE_DIR, "data", "raw", "copernicus_data_o2.nc")
RAW_TEMP_PATH = os.path.join(BASE_DIR, "data", "raw", "copernicus_data_temp.nc")
RAW_NO3_PATH  = os.path.join(BASE_DIR, "data", "raw", "copernicus_data_no3.nc")
RAW_PH_PATH   = os.path.join(BASE_DIR, "data", "raw", "copernicus_data_ph.nc")

PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "ocean_grid.npy")

# --- 5. Model & Log Paths (THIS WAS MISSING) ---
LOG_DIR = os.path.join(BASE_DIR, "logs")
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Automatically create these directories if they don't exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)