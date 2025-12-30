import React from 'react';

export const GridMap = ({ mapImage, agents }: any) => {
  return (
    <div className="relative w-full aspect-square bg-black rounded-xl overflow-hidden shadow-2xl border-2 border-gray-700">
      {/* 1. Map Image from Backend */}
      {mapImage ? (
        <img src={`data:image/png;base64,${mapImage}`} className="w-full h-full object-cover" />
      ) : (
        <div className="flex h-full items-center justify-center text-gray-500 animate-pulse">
          Connecting to Satellite Feed...
        </div>
      )}
      
      {/* 2. Agents Overlay */}
      {agents && agents.map((agent: any) => (
        <div 
          key={agent.id} 
          className="absolute z-10 transition-all duration-500 ease-linear"
          // Map 0-50 grid coordinates to 0-100% CSS positioning
          style={{ 
            left: `${(agent.c / 50) * 100}%`, 
            top: `${(agent.r / 50) * 100}%`, 
            transform: 'translate(-50%, -50%)' 
          }}
        >
           {/* Pulsing UI Effect */}
           <div className="relative flex items-center justify-center">
             <div className="absolute w-8 h-8 bg-white/30 rounded-full animate-ping" />
             <div className="w-4 h-4 bg-white border-2 border-black rounded-full shadow-md z-20" />
             <span className="absolute -top-6 text-[10px] font-bold text-white bg-black/50 px-1 rounded border border-white/20">
               AG-{agent.id}
             </span>
           </div>
        </div>
      ))}
    </div>
  );
};