import { useEffect, useState } from "react";
import { getCurrentUser } from "../../../services/authApi";

export default function ProfileCard({ onClose }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then((data) => {
        setUser(data);
      })
      .catch((error) => {
        console.error("Failed to load profile:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="w-[320px] rounded-2xl border border-[#2A2A2E] bg-[#111113] p-5 shadow-2xl">
        <p className="text-sm text-[#99999F]">
          Loading profile...
        </p>
      </div>
    );
  }

  return (
    <div className="w-[320px] overflow-hidden rounded-2xl border border-[#2A2A2E] bg-[#111113] shadow-2xl">
      <div className="flex items-center justify-between border-b border-[#242427] px-5 py-4">
        <div>
          <p className="text-sm font-semibold text-white">
            Profile
          </p>

          <p className="mt-0.5 text-xs text-[#77777C]">
            Account information
          </p>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="flex h-7 w-7 items-center justify-center rounded-md text-[#77777C] transition hover:bg-[#1B1B1D] hover:text-white"
          aria-label="Close profile"
        >
          ×
        </button>
      </div>

      <div className="px-5 py-5">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-[#3DA7B7]/15 text-lg font-semibold text-[#3DA7B7] ring-1 ring-[#3DA7B7]/30">
            {user?.username?.charAt(0).toUpperCase() || "U"}
          </div>

          <div className="min-w-0">
            <p className="truncate text-base font-semibold text-white">
              {user?.username || "User"}
            </p>

            <p className="mt-1 truncate text-xs text-[#8A8A90]">
              {user?.email || "No email available"}
            </p>
          </div>
        </div>

        <div className="mt-5">
          <div className="rounded-xl border border-[#242427] bg-[#171719] px-4 py-3">
            <p className="text-[11px] uppercase tracking-wider text-[#6F6F75]">
              Role
            </p>

            <p className="mt-1 text-sm text-[#EDEDEF]">
              {user?.role || "USER"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}