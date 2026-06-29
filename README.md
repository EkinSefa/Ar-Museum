



# 🏛️ AR Müzesi Yönetim Sistemi (AR Museum)

[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![MinIO](https://img.shields.io/badge/MinIO-S3-red.svg)](https://min.io/)
[![Docker](https://img.shields.io/badge/Docker-Container-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.13-yellow.svg)](https://www.python.org/)

AR Müzesi, tarihi eser ve objelerin görsellerini yapay zeka yardımıyla **3D modellere** (.glb ve .usdz) dönüştüren, bu modelleri **MinIO S3** uyumlu depolamada saklayan ve kullanıcıların web sayfası üzerinden **Artırılmış Gerçeklik (AR)** deneyimi yaşamasını sağlayan modern bir Django web uygulamasıdır.

---

<!-- GÖRSEL YER TUTUCU: Ana Banner veya Logo Görseli -->
<!-- Buraya projenin genel arayüzünü veya ana banner görselini ekleyebilirsiniz -->
<!-- Örnek Kullanım: ![AR Müzesi Banner](yol/to/banner.png) -->
> **<img width="1600" height="758" alt="Image" src="https://github.com/user-attachments/assets/b3420a0f-36c1-488c-9c53-ab371a79642c" />**

---

## ✨ Özellikler

* **AI Destekli 3D Model Üretimi**:
  * **Tekli Görsel Yüklemeleri**: Stability AI *TripoSR* modeliyle hızlı ve dokulu 3D üretim.
  * **Çoklu Görsel Yüklemeleri**: Tencent *Hunyuan3D-2.1* modeliyle yüksek çözünürlüklü ve detaylı 3D üretim.
  * Üretim işlemleri yerel cihazı yormadan tamamen bulut sunucu havuzları (Hugging Face Spaces) aracılığıyla yürütülür.
* **Artırılmış Gerçeklik (AR) Desteği**: GLTF/GLB ve USDZ formatları sayesinde hem Android hem iOS (Safari Quick Look) cihazlarda yerleşik AR görüntüleme.
* **Gelişmiş Yönetim Paneli**: `django-jazzmin` teması ile modern, duyarlı (responsive) ve şık yönetim arayüzü.
* **Konteyner Altyapısı**: Django, PostgreSQL ve MinIO servislerinin tamamı Docker üzerinde izole çalışır.
* **Otomatik S3 MIME Yapılandırması**: Tarayıcıların ve AR cihazlarının modelleri doğru açabilmesi için S3 nesnelerinin MIME tipleri otomatik olarak yönetilir.

---

<!-- GÖRSEL YER TUTUCU: Uygulama Ekran Görüntüleri Karuseli veya Yan Yana Görseller -->
<!-- Yönetim paneli, 3D model görüntüleme ekranı gibi ekran görüntülerini buraya yerleştirebilirsiniz -->
### 📱 Ekran Görüntüleri

| Yönetim Paneli (Admin) | 3D Model Görüntüleme | AR Deneyimi |
|:---:|:---:|:---:|
| <img height="320" alt="Yönetim Paneli" src="https://github.com/user-attachments/assets/d2fc12aa-85b9-467c-8bbd-e493ed1e021a" /> | <img height="320" alt="3D Model Görüntüleme" src="https://github.com/user-attachments/assets/b84a7f29-3c5f-49fe-bfee-3ad24ce87852" /> | <img height="320" alt="AR Deneyimi" src="https://github.com/user-attachments/assets/7821b49f-faf1-4943-b776-6f711b21abbf" /> |

---

<!-- VİDEO YER TUTUCU: Tanıtım Videosu veya Demo GIF -->
### 🎥 Proje Tanıtım Videosu

<!-- Aşağıdaki alana YouTube linki, Github Video formatı veya demo GIF'inizi ekleyebilirsiniz -->
> [![AR Müzesi Demo Videosu](https://img.youtube.com/vi/Gv4UWYUSglk/0.jpg)](https://www.youtube.com/watch?v=Gv4UWYUSglk)



---

## 🛠️ Teknolojik Mimari

<img width="2816" height="1536" alt="Image" src="https://github.com/user-attachments/assets/04d0a367-c28d-4d5f-b59d-f5fa5ee42df7" />

---

## 🚀 Kurulum ve Çalıştırma

### 1. Hazırlık (.env Yapılandırması)
Projenin kök dizinindeki `.env.example` dosyasının adını `.env` olarak değiştirin ve içeriğini kendinize göre güncelleyin:
```bash
cp .env.example .env
```
Gerekli parametreleri doldurun:
* `DJANGO_SECRET_KEY`: Güvenli bir Django anahtarı.
* `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY`: S3 / MinIO erişim bilgileri.
* `DB_PASSWORD`: PostgreSQL veritabanı şifreniz.

---

### 2. Docker ile Hızlı Kurulum (Önerilen)
Bilgisayarınızda Docker ve Docker Compose kuruluysa, tüm bağımlılıkları (Web, Database, MinIO S3) tek bir komutla ayağa kaldırabilirsiniz:
```bash
docker-compose up --build
```
Bu komut çalıştırıldığında:
1. Docker imajları derlenir.
2. PostgreSQL ve MinIO servisleri ayağa kalkar.
3. Django servisi veritabanının hazır olmasını bekler, ardından veritabanı göçlerini (migration) otomatik olarak yapar.
4. MinIO üzerinde `ar-museum` kovası otomatik oluşturulur ve dışarıya açılır.
5. Uygulama `http://localhost:8000` adresinden yayına başlar.

---

### 3. Manuel Kurulum (Yerel Ortam)
Projeyi kendi yerel Python ortamınızda çalıştırmak isterseniz:

1. **Bağımlılıkları Kurun**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Veritabanını Hazırlayın**: Yerelde bir PostgreSQL sunucusu başlatın ve `.env` dosyasındaki şifre/bağlantı ayarlarını yapın. Tabloları oluşturun:
   ```bash
   python manage.py migrate
   ```
3. **Uygulamayı Çalıştırın**:
   ```bash
   python manage.py runserver
   ```

---

## 👥 MinIO Depolama Bilgileri (Yerel Docker)

Docker üzerinde çalışan yerel depolama yönetim paneline erişmek için:
* **Yönetim Paneli Adresi**: [http://localhost:9001](http://localhost:9001)
* **Kullanıcı Adı**: `.env` dosyanızdaki `AWS_ACCESS_KEY_ID` değeri.
* **Şifre**: `.env` dosyanızdaki `AWS_SECRET_ACCESS_KEY` değeri.

---

## 📬 İletişim

Proje hakkında sorularınız, geri bildirimleriniz veya iş birliği teklifleriniz için benimle iletişime geçebilirsiniz:

<table>
  <tr style="border: none; background: none;">
    <td width="100" style="border: none; background: none; padding: 0; margin: 0;">
      <a href="http://www.linkedin.com/in/u%C4%9Fur-g%C3%BClaydin-9053902b6" target="_blank">
        <img src="https://images.weserv.nl/?url=https%3A%2F%2Fmedia.licdn.com%2Fdms%2Fimage%2Fv2%2FD4D03AQGCopOawLDLxg%2Fprofile-displayphoto-scale_200_200%2FB4DZ769vlgGkAc-%2F0%2F1782326951936%3Fe%3D2147483647%26v%3Dbeta%26t%3DLY9VRQ1CkZRQ1x8AbcwHM-AutqHQzwCmlV5yjPSH8Ho&w=100&h=100&fit=cover&mask=circle" width="100" height="100" alt="Uğur Gülaydın" style="display: block; border: none;" />
      </a>
    </td>
    <td style="border: none; background: none; padding-left: 20px; vertical-align: middle;">
      <strong style="font-size: 20px;">UĞUR GÜLAYDIN</strong><br />
      Anında iletişim ve ağ kurmak için:<br />
      👉 <a href="[https://www.linkedin.com/in/sefa-ekin-01130a273)" target="_blank" style="text-decoration: none; font-weight: bold;">LinkedIn üzerinden bağlanın</a>
    </td>
  </tr>
</table>

---

## 📝 Lisans
Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
