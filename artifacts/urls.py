from django.urls import path
from .views import (
    ArtifactListView, ArtifactDetailView, ArtifactARView,
    ScannerView, ScanStatusView, VideoStreamView
)

app_name = 'artifacts'

urlpatterns = [
    path('', ArtifactListView.as_view(), name='index'),
    path('artifact/<int:pk>/', ArtifactDetailView.as_view(), name='detail'),
    path('artifact/<int:pk>/ar/', ArtifactARView.as_view(), name='ar_view'),
    path('scanner/', ScannerView.as_view(), name='scanner'),
    path('scanner/status/<int:pk>/', ScanStatusView.as_view(), name='scan_status'),
    path('video/AR.mp4', VideoStreamView.as_view(), name='video_stream'),
]
