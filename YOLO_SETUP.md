# Sambungan YOLO — status sebenar
Kod dashboard kini mempunyai sambungan YOLO11n melalui OpenCV DNN.
Model parcel_label belum dilatih. Oleh itu belum ada kotak YOLO/confidence di kamera.
Sistem pemeriksaan medan OpenCV masih berfungsi tanpa model.

## Data
datasets/parcel_label_starter mempunyai 120 gambar sintetik latihan dan anotasi YOLO.
Sediakan gambar validation berasingan daripada kamera sebenar (termasuk tanpa label); anotasi dengan kelas 0 parcel_label.
Jangan guna imej sama untuk latihan dan pengesahan, atau anggap variasi template membuktikan ketepatan kamera.

## Latihan
Python sedia ada projek ialah 32-bit. Kekalkan .venv sedia ada untuk dashboard.
Gunakan Python 64-bit berasingan dan pasang PyTorch yang sesuai dengan GPU, kemudian requirements-training.txt.
Sediakan dataset YAML:
```yaml
path: C:/laragon/www/packaging-label-inspection/datasets/parcel_label_starter
train: images/train
val: images/val
names:
  0: parcel_label
```
images/val dan labels/val mesti diisi dengan data pengesahan sebenar sebelum latihan.
Jalankan train_yolo.py --data path/to/data.yaml --device 0.
Skrip melatih YOLO11n dan mengeksport models/parcel_label.onnx.

## Dashboard
Model dimuat sekali semasa startup. Jika fail tiada, status menunjukkan model belum tersedia.
Kotak hijau dan confidence adalah daripada YOLO untuk parcel_label sahaja.
Confidence bukan peratus ketepatan, dan bukan skor kelengkapan medan.
OpenCV semak lima medan menggunakan template/penanda sedia ada; label tanpa template itu belum boleh diperiksa.
YOLO inference draft ini guna CPU OpenCV, bukan RTX 4050. Prestasi sebenar belum diukur.
Paparan overlay menggunakan frame yang sama dengan inference, untuk mengelakkan kotak tertinggal pada objek bergerak.
Keputusan JSON mengandungi pengesanan YOLO; imej asal kekal tanpa anotasi.

