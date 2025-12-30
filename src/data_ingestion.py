# data_ingestion.py
# FIXES:
# 1. Geometric Flip: Ensures North is Top (Row 0) and West is Left (Col 0).
# 2. Log Scaling: Keeps specific outliers visible while showing subtle currents.

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
import os

# Import config safely
try:
    from src.config import *
except ImportError:
    from config import *

class OceanEnvironmentGenerator:
    def __init__(self):
        self.grid_w = GRID_WIDTH
        self.grid_h = GRID_HEIGHT

    def process_layer(self, file_path, var_names_list, layer_name="Unknown"):
        """
        Generic function to load, average, resize, FLIP, and LOG-SCALE ocean data.
        """
        if not os.path.exists(file_path):
            print(f"⚠️ {layer_name}: File missing at {file_path}. Generating noise.")
            return np.random.rand(self.grid_w, self.grid_h)

        print(f"📂 {layer_name}: Processing {os.path.basename(file_path)}...")
        try:
            ds = xr.open_dataset(file_path)
            target_var = next((v for v in var_names_list if v in ds), None)
            
            if not target_var:
                print(f"   ❌ {layer_name}: Variable not found. Available: {list(ds.keys())}")
                return np.random.rand(self.grid_w, self.grid_h)

            data_var = ds[target_var]

            # 1. Time Averaging (1 Month Mean)
            if 'time' in data_var.dims:
                data_slice = data_var.mean(dim='time', skipna=True)
            else:
                data_slice = data_var

            # 2. Depth Selection (Surface only)
            if 'depth' in data_slice.dims:
                data_slice = data_slice.isel(depth=0)
            
            # Extract values and handle NaNs
            raw_array = data_slice.values
            valid_median = np.nanmedian(raw_array)
            raw_array = np.nan_to_num(raw_array, nan=valid_median)

            # 3. Resize to Simulation Grid (50x50)
            zoom_factors = (self.grid_w / raw_array.shape[0], self.grid_h / raw_array.shape[1])
            resized_grid = zoom(raw_array, zoom_factors, order=1)

            # --- 4. GEOMETRIC CORRECTION (The "Upside Down" Fix) ---
            # Satellite data is usually South-to-North (Row 0 is South).
            # We flip it Upside-Down so Row 0 becomes North (Top of Map).
            resized_grid = np.flipud(resized_grid)

            # --- 5. LOGARITHMIC SCALING (The "Outlier" Fix) ---
            # A. Shift to positive
            if np.min(resized_grid) < 0:
                resized_grid = resized_grid - np.min(resized_grid)

            # B. Apply Log Transform
            log_grid = np.log1p(resized_grid)

            # C. Min-Max Normalize
            d_min = log_grid.min()
            d_max = log_grid.max()
            
            if d_max - d_min == 0:
                norm_grid = np.zeros_like(log_grid)
            else:
                norm_grid = (log_grid - d_min) / (d_max - d_min)
            
            return norm_grid
            
        except Exception as e:
            print(f"❌ {layer_name} Error: {e}")
            return np.random.rand(self.grid_w, self.grid_h)

    def load_and_combine_data(self):
        print("🌊 Starting Multi-Parameter Data Ingestion (Corrected Geometry)...")

        # 1. Chlorophyll
        grid_chl = self.process_layer(
            RAW_CHL_PATH, 
            ['chl', 'CHL', 'mass_concentration_of_chlorophyll_a_in_sea_water'],
            "Chlorophyll"
        )

        # 2. Oxygen
        grid_o2 = self.process_layer(
            RAW_O2_PATH, 
            ['o2', 'O2', 'mole_concentration_of_dissolved_molecular_oxygen_in_sea_water'],
            "Oxygen"
        )

        # 3. Temperature
        grid_temp = self.process_layer(
            RAW_TEMP_PATH, 
            ['thetao', 'temperature', 'sea_water_potential_temperature'],
            "Temperature"
        )

        # 4. Nitrate
        grid_no3 = self.process_layer(
            RAW_NO3_PATH, 
            ['no3', 'NO3', 'mole_concentration_of_nitrate_in_sea_water'],
            "Nitrate"
        )

        # 5. pH
        grid_ph = self.process_layer(
            RAW_PH_PATH, 
            ['ph', 'PH', 'sea_water_ph_reported_on_total_scale'],
            "pH"
        )

        # --- Stack 5 Channels ---
        combined_grid = np.stack([grid_chl, grid_o2, grid_temp, grid_no3, grid_ph], axis=-1)
        
        print(f"✅ Data Combined. Final Shape: {combined_grid.shape}")
        return combined_grid

    def save_environment(self, grid_data):
        os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
        np.save(PROCESSED_DATA_PATH, grid_data)
        print(f"💾 Saved processed grid to {PROCESSED_DATA_PATH}")

    def visualize(self, grid_data):
        fig, ax = plt.subplots(1, 5, figsize=(20, 4))
        titles = ["Chlorophyll", "Oxygen", "Temp", "Nitrate", "pH"]
        # Standard scientific colormaps
        cmaps = ["viridis", "plasma", "inferno", "cividis", "twilight"]
        
        for i in range(5):
            # origin='upper' puts Row 0 at the top. 
            # Since we did flipud, Row 0 is now North, so North is at Top. Correct.
            im = ax[i].imshow(grid_data[:, :, i], cmap=cmaps[i], origin='upper')
            ax[i].set_title(titles[i])
            ax[i].axis('off')
            
        plt.suptitle(f"Bay of Bengal Environment (Corrected North-Up Orientation)")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    loader = OceanEnvironmentGenerator()
    ocean_data = loader.load_and_combine_data()
    loader.save_environment(ocean_data)
    loader.visualize(ocean_data)