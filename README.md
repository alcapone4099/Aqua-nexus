# 🌊 AquaQ Nexus: Multi-Agent Oceanographic Surveillance

**AquaQ Nexus** is a specialized **Multi-Agent Reinforcement Learning (MARL)** platform designed to optimize autonomous ocean monitoring. It simulates a swarm of Autonomous Underwater Vehicles (AUVs) trained to detect high-value oceanographic features (such as Algal Blooms and Hypoxic Zones) in the **Bay of Bengal**.

The project bridges the gap between **Satellite Oceanography** and **Swarm Robotics**, providing a sophisticated web interface for real-time telemetry and explainable AI visualization.

---

## 🌍 1. The Scientific Basis & Data Pipeline

### The Environment: Bay of Bengal

The simulation operates on real-world satellite data coordinates: **Latitude 5°N - 22°N** and **Longitude 80°E - 96°E**.

### Dataset Ingestion

We utilize **NetCDF (.nc)** files sourced from the **Copernicus Marine Service**.
The raw data undergoes a rigorous preprocessing pipeline (`src/data_ingestion.py`):

1. **Time-Averaging:** Compresses 1 month of temporal data into a mean composite to represent persistent ocean conditions.
2. **Geometric Correction:** Applies `np.flipud` to correct satellite indexing, ensuring **North is Top** and **West is Left**.
3. **Logarithmic Scaling (Log1p):** Raw ocean data is heavily skewed (outliers). We apply `log(1 + x)` scaling followed by Min-Max normalization. This preserves massive outliers (pollution spikes) while making subtle gradients (currents/eddies) visible to the AI.

### The 5 Ocean Parameters

The agents monitor five distinct layers, switchable in the UI:

* **Chlorophyll-a (Chl):** Proxy for phytoplankton. High values indicate Algal Blooms.
* **Dissolved Oxygen (O2):** Critical for marine life. Low values (<2ml/L) indicate "Dead Zones."
* **Temperature (SST):** Drivers of cyclogenesis and coral bleaching.
* **Nitrate (NO3):** Nutrient runoff from agriculture (Ganges-Brahmaputra delta).
* **pH:** Monitors ocean acidification trends.

---

## 🧠 2. The Intelligence: Reinforcement Learning (RL)

### Framework

* **Algorithm:** **PPO (Proximal Policy Optimization)**.
* **Library:** `Stable-Baselines3`.
* **Environment:** Custom `Gymnasium` environment (`OceanMonitorEnv`).

### Agent State Space (The Input)

The Neural Network receives a flattened vector for each agent containing:

1. **Position:** Normalized `(x, y)` coordinates.
2. **Energy:** Battery level `(0.0 - 1.0)`.
3. **Sensor Readings:** The exact values of the 5 chemical layers at the current location.

### Action Space (The Output)

A **Discrete** action space with 5 options:

* `0`: **HOLD/SCAN** (Consumes energy, gathers high-fidelity data).
* `1`: **MOVE SOUTH**
* `2`: **MOVE NORTH**
* `3`: **MOVE WEST**
* `4`: **MOVE EAST**

### Reward Function

The swarm is trained to maximize:


* **Positive:** Finding high Chlorophyll concentration (Algae).
* **Negative:** Every movement costs battery. Colliding with other agents applies a heavy penalty to encourage dispersion.

---

## 💻 3. Technical Architecture

### Backend (`/aquaq-web/backend`)

Built with **FastAPI**. It serves as the bridge between the Python simulation and the React frontend.

* **Headless Rendering:** Uses `matplotlib.use('Agg')` to generate high-resolution map tiles on the server side to avoid GUI crashes.
* **Simulation Loop:** Maintains the `OceanEnv` instance and steps it forward upon request.
* **Visual Cortex Extraction:** Slices a **5x5 matrix** around each agent from the global grid to simulate the agent's "local vision."

### Frontend (`/aquaq-web/frontend`)

Built with **React (Vite) + TypeScript**.

* **Styling:** **Tailwind CSS** (Dark Mode / Sci-Fi aesthetic).
* **Visualization:**
* **Global Map:** Real-time Base64 image stream from backend.
* **Visual Cortex:** A dynamic 5x5 grid showing exactly what the selected agent "sees."
* **Telemetry:** `Recharts` line graphs tracking live sensor history.


* **Scientific Context:** Dynamic side-panels explaining the oceanographic significance of the active layer.

---

## 🚀 4. Installation & Setup

### Prerequisites

* Python 3.9+
* Node.js & npm

### Step 1: Clone and Setup Python

```bash
# 1. Create Virtual Env
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 2. Install Python Dependencies
pip install numpy pandas xarray netCDF4 matplotlib scipy gymnasium stable-baselines3 fastapi uvicorn

```

### Step 2: Data Ingestion

Place your 5 `.nc` files in `data/raw/`. Then run the ingestion engine to generate the log-scaled environment.

```bash
python src/data_ingestion.py

```

### Step 3: Train the Swarm

Train the PPO agents on the processed data.

```bash
python src/train.py

```

### Step 4: Launch the Web Platform

**Terminal 1 (Backend):**

```bash
cd aquaq-web/backend
uvicorn app.main:app --reload

```

**Terminal 2 (Frontend):**

```bash
cd aquaq-web/frontend
npm install
npm run dev

```

---

## 📂 5. Project Structure

```text
AquaQ_MARL/
├── data/
│   ├── raw/                   # Source .nc files (Copernicus)
│   └── processed/             # ocean_grid.npy (The simulation world)
├── models/                    # Trained PPO .zip models
├── src/
│   ├── config.py              # Global settings (Lat/Lon, Grid Size)
│   ├── data_ingestion.py      # Log-scaling & Geometric correction logic
│   ├── environment.py         # Gymnasium RL Environment
│   └── train.py               # PPO Training Script
└── aquaq-web/
    ├── backend/
    │   └── app/
    │       ├── main.py        # FastAPI Server & Map Renderer
    │       └── environment.py # Web-specific Sim Wrapper
    └── frontend/
        ├── src/
        │   ├── components/
        │   │   ├── GridMap.tsx    # Global Map Component
        │   │   ├── LocalGrid.tsx  # 5x5 Visual Cortex
        │   │   └── Telemetry.tsx  # Live Sensor Graphs
        │   ├── lib/
        │   │   └── constants.ts   # Unit Conversions & Scientific Text
        │   └── App.tsx            # Main Dashboard Layout

```

---

## ✨ Key Features

1. **Visual Cortex (5x5):**
Allows researchers to debug the agent's behavior by seeing the exact local grid (normalized 0-1) the agent uses for navigation.
2. **Quantum Entropy Metric:**
A visualized metric (Entropy) representing the agent's internal uncertainty. High entropy = "Confused/Searching", Low entropy = "Locked on target".
3. **Real-Time Layer Switching:**
Instantly toggle between Chlorophyll, Temperature, Oxygen, Nitrate, and pH views. The agent's "Visual Cortex" updates its color palette (Viridis, Inferno, Plasma) to match the scientific standard of the active layer.
4. **Physics-Aware Units:**
All data is converted from normalized AI inputs back to real-world units (e.g., **µM** for Nitrate, **°C** for Temp) for display.
