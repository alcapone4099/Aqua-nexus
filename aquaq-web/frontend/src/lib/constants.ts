export const LAYERS = {
  0: { name: 'Chlorophyll', unit: 'Index', cmap: 'viridis', desc: "Chlorophyll-a concentration indicates phytoplankton biomass. High levels often suggest algal blooms fueled by agricultural runoff." },
  1: { name: 'Oxygen', unit: 'ml/L', cmap: 'plasma', desc: "Dissolved Oxygen (DO). Levels below 2 ml/L indicate Hypoxia (Dead Zones). Blue/Purple indicates low oxygen." },
  2: { name: 'Temperature', unit: '°C', cmap: 'inferno', desc: "Sea Surface Temperature (SST). Dark is cold, Yellow/Orange is warm. Drives cyclone formation." },
  3: { name: 'Nitrate', unit: 'µM', cmap: 'cividis', desc: "Nitrate Nutrients. Essential for algae but toxic in excess. Yellow indicates high concentration." },
  4: { name: 'pH', unit: 'pH', cmap: 'twilight', desc: "Ocean Acidity. Tracks carbon absorption. Purple/Pink gradients indicate pH shifts." },
};

export const convertUnit = (val: number, type: number) => {
  const v = Math.max(0, Math.min(1, val));
  switch (type) {
    case 1: return (3.0 + v * 4.0).toFixed(2); // O2
    case 2: return (26.0 + v * 5.0).toFixed(1); // Temp
    case 3: return (v * 5.0).toFixed(2); // Nitrate
    case 4: return (8.05 + v * 0.20).toFixed(2); // pH
    default: return v.toFixed(2); // Chl
  }
};

// --- COLOR INTERPOLATION LOGIC ---
const interpolate = (val: number, colors: string[]) => {
  // val is 0..1
  if (val <= 0) return colors[0];
  if (val >= 1) return colors[colors.length - 1];
  
  const step = 1 / (colors.length - 1);
  const idx = Math.floor(val / step);
  const r = (val - (idx * step)) / step; // remainder
  
  const c1 = hexToRgb(colors[idx]);
  const c2 = hexToRgb(colors[idx + 1]);
  
  const result = [
    Math.round(c1[0] + (c2[0] - c1[0]) * r),
    Math.round(c1[1] + (c2[1] - c1[1]) * r),
    Math.round(c1[2] + (c2[2] - c1[2]) * r)
  ];
  return `rgb(${result[0]}, ${result[1]}, ${result[2]})`;
};

const hexToRgb = (hex: string) => {
  const bigint = parseInt(hex.replace('#', ''), 16);
  return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
};

// Approximations of Matplotlib Colormaps
const CMAPS: any = {
  viridis: ['#440154', '#3b528b', '#21918c', '#5ec962', '#fde725'],
  plasma:  ['#0d0887', '#6a00a8', '#b12a90', '#e16462', '#fca636'],
  inferno: ['#000004', '#420a68', '#932667', '#dd513a', '#fcffa4'],
  cividis: ['#002051', '#39456B', '#7C7B78', '#BFBCC0', '#FDEA45'],
  twilight:['#e2d9e2', '#697c98', '#462d4e', '#883348', '#d09081'],
};

export const getMapColor = (value: number, cmapName: string) => {
  if (value === -1) return '#000000'; // Edge/Padding
  return interpolate(value, CMAPS[cmapName] || CMAPS.viridis);
};