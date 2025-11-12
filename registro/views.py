import csv
import re
import os
import logging, traceback

from django.http import FileResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.conf import settings
from django.db import transaction
# arriba
from django.utils import timezone


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Participant
from .serializers import ParticipantSerializer
from .pdf_generator import generar_credencial_pdf

logger = logging.getLogger(__name__)

# =======================
# Generación de folio
# =======================

def generar_clave(plantel: str) -> str:
    """
    Genera folio por plantel con 4 dígitos:
    Primaria0001, Secundaria0001, Preparatoria0001, etc.
    Busca el mayor consecutivo existente (terminación numérica) y suma 1.
    """
    prefix = (plantel or "").strip().title()  # "Primaria"|"Secundaria"|"Preparatoria"

    existentes = (
        Participant.objects
        .filter(plantel=plantel)
        .exclude(clave__isnull=True)
        .exclude(clave__exact="")   # 🔹 evita cadenas vacías
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
    @transaction.atomic
    def post(self, request):
        try:
            serializer = ParticipantSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data

            # Normaliza
            full_name  = (data.get("full_name") or "").strip()
            plantel    = (data.get("plantel") or "").strip()
            child_name = (data.get("child_name") or "").strip() or None
            grado      = (data.get("grado") or "").strip() or None
            role       = (data.get("role") or "").strip()

            # Define roles de adulto y calcula role_value en MAYÚSCULAS
            ADULTO_ROLES = ["ACOMPAÑANTE HOMBRE", "ACOMPAÑANTE MUJER", "ABUELITO", "ABUELITA", "TUTOR"]
            role_value = (role or "").upper()

            # Genera folio SOLO para adultos; para alumnos deja None (no vacío)
            clave_generada = generar_clave(plantel) if role_value in ADULTO_ROLES else None

            participant = Participant.objects.create(
                full_name=full_name,
                plantel=plantel,
                child_name=child_name,
                grado=grado,
                role=role_value,     # guarda ya en MAYÚSCULAS
                clave=clave_generada # None para alumnos, folio para adultos
            )

            # Generar PDF (acepta bytes o ruta)
            pdf_out = generar_credencial_pdf(participant)
            if isinstance(pdf_out, (bytes, bytearray)):
                pdf_bytes = bytes(pdf_out)
                resp = HttpResponse(pdf_bytes, content_type="application/pdf")
            elif isinstance(pdf_out, str) and os.path.exists(pdf_out):
                resp = FileResponse(open(pdf_out, "rb"), content_type="application/pdf")
            else:
                raise ValueError("El generador de PDF no devolvió bytes ni una ruta válida.")

            filename = f'{participant.clave or "credencial"}.pdf'
            resp["Content-Disposition"] = f'attachment; filename="{filename}"'
            return resp

        except Exception as e:
            logger.error("REGISTER_ERROR: %s", e)
            logger.error("TRACE:\n%s", traceback.format_exc())
            return Response(
                {"error": "Server error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =======================
# 2) Listado de participantes (panel admin)
# =======================

class ParticipantListView(APIView):
    def get(self, request):
        qs = Participant.objects.all().order_by("-created_at", "-id")
        serializer = ParticipantSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# =======================
# 3) Exportar CSV
# =======================

class ExportParticipantsCSV(APIView):
    """
    GET /api/participants/export_csv/
    """
    def get(self, request, *args, **kwargs):
        qs = Participant.objects.all().order_by("plantel", "role", "full_name")
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="participantes_maraton.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "ID",
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
                p.id,
                p.clave or "",
                p.full_name or "",   # 🔄 corrige el orden con el encabezado
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
    def get(self, request):
        total = Participant.objects.count()
        por_plantel = list(Participant.objects.values("plantel").annotate(total=Count("id")).order_by("plantel"))
        por_role    = list(Participant.objects.values("role").annotate(total=Count("id")).order_by("role"))
        data = {"total": total, "por_plantel": por_plantel, "por_role": por_role}
        return Response(data, status=status.HTTP_200_OK)

# =======================
# 5) Reimpresión de gafete
# =======================

class ReprintPdfView(APIView):
    """
    /api/participants/reprint/?q=Primaria0007  ó  /api/participants/reprint/?q=12
    """
    def get(self, request, *args, **kwargs):
        q = request.query_params.get("q") or request.GET.get("q")
        if not q:
            return Response({"detail": "Falta parámetro q"}, status=400)

        qs = Participant.objects.all()
        participant = None
        try:
            participant = qs.get(clave__iexact=q)
        except Participant.DoesNotExist:
            try:
                participant = qs.get(pk=int(q))
            except (ValueError, Participant.DoesNotExist):
                raise Http404("Participante no encontrado")

        pdf_out = generar_credencial_pdf(participant)
        if isinstance(pdf_out, (bytes, bytearray)):
            resp = HttpResponse(bytes(pdf_out), content_type="application/pdf")
        elif isinstance(pdf_out, str) and os.path.exists(pdf_out):
            resp = FileResponse(open(pdf_out, "rb"), content_type="application/pdf")
        else:
            return Response({"error": "PDF inválido"}, status=500)

        resp["Content-Disposition"] = f'attachment; filename="{participant.clave or "credencial"}.pdf"'
        return resp
