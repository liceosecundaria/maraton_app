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
      <header style={{ display: "flex", justifyContent: "center" }}>
        <div
          style={{
            width: "100%",
            maxWidth: "1100px",
            background: "#ffffff",
            borderRadius: "14px",
            boxShadow: "0 6px 18px rgba(0,0,0,0.08)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "18px 28px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <img src={logoLMA} alt="LMA" style={{ height: "170px" }} />
            <div>
              <h1
                style={{
                  fontSize: "4.6rem",
                  fontWeight: 900,
                  color: "#001B5E",
                  margin: 0,
                  lineHeight: 1.2,
                  textAlign: "center",
                }}
              >
                MARATÓN LMA 2025
              </h1>
              <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
                <span style={{ height: 15, width: 250, background: "#003366", borderRadius: 2 }} />
                <span style={{ height: 15, width: 250, background: "#C62828", borderRadius: 2 }} />
                <span style={{ height: 15, width: 250, background: "#2E7D32", borderRadius: 2 }} />
              </div>
            </div>
          </div>

          <div style={{ position: "relative", display: "inline-block" }}>
            <img src={zorro} alt="Zorro" style={{ height: "170px" }} onClick={openAdmin}
              title="Administración" />
            
          </div>
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
