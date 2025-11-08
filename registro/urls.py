# registro/urls.py
from django.urls import path
from .views import (
    RegisterParticipantView,
    
    ExportParticipantsCSV,
    ParticipantsStats,
    ParticipantListView,
    ReprintPdfView,
    
)

urlpatterns = [
    path("register/", RegisterParticipantView.as_view(), name="register"),
    
    # exportar CSV
    path("participants/export/", ExportParticipantsCSV.as_view(), name="export_csv"),

    # estadísticas
    path("participants/stats/", ParticipantsStats.as_view(), name="participants_stats"),

    # listar participantes (si ya lo tienes)
    path("participants/", ParticipantListView.as_view(), name="participants_list"),

    # reimprimir por clave (si ya lo tienes)
    path(
        "participants/<str:clave>/reprint/",
        ReprintPdfView.as_view(),
        name="reprint_pdf",
    ),
    path("participants/reprint/", ReprintPdfView.as_view(), name="reprint_pdf"),

    
]



