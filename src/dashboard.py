import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import numpy as np
import os
import sys
from collections import deque

# Ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.environment import OceanMonitorEnv
    from src.config import MODEL_DIR
except ImportError:
    from environment import OceanMonitorEnv
    MODEL_DIR = "./models/"

from stable_baselines3 import PPO

# --- 1. REALISM CONFIGURATION ---
class UnitConverter:
    """
    Converts normalized AI inputs (0-1) to realistic Bay of Bengal physical units.
    Ranges based on typical oceanographic data for the region.
    """
    @staticmethod
    def convert(value, sensor_type):
        # Clip input to 0-1 just in case
        val = max(0.0, min(1.0, value))
        
        if sensor_type == 'o2':
            # Dissolved Oxygen: 3.0 - 7.0 ml/L (Healthy ocean surface)
            return 3.0 + (val * 4.0)
        
        elif sensor_type == 'temp':
            # SST (Sea Surface Temp): 26°C - 31°C (Tropical Bay of Bengal)
            return 26.0 + (val * 5.0)
            
        elif sensor_type == 'no3':
            # Nitrate: 0 - 5 micromolar (µM) (Usually low at surface)
            return val * 5.0
            
        elif sensor_type == 'ph':
            # pH: 8.05 - 8.25 (Ocean is very stable alkaline)
            return 8.05 + (val * 0.20)
            
        return val

# --- 2. SETUP SIMULATION ---
print("🎥 Booting Robust Mission Control...")
env = OceanMonitorEnv()
model_path = os.path.join(MODEL_DIR, "ppo_swarm_agent_100k.zip")

# Fallback for visualization if model doesn't exist yet
if not os.path.exists(model_path):
    print(f"⚠️ Warning: Model not found at {model_path}. Visualizing random agent.")
    model = None
else:
    model = PPO.load(model_path)

obs, _ = env.reset()

# --- 3. SETUP DASHBOARD LAYOUT ---
plt.style.use('dark_background') 
fig = plt.figure(figsize=(16, 9))
fig.suptitle("Swarm Intelligence: Live Sensor Telemetry (Bay of Bengal)", fontsize=16, weight='bold', color='white')

gs = GridSpec(4, 2, figure=fig, width_ratios=[1.5, 1])

# Left Panel: Tactical Map
ax_map = fig.add_subplot(gs[:, 0])
ocean_map = env.ocean_data[:, :, 0] # Chlorophyll view
im = ax_map.imshow(ocean_map, cmap='viridis', origin='upper')
plt.colorbar(im, ax=ax_map, label="Chlorophyll Density (Normalized)", fraction=0.046, pad=0.04)
ax_map.set_title("Tactical View: Chlorophyll Blobs", color='white')

# Agents (Scatter)
initial_pos = np.array(env.agents_pos)
colors = ['#ff3333', '#ffaa00', '#00ffff', '#ffffff'] 
agents_scatter = ax_map.scatter(initial_pos[:, 1], initial_pos[:, 0], c=colors, s=180, edgecolors='black', label='Swarm')
ax_map.legend(loc="upper right", facecolor='#333333', labelcolor='white')

# Right Panel: 4 Sensor Graphs
ax_o2 = fig.add_subplot(gs[0, 1])
ax_temp = fig.add_subplot(gs[1, 1])
ax_no3 = fig.add_subplot(gs[2, 1])
ax_ph = fig.add_subplot(gs[3, 1])

# Initialize History with Realistic Values
r, c = env.agents_pos[0]
raw_data = env.ocean_data[r, c] # [Chl, O2, Temp, No3, pH]
MAX_HISTORY = 100

history = {
    'o2': deque([UnitConverter.convert(raw_data[1], 'o2')] * MAX_HISTORY, maxlen=MAX_HISTORY),
    'temp': deque([UnitConverter.convert(raw_data[2], 'temp')] * MAX_HISTORY, maxlen=MAX_HISTORY),
    'no3': deque([UnitConverter.convert(raw_data[3], 'no3')] * MAX_HISTORY, maxlen=MAX_HISTORY),
    'ph': deque([UnitConverter.convert(raw_data[4], 'ph')] * MAX_HISTORY, maxlen=MAX_HISTORY)
}

# Lines
x_axis = np.arange(MAX_HISTORY)
line_o2, = ax_o2.plot(x_axis, history['o2'], 'c-', lw=2)
line_temp, = ax_temp.plot(x_axis, history['temp'], 'r-', lw=2)
line_no3, = ax_no3.plot(x_axis, history['no3'], 'g-', lw=2)
line_ph, = ax_ph.plot(x_axis, history['ph'], 'm-', lw=2)

def setup_plot(ax, title, unit, color):
    ax.set_ylabel(f"{title}\n({unit})", fontsize=9, weight='bold', color=color)
    ax.grid(True, linestyle='--', alpha=0.2, color='white')
    ax.set_xlim(0, MAX_HISTORY - 1)
    ax.set_xticklabels([])

setup_plot(ax_o2, "Oxygen", "ml/L", 'cyan')
setup_plot(ax_temp, "Temperature", "°C", 'red')
setup_plot(ax_no3, "Nitrate", "µM", 'lightgreen')
setup_plot(ax_ph, "pH Level", "Scale", 'magenta')

# --- 4. UPDATE LOOP ---
def update(frame):
    global obs
    
    # 1. AI Action
    if model:
        action, _ = model.predict(obs, deterministic=False) 
    else:
        action = env.action_space.sample() # Random fallback
        
    obs, _, terminated, _, _ = env.step(action)
    
    if terminated:
        obs, _ = env.reset()
    
    # 2. Update Map Agents
    pos = np.array(env.agents_pos)
    agents_scatter.set_offsets(np.c_[pos[:, 1], pos[:, 0]])
    
    # 3. Update Sensors (Agent 1)
    r, c = env.agents_pos[0]
    data = env.ocean_data[r, c] # [Chl, O2, Temp, No3, pH]
    
    # CONVERT TO REAL UNITS BEFORE PLOTTING
    history['o2'].append(UnitConverter.convert(data[1], 'o2'))
    history['temp'].append(UnitConverter.convert(data[2], 'temp'))
    history['no3'].append(UnitConverter.convert(data[3], 'no3'))
    history['ph'].append(UnitConverter.convert(data[4], 'ph'))
    
    # 4. Dynamic Scaling
    def update_line(line, ax, data_deque):
        data_list = list(data_deque)
        line.set_ydata(data_list)
        
        min_val = min(data_list)
        max_val = max(data_list)
        # Add buffer
        padding = (max_val - min_val) * 0.2 if max_val != min_val else 0.1
        ax.set_ylim(min_val - padding, max_val + padding)

    update_line(line_o2, ax_o2, history['o2'])
    update_line(line_temp, ax_temp, history['temp'])
    update_line(line_no3, ax_no3, history['no3'])
    update_line(line_ph, ax_ph, history['ph'])

    return agents_scatter, line_o2, line_temp, line_no3, line_ph

# --- 5. ANIMATE ---
print("🚀 Dashboard Live. Close window to stop.")
ani = animation.FuncAnimation(fig, update, frames=None, interval=100, blit=False, cache_frame_data=False)

plt.tight_layout()
plt.show()