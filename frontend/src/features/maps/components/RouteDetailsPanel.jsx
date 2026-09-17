import { getRiskLabel, formatRiskScore, formatDistance } from '../../../utils/risk';

export default function RouteDetailsPanel({ map, safeRoute }) {
  if (!map && !safeRoute) return null;

  const innerMap = map?.route_data || map || {};
  const activeRoute = safeRoute || innerMap.safe_route || innerMap.safeRoute || innerMap;

  const pfzName =
    innerMap.pfz?.name ||
    innerMap.pfz_name ||
    map?.title ||
    innerMap.name ||
    'Selected route';

  const routeId =
    activeRoute?.route_id ||
    activeRoute?.routeId ||
    innerMap.route_id ||
    innerMap.routeId ||
    '—';

  const riskLabel = getRiskLabel(activeRoute) || getRiskLabel(innerMap);
  const waypointCount =
    activeRoute?.waypoints?.length ??
    innerMap?.waypoints?.length ??
    innerMap?.waypoint_count ??
    null;
  const isSafe = activeRoute?.safe ?? innerMap?.safe ?? true;

  return (
    <div className="rounded-xl border border-[#202023] bg-[#0A0A0C] p-4 sm:p-5">
      <p className="text-xs font-semibold uppercase tracking-wider text-[#3DA7B7]">{pfzName}</p>
      <h3 className="mt-1 font-display text-lg sm:text-xl font-bold text-white tracking-tight">
        {routeId}
      </h3>

      <p className="mt-3 text-2xl font-bold text-white tracking-tight">
        {formatDistance(activeRoute)}
      </p>

      <div className="mt-4 grid grid-cols-2 gap-3 border-t border-[#202023] pt-4">
        <div>
          <p className="text-[10px] font-medium uppercase tracking-wider text-[#77777C]">Risk score</p>
          <p className="mt-1 text-sm font-semibold text-white">{formatRiskScore(activeRoute)}</p>
        </div>
        <div>
          <p className="text-[10px] font-medium uppercase tracking-wider text-[#77777C]">Risk level</p>
          <p className="mt-1 text-sm font-semibold text-[#3DA7B7]">{riskLabel || 'LOW'}</p>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-[#202023] pt-3">
        <span
          className={`inline-flex items-center gap-1.5 text-[11px] font-bold tracking-wider rounded-md border px-2.5 py-1 uppercase ${
            isSafe
              ? 'border-[#3DA7B7]/40 bg-[#3DA7B7]/10 text-[#3DA7B7]'
              : 'border-amber-500/40 bg-amber-500/10 text-amber-400'
          }`}
        >
          <span className={`h-1.5 w-1.5 rounded-full ${isSafe ? 'bg-[#3DA7B7]' : 'bg-amber-400'}`} />
          {isSafe ? 'SAFE ROUTE' : 'REVIEW ROUTE'}
        </span>

        {waypointCount != null && (
          <span className="text-xs text-[#77777C] font-medium">{waypointCount} waypoints</span>
        )}
      </div>
    </div>
  );
}
