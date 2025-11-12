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
    prefix = (plantel or "").strip().title()  # Primaria|Secundaria|Preparatoria
    existentes = (Participant.objects
                  .filter(plantel=plantel)
                  .exclude(clave__isnull=True)
                  .exclude(clave__exact="")
                  .values_list("clave", flat=True))
    max_n = 0
    for clave in existentes:
        import re
        m = re.search(r'(\d+)$', clave or "")
        if m:
            n = int(m.group(1))
            if n > max_n:
                max_n = n
    return f"{prefix}{max_n+1:04d}"

class RegisterParticipantView(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            s = ParticipantSerializer(data=request.data)
            if not s.is_valid():
                return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)
            data = s.validated_data

            plantel = (data.get("plantel") or "").strip()
            clave_generada = generar_clave(plantel)  # ← SIEMPRE

            participant = Participant.objects.create(
                full_name=(data.get("full_name") or "").strip(),
                plantel=plantel,
                child_name=(data.get("child_name") or "").strip(),
                grado=(data.get("grado") or "").strip(),
                role=(data.get("role") or "").strip().upper(),
                clave=clave_generada,
            )

            pdf_out = generar_credencial_pdf(participant)

            # --- Devolver PDF (acepta bytes o ruta en disco) ---
            if isinstance(pdf_out, (bytes, bytearray)):
                resp = HttpResponse(bytes(pdf_out), content_type="application/pdf")
                resp["Content-Disposition"] = (
                    f'attachment; filename="{participant.clave or "credencial"}.pdf"'
                )
                return resp

            if isinstance(pdf_out, str) and os.path.exists(pdf_out):
                return FileResponse(
                    open(pdf_out, "rb"),
                    as_attachment=True,
                    filename=f'{participant.clave or "credencial"}.pdf',
                    content_type="application/pdf",
                )

            # Si llegó aquí, no hubo PDF válido
            return Response({"error": "No se pudo generar el PDF"}, status=500)

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
