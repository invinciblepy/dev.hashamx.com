import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ProjectsPage from "./pages/ProjectsPage";

function App() {
  return (
    <Router basename="/dev.hashamx.com">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/project/:scraperName" element={<ProjectsPage />} />
      </Routes>
    </Router>
  );
}

export default App
