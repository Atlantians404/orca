import { useEffect, useMemo } from 'react';
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  Polyline,
  Polygon,
  Marker,
  Popup,
  useMap,
} from 'react-leaflet';
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
      map.fitBounds(bounds, { padding: [36, 36] });
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

function waypointLatLngs(route) {
  if (!route) return [];

  // Check route waypoints array
  if (Array.isArray(route.waypoints) && route.waypoints.length) {
    return route.waypoints
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
  }

  // GeoJSON is [longitude, latitude] — Leaflet wants [latitude, longitude]
  const coords = route.geojson?.geometry?.coordinates || route.geojson?.coordinates;
  if (Array.isArray(coords)) {
    return coords.map(([lon, lat]) => [lat, lon]);
  }

  return [];
}

/**
 * MapView
 *
 * Renders the safest route (solid, heavier line), any candidate routes
 * (dashed, lighter), marine zones (restricted = dashed border,
 * protected = dotted border — monochrome ORCA styling),
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
    return [...safePoints, ...candidatePointSets.flat()];
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

        <MapResizeFix />
        {allPoints.length > 0 && <FitBounds points={allPoints} />}

        {/* Marine zones — normalized restriction handling */}
        {marineZones.map((zone, idx) => {
          const zoneType = (zone.type || '').toLowerCase();
          const restrictionLevel = (zone.restriction_level || '').toLowerCase();

          const isRestricted = zoneType.includes('restricted') || restrictionLevel === 'restricted';
          const isProtected = zoneType.includes('protected') || restrictionLevel === 'protected';

          const style = {
            color: '#FFFFFF',
            weight: 1.2,
            opacity: 0.65,
            fillColor: '#FFFFFF',
            fillOpacity: isRestricted ? 0.08 : 0.04,
            dashArray: isRestricted ? '6 4' : isProtected ? '1 5' : '4 4',
          };

          const key = zone.id || zone.name || idx;

          if (zone.geometry) {
            return (
              <GeoJSON
                key={key}
                data={zone.geometry}
                style={style}
                eventHandlers={{
                  click: () => onZoneClick?.(zone),
                }}
              >
                <Popup>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13 }}>
                    <strong>{zone.name || (isRestricted ? 'Restricted Zone' : 'Protected Zone')}</strong>
                    <div>Type: {zone.type || 'Marine Zone'}</div>
                    {zone.restriction_level && <div>Restriction: {zone.restriction_level}</div>}
                    {zone.state && <div>State: {zone.state}</div>}
                  </div>
                </Popup>
              </GeoJSON>
            );
          }

          if (Array.isArray(zone.coordinates) && zone.coordinates.length > 0) {
            const polygonCoords = zone.coordinates.map((ring) =>
              Array.isArray(ring)
                ? ring.map((pt) => (Array.isArray(pt) && pt.length >= 2 ? [pt[1], pt[0]] : pt))
                : ring
            );

            return (
              <Polygon
                key={key}
                positions={polygonCoords}
                pathOptions={style}
                eventHandlers={{
                  click: () => onZoneClick?.(zone),
                }}
              >
                <Popup>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13 }}>
                    <strong>{zone.name || (isRestricted ? 'Restricted Zone' : 'Protected Zone')}</strong>
                    <div>Type: {zone.type || 'Marine Zone'}</div>
                    {zone.restriction_level && <div>Restriction: {zone.restriction_level}</div>}
                  </div>
                </Popup>
              </Polygon>
            );
          }

          return null;
        })}

        {/* Candidate routes — dashed, lower emphasis */}
        {candidateRoutes.map((route, i) => {
          if (!route) return null;
          const points = waypointLatLngs(route);
          const key = route.route_id || `candidate-${i}`;
          const eventHandlers = { click: () => onRouteClick?.(route) };

          if (route.geojson) {
            return (
              <GeoJSON
                key={key}
                data={route.geojson}
                style={{ color: '#FFFFFF', weight: 2, opacity: 0.45, dashArray: '5 5' }}
                eventHandlers={eventHandlers}
              >
                <Popup>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13 }}>
                    <strong>{route.route_id || `Candidate Route ${i + 1}`}</strong>
                    <div>{route.distance_km?.toFixed?.(2) ?? '—'} km</div>
                    <div>Risk score: {route.risk_score ?? '—'}</div>
                  </div>
                </Popup>
              </GeoJSON>
            );
          }

          if (points.length > 1) {
            return (
              <Polyline
                key={key}
                positions={points}
                pathOptions={{ color: '#FFFFFF', weight: 2, opacity: 0.45, dashArray: '5 5' }}
                eventHandlers={eventHandlers}
              >
                <Popup>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13 }}>
                    <strong>{route.route_id || `Candidate Route ${i + 1}`}</strong>
                    <div>{route.distance_km?.toFixed?.(2) ?? '—'} km</div>
                    <div>Risk score: {route.risk_score ?? '—'}</div>
                  </div>
                </Popup>
              </Polyline>
            );
          }

          return null;
        })}

        {/* Safest route — solid, heaviest line */}
        {safeRoute && (() => {
          const points = safePoints;
          const eventHandlers = { click: () => onRouteClick?.(safeRoute) };

          if (safeRoute.geojson) {
            return (
              <GeoJSON
                data={safeRoute.geojson}
                style={{ color: '#FFFFFF', weight: 4, opacity: 0.95 }}
                eventHandlers={eventHandlers}
              >
                <Popup>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13 }}>
                    <strong>{safeRoute.route_id || 'Safest route'}</strong>
                    <div>{safeRoute.distance_km?.toFixed?.(2) ?? '—'} km</div>
                    <div>Risk score: {safeRoute.risk_score ?? '—'}</div>
                  </div>
                </Popup>
              </GeoJSON>
            );
          }

          if (points.length > 1) {
            return (
              <Polyline
                positions={points}
                pathOptions={{ color: '#FFFFFF', weight: 4, opacity: 0.95 }}
                eventHandlers={eventHandlers}
              >
                <Popup>
                  <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 13 }}>
                    <strong>{safeRoute.route_id || 'Safest route'}</strong>
                    <div>{safeRoute.distance_km?.toFixed?.(2) ?? '—'} km</div>
                    <div>Risk score: {safeRoute.risk_score ?? '—'}</div>
                  </div>
                </Popup>
              </Polyline>
            );
          }

          return null;
        })()}

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
