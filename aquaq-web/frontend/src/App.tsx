import { useState, useEffect } from 'react';
import axios from 'axios';
import { GridMap } from './components/GridMap';
import { LocalGrid } from './components/LocalGrid'; 
import { convertUnit, LAYERS } from './lib/constants';
import { Play, Square, RotateCcw, Cpu, Wifi, Activity, Battery, Crosshair, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Circle } from 'lucide-react';

const API = "http://localhost:8000";

function App() {
  const [data, setData] = useState<any>(null);
  const [activeLayer, setActiveLayer] = useState(0);
  const [selectedAgentId, setSelectedAgentId] = useState(0);
  const [running, setRunning] = useState(false);

  const updateState = async () => {
    try {
      const res = await axios.post(`${API}/state`, { layer: activeLayer });
      setData(res.data);
    } catch (e) { console.error(e); }
  };

  useEffect(() => { updateState(); }, [activeLayer]);

  useEffect(() => {
    let interval: any;
    if (running) {
      interval = setInterval(async () => {
        await axios.post(`${API}/step`);
        updateState();
      }, 500);
    }
    return () => clearInterval(interval);
  }, [running, activeLayer]);

  const reset = async () => { 
    setRunning(false); 
    await axios.post(`${API}/reset`); 
    updateState(); 
  };

  const selectedAgent = data?.agents.find((a: any) => a.id === selectedAgentId);
  const currentLayerInfo = LAYERS[activeLayer as keyof typeof LAYERS];

  // Icon Helper for Actions
  const getActionIcon = (act: string) => {
    if (act === "NORTH") return <ArrowUp size={16} />;
    if (act === "SOUTH") return <ArrowDown size={16} />;
    if (act === "WEST") return <ArrowLeft size={16} />;
    if (act === "EAST") return <ArrowRight size={16} />;
    return <Circle size={10} />;
  }

  return (
    // FIX: Use min-h-screen to allow scrolling if needed
    <div className="min-h-screen w-full bg-black text-white p-6 font-mono">
      
      {/* HEADER */}
      <header className="flex justify-between items-center bg-[#18181b] p-4 rounded-xl mb-6 border border-white/10 shadow-lg sticky top-0 z-50">
        <div className="flex items-center gap-3">
            <div className="p-2 bg-cyan-500/10 rounded-lg"><Cpu className="text-cyan-400" size={24} /></div>
            <div>
                <h1 className="text-xl font-black text-white tracking-widest">AQUAQ <span className="text-cyan-400">NEXUS</span></h1>
                <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase font-bold">
                    <Wifi size={10} className="text-green-500"/> Connection Stable
                </div>
            </div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setRunning(!running)} className={`px-6 py-2 rounded-lg font-bold flex items-center gap-2 transition-all ${running ? 'bg-red-500/20 text-red-500' : 'bg-cyan-500/20 text-cyan-500'}`}>
            {running ? <><Square size={16}/> STOP</> : <><Play size={16}/> RUN</>}
          </button>
          <button onClick={reset} className="p-3 bg-gray-800 rounded-lg hover:bg-gray-700 text-gray-400 hover:text-white"><RotateCcw size={18}/></button>
        </div>
      </header>

      {/* MAIN GRID */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        
        {/* --- LEFT PANEL: MAP & SCIENCE --- */}
        <div className="col-span-1 md:col-span-8 flex flex-col gap-6">
          
          {/* 1. Map View */}
          <div className="bg-[#18181b] rounded-xl p-2 border border-white/10 flex justify-center relative shadow-inner min-h-[500px]">
            {data ? <GridMap mapImage={data.map_image} agents={data.agents} /> : <div className="text-gray-500 self-center">Connecting...</div>}
          </div>
          
          {/* 2. Scientific Context & Layer Controls */}
          <div className="bg-[#18181b] p-6 rounded-xl border border-white/10 flex flex-col gap-4">
            
            {/* Layer Buttons */}
            <div className="flex gap-2 overflow-x-auto">
                {Object.entries(LAYERS).map(([id, l]: any) => (
                <button key={id} onClick={() => setActiveLayer(Number(id))} 
                    className={`flex-1 py-4 px-2 text-xs uppercase tracking-wider rounded-lg font-bold whitespace-nowrap transition-all ${activeLayer === Number(id) ? 'bg-white text-black shadow-lg scale-105' : 'bg-black/30 text-gray-500 hover:text-white'}`}>
                    {l.name}
                </button>
                ))}
            </div>

            {/* Scientific Text */}
            <div className="flex gap-4 items-start p-4 bg-cyan-900/10 rounded-lg border border-cyan-500/20">
                <Activity className="text-cyan-400 shrink-0 mt-1" size={24}/>
                <div>
                    <h3 className="text-sm font-bold text-cyan-400 mb-2 uppercase">Scientific Context: {currentLayerInfo.name}</h3>
                    <p className="text-sm text-gray-300 leading-relaxed font-sans">{currentLayerInfo.desc}</p>
                </div>
            </div>
          </div>
        </div>

        {/* --- RIGHT PANEL: AGENT INSPECTOR --- */}
        <div className="col-span-1 md:col-span-4 bg-[#18181b] rounded-xl border border-white/10 flex flex-col h-fit sticky top-24">
          
          {/* 1. Agent Navigation Tabs */}
          <div className="flex border-b border-white/10">
            {[0, 1, 2, 3].map(id => (
                <button 
                    key={id}
                    onClick={() => setSelectedAgentId(id)}
                    className={`flex-1 py-4 text-xs font-bold uppercase tracking-widest transition-colors ${selectedAgentId === id ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-600 hover:text-gray-300'}`}
                >
                    AG-{id}
                </button>
            ))}
          </div>

          {/* 2. Selected Agent Details */}
          {selectedAgent ? (
            <div className="p-6 flex flex-col gap-6">
                
                {/* Status Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-gray-800 rounded-full border border-gray-600">
                            <Crosshair className="text-white" size={24}/>
                        </div>
                        <div>
                            <div className="text-xl font-black text-white">AGENT-{selectedAgent.id}</div>
                            <div className="text-[10px] text-green-400 font-bold uppercase tracking-widest flex items-center gap-2">
                                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"/> 
                                Operational
                            </div>
                        </div>
                    </div>
                    
                    {/* ACTION DISPLAY */}
                    <div className="text-right bg-black/40 px-3 py-2 rounded border border-white/10">
                        <div className="text-[9px] text-gray-500 uppercase font-bold mb-1">Current Action</div>
                        <div className="text-sm font-bold text-cyan-400 flex items-center justify-end gap-2">
                           {selectedAgent.last_action_desc}
                           {getActionIcon(selectedAgent.last_action_desc)}
                        </div>
                    </div>
                </div>

                <div className="h-px bg-white/10"/>

                {/* VISUAL CORTEX (5x5 GRID) */}
                <div className="flex justify-center py-2">
                    {/* We pass activeLayer so it knows which colormap and unit to use */}
                    <LocalGrid grid={selectedAgent.local_view} layerId={activeLayer} />
                </div>

                {/* STATE VECTOR & BATTERY */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                        <div className="flex items-center gap-2 text-gray-400 text-[10px] uppercase font-bold mb-2">
                            <Battery size={12}/> Battery
                        </div>
                        <div className="text-2xl font-bold text-white">{(selectedAgent.battery * 100).toFixed(0)}%</div>
                        <div className="h-1.5 bg-gray-700 rounded-full mt-2 overflow-hidden">
                            <div style={{width: `${selectedAgent.battery * 100}%`}} className={`h-full ${selectedAgent.battery < 0.3 ? 'bg-red-500' : 'bg-green-500'}`}/>
                        </div>
                    </div>

                    <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                        <div className="flex items-center gap-2 text-gray-400 text-[10px] uppercase font-bold mb-2">
                            <Activity size={12}/> Entropy (Q)
                        </div>
                        <div className="text-2xl font-bold text-purple-400">{selectedAgent.quantum_entropy.toFixed(2)}</div>
                        <div className="text-[9px] text-gray-600 mt-1">Uncertainty Metric</div>
                    </div>
                </div>

                {/* STATE SPACE (RAW SENSORS) */}
                <div className="bg-black/20 p-4 rounded-lg border border-white/5">
                    <div className="text-[10px] text-gray-500 uppercase tracking-widest mb-3 font-bold border-b border-gray-700 pb-1">State Vector (Normalized)</div>
                    <div className="grid grid-cols-5 gap-1 text-center">
                        {selectedAgent.sensors.map((val: number, idx: number) => (
                             <div key={idx} className="bg-gray-900 rounded p-1">
                                <div className="text-[8px] text-gray-500 mb-1">{Object.values(LAYERS)[idx].name.slice(0,3)}</div>
                                <div className="text-[10px] font-mono text-cyan-400">{val.toFixed(2)}</div>
                             </div>
                        ))}
                    </div>
                </div>

            </div>
          ) : (
            <div className="p-10 text-center text-gray-500 animate-pulse">Establishing Uplink...</div>
          )}
        </div>

      </div>
    </div>
  );
}

export default App;