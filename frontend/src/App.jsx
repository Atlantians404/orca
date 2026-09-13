import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './features/landingpage';
import ChatPage from './features/chat/pages/ChatPage';
import AppLayout from './components/layout/AppLayout';
import MapsPage from "./pages/MapsPage";
import ProfilePage from "./pages/ProfilePage";
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
<<<<<<< HEAD
=======
<<<<<<< HEAD

        {/* Routes inside AppLayout get the sidebar + collapse/drawer behavior */}
        <Route element={<AppLayout />}>
          <Route path="/test-sessions" element={<ChatPage />} />
          <Route path="/maps" element={<MapsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
=======
>>>>>>> origin/main
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/test-sessions" element={<ChatPage />} />
>>>>>>> origin/main
      </Routes>
    </BrowserRouter>
  );
}