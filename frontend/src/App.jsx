import { BrowserRouter, Routes, Route } from "react-router-dom";

import LandingPage from "./features/landingpage";
import ChatPage from "./features/chat/pages/ChatPage";
import AppLayout from "./components/layout/AppLayout";
import MapsPage from "./pages/MapsPage";
import ProfilePage from "./pages/ProfilePage";


export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Landing page */}
        <Route
          path="/"
          element={<LandingPage />}
        />


        {/* =================================================
            APPLICATION LAYOUT

            These pages share:
            - Sidebar
            - Chat UI
            - Maps
            - Profile
            - Sidebar collapse/drawer
            ================================================= */}

        <Route element={<AppLayout />}>

          {/* Main chat */}
          <Route
            path="/chat"
            element={<ChatPage />}
          />

          {/* Existing test/session route */}
          <Route
            path="/test-sessions"
            element={<ChatPage />}
          />

          {/* Maps */}
          <Route
            path="/maps"
            element={<MapsPage />}
          />

          {/* Profile */}
          <Route
            path="/profile"
            element={<ProfilePage />}
          />

        </Route>

      </Routes>
    </BrowserRouter>
  );
}