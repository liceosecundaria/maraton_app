# registro/serializers.py
# registro/serializers.py
from rest_framework import serializers
from .models import Participant

PLANTELES = ["Primaria", "Secundaria", "Preparatoria"]
ROLES = [
    "ACOMPAÑANTE HOMBRE",
    "ACOMPAÑANTE MUJER",
    "ABUELITO",
    "ABUELITA",
    "TUTOR",
    "ALUMNO",
]

from rest_framework import serializers
from .models import Participant

class ParticipantSerializer(serializers.ModelSerializer):
    # Tus campos existentes
    child_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    grado = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    plantel = serializers.CharField()
    full_name = serializers.CharField()
    role = serializers.CharField()

    # Campos adicionales de solo lectura
    clave = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Participant
        fields = [
            "id",
            "full_name",
            "plantel",
            "child_name",
            "grado",
            "role",
            "clave",        # ← Folio único generado por el sistema
            "created_at",   # ← Fecha de registro
        ]



    def to_internal_value(self, data):
        # Normaliza antes de validar choices
        d = super().to_internal_value({
            **data,
            "plantel": (data.get("plantel") or "").strip().title(),   # Primaria|Secundaria|Preparatoria
            "role": (data.get("role") or "").strip().upper(),         # ACOMPAÑANTE MUJER, etc.
            "child_name": (data.get("child_name") or "").strip(),
            "grado": (data.get("grado") or "").strip(),
            "full_name": (data.get("full_name") or "").strip(),
        })
        return d

    def validate(self, attrs):
        # Si es ALUMNO, pide alumno y grado
        if attrs.get("role") == "ALUMNO":
            if not attrs.get("child_name"):
                raise serializers.ValidationError({"child_name": "Requerido para ALUMNO."})
            if not attrs.get("grado"):
                raise serializers.ValidationError({"grado": "Requerido para ALUMNO."})
        return attrs

