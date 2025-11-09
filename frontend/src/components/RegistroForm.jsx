import React, { useState } from "react";
import axios from "axios";
import "../form.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

function RegistroForm() {
  const [formData, setFormData] = useState({
    full_name: "",
    plantel: "",
    child_name: "",
    grado: "",
    role: "",
  });

  const [statusMsg, setStatusMsg] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatusMsg("Generando gafetes...");
  
    // Normaliza lo que envías al backend
    const payload = {
      full_name: (formData.full_name || "").trim(),
      plantel: (formData.plantel || "").trim(),         // "Primaria" | "Secundaria" | "Preparatoria"
      child_name: (formData.child_name || "").trim(),
      grado: (formData.grado || "").trim(),
      role: ((formData.role || "").toUpperCase()).trim() // "ACOMPAÑANTE MUJER" | "ALUMNO" | etc.
    };
  
    try {
      const response = await axios.post(
        "https://maraton-lma-backend.onrender.com/api/register/",
        payload,
        {
          responseType: "arraybuffer",
          validateStatus: () => true,
        }
      );
      
      
      const ct = response.headers["content-type"] || "";
  
      // Si el backend devolvió PDF correcto
      if (response.status >= 200 && response.status < 300 && ct.includes("application/pdf")) {
        const blob = new Blob([response.data], { type: "application/pdf" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "credencial.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
        setStatusMsg("Listo ✅ Se descargó tu gafete.");
        return;
      }
  
     // >>> si no es PDF, intenta leer JSON de error o texto
  let msg = `Error ${response.status}`;
  try {
    const text = new TextDecoder().decode(response.data);
    // intenta JSON
    try {
      const json = JSON.parse(text);
      msg =
        typeof json === "string"
          ? json
          : Object.entries(json)
              .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
              .join(" • ");
    } catch {
      msg = text; // HTML o texto plano del error
    }
  } catch {}
  setStatusMsg(`Error al registrar. ${msg}`);
} catch (err) {
  console.error("FETCH_ERROR", err);
  setStatusMsg(`Error al registrar. ${String(err?.message || err)}`);
}
  };
  

  return (
    <div className="form-card">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Nombre completo (quien corre):</label>
          <input
            type="text"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            required
            className="form-field"
          />
        </div>
  
        <div className="form-group">
          <label className="form-label">Plantel:</label>
          <select
            name="plantel"
            value={formData.plantel}
            onChange={handleChange}
            required
            className="form-field"
          >
            <option value="">Selecciona una opción</option>
            <option value="Primaria">Primaria</option>
            <option value="Secundaria">Secundaria</option>
            <option value="Preparatoria">Preparatoria</option>
          </select>
        </div>
  
        <div className="form-group">
          <label className="form-label">Nombre completo del alumno(a):</label>
          <input
            type="text"
            name="child_name"
            value={formData.child_name}
            onChange={handleChange}
            className="form-field"
          />
        </div>
  
        <div className="form-group">
  <label className="form-label">Grado del alumno/hijo(a):</label>
  <select
    name="grado"
    value={formData.grado}
    onChange={handleChange}
    className="form-field"
    required
  >
    <option value="">Selecciona un grado</option>
    <optgroup label="Primaria">
      <option value="1er Grado Primaria">1er Grado Primaria</option>
      <option value="2do Grado Primaria">2do Grado Primaria</option>
      <option value="3er Grado Primaria">3er Grado Primaria</option>
      <option value="4to Grado Primaria">4to Grado Primaria</option>
      <option value="5to Grado Primaria">5to Grado Primaria</option>
      <option value="6to Grado Primaria">6to Grado Primaria</option>
    </optgroup>
    <optgroup label="Secundaria">
      <option value="1er Grado Secundaria">1er Grado Secundaria</option>
      <option value="2do Grado Secundaria">2do Grado Secundaria</option>
      <option value="3er Grado Secundaria">3er Grado Secundaria</option>
    </optgroup>
    <optgroup label="Preparatoria">
      <option value="1er Semestre Preparatoria">1er Semestre Preparatoria</option>
      <option value="3er Semestre Preparatoria">3er Semestre Preparatoria</option>
    </optgroup>
  </select>
</div>

  
        <div className="form-group">
          <label className="form-label">Eres:</label>
          <select
            name="role"
            value={formData.role}
            onChange={handleChange}
            required
            className="form-field"
          >
            <option value="">Selecciona</option>
            <option value="ACOMPAÑANTE HOMBRE">Acompañante Hombre</option>
            <option value="ACOMPAÑANTE MUJER">Acompañante Mujer</option>
            <option value="ABUELITO">Abuelito</option>
            <option value="ABUELITA">Abuelita</option>
 
          </select>
        </div>
  
        <button type="submit" className="btn-primary">
          Generar gafete PDF
        </button>
  
        <p
          className="form-status"
          style={{
            color:
              statusMsg.includes("Error") || statusMsg.includes("Revisa")
                ? "red"
                : "#333",
            fontWeight:
              statusMsg.includes("Error") || statusMsg.includes("Revisa")
                ? 600
                : 400,
          }}
        >
          {statusMsg}
        </p>
      </form>
    </div>
  );
  
}

export default RegistroForm;
