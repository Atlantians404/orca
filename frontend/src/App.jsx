import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './features/landingpage';
import ChatPage from './features/chat/pages/ChatPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/test-sessions" element={<ChatPage />} />
      </Routes>
    </BrowserRouter>
  );
}