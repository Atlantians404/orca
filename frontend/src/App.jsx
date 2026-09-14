import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";

import LandingPage from "./features/landingpage";
import ChatPage from "./features/chat/pages/ChatPage";
import AppLayout from "./components/layout/AppLayout";
import MapsPage from "./pages/MapsPage";
import ProfilePage from "./pages/ProfilePage";
import Login from "./pages/login";
import Register from "./pages/register";

function LoginPageWrapper() {
  const navigate = useNavigate();
  return (
    <>
      <LandingPage />
      <Login
        isOpen={true}
        onClose={() => navigate('/')}
        onSwitchToRegister={() => navigate('/signup')}
        onLogin={async (payload) => {
          console.log("Logged in:", payload);
          navigate('/chat');
        }}
      />
    </>
  );
}

function RegisterPageWrapper() {
  const navigate = useNavigate();
  return (
    <>
      <LandingPage />
      <Register
        isOpen={true}
        onClose={() => navigate('/')}
        onSwitchToLogin={() => navigate('/login')}
        onRegister={async (payload) => {
          console.log("Registered:", payload);
          navigate('/chat');
        }}
      />
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Landing page */}
        <Route
          path="/"
          element={<LandingPage />}
        />
        <Route
          path="/login"
          element={<LoginPageWrapper />}
        />
        <Route
          path="/signup"
          element={<RegisterPageWrapper />}
        />
        <Route
          path="/register"
          element={<RegisterPageWrapper />}
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