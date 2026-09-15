import { getRiskLabel, formatRiskScore, formatDistance } from '../../../utils/risk';

export default function RouteDetailsPanel({ map, safeRoute }) {
  if (!map) return null;

  const riskLabel = getRiskLabel(safeRoute || map);
  const waypointCount =
    safeRoute?.waypoints?.length ?? map?.waypoints?.length ?? map?.waypoint_count ?? null;
  const isSafe = (safeRoute ?? map)?.safe;

  return (
    <div className="rounded-xl border border-line bg-surface p-5">
      <p className="text-xs text-mute">{map.pfz_name || map.name || 'Saved route'}</p>
      <h3 className="mt-1 font-display text-xl text-ink tracking-tightest">
        {safeRoute?.route_id || map.route_id || '—'}
      </h3>

      <p className="mt-4 text-2xl font-display text-ink tracking-tightest">
        {formatDistance(safeRoute || map)}
      </p>

      <div className="mt-5 grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-mute2 uppercase tracking-wide">Risk score</p>
          <p className="mt-1 text-sm text-ink">{formatRiskScore(safeRoute || map)}</p>
        </div>
        <div>
          <p className="text-xs text-mute2 uppercase tracking-wide">Risk level</p>
          <p className="mt-1 text-sm text-ink">{riskLabel || '—'}</p>
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <span
          className={`inline-flex items-center gap-1.5 text-xs rounded-full border border-line2 px-2.5 py-1 ${
            isSafe ? 'text-ink' : 'text-mute'
          }`}
        >
          <span className={`h-1.5 w-1.5 rounded-full ${isSafe ? 'bg-white' : 'border border-white/60'}`} />
          {isSafe ? 'SAFE ROUTE' : 'REVIEW ROUTE'}
        </span>
      </div>

      {waypointCount != null && (
        <p className="mt-4 text-xs text-mute">{waypointCount} waypoints</p>
      )}
    </div>
  );
}
