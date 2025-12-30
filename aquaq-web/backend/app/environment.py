import numpy as np
import os
import sys

# Point to D:\AquaQ_MARL\data\processed\ocean_grid.npy
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "ocean_grid.npy")

class OceanEnv:
    def __init__(self):
        if os.path.exists(DATA_PATH):
            print(f"✅ Web: Loading Real Data from {DATA_PATH}")
            self.grid = np.load(DATA_PATH) # Shape: (50, 50, 5)
        else:
            print("⚠️ Web: Real data missing. Generating noise.")
            self.grid = np.random.rand(50, 50, 5)
        
        self.grid_h, self.grid_w, _ = self.grid.shape
        self.num_agents = 4
        self.reset()

    def reset(self):
        center = self.grid_h // 2
        # Spawn agents in the middle
        self.agents = [
            {"id": i, "r": center + np.random.randint(-5, 5), "c": center + np.random.randint(-5, 5), "battery": 1.0} 
            for i in range(self.num_agents)
        ]
        self.step_count = 0
        return self.get_state()

    def step(self):
        self.step_count += 1
        for a in self.agents:
            # Simple Logic: Move randomly (You can plug in your PPO model here later)
            action = np.random.randint(0, 5) 
            if action == 1: a["r"] = min(self.grid_h-1, a["r"]+1) # Down
            elif action == 2: a["r"] = max(0, a["r"]-1)            # Up
            elif action == 3: a["c"] = max(0, a["c"]-1)            # Left
            elif action == 4: a["c"] = min(self.grid_w-1, a["c"]+1)# Right
            
            a["battery"] = max(0, a["battery"] - 0.002)
        return self.get_state()

    def get_state(self):
        return {
            "step": self.step_count,
            "agents": self.agents,
            # We don't send the full grid JSON anymore, we render images instead
        }