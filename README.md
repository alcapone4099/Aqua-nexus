# 🌊 AquaQ Nexus

A Multi-Agent Reinforcement Learning (MARL) platform for autonomous ocean monitoring.

## 🚀 Features
- **Swarm Intelligence:** 4 Agents trained via PPO to hunt pollution.
- **Real Physics:** Simulates Chlorophyll, Oxygen, Temp, Nitrate, and pH.
- **Interactive Dashboard:** React + TypeScript frontend with live telemetry.

## 🛠️ Installation

### 1. Backend (Python)
```bash
cd AquaQ_MARL
python -m venv venv
# Windows:
.\venv\Scripts\activate
pip install -r requirements.txt
python src/data_ingestion.py  # Generate environment
uvicorn aquaq-web.backend.app.main:app --reload