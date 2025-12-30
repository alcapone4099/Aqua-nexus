import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
import sys

# Ensure we can find the src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.environment import OceanMonitorEnv
    from src.config import MODEL_DIR
except ImportError:
    from environment import OceanMonitorEnv
    MODEL_DIR = "./models/" # Fallback

from stable_baselines3 import PPO

# 1. Setup the Simulation
print("🎥 Initializing Visualization...")
env = OceanMonitorEnv()

# Construct model path
model_path = os.path.join(MODEL_DIR, "ppo_swarm_agent_100k.zip")

# Check if model exists
if not os.path.exists(model_path):
    print(f"❌ Error: Model not found at {model_path}")
    print("   Did you run 'python -m src.train' first?")
    sys.exit()

model = PPO.load(model_path)
obs, _ = env.reset()

# 2. Setup the Plot
fig, ax = plt.subplots(figsize=(8, 8))

# Background: The Chlorophyll (Pollution) Map
# We take the first channel [:, :, 0] which is Chlorophyll
ocean_map = env.ocean_data[:, :, 0]
im = ax.imshow(ocean_map, cmap='viridis', origin='upper')
plt.colorbar(im, label="Pollution Level (Chlorophyll)")

# --- FIX START ---
# Get initial positions to initialize scatter plot correctly
initial_pos = np.array(env.agents_pos)
initial_x = initial_pos[:, 1] # Col = X
initial_y = initial_pos[:, 0] # Row = Y

# Agents: 4 Dots of different colors
colors = ['red', 'orange', 'cyan', 'white']
# Initialize with actual data points so 'c' argument matches 'x' and 'y' sizes
agents_scatter = ax.scatter(initial_x, initial_y, c=colors, s=150, edgecolors='black', label='Agents')
# --- FIX END ---

# Text for Step Count
step_text = ax.text(0.02, 0.95, 'Step: 0', transform=ax.transAxes, color='white', weight='bold')

# Legend
ax.legend(loc="lower right")
ax.set_title("Multi-Agent Swarm Tracking Pollution")
ax.grid(False) # Turn off grid lines for clearer view

def update(frame):
    global obs
    
    # Predict Action (Deterministic)
    action, _ = model.predict(obs, deterministic=True)
    obs, _, terminated, _, _ = env.step(action)
    
    # Get Agent Positions
    # env.agents_pos is a list of [row, col] -> we need (x, y) which is (col, row)
    positions = np.array(env.agents_pos)
    
    xs = positions[:, 1]
    ys = positions[:, 0]
    
    # Update Scatter Plot
    agents_scatter.set_offsets(np.c_[xs, ys])
    
    # Update Text
    step_text.set_text(f"Step: {frame}")
    
    if terminated:
        ani.event_source.stop()

    return agents_scatter, step_text

# 3. Create Animation
print("🚀 Generating Animation (this might take a moment)...")
ani = animation.FuncAnimation(fig, update, frames=100, interval=200, blit=True)

# 4. Save
output_path = "swarm_mission.gif"
try:
    ani.save(output_path, writer='pillow', fps=5)
    print(f"💾 Animation saved as '{output_path}'")
    print("✅ Done! Open the GIF to see your agents in action.")
except Exception as e:
    print(f"⚠️ Could not save GIF (missing Pillow/ImageMagick?): {e}")
    plt.show() # Fallback to just showing the window

if __name__ == "__main__":
    pass