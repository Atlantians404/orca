import { useState, useEffect, useMemo } from "react";
import {
  Compass,
  MapPin,
  Navigation,
  ShieldAlert,
  Waypoints,
  Loader2,
  Check,
} from "lucide-react";

import logo from "../../../assets/logo.png";
import MapView from "../../maps/components/MapView";
import MapControls from "../../maps/components/MapControls";
import RouteDetailsPanel from "../../maps/components/RouteDetailsPanel";
import { saveMap, getMarineZones } from "../../../services/mapsApi";

export default function ChatMessage({
  message,
  isLatest = false,
  onRequestLocation,
}) {
  const isUser = message.role === "user";

  if (isUser) {
    return <UserTurn message={message} />;
  }

  return (
    <AssistantTurn
      message={message}
      isLatest={isLatest}
      onRequestLocation={onRequestLocation}
    />
  );
}

// ============================================================
// USER MESSAGE
// ============================================================

function UserTurn({ message }) {
  return (
    <div className="group flex flex-col items-end">
      <div className="max-w-[min(85%,640px)] rounded-2xl border border-[#202023] bg-[#161616] px-4 py-3 text-sm leading-relaxed text-white">
        {message.content}
      </div>

      {message.created_at && (
        <div className="mt-1.5 pr-1 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
          <span className="text-[11px] text-[#5C5C5C]">
            {formatTime(message.created_at)}
          </span>
        </div>
      )}
    </div>
  );
}

// ============================================================
// ASSISTANT MESSAGE
// ============================================================

function formatBackendText(text) {
  if (!text) return null;

  const lines = String(text).split("\n");

  return (
    <div className="space-y-2">
      {lines.map((line, index) => {
        const trimmed = line.trim();

        // Preserve empty lines as small spacing
        if (!trimmed) {
          return <div key={index} className="h-1" />;
        }

        // Detect backend Markdown bullet
        const isBullet = trimmed.startsWith("- ");

        const content = isBullet ? trimmed.slice(2) : trimmed;

        // Split **bold text** from normal text
        const parts = content.split(/(\*\*.*?\*\*)/g);

        const formatted = parts.map((part, partIndex) => {
          const isBold = part.startsWith("**") && part.endsWith("**");

          if (isBold) {
            return (
              <strong key={partIndex} className="font-semibold text-white">
                {part.slice(2, -2)}
              </strong>
            );
          }

          return <span key={partIndex}>{part}</span>;
        });

        // Render bullets cleanly
        if (isBullet) {
          return (
            <div key={index} className="flex gap-2">
              <span className="shrink-0 text-[#3DA7B7]">•</span>
              <span>{formatted}</span>
            </div>
          );
        }

        // Normal paragraph
        return (
          <p key={index} className="leading-7">
            {formatted}
          </p>
        );
      })}
    </div>
  );
}

function AssistantTurn({ message, isLatest, onRequestLocation }) {
  const isThinking = message.pending === true;

  return (
    <div className="group flex items-start gap-3">
      {/* ORCA LOGO */}
      <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center">
        <img src={logo} alt="ORCA" className="h-7 w-7 object-contain" />
      </div>

      {/* RESPONSE BODY */}
      <div className="min-w-0 flex-1">
        {isThinking ? (
          <ThinkingIndicator />
        ) : (
          <>
            {/* MAIN BACKEND TEXT CONTENT */}
            {message.content && (
              <div className="text-sm text-[#E5E5E7]">
                {formatBackendText(message.content)}
              </div>
            )}

            {/* WORKFLOW INSTRUCTION / GPS PROMPT */}
            {message.pending_action === "location" &&
              message.workflow_status === "WAITING_FOR_USER" &&
              isLatest && (
                <div className="mt-3 flex flex-col gap-2">
                  <p className="text-sm leading-6 text-[#77777C]">
                    Please share your location or enter coordinates manually.
                  </p>
                  <button
                    type="button"
                    onClick={() => onRequestLocation?.()}
                    className="flex w-fit items-center gap-2 rounded-xl border border-[#202023] bg-[#111113] px-4 py-2.5 text-sm font-medium text-[#3DA7B7] transition hover:border-[#3DA7B7]/40 hover:bg-[#161616]"
                  >
                    <Navigation size={14} aria-hidden="true" />
                    Use My GPS Location
                  </button>
                </div>
              )}

            {message.pending_action === "time" && (
              <p className="mt-2 text-sm leading-6 text-[#77777C]">
                Please enter a suitable fishing time, for example 8 AM.
              </p>
            )}

            {/* STRUCTURED BACKEND DATA & MAP INTEGRATION */}
            {message.response_data && (
              <ResponseDataPanel
                data={message.response_data}
                showMessage={!message.content}
              />
            )}

            {/* WORKFLOW STATUS */}
            {message.workflow_status &&
              message.workflow_status !== "COMPLETED" && (
                <div className="mt-3">
                  <span className="text-[10px] font-medium uppercase tracking-wide text-[#5C5C5C]">
                    {formatWorkflowStatus(message.workflow_status)}
                  </span>
                </div>
              )}

            {message.workflow_status === "COMPLETED" && (
              <div className="mt-3">
                <span className="text-[10px] font-medium uppercase tracking-wide text-[#5C5C5C]">
                  COMPLETED
                </span>
              </div>
            )}

            {/* TIMESTAMP */}
            {message.created_at && (
              <div className="mt-2 flex items-center gap-3">
                <span className="text-[11px] text-[#5C5C5C]">
                  {formatTime(message.created_at)}
                </span>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ============================================================
// THINKING INDICATOR
// ============================================================

function ThinkingIndicator() {
  return (
    <div
      className="flex items-center gap-1.5 py-2"
      role="status"
      aria-label="ORCA is thinking"
    >
      <span
        className="h-1.5 w-1.5 rounded-full bg-[#5C5C5C]"
        style={{ animation: "pulseDot 1.2s ease-in-out infinite" }}
      />
      <span
        className="h-1.5 w-1.5 rounded-full bg-[#5C5C5C]"
        style={{
          animation: "pulseDot 1.2s ease-in-out infinite",
          animationDelay: "0.15s",
        }}
      />
      <span
        className="h-1.5 w-1.5 rounded-full bg-[#5C5C5C]"
        style={{
          animation: "pulseDot 1.2s ease-in-out infinite",
          animationDelay: "0.3s",
        }}
      />
    </div>
  );
}

// ============================================================
// ROUTE NORMALIZATION HELPER
// ============================================================

function normalizeRouteData(data) {
  if (!data || typeof data !== "object") return null;

  const rawRouteResult =
    data.route_result || data.route_data || data.routeData || data;

  const safeRoute =
    rawRouteResult.safe_route ||
    rawRouteResult.safeRoute ||
    (Array.isArray(rawRouteResult.routes)
      ? rawRouteResult.routes.find((r) => r.safe)
      : null) ||
    (rawRouteResult.waypoints || rawRouteResult.geojson
      ? rawRouteResult
      : null) ||
    (data.route && (data.route.waypoints || data.route.geojson)
      ? data.route
      : null);

  const candidateRoutes =
    rawRouteResult.candidate_routes ||
    rawRouteResult.candidateRoutes ||
    (Array.isArray(rawRouteResult.routes)
      ? rawRouteResult.routes.filter((r) => r !== safeRoute)
      : []);

  const pfz = data.pfz || data.pfz_data || rawRouteResult.pfz || null;
  const marineZones =
    data.marine_zones || data.marineZones || rawRouteResult.marine_zones || [];

  const hasSafePoints =
    safeRoute &&
    ((Array.isArray(safeRoute.waypoints) && safeRoute.waypoints.length > 0) ||
      safeRoute.geojson);
  const hasCandidates = candidateRoutes.some(
    (c) =>
      (Array.isArray(c.waypoints) && c.waypoints.length > 0) || c.geojson
  );

  if (!hasSafePoints && !hasCandidates) {
    return null;
  }

  return {
    safeRoute,
    candidateRoutes,
    pfz,
    marineZones,
  };
}

// ============================================================
// INTERACTIVE ROUTE MAP COMPONENT
// ============================================================

function InteractiveRouteMap({ responseData }) {
  const [showCandidates, setShowCandidates] = useState(true);
  const [showZones, setShowZones] = useState(true);
  const [fetchedZones, setFetchedZones] = useState([]);
  const [saveStatus, setSaveStatus] = useState("idle"); // idle | saving | saved | error | dismissed
  const [saveError, setSaveError] = useState("");

  const normalized = useMemo(
    () => normalizeRouteData(responseData),
    [responseData]
  );

  useEffect(() => {
    if (!normalized) return;
    if (normalized.marineZones && normalized.marineZones.length > 0) {
      setFetchedZones(normalized.marineZones);
    } else {
      getMarineZones()
        .then((data) =>
          setFetchedZones(Array.isArray(data) ? data : data?.zones || [])
        )
        .catch(() => {});
    }
  }, [normalized]);

  if (!normalized) return null;

  const { safeRoute, candidateRoutes, pfz } = normalized;
  const marineZones = fetchedZones;

  const handleSave = async () => {
    if (saveStatus === "saving" || saveStatus === "saved") return;

    setSaveStatus("saving");
    setSaveError("");

    try {
      const pfzName = pfz?.name || "Marine Route";
      const routeId = safeRoute?.route_id || "route-map";

      const payload = {
        title: `${pfzName} (${routeId})`,
        route_data: {
          pfz,
          safe_route: safeRoute,
          candidate_routes: candidateRoutes,
          marine_zones: marineZones,
          risk: responseData.risk,
          map: responseData.map,
        },
      };

      await saveMap(payload);
      setSaveStatus("saved");
    } catch (err) {
      setSaveError(err?.message || "Failed to save map");
      setSaveStatus("error");
    }
  };

  const handleDismiss = () => {
    setSaveStatus("dismissed");
  };

  return (
    <div className="mt-4 flex w-full max-w-[640px] flex-col gap-3 rounded-2xl border border-[#202023] bg-[#0F0F0F] p-4">
      {/* Map Controls */}
      <MapControls
        showCandidates={showCandidates}
        onToggleCandidates={() => setShowCandidates((v) => !v)}
        showZones={showZones}
        onToggleZones={() => setShowZones((v) => !v)}
        hasCandidates={candidateRoutes.length > 0}
        hasZones={marineZones.length > 0}
      />

      {/* Interactive Leaflet Map */}
      <div className="relative h-[360px] w-full overflow-hidden rounded-xl border border-[#202023]">
        <MapView
          safeRoute={safeRoute}
          candidateRoutes={showCandidates ? candidateRoutes : []}
          marineZones={showZones ? marineZones : []}
        />
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 rounded-xl border border-[#202023] bg-[#0A0A0A] px-3.5 py-2.5 text-xs text-[#9A9A9A]">
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full border border-white" />
          <span>○ Start</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-white" />
          <span>● Selected PFZ</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-0.5 w-4 bg-white" />
          <span>━━ Safest route</span>
        </div>
        {candidateRoutes.length > 0 && (
          <div className="flex items-center gap-1.5">
            <span className="inline-block w-4 border-b border-dashed border-white/60" />
            <span>- - Candidate route</span>
          </div>
        )}
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-4 border-b border-dashed border-white/80" />
          <span>- - Restricted zone</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-4 border-b border-dotted border-white/60" />
          <span>··· Protected zone</span>
        </div>
      </div>

      {/* Compact Route Details */}
      <RouteDetailsPanel map={responseData} safeRoute={safeRoute} />

      {/* Save Map Prompt */}
      {saveStatus !== "dismissed" && (
        <div className="mt-1 flex items-center justify-between gap-3 rounded-xl border border-[#202023] bg-[#141416] px-4 py-3">
          <div className="flex flex-col">
            <span className="text-xs font-medium text-white">
              {saveStatus === "saved"
                ? "Map saved"
                : saveStatus === "saving"
                ? "Saving map..."
                : saveStatus === "error"
                ? saveError || "Failed to save map"
                : "Save this map?"}
            </span>
            {saveStatus === "saved" && (
              <span className="text-[11px] text-[#77777D]">
                View it anytime on your Maps page.
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {saveStatus === "idle" || saveStatus === "error" ? (
              <>
                <button
                  type="button"
                  onClick={handleSave}
                  className="rounded-lg bg-[#3DA7B7] px-4 py-1.5 text-xs font-semibold text-black transition hover:bg-[#52b8c8]"
                >
                  Yes
                </button>
                <button
                  type="button"
                  onClick={handleDismiss}
                  className="rounded-lg border border-[#2A2A2E] bg-transparent px-4 py-1.5 text-xs font-medium text-[#9A9A9A] transition hover:bg-white/5 hover:text-white"
                >
                  No
                </button>
              </>
            ) : saveStatus === "saving" ? (
              <button
                type="button"
                disabled
                className="flex cursor-not-allowed items-center gap-1.5 rounded-lg bg-[#3DA7B7]/50 px-3.5 py-1.5 text-xs font-semibold text-black opacity-70"
              >
                <Loader2 size={12} className="animate-spin" />
                Saving...
              </button>
            ) : saveStatus === "saved" ? (
              <span className="inline-flex items-center gap-1 rounded-lg border border-[#3DA7B7]/40 bg-[#3DA7B7]/10 px-3 py-1 text-xs font-medium text-[#3DA7B7]">
                <Check size={13} /> Saved
              </span>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================
// RESPONSE DATA PANEL
// ============================================================

function ResponseDataPanel({ data, showMessage = false }) {
  if (!data || typeof data !== "object") {
    return null;
  }

  const { message, map, pfz, risk, route, plan } = data;

  const hasMap =
    map && Array.isArray(map.coordinates) && map.coordinates.length > 0;

  const hasPfz =
    pfz && (pfz.latitude != null || pfz.longitude != null || pfz.name);

  const hasRisk = risk && (risk.level || risk.score != null);

  const hasRoute = route && (route.distance_km != null || route.route_id);

  const hasPlan =
    plan && typeof plan === "object" && Object.keys(plan).length > 0;

  const hasResponseMessage =
    typeof message === "string" && message.trim().length > 0;

  const hasInteractiveRoute = Boolean(normalizeRouteData(data));

  if (
    !hasResponseMessage &&
    !hasMap &&
    !hasPfz &&
    !hasRisk &&
    !hasRoute &&
    !hasPlan &&
    !hasInteractiveRoute
  ) {
    return null;
  }

  return (
    <div className="mt-4 flex max-w-[620px] flex-col gap-2.5">
      {/* BACKEND RESPONSE MESSAGE */}
      {hasResponseMessage && showMessage && (
        <div className="rounded-xl border border-[#202023] bg-[#0F0F0F] px-4 py-3">
          <span className="text-[10px] font-medium uppercase tracking-wide text-[#3DA7B7]">
            ORCA PLAN
          </span>
          <div className="mt-2 text-sm text-[#E5E5E7]">
            {formatBackendText(message)}
          </div>
        </div>
      )}

      {/* PLAN OBJECT */}
      {hasPlan && <PlanPanel plan={plan} />}

      {/* INTERACTIVE LEAFLET ROUTE MAP (If route data is present) */}
      {hasInteractiveRoute && <InteractiveRouteMap responseData={data} />}

      {/* PFZ */}
      {hasPfz && (
        <div className="flex items-start gap-2.5 rounded-xl border border-[#202023] bg-[#0F0F0F] px-4 py-3">
          <MapPin
            size={15}
            className="mt-0.5 shrink-0 text-[#3DA7B7]"
            aria-hidden="true"
          />
          <div className="min-w-0">
            <span className="text-[10px] font-medium uppercase tracking-wide text-[#3DA7B7]">
              Fishing zone
            </span>
            <p className="mt-0.5 text-xs text-white/90">
              {pfz.name || "Selected zone"}
              {pfz.distance_from_source_km != null && (
                <span className="text-[#77777C]">
                  {" "}
                  · {Number(pfz.distance_from_source_km).toFixed(1)} km away
                </span>
              )}
            </p>
            {pfz.latitude != null && pfz.longitude != null && (
              <p className="mt-0.5 text-[11px] text-[#5C5C5C]">
                {formatNumber(pfz.latitude, 4)},{" "}
                {formatNumber(pfz.longitude, 4)}
              </p>
            )}
          </div>
        </div>
      )}

      {/* RISK */}
      {hasRisk && (
        <div className="flex items-center gap-2.5 rounded-xl border border-[#202023] bg-[#0F0F0F] px-4 py-3">
          <ShieldAlert
            size={15}
            className="shrink-0 text-[#3DA7B7]"
            aria-hidden="true"
          />
          <div className="min-w-0">
            <span className="text-[10px] font-medium uppercase tracking-wide text-[#3DA7B7]">
              Risk assessment
            </span>
            <p className="mt-0.5 text-xs text-white/90">
              {risk.level || "—"}
              {risk.score != null && (
                <span className="text-[#77777C]">
                  {" "}
                  · score {formatNumber(risk.score, 2)}
                </span>
              )}
            </p>
          </div>
        </div>
      )}

      {/* ROUTE SUMMARY */}
      {hasRoute && !hasInteractiveRoute && (
        <div className="flex items-start gap-2.5 rounded-xl border border-[#202023] bg-[#0F0F0F] px-4 py-3">
          <Navigation
            size={15}
            className="mt-0.5 shrink-0 text-[#3DA7B7]"
            aria-hidden="true"
          />
          <div className="min-w-0">
            <span className="text-[10px] font-medium uppercase tracking-wide text-[#3DA7B7]">
              Route
            </span>
            <p className="mt-0.5 text-xs text-white/90">
              {route.distance_km != null
                ? `${formatNumber(route.distance_km, 1)} km`
                : route.route_id}
              {route.safe != null && (
                <span className="text-[#77777C]">
                  {" "}
                  · {route.safe ? "within safe limits" : "caution advised"}
                </span>
              )}
            </p>
            {Array.isArray(route.waypoints) && route.waypoints.length > 0 && (
              <p className="mt-0.5 flex items-center gap-1 text-[11px] text-[#5C5C5C]">
                <Waypoints size={11} aria-hidden="true" />
                {route.waypoints.length} waypoints plotted
              </p>
            )}
          </div>
        </div>
      )}

      {/* RAW MAP COORDINATES */}
      {hasMap && !hasInteractiveRoute && (
        <div className="flex items-center gap-2.5 rounded-xl border border-[#202023] bg-[#0F0F0F] px-4 py-3">
          <Compass
            size={15}
            className="shrink-0 text-[#3DA7B7]"
            aria-hidden="true"
          />
          <div className="min-w-0">
            <span className="text-[10px] font-medium uppercase tracking-wide text-[#3DA7B7]">
              Map data
            </span>
            <p className="mt-0.5 text-xs text-white/90">
              {map.coordinates.length} coordinate
              {map.coordinates.length === 1 ? "" : "s"} returned by the backend.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================
// PLAN PANEL
// ============================================================

function PlanPanel({ plan }) {
  return (
    <div className="rounded-xl border border-[#202023] bg-[#0F0F0F] px-4 py-3">
      <div className="mb-3 flex items-center gap-2">
        <Compass size={15} className="text-[#3DA7B7]" aria-hidden="true" />
        <span className="text-[10px] font-medium uppercase tracking-wide text-[#3DA7B7]">
          Fishing trip plan
        </span>
      </div>

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {Object.entries(plan).map(([key, value]) => (
          <div
            key={key}
            className="rounded-lg border border-[#202023] bg-[#0A0A0A] px-3 py-2.5"
          >
            <p className="text-[10px] uppercase tracking-wide text-[#5C5C5C]">
              {formatLabel(key)}
            </p>
            <p className="mt-1 whitespace-pre-wrap text-xs leading-5 text-white/90">
              {formatValue(value)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================
// HELPERS
// ============================================================

function formatTime(value) {
  try {
    return new Date(value).toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

function formatWorkflowStatus(value) {
  return String(value).replaceAll("_", " ").toUpperCase();
}

function formatLabel(value) {
  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatValue(value) {
  if (value === null || value === undefined) {
    return "—";
  }

  if (Array.isArray(value)) {
    return value.map((item) => formatValue(item)).join(", ");
  }

  if (typeof value === "object") {
    return Object.entries(value)
      .map(([key, val]) => `${formatLabel(key)}: ${formatValue(val)}`)
      .join(" · ");
  }

  return String(value);
}

function formatNumber(value, digits = 2) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return String(value);
  }

  return number.toFixed(digits);
}