# YZM 411 Bilgisayarlı Görü -- Ödev #1
## Renk, Aydınlatma ve Örnekleme Analizi Raporu

Bu depo, Ostim Teknik Üniversitesi Yapay Zeka Mühendisliği Bölümü **YZM 411 Bilgisayarlı Görü** dersi kapsamında gerçekleştirilen birinci ödevin kaynak kodlarını, LaTeX raporunu ve deney çıktılarını içermektedir.

------------------------------------

Proje Dosya Yapısı


YZM411-ODEV/
├── main.tex             # LaTeX rapor kaynak kodu
├── main.py              # Görüntü işleme ve analiz Python betiği
├── README.md            # Proje dokümantasyonu
└── sonuclar/            # Deney çıktıları ve görsel dosyaları
    ├── img_normal.jpg   # Normal ışık altında orijinal fotoğraf
    ├── img_golge.jpg    # Gölge koşulunda orijinal fotoğraf
    ├── img_lamba.jpg    # Farklı lamba altında orijinal fotoğraf
    ├── maskeler.png     # RGB ve HSV eşikleme maskeleri görseli
    ├── parlaklik_gama.png # Parlaklık ve gama dönüşümleri görseli
    └── kucultme.png     # Küçültme ve yeniden boyutlandırma karşılaştırması


  Çalıştırma Rehberi
Projeyi yerel ortamınızda çalıştırmak ve analizleri yeniden üretmek için aşağıdaki adımları izleyebilirsiniz:


Gerekli kütüphanelerin kurulu olduğundan emin olun (OpenCV, NumPy, Matplotlib, Pandas):

Bash
pip install opencv-python numpy matplotlib pandas


Python betiğini çalıştırarak analizleri ve çıktı görsellerini \texttt{sonuclar/} klasörüne kaydedin:
python main.py

Ödev Kapsamı ve Özet BulgularOrijinal Veri Seti (Adım 2): Sahne ve kamera konumu sabit tutularak normal ışık, gölge ve farklı lamba koşullarında özgün fotoğraflar kaydedilmiştir.Renk Sabitliği ve Eşikleme (Hedef 1 & 2): Sabit RGB ve HSV eşiklerinin farklı aydınlatma koşullarındaki başarımları incelenmiş; gölge altında beklenmeyen yanlış pozitif artışları sayısal olarak analiz edilmiştir.Parlaklık ve Gama Dönüşümü (Hedef 3): Parlaklık kaydırma (b=+40) ve üssel gama dönüşümlerinin (gamma=0.5, 2.0) piksel istatistikleri ve görsel etkileri incelenmiştir.Uzamsal Örnekleme (Hedef 4): 1/4 oranında küçültülen görüntülerin {INTER_NEAREST} ve {INTER_AREA} yöntemleriyle geri büyütülmesindeki kalite kayıpları MSE (Hata Kareler Ortalaması) metriğiyle karşılaştırılmıştır.


Yazar
Ad Soyad: Buğra Pergel

Öğrenci Numarası: 230212045

Bölüm: Yapay Zeka Mühendisliği

Ders Sorumlusu: Öğr. Gör. Melisa Gözet
