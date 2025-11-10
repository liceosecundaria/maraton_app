// src/App.jsx
// src/App.jsx
import React from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import RegistroForm from "./components/RegistroForm.jsx";
import AdminPanel from "./components/AdminPanel.jsx";
import logoLMA from "./assets/logo_lma.png";
import zorro from "./assets/zorro_maraton.png";

const ADMIN_PIN = "lma2025";

export default function App() {
  const navigate = useNavigate();

  const openAdmin = () => {
    const pin = window.prompt("Ingrese PIN administrativo:");
    if (pin === ADMIN_PIN) {
      navigate("/admin");
    } else if (pin !== null) {
      alert("PIN incorrecto.");
    }
  };

  return (
    <div className="app-shell">
      <header className="site-header">
  <div className="site-header-inner">
    <div className="site-header-left">
      <img src={logoLMA} alt="LMA" className="site-logo" />
      <div>
      <h1
  style={{
    fontSize: "clamp(1.8rem, 5vw, 3rem)", // 👈 tamaño flexible
    fontWeight: 900,
    color: "#001B5E",
    margin: 0,
    lineHeight: 1.2,
    textAlign: "center",
  }}
>
  MARATÓN LMA 2025
</h1>


        <div className="site-title-bars">
          <span className="bar bar-azul" />
          <span className="bar bar-roja" />
          <span className="bar bar-verde" />
        </div>
      </div>
    </div>

    <img src={zorro} alt="Zorro" className="site-mascota"  onClick={openAdmin}/>
  </div>
</header>


      {/* Definimos las páginas */}
      <Routes>
        <Route path="/" element={<RegistroForm />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>

      <footer className="site-footer">
        <div style={{ fontWeight: 600, color: "#001B5E", marginBottom: 2 }}>
          Conmemoración del 20 de Noviembre — Maratón LMA 2025
        </div>
        <div style={{ fontSize: "14px" }}>
          © {new Date().getFullYear()} Liceo México Americano — Todos los derechos reservados.
        </div>
        <div style={{ display: "flex", width: "100%", height: "6px", marginTop: "14px" }}>
          <div style={{ flex: 1, backgroundColor: "#003366" }} />
          <div style={{ flex: 1, backgroundColor: "#C62828" }} />
          <div style={{ flex: 1, backgroundColor: "#2E7D32" }} />
        </div>
      </footer>
    </div>
  );
}
