export default function MapControls({
  showCandidates,
  onToggleCandidates,
  showZones,
  onToggleZones,
  hasCandidates,
  hasZones,
}) {
  if (!hasCandidates && !hasZones) return null;

  return (
    <div className="flex items-center gap-3 mb-3">
      {hasCandidates && (
        <button
          type="button"
          onClick={onToggleCandidates}
          className={`text-xs rounded-full border px-3 py-1.5 transition-colors ${
            showCandidates ? 'border-line2 text-ink' : 'border-line text-mute hover:text-ink'
          }`}
        >
          Candidate routes
        </button>
      )}
      {hasZones && (
        <button
          type="button"
          onClick={onToggleZones}
          className={`text-xs rounded-full border px-3 py-1.5 transition-colors ${
            showZones ? 'border-line2 text-ink' : 'border-line text-mute hover:text-ink'
          }`}
        >
          Marine zones
        </button>
      )}
    </div>
  );
}
