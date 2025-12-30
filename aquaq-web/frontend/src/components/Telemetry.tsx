import React from 'react';
import { LineChart, Line, YAxis, ResponsiveContainer } from 'recharts';
import { LAYERS } from '../lib/constants';

export const Telemetry = ({ history }: any) => {
  // We track Agent 0 (Swarm Leader) for the main graphs
  const agent0Data = history[0] || [];

  return (
    <div className="h-full overflow-y-auto pr-2 space-y-4">
      {Object.entries(LAYERS).slice(1).map(([id, layer]: any) => (
        <div key={id} className="bg-[#18181b] p-3 rounded-xl border border-white/10 shadow-lg">
          <div className="flex justify-between text-xs font-bold mb-2" style={{color: layer.color}}>
            <span className="uppercase tracking-wider">{layer.name}</span>
            <span className="bg-black/40 px-2 rounded">
              {agent0Data.length > 0 ? agent0Data[agent0Data.length-1][`l${id}`] : '--'} {layer.unit}
            </span>
          </div>
          <div className="h-16 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={agent0Data}>
                <YAxis domain={['auto', 'auto']} hide />
                <Line 
                  type="monotone" 
                  dataKey={`l${id}`} 
                  stroke={layer.color} 
                  strokeWidth={2} 
                  dot={false}
                  isAnimationActive={false} // Improves performance for live data
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      ))}
    </div>
  );
};