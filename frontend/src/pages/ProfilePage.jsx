import { useState } from "react";
import ProfileCard from "../features/chat/components/ProfileCard";

export default function ProfilePage() {
  const [showProfile, setShowProfile] = useState(true);

  return (
    <div className="relative flex h-full items-center justify-center bg-[#0A0A0B]">
      {showProfile && (
        <ProfileCard onClose={() => setShowProfile(false)} />
      )}
    </div>
  );
}