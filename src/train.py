import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import os
import time
import sys
import numpy as np

# --- 1. Path Setup (Crucial for Imports) ---
# This ensures Python can find 'src' even if you run from different folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.environment import OceanMonitorEnv
    from src.config import LOG_DIR, MODEL_DIR
except ImportError:
    # Fallback if running directly as a script without the package structure
    from environment import OceanMonitorEnv
    # Define default paths if config import fails
    LOG_DIR = "./logs/MARL_PPO/"
    MODEL_DIR = "./models/"

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

def train_swarm():
    """
    Trains a Centralized PPO Agent that controls 4 Underwater Drones simultaneously.
    """
    print("🚀 Initializing Multi-Agent Swarm Environment...")
    
    # Create the environment and wrap it for the agent
    # DummyVecEnv is standard for single-process training in Stable Baselines3
    env = DummyVecEnv([lambda: OceanMonitorEnv()])

    print("🧠 Defining Swarm Commander (PPO Brain)...")
    
    # NETWORK ARCHITECTURE:
    # We use a larger neural network (256x256 neurons) compared to single-agent.
    # Why? The input state is huge (32 values: 8 features * 4 agents).
    # The brain needs more capacity to process the correlations between agents.
    policy_kwargs = dict(net_arch=[256, 256])

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,               # 1 = Info, 0 = Silent
        learning_rate=0.0003,    # Standard robust learning rate
        n_steps=2048,            # Steps per update buffer
        batch_size=64,           # Batch size for gradient descent
        gamma=0.99,              # Discount factor (Long-term planning)
        policy_kwargs=policy_kwargs,
        tensorboard_log=LOG_DIR,
        device="auto"            # Uses GPU if available
    )

    # --- TRAINING PHASE ---
    TRAINING_STEPS = 100_000
    print(f"🏋️‍♂️ Starting Swarm Training ({TRAINING_STEPS} steps)...")
    print("   (Agents are learning to coordinate and avoid collisions)")
    
    start_time = time.time()
    
    model.learn(total_timesteps=TRAINING_STEPS)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Training Complete in {duration:.2f} seconds ({duration/60:.2f} min)!")
    
    # Save the Trained Model
    save_path = os.path.join(MODEL_DIR, "ppo_swarm_agent_100k.zip")
    model.save(save_path)
    print(f"💾 Hive Mind Model saved to: {save_path}")
    
    return model, save_path

def test_swarm(model_path):
    """
    Loads the trained model and visualizes a test mission.
    """
    print("\n🕵️‍♂️ Testing Trained Swarm Performance...")
    
    # Re-initialize environment for testing
    env = OceanMonitorEnv()
    
    # Load the specific model file
    model = PPO.load(model_path)
    
    obs, _ = env.reset()
    total_reward = 0
    terminated = False
    step_count = 0
    
    # Visualization Header
    print("-" * 80)
    print(f"{'Step':<5} | {'Ag1 Chl':<8} | {'Ag2 Chl':<8} | {'Ag3 Chl':<8} | {'Ag4 Chl':<8} | {'Action Vector (Ag1-4)'}")
    print("-" * 80)

    # Run a short simulation (max 20 steps for display)
    while not terminated and step_count < 20:
        # Predict best action (Deterministic = True means no randomness, pure skill)
        action, _ = model.predict(obs, deterministic=True)
        
        obs, reward, terminated, _, info = env.step(action)
        total_reward += reward
        step_count += 1
        
        # Parse Info for display
        p = info['pollution_found'] # List of 4 values
        
        # Display Row
        # Action is an array like [1, 0, 4, 3]
        print(f"{step_count:<5} | {p[0]:.4f}   | {p[1]:.4f}   | {p[2]:.4f}   | {p[3]:.4f}   | {action}")

    print("-" * 80)
    print(f"🏁 Test Mission Finished. Total Collective Reward: {total_reward:.2f}")

if __name__ == "__main__":
    # 1. Train
    model, path = train_swarm()
    
    # 2. Test immediately using the path of the saved model
    test_swarm(path)