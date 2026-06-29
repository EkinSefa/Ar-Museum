from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from .models import Artifact, ReconstructionSession, SessionImage
from django.conf import settings
import subprocess
import os
import threading
import tempfile
import shutil
from django.core.files.base import ContentFile
from django.core.files import File

class ArtifactListView(ListView):
    model = Artifact
    template_name = 'artifacts/index.html'
    context_object_name = 'artifacts'
    paginate_by = 20

class ArtifactDetailView(DetailView):
    model = Artifact
    template_name = 'artifacts/detail.html'
    context_object_name = 'object'

class ArtifactARView(DetailView):
    model = Artifact
    template_name = 'artifacts/ar_view.html'
    context_object_name = 'object'

class ScannerView(View):
    def get(self, request):
        return render(request, 'artifacts/scanner.html')

    def post(self, request):
        title = request.POST.get('title', 'Yeni Tarama')
        description = request.POST.get('description', '')
        images = request.FILES.getlist('images')
        
        if not images:
            return render(request, 'artifacts/scanner.html', {'error': 'Lütfen en az bir görsel yükleyin.'})
            
        session = ReconstructionSession.objects.create(title=title, description=description)
        
        
        for i, img in enumerate(images):
            session_image = SessionImage.objects.create(
                session=session,
                image=img,
                is_primary=(i == 0)
            )
        
        # İşlemi başlat - S3 üzerinde .path çalışmadığı için ID üzerinden ilerliyoruz
        threading.Thread(target=self.run_sf3d, args=(session.id,)).start()
        
        return redirect('artifacts:scan_status', pk=session.id)

    def run_sf3d(self, session_id):
        import sys
        session = ReconstructionSession.objects.get(id=session_id)
        session.status = 'processing'
        session.save()
        
        # Geçici çalışma dizini oluştur
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 1. Tüm görselleri bul ve doğrula
            all_images = list(session.images.all())
            if not all_images:
                raise ValueError("İşlenecek görsel bulunamadı.")
            
            # Birincil görseli belirle
            primary_image = session.images.filter(is_primary=True).first() or all_images[0]
            
            # 2. Birincil görseli kaydet
            local_input_path = os.path.join(temp_dir, "input_image.png")
            with open(local_input_path, 'wb') as f:
                f.write(primary_image.image.read())
            
            # Diğer açılardaki görselleri kaydet
            other_images = [img for img in all_images if img.id != primary_image.id]
            local_paths = []
            for i, img in enumerate(other_images[:4]): # En fazla 4 ek açı desteklenir
                path = os.path.join(temp_dir, f"mv_{i}.png")
                with open(path, 'wb') as f:
                    f.write(img.image.read())
                local_paths.append(path)
            
            # 3. Çıktı yolu belirle (geçici yerel dosya)
            local_output_path = os.path.join(temp_dir, "output.glb")
            
            # 4. processor.py'ı yerel dosyalar ve tüm bakış açılarıyla çalıştır
            script_path = os.path.join(os.path.dirname(__file__), 'processor.py')
            cmd = [sys.executable, script_path, '--input', local_input_path, '--output', local_output_path]
            
            # Ek açı argümanlarını komuta ekle
            mv_args = ['--mv-front', '--mv-back', '--mv-left', '--mv-right']
            for path, arg in zip(local_paths, mv_args):
                cmd.extend([arg, path])
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(local_output_path):
                # 5. Sonucu oku ve Artifact olarak S3'e kaydet
                output_filename = f"model_{session.id}.glb"
                
                method_used = "Hunyuan3D-2.1" if len(local_paths) > 0 else "TripoSR"
                desc = session.description if session.description else f"{session.created_at} tarihinde {method_used} ile üretildi."
                artifact = Artifact.objects.create(
                    title=session.title,
                    description=desc,
                    image=primary_image.image
                )
                
                # S3'e dosya handle'ı üzerinden kaydet (MissingContentLength hatasını önlemek için)
                with open(local_output_path, 'rb') as f:
                    artifact.model_3d.save(output_filename, File(f))
                
                session.result_artifact = artifact
                session.status = 'completed'
            else:
                session.status = 'failed'
                # Hata detaylarını birleştirerek raporla
                error_detail = []
                if result.stdout: error_detail.append(f"STDOUT: {result.stdout}")
                if result.stderr: error_detail.append(f"STDERR: {result.stderr}")
                
                session.error_message = "\n".join(error_detail) if error_detail else "İşlem bitti ancak sonuç dosyası bulunamadı ve çıktı üretilmedi."
            
            session.save()
        except Exception as e:
            session.status = 'failed'
            session.error_message = str(e)
            session.save()
        finally:
            # 6. Temizlik: Geçici dizini sil
            shutil.rmtree(temp_dir, ignore_errors=True)

class ScanStatusView(DetailView):
    model = ReconstructionSession
    template_name = 'artifacts/scan_status.html'
    context_object_name = 'session'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': self.object.status,
                'error_message': self.object.error_message,
                'artifact_id': self.object.result_artifact.id if self.object.result_artifact else None
            })
        return super().get(request, *args, **kwargs)


import re
from django.http import StreamingHttpResponse

class VideoStreamView(View):
    def get(self, request, *args, **kwargs):
        video_path = os.path.join(settings.BASE_DIR, 'artifacts', 'static', 'video', 'AR.mp4')
        
        if not os.path.exists(video_path):
            from django.http import Http404
            raise Http404("Video not found")

        file_size = os.path.getsize(video_path)
        
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        
        if range_match:
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte) if first_byte else 0
            last_byte = int(last_byte) if last_byte else file_size - 1
            if last_byte >= file_size:
                last_byte = file_size - 1
            length = last_byte - first_byte + 1
            
            def file_iterator():
                with open(video_path, 'rb') as f:
                    f.seek(first_byte)
                    remaining = length
                    while remaining > 0:
                        chunk_size = min(remaining, 8192)
                        data = f.read(chunk_size)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data
                        
            response = StreamingHttpResponse(file_iterator(), status=206, content_type='video/mp4')
            response['Content-Length'] = str(length)
            response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
            response['Accept-Ranges'] = 'bytes'
            return response
        else:
            def file_iterator():
                with open(video_path, 'rb') as f:
                    while True:
                        data = f.read(8192)
                        if not data:
                            break
                        yield data
            response = StreamingHttpResponse(file_iterator(), content_type='video/mp4')
            response['Content-Length'] = str(file_size)
            response['Accept-Ranges'] = 'bytes'
            return response


from django.contrib.admin.models import LogEntry
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.template.loader import render_to_string

@method_decorator(staff_member_required, name='dispatch')
class AdminLogsView(ListView):
    model = LogEntry
    template_name = 'admin/system_logs.html'
    context_object_name = 'logs'
    paginate_by = 10

    def get_queryset(self):
        return LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')

    def get(self, request, *args, **kwargs):
        if request.GET.get('ajax') == 'true':
            action = request.GET.get('action')
            
            if action == 'poll':
                since_id = request.GET.get('since_id')
                try:
                    since_id = int(since_id)
                    new_logs = LogEntry.objects.filter(id__gt=since_id).select_related('user', 'content_type').order_by('-action_time')
                except (TypeError, ValueError):
                    new_logs = []
                
                logs_html = []
                for entry in new_logs:
                    html = render_to_string('admin/includes/timeline_item.html', {'entry': entry}, request=request)
                    logs_html.append({
                        'id': entry.id,
                        'html': html
                    })
                
                latest_log = LogEntry.objects.order_by('-id').first()
                latest_id = latest_log.id if latest_log else 0
                
                return JsonResponse({
                    'new_logs': logs_html,
                    'latest_id': latest_id
                })
                
            else:
                self.object_list = self.get_queryset()
                context = self.get_context_data()
                
                timeline_html = render_to_string('admin/includes/timeline_list.html', context, request=request)
                pagination_html = render_to_string('admin/includes/pagination_controls.html', context, request=request)
                
                return JsonResponse({
                    'timeline_html': timeline_html,
                    'pagination_html': pagination_html,
                })
                
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        
        latest_log = LogEntry.objects.order_by('-id').first()
        context['latest_id'] = latest_log.id if latest_log else 0
        
        return self.render_to_response(context)


