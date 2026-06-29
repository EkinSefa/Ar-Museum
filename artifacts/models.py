from django.db import models

class Artifact(models.Model):
    title = models.CharField(max_length=200, verbose_name="Eser Adı")
    description = models.TextField(verbose_name="Detaylı Açıklama")
    image = models.ImageField(upload_to='artifacts/images/', verbose_name="Kapak Görseli")
    model_3d = models.FileField(upload_to='artifacts/models/', verbose_name="3D Model (GLB/GLTF)")
    model_ios = models.FileField(upload_to='artifacts/models/', blank=True, null=True, verbose_name="iOS AR Modeli (USDZ)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Eser"
        verbose_name_plural = "Eserler"

    def __str__(self):
        return self.title

class ReconstructionSession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Bekliyor'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Hata Oluştu'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Oturum Adı")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Durum")
    created_at = models.DateTimeField(auto_now_add=True)
    result_artifact = models.OneToOneField(Artifact, on_delete=models.SET_NULL, null=True, blank=True, related_name='reconstruction_session')
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "3D Tarama Oturumu"
        verbose_name_plural = "3D Tarama Oturumları"

class SessionImage(models.Model):
    session = models.ForeignKey(ReconstructionSession, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='reconstructions/images/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
