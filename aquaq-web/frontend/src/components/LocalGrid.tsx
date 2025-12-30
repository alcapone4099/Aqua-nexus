import React from 'react';
import { getMapColor, convertUnit, LAYERS } from '../lib/constants';

export const LocalGrid = ({ grid, layerId }: any) => {
  if (!grid) return <div className="text-gray-500 text-xs">NO SIGNAL</div>;

  const layerInfo = LAYERS[layerId as keyof typeof LAYERS];

  return (
    <div className="flex flex-col items-center">
      <div className="text-[10px] text-gray-500 mb-1 uppercase tracking-widest font-bold">
        Visual Cortex ({layerInfo.name})
      </div>
      
      {/* Grid Container */}
      <div className="grid grid-cols-5 gap-0.5 p-1 bg-black rounded border border-gray-700 shadow-xl">
        {grid.map((row: number[], rIdx: number) => (
            row.map((val: number, cIdx: number) => {
                const isCenter = rIdx === 2 && cIdx === 2;
                
                // 1. Get Color based on Map Type (Viridis/Inferno/etc)
                const bgColor = getMapColor(val, layerInfo.cmap);
                
                // 2. Get Real Scientific Value
                // If val is -1 (padding), show nothing
                const displayVal = val === -1 ? '' : convertUnit(val, layerId);
                
                return (
                    <div 
                        key={`${rIdx}-${cIdx}`}
                        className={`
                          w-10 h-10 flex items-center justify-center text-[10px] font-mono font-bold
                          transition-all duration-300 rounded-sm
                          ${isCenter ? 'ring-2 ring-white z-10' : ''}
                        `}
                        style={{ 
                            backgroundColor: bgColor,
                            // If background is very bright, make text black. Else white.
                            color: val > 0.6 ? 'black' : 'white'
                        }}
                    >
                      {displayVal}
                    </div>
                )
            })
        ))}
      </div>
      
      <div className="mt-1 text-[9px] text-gray-500 flex gap-2">
        <span>Unit: {layerInfo.unit}</span>
      </div>
    </div>
  );
};