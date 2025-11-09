import React, { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE;


// Debajo de los imports y antes del export default function AdminPanel()...
const formatDateTime = (isoString) => {
    if (!isoString) return "";
    const d = new Date(isoString);
    return d.toLocaleString("es-MX", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };
  

export default function AdminPanel() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [busca, setBusca] = useState("");

  // Carga lista
  const load = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/participants/`, {
        validateStatus: () => true,
      });
      if (res.status === 200) {
        setRows(res.data || []);
      } else {
        alert("Error listando participantes");
      }
    } catch (e) {
      console.error(e);
      alert("Error de red listando participantes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  // Descargar CSV como archivo
const onDownloadCSV = async () => {
    try {
      const res = await axios.get(`${API_BASE}/participants/export/`, {
        responseType: "blob",
        validateStatus: () => true,
      });
  
      if (res.status === 200) {
        const cd = res.headers["content-disposition"] || "";
        const m = /filename="?([^"]+)"?/i.exec(cd);
        const filename = m ? m[1] : "participantes.csv";
  
        const blob = new Blob([res.data], { type: "text/csv;charset=utf-8" });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        const text = await new Response(res.data).text();
        alert(`Error al descargar CSV: ${text || res.status}`);
      }
    } catch (e) {
      console.error(e);
      alert("Error al descargar CSV (red/CORS)");
    }
  };
  
  // Reimpresión de PDF (abre nueva pestaña)
  const onReprint = () => {
    const q = (busca || "").trim();
    if (!q) {
      alert("Escribe un folio o id");
      return;
    }
    const url = `${API_BASE}/participants/reprint/?q=${encodeURIComponent(q)}`;
    window.open(url, "_blank"); // Deja que el navegador lo descargue/abra
  };

  return (
    <div style={{ padding: 16 }}>
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
    <h2 style={{ marginTop: 0 }}>Panel administrativo</h2>
    <button
      onClick={() => {
        window.location.href = "/"; // Ruta principal del registro
      }}
      style={{
        backgroundColor: "#eee",
        border: "1px solid #ccc",
        borderRadius: "6px",
        padding: "6px 12px",
        cursor: "pointer",
      }}
    >
      ← Regresar al registro
    </button>
  </div>


      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button onClick={load} disabled={loading}>
          {loading ? "Cargando..." : "Actualizar lista"}
        </button>

        <button onClick={onDownloadCSV}>Descargar CSV</button>

        <input
          placeholder="Folio (p.ej. Primaria0007) o ID"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          style={{ flex: 1, padding: "8px 10px" }}
        />
        <button onClick={onReprint}>Reimprimir PDF</button>
      </div>

      <div style={{ overflow: "auto", maxHeight: 400, border: "1px solid #ddd" }}>
        <table width="100%" cellPadding="8" style={{ borderCollapse: "collapse" }}>
          <thead style={{ background: "#f5f5f5" }}>
            <tr>
              <th align="left">ID</th>
              <th align="left">Folio</th>
              <th align="left">Plantel</th>
              <th align="left">Nombre</th>
              <th align="left">Alumno</th>
              <th align="left">Grado</th>
              <th align="left">Rol</th>
              <th align="left">Creado</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} style={{ borderTop: "1px solid #eee" }}>
                <td>{r.id}</td>
                <td>{r.clave}</td>
                <td>{r.plantel}</td>
                <td>{r.full_name}</td>
                <td>{r.child_name}</td>
                <td>{r.grado}</td>
                <td>{r.role}</td>
                <td>{formatDateTime(r.created_at)}</td>

              </tr>
            ))}
            {rows.length === 0 && !loading && (
              <tr>
                <td colSpan={8} align="center" style={{ padding: 20, color: "#666" }}>
                  Sin registros
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <p style={{ marginTop: 12, color: "#666" }}>
        Tip: escribe un <b>ID</b> (número) o un <b>Folio</b> (p.ej. <i>Primaria0007</i>) y pulsa “Reimprimir PDF”.
      </p>
    </div>
  );
}
