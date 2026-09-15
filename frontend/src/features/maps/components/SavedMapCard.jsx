import { Trash2 } from 'lucide-react';
import { getRiskLabel, formatRiskScore, formatDistance } from '../../../utils/risk';

export default function SavedMapCard({ map, active, onOpen, onDelete, deleting }) {
  const riskLabel = getRiskLabel(map);

  return (
    <div
      className={`rounded-xl border p-4 transition-colors ${
        active ? 'border-line2 bg-surface2' : 'border-line bg-surface hover:border-line2'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm text-ink font-medium truncate">
            {map.pfz_name || map.name || 'Saved route'}
          </p>
          <p className="mt-1 text-xs text-mute">Route: {map.route_id || map.routeId || '—'}</p>
        </div>
        <button
          type="button"
          onClick={() => onDelete(map.id ?? map.map_id)}
          disabled={deleting}
          aria-label="Delete saved map"
          className="shrink-0 flex items-center justify-center h-7 w-7 rounded-md text-mute hover:text-ink hover:bg-white/5 transition-colors disabled:opacity-40"
        >
          <Trash2 size={14} />
        </button>
      </div>

      <div className="mt-3 flex items-center gap-4 text-xs text-mute">
        <span>{formatDistance(map)}</span>
        {riskLabel && (
          <span className="inline-flex items-center gap-1.5">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                riskLabel === 'HIGH' ? 'bg-white' : riskLabel === 'MEDIUM' ? 'bg-white/60' : 'border border-white/70'
              }`}
            />
            {formatRiskScore(map)} · {riskLabel}
          </span>
        )}
      </div>

      <button
        type="button"
        onClick={() => onOpen(map.id ?? map.map_id)}
        className="mt-4 w-full text-right text-sm text-ink hover:text-mute transition-colors"
      >
        Open Map →
      </button>
    </div>
  );
}
