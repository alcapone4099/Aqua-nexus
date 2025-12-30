# 🌊 AquaQ Nexus

A Multi-Agent Reinforcement Learning (MARL) platform for autonomous ocean monitoring.
**System Type:** Multi-Agent Reinforcement Learning (MARL) Simulation for Oceanographic Monitoring.
**Region of Interest:** Bay of Bengal (Lat: 5°N–22°N, Lon: 80°E–96°E).

## 🚀 Features
- **Swarm Intelligence:** 4 Agents trained via PPO to hunt pollution.
- **Real Physics:** Simulates Chlorophyll, Oxygen, Temp, Nitrate, and pH.
- **Interactive Dashboard:** React + TypeScript frontend with live telemetry.

## 🛠️ Installation

### Backend (Python)
```bash
cd AquaQ_MARL
python -m venv venv
# Windows:
.\venv\Scripts\activate
pip install -r requirements.txt
python src/data_ingestion.py  # Generate environment
uvicorn aquaq-web.backend.app.main:app --reload


### 1. The Data Layer (The Environment)

The foundation of the project is real-world earth observation data, not random noise.

* **Source:** Copernicus Marine Service (NetCDF format).
* **Timeframe:** 1-Month Average (Nov 28, 2025 – Dec 28, 2025).
* **The 5 Dimensions (Channels):**
1. **Chlorophyll-a (Chl):** Proxy for phytoplankton and algal blooms.
2. **Dissolved Oxygen (O2):** Critical for marine life; low values indicate "Dead Zones."
3. **Temperature (SST):** Driver of cyclones and coral bleaching.
4. **Nitrate (NO3):** Agricultural runoff/nutrients.
5. **pH:** Ocean acidification monitoring.



**The Preprocessing Pipeline (`data_ingestion.py`):**
Raw satellite data is messy (clouds, land masks, extreme outliers). We apply a rigorous pipeline:

1. **Time Averaging:** We collapse the time dimension to create a stable "Monthly Composite."
2. **Geometric Correction:** Satellite data is indexed South-to-North. We apply `np.flipud` to ensure the map renders with North at the top (Kolkata) and South at the bottom (Sri Lanka).
3. **Logarithmic Scaling:** Ocean data follows a "long tail" distribution (massive outliers). We apply `np.log1p(x)` to "squash" the outliers. This allows the AI (and the human eye) to see subtle gradients in currents and eddies, rather than just one bright spot and a black map.
4. **Normalization:** All data is scaled strictly between `0.0` and `1.0` for the Neural Network.

**Final Output:** A 3D Tensor of shape `(50, 50, 5)` saved as `ocean_grid.npy`.

---

### 2. The Intelligence Layer (Reinforcement Learning)

The "Brains" of the swarm are powered by Deep Reinforcement Learning.

* **Framework:** Stable Baselines3 (PyTorch backend).
* **Algorithm:** **PPO (Proximal Policy Optimization)**. PPO is chosen for its stability and ability to handle continuous/discrete hybrid spaces effectively.
* **Architecture:** **CTDE (Centralized Training, Decentralized Execution)**.
* *Training:* The model learns from the global state.
* *Execution:* Each agent acts based on its local view.



#### The Agent Specifications:

* **State Space (Input Vector):** What the agent "sees" at every timestep.
* `[x, y]` (Normalized Position)
* `[Battery]` (0.0 to 1.0)
* `[Chl, O2, Temp, NO3, pH]` (Sensor readings at current location).
* *Total Input Dimension:* 8 floats per agent.


* **Action Space (Output):** Discrete.
* `0`: Stay/Scan (Higher reward, battery cost).
* `1`: Move South.
* `2`: Move North.
* `3`: Move West.
* `4`: Move East.


* **Reward Function:**
* **+ Positive:** Proportional to the Chlorophyll level found (incentivizes finding pollution).
* **- Negative:** Small penalty for every movement (battery cost) and a larger penalty for colliding or hitting land.



---

### 3. The Backend Layer (FastAPI)

The bridge between the Python simulation and the Web Interface.

* **Technology:** FastAPI (Python).
* **Rendering Engine:** Matplotlib (Running in `Agg` headless mode).
* **Data Flow:**
1. **Global Map Generation:** The backend slices the 3D tensor at the requested layer (e.g., Layer 2 for Temp). It applies the correct colormap (Inferno, Viridis, etc.) and renders it to a PNG image in memory. This is converted to a **Base64 string** and sent to the frontend.
2. **Local Vision Extraction:** The backend extracts a `5x5` sub-grid around the requested agent. This simulates the agent's limited "Visual Cortex."
3. **Physics Simulation:** It calculates the battery drain and position updates based on the move received.



---

### 4. The Frontend Layer (React + TypeScript)

The "Mission Control" dashboard.

* **Framework:** React (Vite).
* **Styling:** Tailwind CSS (Dark Mode/Sci-Fi aesthetic).
* **State Management:** React Hooks (`useState`, `useEffect`) polling the backend every 500ms.

#### Visualization Techniques:

1. **The GridMap (Left Panel):**
* Displays the Base64 Global Map from the backend.
* Overlays HTML `<div>` elements for agents.
* **Animation:** Uses CSS transitions (`duration-500`) to smooth the movement of agents, making them look like they are gliding rather than teleporting.


2. **The Scientific Context:**
* A dynamic text engine that updates descriptions based on the active layer (e.g., explaining Hypoxia when viewing Oxygen).


3. **The "Visual Cortex" (Right Panel):**
* This is the **5x5 Grid**.
* **Data:** Receives raw normalized floats (0.0 - 1.0) from the backend.
* **Color Math:** The frontend performs client-side color interpolation. It takes a value (e.g., `0.8`) and calculates the exact RGB value between the start and end colors of the active colormap (e.g., blending Yellow and Red for Temperature).
* **Unit Conversion:** It takes the normalized float and maps it back to physical units (e.g., `0.5` -> `28.5°C`) using the linear formulas we defined.


4. **Telemetry (Graphs):**
* Uses `Recharts` to plot the history of sensor readings, providing a temporal view of the mission.



---

### 5. Summary of the Workflow

1. **Ingestion:** Python reads Satellite NC files -> Creates `ocean_grid.npy`.
2. **Training:** PPO Agent interacts with this grid to learn a policy -> Saves `ppo_swarm.zip`.
3. **Server:** FastAPI loads the grid + PPO model.
4. **Client:** React requests "State".
5. **Response:** Server returns `{MapImage (Base64), AgentPositions, LocalGrid(5x5), SensorReadings}`.
6. **Render:** React draws the map, interpolates the colors for the local grid, and updates the graphs.

This system is now a closed-loop "Digital Twin" of a real ocean monitoring mission.
