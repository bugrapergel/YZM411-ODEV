"""
YZM 411 - Odev 1: Renk, Aydinlatma ve Ornekleme
Calistirma:  python main.py
Gerekli paketler: opencv-python, numpy, pandas, matplotlib, pillow
Tum cikti dosyalari ./sonuclar klasorune yazilir.
"""
import os, platform
import cv2, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ===================== AYARLAR =====================
FILES = {
    "normal": "img_normal.jpg",
    "golge":  "img_golge.jpg",
    "lamba":  "img_lamba.jpg",
}

# Sarı bölgeleri ("Fenerbahçe" ve "DINHO" yazıları ile bardaktaki sarı alanlar) yakalamak için dondurulmuş eşikler
RGB_LOW,  RGB_HIGH = (140, 130, 10),  (255, 255, 110)   # (R, G, B) - Sarı tonları
HSV_LOW,  HSV_HIGH = (18, 90, 90),    (38, 255, 255)    # OpenCV Sarı/Sarı-Yeşil aralığı

OUT = "sonuclar"
# ===================================================

# ---- TAHMINLER: Deneyleri calistirmadan once yazilmistir (2 cumle) ----
TAHMINLER = {
    "Deney5_renk_esikleri": (
        "Isik yonu ve golge degistiginde piksel parlakliklari kayacagi icin sabit RGB esiklerinin "
        "sectigi sari alan orani ciddi oranda degisecektir. HSV uzayindaki Ton (H) kanali ise "
        "aydinlatma siddetinden bagimsiz oldugu icin uc fotografta da daha tutarli maske uretecektir."
    ),
    "Deney6_parlaklik_b40": (
        "Parlaklik degeri b=+40 kaydirildiginda goruntu ortalamasi yaklasik 40 birim artacaktir. "
        "Ancak defter ve bardagin beyaz kisimlarinda 255 sinirinda doyuma ulasan (kirpilan) pikseller "
        "nedeniyle gercek ortalama artisi 40'tan biraz daha dusuk olacaktir."
    ),
    "Deney6_gama_0.5": (
        "Gama=0.5 donusumu ozellikle derginin koyu lacivert kisimlarini ve golgeleri acarak goruntuyu "
        "aydinlatacaktir. Bu dogrusal olmayan genisleme sonucunda piksel ortalamasi belirgin sekilde yukselecektir."
    ),
    "Deney6_gama_2.0": (
        "Gama=2.0 donusumu orta ve koyu tonlari sifira dogru bastirarak goruntuyu genel olarak karartacaktir. "
        "Islem sonucunda genel piksel ortalamasi orijinal degerin altina dusecektir."
    ),
    "Deney7_kucultme": (
        "Dergi uzerindeki yazilar 1/4 oraninda kucultuldugunde ince harf detaylari kaybolacaktir. "
        "INTER_NEAREST yontemi harf kenarlarinda tirtiklanma (aliasing) yaparken, INTER_AREA yontemi "
        "komsu piksellerin ortalamasini alarak yazilari bulaniklastiracaktir."
    ),
}

os.makedirs(OUT, exist_ok=True)
log = []

def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    log.append(s)

# ----------------------------- Yukleme -----------------------------
def load_rgb(path):
    bgr = cv2.imread(path)
    if bgr is None:
        raise FileNotFoundError(f"HATA: '{path}' bulunamadi! Lutfen 3 fotografi proje klasorune ekleyin.")
    return bgr, cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

imgs_bgr, imgs = {}, {}
for k, p in FILES.items():
    imgs_bgr[k], imgs[k] = load_rgb(p)

# Görüntü boyutlarını alıp tüm fotoğrafları normal fotoğrafın boyutuna eşitleyelim (boyut farkı hatasını önler)
H, W = imgs["normal"].shape[:2]
for k in imgs:
    if imgs[k].shape[:2] != (H, W):
        imgs[k] = cv2.resize(imgs[k], (W, H))
        imgs_bgr[k] = cv2.resize(imgs_bgr[k], (W, H))

# Senin fotoğraf boyutuna (W, H) göre otomatik ayarlanan koordinatlar:
# 1. Piksel: Bardaktaki sarı bölge, 2. Piksel: Dergideki sarı başlık, 3. Piksel: Öndeki kareli defter
PIXELS = [
    (int(W * 0.22), int(H * 0.56)),
    (int(W * 0.58), int(H * 0.28)),
    (int(W * 0.45), int(H * 0.82))
]

# Bardak üzerindeki sarı alan ROI (x0, y0, x1, y1)
OBJ_ROI = (int(W * 0.18), int(H * 0.53), int(W * 0.28), int(H * 0.60))

# Dergi üzerindeki "MUHTEŞEM TARAFTARA" yazı bölgesi ROI (x0, y0, x1, y1)
TEXT_ROI = (int(W * 0.38), int(H * 0.58), int(W * 0.85), int(H * 0.72))

say("== Ortam ==")
say("python", platform.python_version(), "| numpy", np.__version__,
    "| opencv", cv2.__version__, "| pandas", pd.__version__,
    "| matplotlib", matplotlib.__version__)
say("Esikler  RGB:", RGB_LOW, RGB_HIGH, " HSV:", HSV_LOW, HSV_HIGH)
say("Dosyalar:", FILES)

# ----------------------------- EXIF -----------------------------
say("\n== EXIF (Adim 2c icin) ==")
try:
    from PIL import Image
    for k, p in FILES.items():
        ex = Image.open(p).getexif()
        sub = ex.get_ifd(0x8769) if ex else {}
        say(f"{k}: ExposureTime={sub.get(33434)}, FNumber={sub.get(33437)}, ISO={sub.get(34855)}, "
            f"ExposureMode={sub.get(41986)} (0=otomatik,1=manuel), "
            f"WhiteBalance={sub.get(41987)} (0=otomatik,1=manuel)")
    say("Not: Deger None ise EXIF yok demektir; kamera ayarini kendiniz not edin.")
except Exception as e:
    say("EXIF okunamadi:", e)

# ----------------------------- Adim 4: Sayisal Yapi -----------------------------
say("\n== Adim 4: Sayisal yapi ==")
for k, im in imgs.items():
    say(f"{k}: shape={im.shape} (H,W,C), dtype={im.dtype}, min={im.min()}, max={im.max()}")

x0, y0 = PIXELS[0]
say(f"\nimg[y, x, kanal] erisimi, piksel (x={x0}, y={y0}) [normal]:")
say("  OpenCV (BGR) :", tuple(int(v) for v in imgs_bgr['normal'][y0, x0]))
say("  Donusturulen (RGB):", tuple(int(v) for v in imgs['normal'][y0, x0]))
say("  Tek kanal erisimi  R =", int(imgs['normal'][y0, x0, 0]),
    " G =", int(imgs['normal'][y0, x0, 1]), " B =", int(imgs['normal'][y0, x0, 2]))

rows = []
for (x, y) in PIXELS:
    r = {"x": x, "y": y}
    for k, im in imgs.items():
        r[k] = tuple(int(v) for v in im[y, x])
        patch = im[max(y-2, 0):y+3, max(x-2, 0):x+3].reshape(-1, 3).mean(0)
        r[k + "_5x5ort"] = tuple(round(float(v), 1) for v in patch)
    rows.append(r)
df_pix = pd.DataFrame(rows)
df_pix.to_csv(f"{OUT}/piksel_degerleri.csv", index=False)
say("\n" + df_pix.to_string())

# ----------------------------- Adim 5: Sabit Esikli Maskeler -----------------------------
say("\n== Adim 5: Sabit esikli maskeler ==")
xa, ya, xb, yb = OBJ_ROI
roi = imgs["normal"][ya:yb, xa:xb]
roi_hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
say("OBJ_ROI RGB 5.-95. yuzdelik:",
    np.percentile(roi.reshape(-1, 3), [5, 95], axis=0).astype(int).tolist())
say("OBJ_ROI HSV 5.-95. yuzdelik:",
    np.percentile(roi_hsv.reshape(-1, 3), [5, 95], axis=0).astype(int).tolist())

masks, tablo = {}, []
for k, im in imgs.items():
    m_rgb = cv2.inRange(im, np.array(RGB_LOW, np.uint8), np.array(RGB_HIGH, np.uint8))
    hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV)
    m_hsv = cv2.inRange(hsv, np.array(HSV_LOW, np.uint8), np.array(HSV_HIGH, np.uint8))
    masks[(k, "RGB")], masks[(k, "HSV")] = m_rgb, m_hsv
    area = m_rgb.size
    tablo.append({"foto": k,
                  "RGB_piksel": int((m_rgb > 0).sum()), "RGB_oran_%": round(100*(m_rgb > 0).sum()/area, 2),
                  "HSV_piksel": int((m_hsv > 0).sum()), "HSV_oran_%": round(100*(m_hsv > 0).sum()/area, 2)})
df_mask = pd.DataFrame(tablo)
df_mask.to_csv(f"{OUT}/maske_tablosu.csv", index=False)
say("\n" + df_mask.to_string(index=False))
say("NOT: Maske alan orani dogruluk olcutu DEGILDIR; yalnizca esigi gecen piksel oranidir.")

fig, ax = plt.subplots(3, 3, figsize=(12, 9))
for i, k in enumerate(imgs):
    ax[i, 0].imshow(imgs[k]); ax[i, 0].set_title(f"{k} (orijinal)")
    ax[i, 1].imshow(masks[(k, "RGB")], cmap="gray"); ax[i, 1].set_title(f"{k} RGB maske")
    ax[i, 2].imshow(masks[(k, "HSV")], cmap="gray"); ax[i, 2].set_title(f"{k} HSV maske")
    for a in ax[i]: a.axis("off")
plt.tight_layout(); plt.savefig(f"{OUT}/maskeler.png", dpi=150); plt.close()

# ----------------------------- Adim 6: Parlaklik ve Gama -----------------------------
say("\n== Adim 6: Parlaklik ve gama (normal fotograf) ==")

def parlaklik_kaydir(I, b):
    return np.clip(I.astype(np.float64) + b, 0, 255)

def gama(I, g):
    return np.clip(255.0 * ((I.astype(np.float64) / 255.0) ** g), 0, 255)

I = imgs["normal"]
say(f"Orijinal ortalama: {I.mean():.2f}")
sonuc = {}
J = parlaklik_kaydir(I, 40)
clip_orani = 100.0 * (J >= 255).mean()
say(f"b=+40: beklenen ort ~ {I.mean()+40:.2f} | olculen {J.mean():.2f} | 255'te kirpilan %: {clip_orani:.2f}")
sonuc["b=+40"] = J
for g in (0.5, 2.0):
    Jg = gama(I, g)
    say(f"gama={g}: olculen ort {Jg.mean():.2f}  (gama<1 aydinlatir, gama>1 karartir)")
    sonuc[f"gama={g}"] = Jg
say("Kontrol: 64 -> gama0.5:", round(float(gama(np.array([64]), 0.5)[0]), 1),
    "| gama2.0:", round(float(gama(np.array([64]), 2.0)[0]), 1))

# fig, ax = plt.subplots(1, 4... ile başlayan kısmı silip bunu yapıştır:
fig, axes = plt.subplots(2, 2, figsize=(10, 10))
ax = axes.flatten()
ax[0].imshow(I); ax[0].set_title(f"orijinal ort={I.mean():.1f}")
for a, (n, Jx) in zip(ax[1:], sonuc.items()):
    a.imshow(Jx.astype(np.uint8)); a.set_title(f"{n} ort={Jx.mean():.1f}")
for a in ax: a.axis("off")
plt.tight_layout(); plt.savefig(f"{OUT}/parlaklik_gama.png", dpi=150); plt.close()

# ----------------------------- Adim 7: Kucultme -----------------------------
say("\n== Adim 7: 1/4 kucultme ==")
xa, ya, xb, yb = TEXT_ROI
crop = imgs["normal"][ya:yb, xa:xb]
h, w = crop.shape[:2]
h, w = h - h % 4, w - w % 4
crop = crop[:h, :w]
small_n = cv2.resize(crop, (w//4, h//4), interpolation=cv2.INTER_NEAREST)
small_a = cv2.resize(crop, (w//4, h//4), interpolation=cv2.INTER_AREA)
up_n = cv2.resize(small_n, (w, h), interpolation=cv2.INTER_NEAREST)
up_a = cv2.resize(small_a, (w, h), interpolation=cv2.INTER_NEAREST)
mse_n = float(((crop.astype(float) - up_n) ** 2).mean())
mse_a = float(((crop.astype(float) - up_a) ** 2).mean())
say(f"Kesit {w}x{h} -> {w//4}x{h//4}")
say(f"MSE (orijinal vs buyutulmus)  NEAREST: {mse_n:.1f} | AREA: {mse_a:.1f}")
say("NOT: MSE okunabilirligin tek olcusu degildir; gorsel yorum da yazin.")

# fig, ax = plt.subplots(1, 3... ile başlayan kısmı silip bunu yapıştır:
fig, ax = plt.subplots(3, 1, figsize=(6, 12))
for a, im_, t in zip(ax, (crop, up_n, up_a),
                     ("orijinal kesit", "1/4 NEAREST -> buyutme", "1/4 AREA -> buyutme")):
    a.imshow(im_, interpolation="nearest"); a.set_title(t); a.axis("off")
plt.tight_layout(); plt.savefig(f"{OUT}/kucultme.png", dpi=150); plt.close()

# ----------------------------- Kayit -----------------------------
pd.DataFrame(list(TAHMINLER.items()), columns=["deney", "tahmin"]).to_csv(
    f"{OUT}/tahminler.csv", index=False)
with open(f"{OUT}/ham_cikti.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log))
print(f"\nTamam. Cikti klasoru: {OUT}/")