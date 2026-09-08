# Parcel Label Checker Dashboard â€” YOLO + OpenCV

Dashboard memeriksa lima medan pada satu template label parcel: Parcel ID, nama penerima, alamat, poskod dan tarikh penghantaran.

## Jalankan
```
.\.venv\Scripts\python.exe dashboard.py
```
Atau buka `run.bat`. RB3 ialah kamera lalai; pilih built-in webcam sebagai backup. Tekan Henti sebelum menukar sumber. Untuk mula tanpa sambungan RB3:
```
.\.venv\Scripts\python.exe dashboard.py --webcam
```

## Cara guna
- Tunjukkan satu label tegak dengan semua lima medan kelihatan.
- Kotak hijau `filled`: model mengesan medan berisi.
- Kotak merah `empty`: model mengesan medan kosong.
- Nombor pada kotak ialah confidence YOLO (0 hingga 1), bukan peratus ketepatan projek.
- PASS: lima medan dikesan dan semuanya filled. FAIL: lima medan dikesan dan sekurang-kurangnya satu empty. RETAKE: bilangan/susunan medan tidak memenuhi template.
- Buka Gambar Demo untuk mencuba gambar dalam `templates`.
- CHECK & SIMPAN menyimpan gambar, keputusan dan skor dalam `results_fields`.

Model medan `models/parcel_fields.onnx` diberi keutamaan. Status dashboard menunjukkan model aktif. Model YOLO objek umum COCO yang lama bukan pengesan kelengkapan medan.

Ini prototaip yang dilatih menggunakan gambar sintetik daripada satu keluarga template. Ia belum mempunyai pengukuran ketepatan menggunakan set ujian kamera bebas. Pantulan skrin, kabur dan sudut kamera boleh mengubah keputusan. Nama medan dipadankan mengikut urutan atas ke bawah; gunakan template yang dibekalkan.

OCR pralatih membaca isi lima medan secara automatik dan memaparkan teks bersama status medan di sebelah kanan. Teks disimpan dalam fail JSON bersama gambar dan keputusan. OCR tidak mengesahkan kesahihan ID, alamat atau tarikh; keputusan PASS/FAIL masih daripada YOLO.

## Pembangunan
Dashboard menggunakan OpenCV DNN pada CPU. Latihan berasingan menggunakan `.venv-train` (Python 64-bit); persekitaran dashboard asal dikekalkan.
Lihat `FIELD_MODEL_GUIDE.md` untuk dataset dan latihan. `app.py` dan `inspection.py` mengekalkan pemeriksaan OpenCV terdahulu bagi tujuan perbandingan; laluan YOLO dashboard menggunakan keputusan model medan.

## OCR langsung (dikemas kini)
- Panel kanan kini menyatukan nama medan, status/confidence YOLO dan teks OCR. Tiada tab OCR berasingan.
- Buka kamera atau gambar demo: OCR bermula automatik tanpa CHECK. Ia membaca imej terkini dalam proses latar, satu kerja pada satu masa, dengan sela 0.5 saat selepas bacaan selesai. Ujian demo mengambil kira-kira 1–2 saat setiap bacaan; kelajuan kamera sebenar bergantung pada beban komputer.
- Empat penanda sudut diperlukan untuk menentukan ruang teks. OCR tidak lagi memerlukan YOLO berjaya mengesan kelima-lima medan. Gunakan template satu baris yang dibekalkan.
- CHECK & SIMPAN hanya apabila mahu merekod: bacaan OCR dibuat pada gambar yang sama disimpan. Bacaan automatik tidak menambah sejarah.
- Teks memaparkan bacaan terkini dengan masa tangkapannya; ia tidak dikemas kini pada setiap frame video. Tukar sumber/Henti mengosongkan bacaan dan menolak hasil lama yang masih diproses.
- Tiada teks dapat dibaca tidak membuktikan medan kosong; gambar mungkin kabur. PASS/FAIL dan confidence kotak kekal daripada YOLO.
- RapidOCR 1.4.4 menggunakan model pralatih tempatan, tanpa latihan baharu atau penghantaran gambar ke internet. Pasang menggunakan `.venv-train\Scripts\python.exe -m pip install -r requirements-ocr.txt`.
- Ujian automatik: `.venv\Scripts\python.exe test_ocr_dashboard.py` (bacaan tanpa klik, pertukaran lengkap-ke-kosong, simpanan gambar tepat dan susun atur 900x680).
