import os
import sys
import shutil
import argparse
from gradio_client import Client, handle_file

def process_image(input_path, output_path, mv_front=None, mv_back=None, mv_left=None, mv_right=None):
    # Eğer çoklu görsel varsa en gelişmiş Hunyuan3D-2.1 modelini kullan
    if mv_front or mv_back or mv_left or mv_right:
        print("Çoklu görsel tespit edildi. Hunyuan3D-2.1 ile yüksek kaliteli üretim başlatılıyor...")
        
        # Aktif ve çalışan GPU destekli yedekli sunucu havuzu
        spaces = [
            "Gemini899/Dream-Hunyuan3D-2.1",
            "AliothTalks/Hunyuan3D-2.1",
            "joaojack/Hunyuan3D-2.1",
            "a2post/Hunyuan3D-2.1"
        ]
        
        for space in spaces:
            try:
                print(f"Hunyuan3D-2.1 sunucusuna bağlanılıyor: {space}")
                client = Client(space)
                print("Bulut üzerinde yüksek kaliteli 3D model üretimi başlatıldı (/shape_generation)...")
                
                # Çoklu bakış parametrelerini eşleştir
                result = client.predict(
                    handle_file(input_path), # image
                    handle_file(mv_front) if mv_front else None,
                    handle_file(mv_back) if mv_back else None,
                    handle_file(mv_left) if mv_left else None,
                    handle_file(mv_right) if mv_right else None,
                    30,     # steps
                    5.0,    # guidance_scale
                    1234,   # seed
                    256,    # octree_resolution
                    True,   # check_box_rembg
                    8000,   # num_chunks
                    True,   # randomize_seed
                    api_name="/shape_generation"
                )
                
                if result and len(result) > 0:
                    glb_info = result[0]
                    # Gradio client bazen bir dict, bazen doğrudan dosya yolu stringi dönebilir
                    glb_path = None
                    if isinstance(glb_info, dict) and 'value' in glb_info:
                        glb_path = glb_info['value']
                    elif isinstance(glb_info, str):
                        glb_path = glb_info
                    
                    if glb_path and os.path.exists(glb_path):
                        shutil.copy(glb_path, output_path)
                        print(f"Yüksek kaliteli 3D model başarıyla tamamlandı ve kaydedildi ({space}): {output_path}")
                        return True
                raise ValueError("API'den geçersiz yanıt alındı.")
            except Exception as e:
                print(f"Uyarı: {space} sunucusunda işlem başarısız oldu. Sonraki sunucu deneniyor. Hata: {e}")
                continue
                
        sys.stderr.write("HATA: Tüm Hunyuan3D-2.1 sunucuları kota veya yoğunluk nedeniyle başarısız oldu.\n")
        return False
        
    else:
        # Tek görsel varsa hızlı ve dokulu TripoSR modelini kullan
        print("Tek görsel tespit edildi. TripoSR ile dokulu üretim başlatılıyor...")
        try:
            client = Client("stabilityai/TripoSR")
            
            # Adım 1: Ön İşleme (Arka Plan Temizleme)
            processed_image = client.predict(
                handle_file(input_path),
                True,
                0.85,
                api_name="/preprocess"
            )
            
            # Adım 2: Model Üretimi
            result = client.predict(
                handle_file(processed_image),
                256,
                api_name="/generate"
            )
            
            if result and len(result) > 1:
                glb_path = result[1]
                if os.path.exists(glb_path):
                    shutil.copy(glb_path, output_path)
                    print(f"3D Model başarıyla tamamlandı ve kaydedildi (TripoSR): {output_path}")
                    return True
            raise ValueError("API'den geçersiz yanıt alındı.")
        except Exception as e:
            sys.stderr.write(f"HATA: TripoSR üretimi başarısız oldu: {e}\n")
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mv-front", default=None)
    parser.add_argument("--mv-back", default=None)
    parser.add_argument("--mv-left", default=None)
    parser.add_argument("--mv-right", default=None)
    args = parser.parse_args()
    
    success = process_image(
        args.input, 
        args.output,
        mv_front=args.mv_front,
        mv_back=args.mv_back,
        mv_left=args.mv_left,
        mv_right=args.mv_right
    )
    if not success:
        sys.stderr.write("HATA: İşlem başarısız oldu.\n")
        sys.exit(1)
    sys.exit(0)
