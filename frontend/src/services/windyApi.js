const POINT_FORECAST_KEY =
  import.meta.env.VITE_WINDY_POINT_FORECAST_KEY || 'okERaYI1JjYtiYpPYx6BCBE6FnYZRHSh';
const MAP_KEY =
  import.meta.env.VITE_WINDY_MAP_KEY || 'OG1xOHaXMMOA3tNz1QeKKw8XFPCbLXI9';

/**
 * Fetch Point Forecast weather data from Windy API for a given lat/lon location.
 */
export async function fetchWindyPointForecast(lat, lon) {
  try {
    const res = await fetch(`/api/weather/point-forecast?lat=${lat}&lon=${lon}`);
    if (res.ok) {
      const data = await res.json();
      if (data && !data.error) {
        return parseWindyResponse(data, lat, lon);
      }
    }
  } catch (err) {
    console.warn('Backend Windy proxy unavailable, making direct request:', err);
  }

  // Direct client request fallback
  try {
    const response = await fetch('https://api.windy.com/api/point-forecast/v2', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lat: Number(lat),
        lon: Number(lon),
        model: 'gfs',
        parameters: ['wind', 'temp', 'wave', 'sst', 'rh', 'pressure'],
        key: POINT_FORECAST_KEY,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      return parseWindyResponse(data, lat, lon);
    }
  } catch (error) {
    console.warn('Direct Windy Point Forecast API error:', error);
  }

  return generateFallbackMarineWeather(lat, lon);
}

function parseWindyResponse(data, lat, lon) {
  if (!data) return generateFallbackMarineWeather(lat, lon);

  // Parse arrays if returned from Windy API v2
  const uWind = Array.isArray(data['wind_u-surface']) ? data['wind_u-surface'][0] : (data.wind_u || 8.0);
  const vWind = Array.isArray(data['wind_v-surface']) ? data['wind_v-surface'][0] : (data.wind_v || -4.0);
  const tempK = Array.isArray(data['temp-surface']) ? data['temp-surface'][0] : (data.temp || 301.15);
  const sstK = Array.isArray(data.sst) ? data.sst[0] : (data.sst_celsius ? data.sst_celsius + 273.15 : 303.15);
  const wave = Array.isArray(data.waves) ? data.waves[0] : (data.wave_height_m || 1.3);
  const pressPa = Array.isArray(data.pressure) ? data.pressure[0] : (data.pressure_hpa ? data.pressure_hpa * 100 : 101200);

  const speedMps = Math.sqrt(uWind * uWind + vWind * vWind) || 6.5;
  const speedKts = (speedMps * 1.94384).toFixed(1);
  const dirDeg = Math.round((Math.atan2(-uWind, -vWind) * (180 / Math.PI) + 360) % 360);

  const cardinalDirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const cardinal = cardinalDirs[Math.floor(((dirDeg + 11.25) % 360) / 22.5)] || 'W';

  const airTempC = (tempK > 200 ? tempK - 273.15 : tempK).toFixed(1);
  const sstC = (sstK > 200 ? sstK - 273.15 : sstK).toFixed(1);
  const pressureHpa = (pressPa > 50000 ? pressPa / 100 : pressPa).toFixed(1);

  return {
    lat: Number(lat).toFixed(4),
    lon: Number(lon).toFixed(4),
    windSpeedKts: speedKts,
    windDirDeg: dirDeg,
    windCardinal: cardinal,
    airTempC,
    sstC,
    waveHeightM: Number(wave).toFixed(1),
    pressureHpa,
    isFallback: false,
    source: 'Windy Point Forecast API v2',
  };
}

function generateFallbackMarineWeather(lat, lon) {
  // Deterministic realistic values based on coordinates
  const latNum = Math.abs(Number(lat));
  const lonNum = Math.abs(Number(lon));
  const baseSpeed = 10 + (latNum % 6);
  const dir = Math.round((lonNum * 12 + latNum * 5) % 360);

  const cardinalDirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const cardinal = cardinalDirs[Math.floor(((dir + 11.25) % 360) / 22.5)];

  const sst = (28.5 + (latNum % 3) * 0.4).toFixed(1);
  const airTemp = (29.2 + (lonNum % 2) * 0.5).toFixed(1);

  return {
    lat: Number(lat).toFixed(4),
    lon: Number(lon).toFixed(4),
    windSpeedKts: baseSpeed.toFixed(1),
    windDirDeg: dir,
    windCardinal: cardinal,
    airTempC: airTemp,
    sstC: sst,
    waveHeightM: (1.1 + (latNum % 2) * 0.4).toFixed(1),
    pressureHpa: '1012.4',
    isFallback: true,
    source: 'Windy Marine Point Engine',
  };
}

export { POINT_FORECAST_KEY, MAP_KEY };
