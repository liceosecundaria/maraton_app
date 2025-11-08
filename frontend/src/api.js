export async function registrarParticipante(formData) {
    const response = await fetch("http://localhost:8000/api/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });
  
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw err;
    }
  
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
  
    const a = document.createElement("a");
    a.href = url;
    a.download = "credencial.pdf";
    a.click();
  
    window.URL.revokeObjectURL(url);
  }
  