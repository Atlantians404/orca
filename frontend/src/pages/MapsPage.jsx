import { useEffect, useState, useCallback } from 'react';
import { Loader2 } from 'lucide-react';
import {
  getSavedMaps,
  getMap,
  deleteMap,
  getMarineZones,
} from '../services/mapsApi';
import SavedMapCard from '../features/maps/components/SavedMapCard';
import MapView from '../features/maps/components/MapView';
import RouteDetailsPanel from '../features/maps/components/RouteDetailsPanel';
import MapControls from '../features/maps/components/MapControls';

export default function MapsPage() {
  const [maps, setMaps] = useState([]);
  const [listStatus, setListStatus] = useState('loading'); // loading | ready | error

  const [selectedId, setSelectedId] = useState(null);
  const [selectedMap, setSelectedMap] = useState(null);
  const [detailStatus, setDetailStatus] = useState('idle'); // idle | loading | ready | error

  const [marineZones, setMarineZones] = useState([]);

  const [deletingId, setDeletingId] = useState(null);
  const [showCandidates, setShowCandidates] = useState(true);
  const [showZones, setShowZones] = useState(true);

  const loadMaps = useCallback(async () => {
    setListStatus('loading');
    try {
      const data = await getSavedMaps();
      setMaps(Array.isArray(data) ? data : data?.maps || []);
      setListStatus('ready');
    } catch (err) {
      console.error('Failed to load saved maps:', err);
      setListStatus('error');
    }
  }, []);

  useEffect(() => {
    loadMaps();
    getMarineZones()
      .then((data) => setMarineZones(Array.isArray(data) ? data : data?.zones || []))
      .catch((err) => console.error('Failed to load marine zones:', err));
  }, [loadMaps]);

  const openMap = useCallback(async (mapId) => {
    setSelectedId(mapId);
    setDetailStatus('loading');
    try {
      const data = await getMap(mapId);
      setSelectedMap(data);
      setDetailStatus('ready');
    } catch (err) {
      console.error('Failed to load map:', err);
      setDetailStatus('error');
    }
  }, []);

  const handleDelete = useCallback(
    async (mapId) => {
      setDeletingId(mapId);
      try {
        await deleteMap(mapId);
        setMaps((prev) => prev.filter((m) => (m.id ?? m.map_id) !== mapId));
        if (selectedId === mapId) {
          setSelectedId(null);
          setSelectedMap(null);
        }
      } catch (err) {
        console.error('Failed to delete map:', err);
      } finally {
        setDeletingId(null);
      }
    },
    [selectedId]
  );

  const innerMap = selectedMap?.route_data || selectedMap;
  const rawRouteResult = innerMap?.route_result || innerMap;
  const safeRoute =
    rawRouteResult?.safe_route ||
    rawRouteResult?.safeRoute ||
    innerMap?.safe_route ||
    innerMap?.safeRoute ||
    rawRouteResult;
  const candidateRoutes =
    rawRouteResult?.candidate_routes ||
    rawRouteResult?.candidateRoutes ||
    innerMap?.candidate_routes ||
    innerMap?.candidateRoutes ||
    [];
  const displayedMarineZones =
    innerMap?.marine_zones && innerMap?.marine_zones.length > 0
      ? innerMap.marine_zones
      : marineZones;

  return (
    <div className="h-full w-full flex flex-col lg:flex-row overflow-hidden bg-void">
      {/* Saved maps list */}
      <aside className="w-full lg:w-[360px] shrink-0 border-b lg:border-b-0 lg:border-r border-line overflow-y-auto p-5">
        <h1 className="font-display text-lg tracking-tightest text-ink">Saved maps</h1>

        {listStatus === 'loading' && (
          <div className="mt-8 flex items-center gap-2 text-sm text-mute">
            <Loader2 size={16} className="animate-spin" /> Loading saved maps…
          </div>
        )}

        {listStatus === 'error' && (
          <div className="mt-8 text-sm text-mute">
            Couldn't load your saved maps.{' '}
            <button type="button" onClick={loadMaps} className="text-ink underline">
              Try again
            </button>
          </div>
        )}

        {listStatus === 'ready' && maps.length === 0 && (
          <div className="mt-8">
            <p className="text-sm text-ink">No saved maps yet</p>
            <p className="mt-1.5 text-sm text-mute">
              Generate a route and save it here for quick access.
            </p>
          </div>
        )}

        {listStatus === 'ready' && maps.length > 0 && (
          <div className="mt-6 space-y-3">
            {maps.map((map) => {
              const id = map.id ?? map.map_id;
              return (
                <SavedMapCard
                  key={id}
                  map={map}
                  active={id === selectedId}
                  onOpen={openMap}
                  onDelete={handleDelete}
                  deleting={deletingId === id}
                />
              );
            })}
          </div>
        )}
      </aside>

      {/* Selected map */}
      <section className="flex-1 min-h-0 min-w-0 p-5 overflow-y-auto">
        {!selectedId && (
          <div className="h-full flex items-center justify-center text-sm text-mute">
            Select a saved map to view its route.
          </div>
        )}

        {selectedId && detailStatus === 'loading' && (
          <div className="h-full flex items-center justify-center gap-2 text-sm text-mute">
            <Loader2 size={16} className="animate-spin" /> Loading route…
          </div>
        )}

        {selectedId && detailStatus === 'error' && (
          <div className="h-full flex items-center justify-center text-sm text-mute">
            Couldn't load this map.{' '}
            <button type="button" onClick={() => openMap(selectedId)} className="text-ink underline ml-1">
              Try again
            </button>
          </div>
        )}

        {selectedId && detailStatus === 'ready' && selectedMap && (
          <div className="h-full flex flex-col lg:flex-row gap-5">
            <div className="flex-1 min-h-[360px] flex flex-col">
              <MapControls
                showCandidates={showCandidates}
                onToggleCandidates={() => setShowCandidates((v) => !v)}
                showZones={showZones}
                onToggleZones={() => setShowZones((v) => !v)}
                hasCandidates={candidateRoutes.length > 0}
                hasZones={displayedMarineZones.length > 0}
              />
              <div className="flex-1 min-h-0 min-h-[360px] relative rounded-xl overflow-hidden border border-line">
                <MapView
                  safeRoute={safeRoute}
                  candidateRoutes={showCandidates ? candidateRoutes : []}
                  marineZones={showZones ? displayedMarineZones : []}
                />
              </div>
            </div>
            <div className="w-full lg:w-72 shrink-0">
              <RouteDetailsPanel map={selectedMap} safeRoute={safeRoute} />
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
