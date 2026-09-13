<<<<<<< HEAD
import { useState } from 'react';
import Login from './pages/login';
import Register from './pages/register';
import orcaLogo from './assets/orca-logo.png';
import './App.css';
import Navbar from './landing/Navbar';
import Hero from './landing/Hero';
import ProductVideo from './landing/ProductVideo';
import ProductShowcase from './landing/ProductShowcase';
import Features from './landing/Features';
import PlatformCapabilities from './landing/PlatformCapabilities';
import FisherFocus from './landing/FisherFocus';
import HowItWorks from './landing/HowItWorks';
import MapShowcase from './landing/MapShowcase';
import FinalCTA from './landing/FinalCTA';
import Footer from './landing/Footer';

export default function LandingPage() {
  return (
    <div className="bg-void min-h-screen font-body">
      <Navbar />
      <main>
        <Hero />
        <ProductVideo />
        <ProductShowcase />
        <Features />
        <PlatformCapabilities />
        <FisherFocus />
        <HowItWorks />
        <MapShowcase />
        <FinalCTA />
      </main>
      <Footer />
    </div>
=======
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
>>>>>>> 0e54a27cdbd1775ac4fedf774a43cc1bef6b467c
  );
}