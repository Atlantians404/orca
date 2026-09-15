import { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { X, Loader2, MapPin, Navigation } from "lucide-react";

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
// CUSTOM MARKER ICON (ORCA accent)
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

// ============================================================
// HELPER: Fly map to location
// ============================================================

function FlyTo({ position }) {
  const map = useMap();

  useEffect(() => {
    if (position) {
      map.flyTo(position, 14, { duration: 1.2 });
    }
  }, [position, map]);

  return null;
}

// ============================================================
// LOCATION PICKER MODAL
// ============================================================

export default function LocationPicker({ onConfirm, onClose }) {
  const [coords, setCoords] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | ready | error | denied
  const [errorMsg, setErrorMsg] = useState("");
  const overlayRef = useRef(null);

  // --------------------------------------------------------
  // AUTO-DETECT GPS
  // --------------------------------------------------------

  useEffect(() => {
    if (!navigator.geolocation) {
      setStatus("error");
      setErrorMsg("Geolocation is not supported by your browser.");
      return;
    }

    setStatus("loading");

    const watchId = navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setCoords([latitude, longitude]);
        setStatus("ready");
      },
      (err) => {
        if (err.code === 1) {
          setStatus("denied");
          setErrorMsg(
            "Location access was denied. Please enable GPS in your browser settings."
          );
        } else if (err.code === 2) {
          setStatus("error");
          setErrorMsg(
            "Location unavailable. Please check your device GPS."
          );
        } else {
          setStatus("error");
          setErrorMsg("Location request timed out. Please try again.");
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0,
      }
    );

    return () => {
      // getCurrentPosition doesn't return a watchId, but this is safe
    };
  }, []);

  // --------------------------------------------------------
  // CLOSE ON BACKDROP CLICK
  // --------------------------------------------------------

  const handleBackdropClick = (e) => {
    if (e.target === overlayRef.current) {
      onClose();
    }
  };

  // --------------------------------------------------------
  // CONFIRM
  // --------------------------------------------------------

  const handleConfirm = () => {
    if (coords) {
      const coordString = `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`;
      onConfirm(coordString);
    }
  };

  // --------------------------------------------------------
  // RENDER
  // --------------------------------------------------------

  return (
    <div
      ref={overlayRef}
      onClick={handleBackdropClick}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      style={{ animation: "fadeIn 0.2s ease-out" }}
    >
      <div
        className="relative mx-4 flex w-full max-w-[480px] flex-col overflow-hidden rounded-2xl border border-[#202023] bg-[#0F0F0F] shadow-2xl"
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
              Your Current Location
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

        <div className="px-5 py-4">

          {/* -- LOADING -- */}
          {status === "loading" && (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2
                size={28}
                className="animate-spin text-[#3DA7B7]"
              />
              <p className="mt-3 text-sm text-[#9A9A9A]">
                Detecting your GPS location...
              </p>
            </div>
          )}

          {/* -- ERROR / DENIED -- */}
          {(status === "error" || status === "denied") && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <MapPin
                size={28}
                className="text-red-400"
              />
              <p className="mt-3 max-w-[320px] text-sm leading-6 text-[#9A9A9A]">
                {errorMsg}
              </p>

              <button
                type="button"
                onClick={onClose}
                className="mt-5 rounded-lg border border-[#2A2A2E] bg-[#161616] px-5 py-2 text-xs font-medium text-white transition hover:border-[#3DA7B7]/40 hover:bg-[#1A1A1A]"
              >
                Close
              </button>
            </div>
          )}

          {/* -- MAP -- */}
          {status === "ready" && coords && (
            <>
              {/* Coordinates Display */}
              <div className="mb-3 flex items-center gap-2 rounded-lg border border-[#202023] bg-[#0A0A0A] px-3 py-2">
                <MapPin
                  size={14}
                  className="shrink-0 text-[#3DA7B7]"
                />
                <span className="text-xs text-[#9A9A9A]">
                  {coords[0].toFixed(6)}, {coords[1].toFixed(6)}
                </span>
              </div>

              {/* Leaflet Map */}
              <div
                className="overflow-hidden rounded-xl border border-[#202023]"
                style={{ height: 260 }}
              >
                <MapContainer
                  center={coords}
                  zoom={14}
                  scrollWheelZoom={true}
                  style={{ height: "100%", width: "100%" }}
                  zoomControl={false}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <Marker position={coords} icon={orcaIcon} />
                  <FlyTo position={coords} />
                </MapContainer>
              </div>
            </>
          )}
        </div>

        {/* ====== FOOTER ====== */}

        {status === "ready" && coords && (
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
              className="rounded-lg bg-[#3DA7B7] px-5 py-2 text-xs font-semibold text-black transition hover:bg-[#52b8c8]"
            >
              Confirm Location
            </button>
          </div>
        )}
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
