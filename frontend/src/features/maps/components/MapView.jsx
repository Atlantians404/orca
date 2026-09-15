import { useEffect, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// ---------------------------------------------------------------
// Monochrome divIcon markers (no default Leaflet marker images,
// no color — shape and fill only, matching the rest of ORCA).
// ---------------------------------------------------------------
function dotIcon({ ring = false, filled = true, size = 16 }) {
  const inner = filled ? '#FFFFFF' : 'transparent';
  const border = filled ? '2px solid #FFFFFF' : '2px solid rgba(255,255,255,0.9)';
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
        ${ring ? `<span style="position:absolute;inset:0;border-radius:9999px;border:1px solid rgba(255,255,255,0.4);"></span>` : ''}
        <span style="
          width:${size}px;height:${size}px;border-radius:9999px;
          background:${inner};border:${border};
          box-shadow:0 0 0 3px rgba(5,5,5,0.9);
        "></span>
      </span>
    `,
  });
}

const startIcon = dotIcon({ filled: false, size: 14 });
const destinationIcon = dotIcon({ filled: true, ring: true, size: 16 });

// Extracts a Leaflet LatLng bounds source from whatever combination of
// route/marker data is currently available, so the map can fit to it.
function FitBounds({ points }) {
  const map = useMap();
  useEffect(() => {
    if (!points || points.length === 0) return;
    const bounds = L.latLngBounds(points);
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [32, 32] });
    }
  }, [points, map]);
  return null;
}

function waypointLatLngs(route) {
  if (!route) return [];
  if (Array.isArray(route.waypoints) && route.waypoints.length) {
    return route.waypoints
      .filter((w) => typeof w.latitude === 'number' && typeof w.longitude === 'number')
      .map((w) => [w.latitude, w.longitude]);
  }
  const coords = route.geojson?.geometry?.coordinates;
  if (Array.isArray(coords)) {
    // GeoJSON is [lon, lat] — Leaflet wants [lat, lon]
    return coords.map(([lon, lat]) => [lat, lon]);
  }
  return [];
}

/**
 * MapView
 *
 * Renders the safest route (solid, heavier line), any candidate routes
 * (dashed, lighter), marine zones (restricted = dashed border,
 * protected = dotted border — no color per the ORCA monochrome rule),
 * and start/destination markers. Auto-fits bounds to whatever is
 * currently displayed.
 */
export default function MapView({
  safeRoute,
  candidateRoutes = [],
  marineZones = [],
  onRouteClick,
  onZoneClick,
}) {
  const safePoints = useMemo(() => waypointLatLngs(safeRoute), [safeRoute]);
  const candidatePointSets = useMemo(
    () => candidateRoutes.map((r) => waypointLatLngs(r)),
    [candidateRoutes]
  );

  const allPoints = useMemo(() => {
    const pts = [...safePoints, ...candidatePointSets.flat()];
    return pts;
  }, [safePoints, candidatePointSets]);

  const startPoint = safePoints[0];
  const destinationPoint = safePoints[safePoints.length - 1];

  return (
    <div className="h-full w-full overflow-hidden rounded-lg border border-line">
      <MapContainer
        center={startPoint || [13.0, 80.2]}
        zoom={7}
        scrollWheelZoom
        className="h-full w-full"
        style={{ background: '#0A0A0A' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {allPoints.length > 0 && <FitBounds points={allPoints} />}

        {/* Marine zones — rendered from real geometry when present */}
        {marineZones.map((zone) => {
          const isRestricted = (zone.type || '').toLowerCase() === 'restricted';
          if (!zone.geometry) return null;
          return (
            <GeoJSON
              key={zone.id}
              data={zone.geometry}
              style={{
                color: '#FFFFFF',
                weight: 1.2,
                opacity: 0.6,
                fillColor: '#FFFFFF',
                fillOpacity: isRestricted ? 0.06 : 0.03,
                dashArray: isRestricted ? '6 4' : '1 5',
              }}
              eventHandlers={{
                click: () => onZoneClick?.(zone),
              }}
            >
              <Popup>
                <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13 }}>
                  <strong>{zone.name || 'Marine zone'}</strong>
                  <div>Type: {zone.type || 'unknown'}</div>
                  {zone.restriction_level && <div>Restriction: {zone.restriction_level}</div>}
                  {zone.state && <div>State: {zone.state}</div>}
                </div>
              </Popup>
            </GeoJSON>
          );
        })}

        {/* Candidate routes — dashed, lower emphasis */}
        {candidateRoutes.map((route, i) =>
          route?.geojson ? (
            <GeoJSON
              key={route.route_id || i}
              data={route.geojson}
              style={{ color: '#FFFFFF', weight: 2, opacity: 0.4, dashArray: '5 5' }}
              eventHandlers={{ click: () => onRouteClick?.(route) }}
            >
              <Popup>
                <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13 }}>
                  <strong>{route.route_id || `Route ${i + 1}`}</strong>
                  <div>{route.distance_km?.toFixed?.(2) ?? '—'} km</div>
                  <div>Risk score {route.risk_score ?? '—'}</div>
                </div>
              </Popup>
            </GeoJSON>
          ) : null
        )}

        {/* Safest route — solid, heaviest line */}
        {safeRoute?.geojson && (
          <GeoJSON
            data={safeRoute.geojson}
            style={{ color: '#FFFFFF', weight: 4, opacity: 0.95 }}
            eventHandlers={{ click: () => onRouteClick?.(safeRoute) }}
          >
            <Popup>
              <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13 }}>
                <strong>{safeRoute.route_id || 'Safest route'}</strong>
                <div>{safeRoute.distance_km?.toFixed?.(2) ?? '—'} km</div>
                <div>Risk score {safeRoute.risk_score ?? '—'}</div>
              </div>
            </Popup>
          </GeoJSON>
        )}

        {startPoint && (
          <Marker position={startPoint} icon={startIcon}>
            <Popup>Start location</Popup>
          </Marker>
        )}
        {destinationPoint && (
          <Marker position={destinationPoint} icon={destinationIcon}>
            <Popup>Selected PFZ / destination</Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
