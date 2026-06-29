from django.contrib import admin
from .models import Artifact

@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
