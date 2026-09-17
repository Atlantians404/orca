import { useEffect, useState, useRef, useCallback } from "react";
import { MapContainer, TileLayer, Marker, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { X, Loader2, MapPin, Navigation, Search, RefreshCw } from "lucide-react";

// ============================================================
// FIX LEAFLET DEFAULT ICON (Vite bundler issue)
// ============================================================

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

// ============================================================
// CUSTOM MARKER ICON
// ============================================================

const orcaIcon = new L.Icon({
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// DEFAULT FALLBACK COORDS (Chennai Coast, India)
const DEFAULT_COORDS = [13.0827, 80.2707];

// ============================================================
// MAP HELPERS
// ============================================================

function FlyTo({ position }) {
  const map = useMap();

  useEffect(() => {
    if (position) {
      map.flyTo(position, 13, { duration: 1.2 });
    }
  }, [position, map]);

  return null;
}

function MapEventsHandler({ onLocationChange }) {
  useMapEvents({
    click(e) {
      onLocationChange([e.latlng.lat, e.latlng.lng]);
    },
  });
  return null;
}

function MapResizeFix() {
  const map = useMap();

  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 200);
    return () => clearTimeout(timer);
  }, [map]);

  return null;
}

// ============================================================
// LOCATION PICKER MODAL
// ============================================================

export default function LocationPicker({ onConfirm, onClose }) {
  const [coords, setCoords] = useState(DEFAULT_COORDS);
  const [status, setStatus] = useState("loading"); // loading | ready | fallback
  const [errorMsg, setErrorMsg] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const overlayRef = useRef(null);

  // --------------------------------------------------------
  // GPS DETECT
  // --------------------------------------------------------

  const detectGPS = useCallback(() => {
    if (!navigator.geolocation) {
      setStatus("fallback");
      setErrorMsg(
        "Geolocation not supported by browser. Search or click on the map to set location."
      );
      return;
    }

    setStatus("loading");
    setErrorMsg("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setCoords([latitude, longitude]);
        setStatus("ready");
      },
      (err) => {
        setStatus("fallback");
        if (err.code === 1) {
          setErrorMsg(
            "GPS access denied. You can search for a location or click anywhere on the map."
          );
        } else if (err.code === 2) {
          setErrorMsg(
            "GPS signal unavailable. Search or click on the map below."
          );
        } else {
          setErrorMsg(
            "GPS request timed out. Search or click on the map below."
          );
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  }, []);

  useEffect(() => {
    detectGPS();
  }, [detectGPS]);

  // --------------------------------------------------------
  // SEARCH LOCATION (NOMINATIM GEOCLEANING)
  // --------------------------------------------------------

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    setErrorMsg("");

    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          searchQuery.trim()
        )}`
      );
      const data = await res.json();

      if (Array.isArray(data) && data.length > 0) {
        const lat = parseFloat(data[0].lat);
        const lon = parseFloat(data[0].lon);
        setCoords([lat, lon]);
        setStatus("ready");
      } else {
        setErrorMsg(`No locations found for "${searchQuery}".`);
      }
    } catch {
      setErrorMsg("Failed to search location. Please try again.");
    } finally {
      setSearching(false);
    }
  };

  // --------------------------------------------------------
  // CLOSE ON BACKDROP CLICK
  // --------------------------------------------------------

  const handleBackdropClick = (e) => {
    if (e.target === overlayRef.current) {
      onClose();
    }
  };

  const [submitting, setSubmitting] = useState(false);

  // --------------------------------------------------------
  // CONFIRM
  // --------------------------------------------------------

  const handleConfirm = () => {
    if (!coords || submitting) return;

    setSubmitting(true);

    const location = {
      latitude: Number(coords[0].toFixed(6)),
      longitude: Number(coords[1].toFixed(6)),
    };

    onConfirm(location);
  };

  return (
    <div
      ref={overlayRef}
      onClick={handleBackdropClick}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      style={{ animation: "fadeIn 0.2s ease-out" }}
    >
      <div
        className="relative mx-4 flex w-full max-w-[520px] flex-col overflow-hidden rounded-2xl border border-[#202023] bg-[#0F0F0F] shadow-2xl"
        style={{ animation: "slideUp 0.25s ease-out" }}
      >
        {/* ====== HEADER ====== */}

        <div className="flex items-center justify-between border-b border-[#202023] px-5 py-3.5">
          <div className="flex items-center gap-2.5">
            <Navigation
              size={16}
              className="text-[#3DA7B7]"
              aria-hidden="true"
            />
            <h2 className="text-sm font-medium text-white">
              Select Location
            </h2>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close location picker"
            className="flex h-7 w-7 items-center justify-center rounded-full text-[#77777D] transition hover:bg-white/5 hover:text-white"
          >
            <X size={16} />
          </button>
        </div>

        {/* ====== BODY ====== */}

        <div className="space-y-3 px-5 py-4">

          {/* SEARCH BAR */}
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-1">
              <Search
                size={15}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[#77777D]"
              />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search city, port, or region (e.g. Chennai)..."
                className="w-full rounded-xl border border-[#202023] bg-[#0A0A0A] py-2 pl-9 pr-3 text-xs text-white placeholder-[#5F5F65] outline-none transition focus:border-[#3DA7B7]/50"
              />
            </div>
            <button
              type="submit"
              disabled={searching || !searchQuery.trim()}
              className="rounded-xl border border-[#2A2A2E] bg-[#161616] px-3.5 py-2 text-xs font-medium text-white transition hover:bg-[#202025] disabled:opacity-40"
            >
              {searching ? (
                <Loader2 size={14} className="animate-spin text-[#3DA7B7]" />
              ) : (
                "Search"
              )}
            </button>
          </form>

          {/* GPS DETECT BUTTON & COORDINATES */}
          <div className="flex items-center justify-between gap-2">
            <button
              type="button"
              onClick={detectGPS}
              disabled={status === "loading"}
              className="flex items-center gap-1.5 rounded-lg border border-[#202023] bg-[#0A0A0A] px-2.5 py-1.5 text-xs text-[#3DA7B7] transition hover:bg-[#151515] disabled:opacity-50"
            >
              <RefreshCw
                size={12}
                className={status === "loading" ? "animate-spin" : ""}
              />
              {status === "loading" ? "Detecting GPS..." : "Use My GPS"}
            </button>

            {coords && (
              <div className="flex items-center gap-1.5 text-xs text-[#9A9A9A]">
                <MapPin size={13} className="text-[#3DA7B7]" />
                <span>
                  {coords[0].toFixed(5)}, {coords[1].toFixed(5)}
                </span>
              </div>
            )}
          </div>

          {/* ERROR / NOTICE BANNER */}
          {errorMsg && (
            <p className="rounded-lg border border-red-900/30 bg-red-950/30 px-3 py-1.5 text-xs text-[#FF8A8A]">
              {errorMsg}
            </p>
          )}

          {/* LOADING STATE */}
          {status === "loading" && (
            <div className="flex flex-col items-center justify-center py-10">
              <Loader2 size={26} className="animate-spin text-[#3DA7B7]" />
              <p className="mt-2 text-xs text-[#9A9A9A]">Detecting location...</p>
            </div>
          )}

          {/* MAP */}
          {status !== "loading" && coords && (
            <div
              className="relative overflow-hidden rounded-xl border border-[#202023]"
              style={{ height: 260 }}
            >
              <MapContainer
                center={coords}
                zoom={12}
                scrollWheelZoom={true}
                style={{ height: "100%", width: "100%" }}
                zoomControl={false}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker
                  position={coords}
                  icon={orcaIcon}
                  draggable={true}
                  eventHandlers={{
                    dragend(e) {
                      const latlng = e.target.getLatLng();
                      setCoords([latlng.lat, latlng.lng]);
                      setStatus("ready");
                    },
                  }}
                />
                <FlyTo position={coords} />
                <MapEventsHandler
                  onLocationChange={(newCoords) => {
                    setCoords(newCoords);
                    setStatus("ready");
                  }}
                />
                <MapResizeFix />
              </MapContainer>

              <div className="absolute bottom-2 left-2 z-[400] rounded-md bg-black/70 px-2 py-1 text-[10px] text-[#9A9A9A] backdrop-blur-md">
                Click map or drag marker to adjust location
              </div>
            </div>
          )}
        </div>

        {/* ====== FOOTER ====== */}

        <div className="flex items-center justify-end gap-3 border-t border-[#202023] px-5 py-3.5">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-[#2A2A2E] bg-transparent px-4 py-2 text-xs font-medium text-[#9A9A9A] transition hover:bg-white/5 hover:text-white"
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={handleConfirm}
            disabled={!coords || submitting}
            className="rounded-lg bg-[#3DA7B7] px-5 py-2 text-xs font-semibold text-black transition hover:bg-[#52b8c8] disabled:opacity-50"
          >
            Confirm Location
          </button>
        </div>
      </div>

      {/* ====== ANIMATIONS ====== */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to   { opacity: 1; }
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
