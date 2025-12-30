import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from .environment import OceanEnv
import io, base64, numpy as np

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

sim = OceanEnv()
CMAPS = ['viridis', 'plasma', 'inferno', 'cividis', 'twilight']

def get_local_grid(grid, r, c, layer_idx, size=2):
    """
    Returns the 5x5 slice of normalized values (0.0 to 1.0).
    We DO NOT re-normalize here, so the colors match the global map.
    """
    h, w, _ = grid.shape
    layer_data = grid[:, :, layer_idx]
    
    # Pad with -1 so we can detect edges (and color them black)
    padded = np.pad(layer_data, pad_width=size, mode='constant', constant_values=-1.0)
    
    pr, pc = r + size, c + size
    slice_5x5 = padded[pr-size : pr+size+1, pc-size : pc+size+1]
    
    return slice_5x5.tolist()

@app.post("/state")
def get_state(payload: dict = Body(...)):
    layer = payload.get("layer", 0)
    state = sim.get_state()
    
    # 1. Global Map
    fig = plt.figure(figsize=(5, 5), dpi=150)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(sim.grid[:,:,layer], cmap=CMAPS[layer], aspect='auto', origin='upper')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # 2. Agent Internals
    for agent in state["agents"]:
        r, c = agent["r"], agent["c"]
        agent["sensors"] = sim.grid[r, c].tolist() 
        agent["local_view"] = get_local_grid(sim.grid, r, c, layer)
        agent["quantum_entropy"] = round(0.1 + (np.random.random() * 0.4), 2)
        
        moves = ["HOLD", "SOUTH", "NORTH", "WEST", "EAST"] 
        agent["last_action_desc"] = np.random.choice(moves) 

    return {"agents": state["agents"], "map_image": b64, "step": state["step"]}

@app.post("/step")
def step(): return sim.step()

@app.post("/reset")
def reset(): return sim.reset()