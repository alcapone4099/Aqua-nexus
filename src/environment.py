import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.config import PROCESSED_DATA_PATH
except ImportError:
    from config import PROCESSED_DATA_PATH

class OceanMonitorEnv(gym.Env):
    """
    MARL Environment: A Swarm of 4 AUVs coordinating to find pollution.
    """
    metadata = {'render_modes': ['console']}

    def __init__(self):
        super(OceanMonitorEnv, self).__init__()
        
        # 1. Load Ocean Data or Generate Realistic Dummy Data
        if os.path.exists(PROCESSED_DATA_PATH):
            print(f"✅ Loading real ocean data from {PROCESSED_DATA_PATH}")
            self.ocean_data = np.load(PROCESSED_DATA_PATH)
        else:
            print("⚠️ Data not found, generating REALISTIC dummy environment...")
            # Create smooth "blobs" instead of random noise
            try:
                from scipy.ndimage import gaussian_filter
                # Generate random noise
                raw_noise = np.random.rand(50, 50, 5).astype(np.float32)
                # Apply Gaussian blur to create "clouds" (Simulating diffusion)
                self.ocean_data = np.zeros_like(raw_noise)
                for i in range(5):
                    self.ocean_data[:,:,i] = gaussian_filter(raw_noise[:,:,i], sigma=2.5)
                
                # Re-normalize to 0-1 after blur
                for i in range(5):
                    d_min, d_max = self.ocean_data[:,:,i].min(), self.ocean_data[:,:,i].max()
                    self.ocean_data[:,:,i] = (self.ocean_data[:,:,i] - d_min) / (d_max - d_min)
                    
            except ImportError:
                print("⚠️ Scipy not installed. Falling back to simple random noise.")
                self.ocean_data = np.random.rand(50, 50, 5).astype(np.float32)

        self.grid_h, self.grid_w, self.channels = self.ocean_data.shape
        
        # --- SWARM CONFIGURATION ---
        self.num_agents = 4
        self.n_actions = 5   # 0=Stay, 1=Up, 2=Down, 3=Left, 4=Right
        
        self.action_space = spaces.MultiDiscrete([self.n_actions] * self.num_agents)

        # Observation Space
        self.obs_per_agent = 3 + self.channels
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(self.obs_per_agent * self.num_agents,), dtype=np.float32
        )

        self.max_steps = 200
        self.agents_pos = [] 
        self.battery = []
        self.current_step = 0
        self.prev_positions = [None] * self.num_agents

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self.agents_pos = []
        self.battery = []
        self.prev_positions = [None] * self.num_agents
        
        center_h, center_w = self.grid_h // 2, self.grid_w // 2
        for _ in range(self.num_agents):
            self.agents_pos.append([
                np.random.randint(center_h - 10, center_h + 10),
                np.random.randint(center_w - 10, center_w + 10)
            ])
            self.battery.append(1.0) 
        
        self.current_step = 0
        return self._get_obs(), {}

    def step(self, actions):
        total_reward = 0
        info = {"pollution_found": [], "collisions": 0}
        new_positions = []

        for i in range(self.num_agents):
            action = actions[i]
            r, c = self.agents_pos[i]
            old_r, old_c = r, c
            
            if self.battery[i] > 0:
                if action == 1: r = min(r + 1, self.grid_h - 1)
                elif action == 2: r = max(r - 1, 0)
                elif action == 3: c = max(c - 1, 0)
                elif action == 4: c = min(c + 1, self.grid_w - 1)
                self.battery[i] -= (0.5 / self.max_steps) 
            
            self.agents_pos[i] = [r, c]
            new_positions.append((r,c))
            
            data = self.ocean_data[r, c]
            chl_level = data[0] 
            
            # REWARD: Focus on High Chlorophyll areas
            total_reward += float(chl_level) * 5.0
            info["pollution_found"].append(chl_level)

            if action == 0 or (r == old_r and c == old_c):
                total_reward -= 0.5 

        unique_locs = len(set(new_positions))
        overlaps = self.num_agents - unique_locs
        if overlaps > 0:
            total_reward -= (overlaps * 2.0)
            info["collisions"] = overlaps

        total_reward -= 0.1 

        self.current_step += 1
        terminated = self.current_step >= self.max_steps
        
        return self._get_obs(), total_reward, terminated, False, info

    def _get_obs(self):
        obs_list = []
        for i in range(self.num_agents):
            r, c = self.agents_pos[i]
            env_data = self.ocean_data[r, c]
            agent_vec = np.concatenate(([r/self.grid_h, c/self.grid_w, self.battery[i]], env_data))
            obs_list.append(agent_vec)
        return np.concatenate(obs_list).astype(np.float32)

if __name__ == "__main__":
    env = OceanMonitorEnv()
    env.reset()
    print("✅ Environment Updated & Ready.")