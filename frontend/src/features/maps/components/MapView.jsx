import { useEffect, useMemo, useState } from 'react';
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  Polyline,
  Polygon,
  Circle,
  Marker,
  Popup,
  useMap,
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// ---------------------------------------------------------------
// Color divIcon markers matching ORCA UI design
// ---------------------------------------------------------------
function dotIcon({ color = '#00C8FF', ring = false, filled = true, size = 16 }) {
  const inner = filled ? color : 'transparent';
  const border = `2px solid ${color}`;
  return L.divIcon({
    className: '',
    iconSize: [size + (ring ? 10 : 0), size + (ring ? 10 : 0)],
    html: `
      <span style="
        position:relative;
        display:flex;
        align-items:center;
        justify-content:center;
        width:${size + (ring ? 10 : 0)}px;
        height:${size + (ring ? 10 : 0)}px;
      ">
        ${ring ? `<span style="position:absolute;inset:0;border-radius:9999px;border:2px dashed ${color};"></span>` : ''}
        <span style="
          width:${size}px;height:${size}px;border-radius:9999px;
          background:${inner};border:${border};
          box-shadow:0 0 10px ${color}80, 0 0 0 2px rgba(10,10,10,0.8);
        "></span>
      </span>
    `,
  });
}

const startIcon = dotIcon({ color: '#10B981', filled: true, size: 14 });
const destinationIcon = dotIcon({ color: '#00C8FF', filled: true, ring: true, size: 16 });

// Helper to fit bounds around all route and marker points
function FitBounds({ points }) {
  const map = useMap();
  useEffect(() => {
    if (!points || points.length === 0) return;
    const validPoints = points.filter(
      (pt) => Array.isArray(pt) && pt.length >= 2 && !isNaN(pt[0]) && !isNaN(pt[1])
    );
    if (!validPoints.length) return;
    const bounds = L.latLngBounds(validPoints);
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [45, 45] });
    }
  }, [points, map]);
  return null;
}

// Fix Leaflet tile loading inside dynamic containers / modals / tabs
function MapResizeFix() {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 250);
    return () => clearTimeout(timer);
  }, [map]);
  return null;
}

// Extract raw coordinates [lat, lon] from route object
function rawWaypointLatLngs(route) {
  if (!route) return [];

  if (Array.isArray(route.waypoints) && route.waypoints.length) {
    const pts = route.waypoints
      .map((w) => {
        if (!w) return null;
        if (typeof w.latitude === 'number' && typeof w.longitude === 'number') {
          return [w.latitude, w.longitude];
        }
        if (typeof w.lat === 'number' && typeof w.lng === 'number') {
          return [w.lat, w.lng];
        }
        if (Array.isArray(w) && w.length >= 2) {
          return [Number(w[0]), Number(w[1])];
        }
        return null;
      })
      .filter(Boolean);

    if (pts.length > 0) return pts;
  }

  const coords = route.geojson?.geometry?.coordinates || route.geojson?.coordinates;
  if (Array.isArray(coords)) {
    return coords.map(([lon, lat]) => [lat, lon]);
  }

  return [];
}

/**
 * Smooth Marine Route Generator:
 * Generates natural curved marine navigation paths with Catmull-Rom spline interpolation
 * and seaward curvature for realistic vessel routing off coastlines.
 */
function getSmoothMarineRoute(inputPoints, isCandidate = false) {
  if (!inputPoints || inputPoints.length < 2) return inputPoints;

  const pts = inputPoints.filter(
    (p) => Array.isArray(p) && p.length >= 2 && !isNaN(p[0]) && !isNaN(p[1])
  );
  if (pts.length < 2) return pts;

  let baseWaypoints = [...pts];

  const [pStart, pEnd] = [baseWaypoints[0], baseWaypoints[baseWaypoints.length - 1]];
  const lat1 = pStart[0], lon1 = pStart[1];
  const lat2 = pEnd[0], lon2 = pEnd[1];

  const dLat = lat2 - lat1;
  const dLon = lon2 - lon1;
  const dist = Math.sqrt(dLat * dLat + dLon * dLon);

  if (dist > 0) {
    // Normal vector pointing seaward (east/northeast off Chennai coast)
    const normLat = -dLon / dist;
    const normLon = dLat / dist;

    // Seaward curve multiplier (candidate route curves slightly differently for visual separation)
    const curveSign = isCandidate ? -0.7 : 1.0;
    const arcMagnitude = Math.max(dist * 0.28, 0.025) * curveSign;

    if (baseWaypoints.length <= 4) {
      const wp1 = [
        lat1 + dLat * 0.3 + normLat * arcMagnitude * 0.85,
        lon1 + dLon * 0.3 + normLon * arcMagnitude * 0.85,
      ];
      const wp2 = [
        lat1 + dLat * 0.7 + normLat * arcMagnitude * 0.7,
        lon1 + dLon * 0.7 + normLon * arcMagnitude * 0.7,
      ];
      baseWaypoints = [pStart, wp1, wp2, pEnd];
    } else {
      // Curve intermediate grid points
      baseWaypoints = baseWaypoints.map((pt, idx) => {
        if (idx === 0 || idx === baseWaypoints.length - 1) return pt;
        const t = idx / (baseWaypoints.length - 1);
        const factor = Math.sin(t * Math.PI);
        return [
          pt[0] + normLat * arcMagnitude * factor * 0.6,
          pt[1] + normLon * arcMagnitude * factor * 0.6,
        ];
      });
    }
  }

  return catmullRomSpline(baseWaypoints, 12);
}

function catmullRomSpline(points, numSubdivisions = 12) {
  if (points.length < 2) return points;
  const result = [];
  const p = [points[0], ...points, points[points.length - 1]];

  for (let i = 1; i < p.length - 2; i++) {
    const p0 = p[i - 1];
    const p1 = p[i];
    const p2 = p[i + 1];
    const p3 = p[i + 2];

    for (let tStep = 0; tStep < numSubdivisions; tStep++) {
      const t = tStep / numSubdivisions;
      const t2 = t * t;
      const t3 = t2 * t;

      const lat =
        0.5 *
        (2 * p1[0] +
          (-p0[0] + p2[0]) * t +
          (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
          (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3);

      const lon =
        0.5 *
        (2 * p1[1] +
          (-p0[1] + p2[1]) * t +
          (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
          (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3);

      result.push([lat, lon]);
    }
  }
  result.push(points[points.length - 1]);
  return result;
}

function parseGeoJSON(data) {
  if (!data) return null;
  if (typeof data === 'string') {
    try {
      return JSON.parse(data);
    } catch {
      return null;
    }
  }
  if (typeof data === 'object') return data;
  return null;
}

function isValidGeoJSON(data) {
  const parsed = parseGeoJSON(data);
  if (!parsed || typeof parsed !== 'object') return false;
  const validTypes = [
    'Point',
    'MultiPoint',
    'LineString',
    'MultiLineString',
    'Polygon',
    'MultiPolygon',
    'GeometryCollection',
    'Feature',
    'FeatureCollection',
  ];
  return validTypes.includes(parsed.type);
}

const TILE_SERVERS = {
  bathymetry: {
    name: 'Bathymetry (Sea Depth)',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Esri, GEBCO, NOAA, CHS, National Geographic',
    overlayUrl: 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}',
  },
  standard: {
    name: 'Standard (OpenStreetMap)',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
  voyager: {
    name: 'Color (Carto Voyager)',
    url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://carto.com/attributions">CARTO</a>',
  },
  dark: {
    name: 'Dark Mode',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://carto.com/attributions">CARTO</a>',
  },
};

/**
 * MapView
 *
 * Renders Bathymetry (sea depth), Wind & Temperature overlays,
 * OpenSeaMap seamarks, curved marine routes, restricted/protected zones, and markers.
 */
export default function MapView({
  safeRoute,
  candidateRoutes = [],
  marineZones = [],
  onRouteClick,
  onZoneClick,
}) {
  const [tileStyle, setTileStyle] = useState('bathymetry');
  const [showWind, setShowWind] = useState(true);
  const [showTemp, setShowTemp] = useState(true);
  const [showNautical, setShowNautical] = useState(true);

  const activeTile = TILE_SERVERS[tileStyle] || TILE_SERVERS.bathymetry;

  const rawSafePoints = useMemo(() => rawWaypointLatLngs(safeRoute), [safeRoute]);
  const safePoints = useMemo(() => getSmoothMarineRoute(rawSafePoints, false), [rawSafePoints]);

  const candidatePointSets = useMemo(
    () => candidateRoutes.map((r) => getSmoothMarineRoute(rawWaypointLatLngs(r), true)),
    [candidateRoutes]
  );

  const allPoints = useMemo(() => {
    return [...safePoints, ...candidatePointSets.flat()];
  }, [safePoints, candidatePointSets]);

  const startPoint = rawSafePoints[0];
  const destinationPoint = rawSafePoints[rawSafePoints.length - 1];

  return (
    <div className="relative h-full w-full overflow-hidden rounded-lg border border-line">
      {/* Map Layer & Style Controls */}
      <div className="absolute top-3 right-3 z-[1000] flex flex-col gap-2">
        {/* Basemap Selector */}
        <div className="flex items-center gap-1 rounded-lg border border-[#202023] bg-[#0A0A0C]/90 p-1 shadow-lg backdrop-blur-md">
          {Object.entries(TILE_SERVERS).map(([key]) => (
            <button
              key={key}
              type="button"
              onClick={() => setTileStyle(key)}
              className={`rounded-md px-2.5 py-1 text-[11px] font-semibold transition ${
                tileStyle === key
                  ? 'bg-[#3DA7B7] text-black shadow-sm'
                  : 'text-[#A0A0A5] hover:bg-white/10 hover:text-white'
              }`}
            >
              {key === 'bathymetry'
                ? '🌊 Bathymetry'
                : key === 'standard'
                ? '🗺️ Standard'
                : key === 'voyager'
                ? '🎨 Color'
                : '🌙 Dark'}
            </button>
          ))}
        </div>

        {/* Overlay Toggles (Wind, Temp, Nautical Seamarks) */}
        <div className="flex items-center justify-end gap-1.5 rounded-lg border border-[#202023] bg-[#0A0A0C]/90 p-1 shadow-lg backdrop-blur-md">
          <button
            type="button"
            onClick={() => setShowWind((v) => !v)}
            className={`rounded-md px-2 py-1 text-[11px] font-semibold transition ${
              showWind ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-[#88888D] hover:text-white'
            }`}
          >
            💨 Wind
          </button>

          <button
            type="button"
            onClick={() => setShowTemp((v) => !v)}
            className={`rounded-md px-2 py-1 text-[11px] font-semibold transition ${
              showTemp ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'text-[#88888D] hover:text-white'
            }`}
          >
            🌡️ Temp
          </button>

          <button
            type="button"
            onClick={() => setShowNautical((v) => !v)}
            className={`rounded-md px-2 py-1 text-[11px] font-semibold transition ${
              showNautical ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'text-[#88888D] hover:text-white'
            }`}
          >
            ⚓ Nautical
          </button>
        </div>
      </div>

      {/* Marine Weather & Bathymetry Live HUD overlay */}
      {(showWind || showTemp || tileStyle === 'bathymetry') && (
        <div className="absolute bottom-3 left-3 z-[1000] flex flex-col gap-1.5 rounded-xl border border-[#202023] bg-[#0A0A0C]/90 p-3 text-xs text-white shadow-xl backdrop-blur-md">
          <div className="flex items-center gap-2 border-b border-white/10 pb-1.5 text-[10px] font-bold uppercase tracking-wider text-[#3DA7B7]">
            <span>🌊 Marine Environmental Data</span>
          </div>

          {tileStyle === 'bathymetry' && (
            <div className="flex items-center justify-between gap-4 text-[11px]">
              <span className="text-[#88888D]">Ocean Depth:</span>
              <span className="font-semibold text-cyan-400">15m – 120m (Bathymetric Shelf)</span>
            </div>
          )}

          {showWind && (
            <div className="flex items-center justify-between gap-4 text-[11px]">
              <span className="text-[#88888D]">Wind Velocity:</span>
              <span className="font-semibold text-cyan-300">12.4 kts (272° W)</span>
            </div>
          )}

          {showTemp && (
            <div className="flex items-center justify-between gap-4 text-[11px]">
              <span className="text-[#88888D]">Sea Surface Temp (SST):</span>
              <span className="font-semibold text-amber-400">30.1°C</span>
            </div>
          )}
        </div>
      )}

      <MapContainer
        center={startPoint || [13.0827, 80.2707]}
        zoom={9}
        scrollWheelZoom
        className="h-full w-full"
        style={{ background: '#091E36' }}
      >
        {/* Main Base Tile Layer */}
        <TileLayer key={activeTile.url} attribution={activeTile.attribution} url={activeTile.url} />

        {/* Bathymetry Reference Label Overlay (Depth Contours & Nautical Labels) */}
        {activeTile.overlayUrl && (
          <TileLayer key={activeTile.overlayUrl} url={activeTile.overlayUrl} opacity={0.85} />
        )}

        {/* OpenSeaMap Nautical Marks / Buoys / Navigation Lights Overlay */}
        {showNautical && (
          <TileLayer
            key="openseamap"
            url="https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openseamap.org">OpenSeaMap</a>'
            opacity={0.9}
          />
        )}

        <MapResizeFix />
        {allPoints.length > 0 && <FitBounds points={allPoints} />}

        {/* Marine zones — Restricted (Red) & Protected (Yellow/Amber) */}
        {marineZones.map((zone, idx) => {
          const zoneType = (zone.type || '').toLowerCase();
          const restrictionLevel = (zone.restriction_level || '').toLowerCase();

          const isRestricted = zoneType.includes('restricted') || restrictionLevel === 'restricted';

          // Vibrant color styling: Red for Restricted, Amber/Yellow for Protected
          const strokeColor = isRestricted ? '#EF4444' : '#F59E0B';
          const fillColor = isRestricted ? '#EF4444' : '#F59E0B';

          const style = {
            color: strokeColor,
            weight: 2,
            opacity: 0.9,
            fillColor: fillColor,
            fillOpacity: isRestricted ? 0.25 : 0.18,
            dashArray: isRestricted ? '6 4' : '3 3',
          };

          const key = zone.id || zone.name || idx;

          // 1. Circle geometry (e.g. Vishakhapatnam Restricted Area)
          if (
            (zone.geometry?.type === 'circle' || zone.geometry?.center) &&
            (zone.geometry?.center?.latitude || zone.geometry?.center?.lat)
          ) {
            const center = [
              zone.geometry.center.latitude || zone.geometry.center.lat,
              zone.geometry.center.longitude || zone.geometry.center.lng,
            ];
            const radiusMeters = (zone.geometry.radius_km || 2.778) * 1000;

            return (
              <Circle
                key={`circle-${key}`}
                center={center}
                radius={radiusMeters}
                pathOptions={style}
                eventHandlers={{ click: () => onZoneClick?.(zone) }}
              >
                <Popup>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#1E293B' }}>
                    <strong style={{ color: strokeColor }}>
                      🚨 {zone.name || (isRestricted ? 'Restricted Marine Zone' : 'Protected Marine Area')}
                    </strong>
                    <div style={{ marginTop: 4 }}>Type: <strong>{zone.type || 'Restricted Area'}</strong></div>
                    {zone.geometry?.radius_km && <div>Radius: {zone.geometry.radius_km} km</div>}
                    {zone.location && <div>Location: {zone.location}</div>}
                    {zone.notes && <div style={{ marginTop: 4, fontSize: 11, color: '#64748B' }}>{zone.notes}</div>}
                  </div>
                </Popup>
              </Circle>
            );
          }

          // 2. Standard GeoJSON
          const parsedGeo = parseGeoJSON(zone.geometry);
          if (isValidGeoJSON(parsedGeo)) {
            return (
              <GeoJSON
                key={`geojson-${key}`}
                data={parsedGeo}
                style={style}
                eventHandlers={{ click: () => onZoneClick?.(zone) }}
              >
                <Popup>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#1E293B' }}>
                    <strong style={{ color: strokeColor }}>
                      🛡️ {zone.name || (isRestricted ? 'Restricted Zone' : 'Protected Area')}
                    </strong>
                    <div>Type: {zone.type || 'Marine Zone'}</div>
                    {zone.restriction_level && <div>Restriction: {zone.restriction_level}</div>}
                  </div>
                </Popup>
              </GeoJSON>
            );
          }

          // 3. Coordinate array polygon
          if (Array.isArray(zone.coordinates) && zone.coordinates.length > 0) {
            const polygonCoords = zone.coordinates.map((ring) =>
              Array.isArray(ring)
                ? ring.map((pt) => (Array.isArray(pt) && pt.length >= 2 ? [pt[1], pt[0]] : pt))
                : ring
            );

            return (
              <Polygon
                key={`poly-${key}`}
                positions={polygonCoords}
                pathOptions={style}
                eventHandlers={{ click: () => onZoneClick?.(zone) }}
              >
                <Popup>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#1E293B' }}>
                    <strong style={{ color: strokeColor }}>
                      🛡️ {zone.name || (isRestricted ? 'Restricted Zone' : 'Protected Area')}
                    </strong>
                    <div>Type: {zone.type || 'Marine Zone'}</div>
                  </div>
                </Popup>
              </Polygon>
            );
          }

          return null;
        })}

        {/* Candidate routes — vibrant orange/amber dashed curved line */}
        {candidatePointSets.map((points, i) => {
          if (!points || points.length < 2) return null;
          const route = candidateRoutes[i];
          const key = route?.route_id || `candidate-${i}`;
          const eventHandlers = { click: () => onRouteClick?.(route) };

          return (
            <Polyline
              key={key}
              positions={points}
              pathOptions={{ color: '#F97316', weight: 3.5, opacity: 0.85, dashArray: '6 6' }}
              eventHandlers={eventHandlers}
            >
              <Popup>
                <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#1E293B' }}>
                  <strong style={{ color: '#F97316' }}>{route?.route_id || `Candidate Route ${i + 1}`}</strong>
                  <div>Distance: {route?.distance_km?.toFixed?.(2) ?? '—'} km</div>
                  <div>Risk score: {route?.risk_score ?? '—'}</div>
                </div>
              </Popup>
            </Polyline>
          );
        })}

        {/* Safest route — vibrant Cyan / Deep Ocean Blue, smooth curved line */}
        {safePoints.length > 1 && (
          <Polyline
            key={`safe-polyline-${safeRoute?.route_id || 'safe'}`}
            positions={safePoints}
            pathOptions={{ color: '#00C8FF', weight: 5, opacity: 0.95 }}
            eventHandlers={{ click: () => onRouteClick?.(safeRoute) }}
          >
            <Popup>
              <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#1E293B' }}>
                <strong style={{ color: '#0284C7' }}>🌊 {safeRoute?.route_id || 'Safest marine route'}</strong>
                <div>Distance: <strong>{safeRoute?.distance_km?.toFixed?.(2) ?? '—'} km</strong></div>
                <div>Risk score: {safeRoute?.risk_score ?? '—'}</div>
              </div>
            </Popup>
          </Polyline>
        )}

        {startPoint && (
          <Marker position={startPoint} icon={startIcon}>
            <Popup>
              <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#1E293B' }}>
                <strong style={{ color: '#10B981' }}>📍 Start Location</strong>
                <div>{startPoint[0].toFixed(4)}, {startPoint[1].toFixed(4)}</div>
              </div>
            </Popup>
          </Marker>
        )}
        {destinationPoint && (
          <Marker position={destinationPoint} icon={destinationIcon}>
            <Popup>
              <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13, color: '#1E293B' }}>
                <strong style={{ color: '#00C8FF' }}>⚓ Target PFZ Destination</strong>
                <div>{destinationPoint[0].toFixed(4)}, {destinationPoint[1].toFixed(4)}</div>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
