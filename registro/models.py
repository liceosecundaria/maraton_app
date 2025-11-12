from django.db import models
import re

PLANTEL_CHOICES = [
    ("Primaria", "Primaria"),
    ("Secundaria", "Secundaria"),
    ("Preparatoria", "Preparatoria"),
]

ROLE_CHOICES = [
    ("ACOMPAÑANTE HOMBRE", "Acompañante Hombres"),
    ("ACOMPAÑANTE MUJER", "Acompañante Mujer"),
    ("ABUELITO", "Abuelito"),
    ("ABUELITA", "Abuelita"),
    ("ALUMNOS LMA BAJAH","ALUMNOS LMA Primaria (primaria baja hombres 1°, 2° y 3°)"),
    ("ALUMNOS LMA BAJAM","ALUMNOS LMA Primaria (primaria baja mujeres 1°, 2° y 3°)"),
    ("ALUMNOS LMA ALTAM","ALUMNOS LMA Primaria (primaria alta mujeres 4°, 5° y 6°)"),
    ("ALUMNOS LMA ALTAH","ALUMNOS LMA Primaria (primaria alta hombres 4°, 5° y 6°)"),
    ("ALUMNOS LMA SECH","ALUMNOS LMA Secundaria (hombres)"),
    ("ALUMNOS LMA SECM","ALUMNOS LMA Secundaria (mujeres)"),
    ("ALUMNOS LMA PREPH","ALUMNOS LMA Preparatoria (hombres)"),
    ("ALUMNOS LMA PREPM","ALUMNOS LMA Preparatoria (mujeres)"),
]
class Participant(models.Model):
    full_name = models.CharField(max_length=200)
    plantel = models.CharField(max_length=50)
    child_name = models.CharField(max_length=200, blank=True, default="")
    grado = models.CharField(max_length=100, blank=True, default="")
    role = models.CharField(max_length=80)
    # Folio: permite null/blank para la creación y lo llenas en views
    clave = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # 🔹 IMPORTANTE: mantener estos dos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    # (NO pongas updated_at si ya te dio guerra)

    def __str__(self):
        return f"{self.full_name} ({self.plantel})"

        return f"{self.full_name} - {self.clave or ''}"

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)  # obtener id
        if creating and not self.clave:
            prefix_map = {"Primaria": "Primaria", "Secundaria": "Secundaria", "Preparatoria": "Prepa"}
            prefix = prefix_map.get(self.plantel, "GEN")

            last = Participant.objects.filter(clave__startswith=prefix).order_by("-id").first()
            num = 1
            if last and last.clave:
                m = re.search(r"(\d+)$", last.clave)
                if m:
                    num = int(m.group(1)) + 1

            self.clave = f"{prefix}{num:04d}"
            super().save(update_fields=["clave"])
