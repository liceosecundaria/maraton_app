from django.urls import path
from .views import RegisterParticipantView, ParticipantListView, ExportParticipantsCSV, ReprintPdfView, ParticipantsStats

urlpatterns = [
    path("register/", RegisterParticipantView.as_view(), name="register"),

    # LISTA
    path("participants/", ParticipantListView.as_view(), name="participants_list"),

    # CSV  ← OJO: export_csv con guion bajo, como en el frontend
    path("participants/export_csv/", ExportParticipantsCSV.as_view(), name="export_csv"),

    # REIMPRIMIR
    path("participants/reprint/", ReprintPdfView.as_view(), name="reprint_pdf"),

    # ESTADÍSTICAS (si la usas)
    path("participants/stats/", ParticipantsStats.as_view(), name="participants_stats"),
]




