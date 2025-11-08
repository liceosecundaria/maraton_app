# registro/views.py

import csv
import re
import os
from django.http import FileResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.db.models import Q
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Participant
from .serializers import ParticipantSerializer
from .pdf_generator import generar_credencial_pdf


# =======================
# Generación de folio
# =======================

def generar_clave(plantel: str) -> str:
    """
    Genera folio por plantel con 4 dígitos:
    Primaria0001, Secundaria0001, Preparatoria0001, etc.
    Toma cualquier folio existente que termine en números.
    """
    prefix = (plantel or "").strip().title()   # "Primaria" | "Secundaria" | "Preparatoria"

    existentes = (
        Participant.objects
        .filter(plantel=plantel)
        .exclude(clave__isnull=True)
        .exclude(clave__exact="")
        .values_list("clave", flat=True)
    )

    max_n = 0
    for clave in existentes:
        m = re.search(r'(\d+)$', (clave or ""))
        if m:
            try:
                n = int(m.group(1))
                if n > max_n:
                    max_n = n
            except ValueError:
                pass

    siguiente = max_n + 1
    return f"{prefix}{siguiente:04d}"


# =======================
# 1) Registro + generación de PDF
# =======================

class RegisterParticipantView(APIView):
    def post(self, request):
        serializer = ParticipantSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        ADULTO_ROLES = ["ACOMPAÑANTE HOMBRE", "ACOMPAÑANTE MUJER",
                        "ABUELITO", "ABUELITA", "TUTOR"]
        role_value = (data.get("role") or "").upper()
        plantel = data.get("plantel") or ""

        clave_generada = generar_clave(plantel) if role_value in ADULTO_ROLES else ""

        participant = Participant.objects.create(
            full_name=data.get("full_name"),
            plantel=plantel,
            child_name=data.get("child_name", ""),
            grado=data.get("grado", ""),
            role=data.get("role"),
            clave=clave_generada,
        )

        pdf_path = generar_credencial_pdf(participant)

        filename = (participant.clave or "credencial") + ".pdf"
        return FileResponse(
            open(pdf_path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )


# =======================
# 2) Listado de participantes (para el panel admin)
# =======================

class ParticipantListView(APIView):
    """
    Devuelve la lista de participantes en JSON.
    GET /api/participants/
    """
    def get(self, request):
        qs = Participant.objects.all().order_by("-created_at", "-id")
        serializer = ParticipantSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# =======================
# 3) Exportar CSV
# =======================

class ExportParticipantsCSV(APIView):
    """
    Descarga un CSV con todos los participantes.
    GET /api/participants/export/
    """
    def get(self, request):
        qs = Participant.objects.all().order_by("plantel", "role", "full_name")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="participantes_maraton.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Folio",
            "Nombre participante",
            "Plantel",
            "Nombre alumno",
            "Grado",
            "Rol",
            "Fecha registro",
        ])

        for p in qs:
            writer.writerow([
                p.clave or "",
                p.full_name or "",
                p.plantel or "",
                p.child_name or "",
                p.grado or "",
                p.role or "",
                p.created_at.strftime("%Y-%m-%d %H:%M") if getattr(p, "created_at", None) else "",
            ])

        return response


# =======================
# 4) Estadísticas simples
# =======================

class ParticipantsStats(APIView):
    """
    Devuelve estadísticas simples para el panel.
    GET /api/participants/stats/
    """
    def get(self, request):
        total = Participant.objects.count()

        por_plantel = list(
            Participant.objects.values("plantel")
            .annotate(total=Count("id"))
            .order_by("plantel")
        )

        por_role = list(
            Participant.objects.values("role")
            .annotate(total=Count("id"))
            .order_by("role")
        )

        data = {
            "total": total,
            "por_plantel": por_plantel,
            "por_role": por_role,
        }
        return Response(data, status=status.HTTP_200_OK)


# =======================
# 5) Reimpresión de gafete
# =======================

class ReprintPdfView(APIView):
    """
    Reimprime un PDF dado un folio (clave) o un ID, vía ?q=
    Ejemplos:
      /api/participants/reprint/?q=Primaria0007
      /api/participants/reprint/?q=12
    """
    def get(self, request, *args, **kwargs):
        # 1) leer parámetro q de la URL
        q = request.query_params.get("q") or request.GET.get("q")
        if not q:
            return Response({"detail": "Falta parámetro q"}, status=400)

        qs = Participant.objects.all()
        participant = None

        # 2) intentar primero por FOLIO (clave)
        try:
            participant = qs.get(clave__iexact=q)
        except Participant.DoesNotExist:
            # 3) si no hay folio, intentar por ID numérico
            try:
                participant = qs.get(pk=int(q))
            except (ValueError, Participant.DoesNotExist):
                raise Http404("Participante no encontrado")

        # 4) generar PDF y devolverlo
        pdf_path = generar_credencial_pdf(participant)
        filename = os.path.basename(pdf_path)

        return FileResponse(
            open(pdf_path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )