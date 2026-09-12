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
  );
}