# registro/models.py
from django.db import models

class Participant(models.Model):
    full_name = models.CharField(max_length=200)
    plantel   = models.CharField(max_length=50)
    child_name = models.CharField(max_length=200, blank=True)
    grado     = models.CharField(max_length=100, blank=True)
    role      = models.CharField(max_length=50)
    clave     = models.CharField(max_length=50, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)  # 👈
    updated_at = models.DateTimeField(auto_now=True)      # 👈


    class Meta:
        indexes = [
            models.Index(fields=["plantel"]),
            models.Index(fields=["clave"]),
            models.Index(fields=["full_name"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.clave})"

    PLANTEL_CHOICES = [
        ("Primaria", "Primaria"),
        ("Secundaria", "Secundaria"),
        ("Preparatoria", "Preparatoria"),
    ]
    ROLE_CHOICES = [
        ("ALUMNO", "Alumno"),
        ("TUTOR", "Tutor"),
        ("ACOMPAÑANTE HOMBRE", "Acompañante Hombre"),
        ("ACOMPAÑANTE MUJER", "Acompañante Mujer"),
        ("ABUELITO", "Abuelito"),
        ("ABUELITA", "Abuelita"),
    ]

    full_name = models.CharField(max_length=120)
    plantel = models.CharField(max_length=20, choices=PLANTEL_CHOICES)
    child_name = models.CharField(max_length=120, blank=True, default="")
    grado = models.CharField(max_length=60, blank=True, default="")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)  # 👈 30
    clave = models.CharField(max_length=40, blank=True, default="")
