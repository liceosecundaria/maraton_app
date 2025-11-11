# registro/models.py
import re
from django.db import models

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
    ("ALUMNOS LMA BAJAH", "ALUMNOS LMA Primaria (primaria baja hombres 1°, 2° y 3°)"),
    ("ALUMNOS LMA BAJAM", "ALUMNOS LMA Primaria (primaria baja mujeres 1°, 2° y 3°)"),
    ("ALUMNOS LMA ALTAM", "ALUMNOS LMA Primaria (primaria alta mujeres 4°, 5° y 6°)"),
    ("ALUMNOS LMA ALTAH", "ALUMNOS LMA Primaria (primaria alta hombres 4°, 5° y 6°)"),
    ("ALUMNOS LMA SECH",  "ALUMNOS LMA Secundaria (hombres)"),
    ("ALUMNOS LMA SECM",  "ALUMNOS LMA Secundaria (mujeres)"),
    ("ALUMNOS LMA PREPH", "ALUMNOS LMA Preparatoria (hombres)"),
    ("ALUMNOS LMA PREPM", "ALUMNOS LMA Preparatoria (mujeres)"),
]


class Participant(models.Model):
    full_name  = models.CharField(max_length=255)
    plantel    = models.CharField(max_length=20, choices=PLANTEL_CHOICES)
    child_name = models.CharField(max_length=255, blank=True, null=True)
    grado      = models.CharField(max_length=255, blank=True, null=True)
    role       = models.CharField(max_length=60, choices=ROLE_CHOICES)

    # FOLIO
    clave      = models.CharField(
        max_length=40,
        blank=True,
        editable=False,
        unique=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.plantel})"

    def save(self, *args, **kwargs):
        """
        Genera un folio secuencial por plantel:
        Primaria0001, Primaria0002, Secundaria0001, etc.
        Independiente de la categoría / role.
        """
        creating = self.pk is None

        # Guardar primero para tener self.id
        super().save(*args, **kwargs)

        if creating and not self.clave:
            prefix_map = {
                "Primaria": "Primaria",
                "Secundaria": "Secundaria",
                "Preparatoria": "Prepa",
            }
            prefix = prefix_map.get(self.plantel, "GEN")

            # Buscar el último folio de ese plantel
            last = (
                Participant.objects
                .filter(clave__startswith=prefix)
                .order_by("-id")
                .first()
            )

            num = 1
            if last and last.clave:
                m = re.search(r"(\d+)$", last.clave)
                if m:
                    num = int(m.group(1)) + 1

            self.clave = f"{prefix}{num:04d}"
            super().save(update_fields=["clave"])
