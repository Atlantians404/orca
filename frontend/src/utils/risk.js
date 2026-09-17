/**
 * ASSUMPTION (flagged per the implementation brief):
 *
 * The example Route Engine payload only includes a numeric `risk_score`
 * and a boolean `safe` — no explicit "LOW / MEDIUM / HIGH" field. This
 * helper only decides which WORD to display next to that number; it
 * never recalculates risk_score itself and never overrides `safe`.
 *
 * If the real API already returns a label (e.g. `risk_level` or
 * `risk_label`), this function prefers that field automatically and
 * the threshold logic below is never reached — delete the fallback
 * once you've confirmed the backend always sends one.
 */
export function getRiskLabel(route) {
  if (!route) return null;

  const explicit = route.risk_level || route.risk_label || route.riskLevel;
  if (explicit) return String(explicit).toUpperCase();

  const score = route.risk_score ?? route.riskScore;
  if (typeof score !== 'number') return null;

  // Placeholder thresholds — replace with whatever the backend's own
  // bucketing is once confirmed. Purely a display grouping, not a
  // recalculation of the score.
  if (score < 30) return 'LOW';
  if (score < 60) return 'MEDIUM';
  return 'HIGH';
}

export function formatRiskScore(route) {
  const score = route?.risk_score ?? route?.riskScore;
  return typeof score === 'number' ? score.toFixed(2) : '—';
}

export function formatDistance(route) {
  const km = route?.distance_km ?? route?.distanceKm;
  return typeof km === 'number' ? `${km.toFixed(2)} km` : '—';
}
