# Parcel Label Inspection Dashboard

YOLO + OpenCV + live OCR for inspecting a fixed parcel label template.

## English

### About the project

The dashboard checks five fields: Parcel ID, recipient name, address, postcode and shipping date. YOLO detects filled or empty fields, while pretrained RapidOCR reads the text automatically and displays it beside each field's status.

- Green box: `filled`. Red box: `empty`.
- Each box displays the YOLO confidence score (0 to 1), not the project's measured accuracy.
- **PASS:** all five fields are detected and filled.
- **FAIL:** all five fields are detected and at least one is empty.
- **RETAKE:** the field count or arrangement does not match the expected template.

### Requirements for another Windows laptop

1. Install **Git** and **Python 3.12 (64-bit)**. Enable **Add Python to PATH** and install the Python launcher (`py`).
2. Have an internet connection for the initial download and dependency installation.
3. Use a built-in/USB webcam, an appropriately configured Qualcomm RB3, or the supplied demo images.
4. Sign in with a GitHub account that has access to this **private repository**. The owner must grant access before you can clone or pull it.

A dedicated GPU is not required to run the dashboard; it uses OpenCV DNN on the CPU. The trained YOLO model is included, so **you do not need to train a model again**.

### First-time setup

Open PowerShell or the VS Code terminal and run:

```powershell
git clone https://github.com/sitiradhiah/packaging-label-inspection.git
cd packaging-label-inspection
```

Create the dashboard environment and install its libraries:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create the separate 64-bit OCR environment:

```powershell
py -3.12 -m venv .venv-train
.\.venv-train\Scripts\python.exe -m pip install -r requirements-ocr.txt
```

The folder name `.venv-train` is required by the current OCR code, even when you only run OCR. **Do not install `requirements-training.txt` unless you intend to train a model.** No environment activation command is needed when using the full Python paths above.

### Run with a laptop webcam

```powershell
.\.venv\Scripts\python.exe dashboard.py --webcam
```

Click **Mula Webcam** to start the camera. Alternatively, click **Buka Gambar Demo** and select a file from `templates` to try the project without a camera.

### Run with Qualcomm RB3

RB3 additionally requires Android SDK **Platform Tools (ADB)** on the laptop, an authorised USB connection, and a compatible camera/GStreamer setup on the board. The current code expects `gst-launch-1.0`, `qtiqmmfsrc` and camera index 0 on the RB3. It searches for ADB on PATH or at `%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe`.

Connect exactly one authorised ADB device and check the connection:

```powershell
adb devices
.\.venv\Scripts\python.exe dashboard.py --rb3
```

The RB3 connection starts automatically in this mode. Running `dashboard.py` without options, or opening `run.bat`, also uses RB3 by default. Click **Henti** before changing the camera source.

### Inspect and save

1. Show one upright label using the supplied template, with all five fields and four corner markers visible.
2. YOLO boxes and field statuses appear in the camera view and right panel.
3. OCR reads automatically; no CHECK click is needed. The right panel displays the latest recognised text and capture time. Demo readings took around 1-2 seconds; speed depends on the computer and image. OCR does not update on every video frame.
4. Click **CHECK & SIMPAN** to save an inspection. OCR is read from the same image that is saved. Automatic readings do not add history records.
5. Click **Buka Excel (OCR)** to generate and open the CSV containing recognised text. Use **Folder Keputusan** to find saved images, JSON details and CSV records in `results_fields`.

The OCR export uses the saved JSON readings, replacing field-status words such as `FILLED` with recognised text. Close a CSV in Excel before saving to that same file. If the OCR export is locked, the export button creates a timestamped copy.

### Update an existing copy

Stop the dashboard, open a terminal in the project folder, then run:

```powershell
git pull
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-train\Scripts\python.exe -m pip install -r requirements-ocr.txt
.\.venv\Scripts\python.exe dashboard.py --webcam
```

Keep your local code changes before resolving any Git conflicts. Restart the dashboard after updates so it loads the new code.

### What is included in GitHub?

- Application code, dependency lists, demo label templates and `models/parcel_fields.onnx`.
- Python environments (`.venv`, `.venv-train`) are excluded: recreate them using the setup steps.
- Camera records, logs, generated datasets and training runs are excluded. They remain on the original laptop.

### Limitations and checks

The YOLO model was trained on synthetic images from one template family. All 32 filled/empty demo combinations passed checks, but independent real-world camera accuracy has not been measured. Blur, glare, small text and unusual angles can affect results. OCR can omit spaces or misread characters and does not validate the meaning or correctness of an ID, address or date. Four corner markers are required for the current OCR alignment; OCR can run even when YOLO has not detected all five fields.

Run the basic checks without opening a camera:

```powershell
.\.venv\Scripts\python.exe -m unittest test_fields test_yolo_field_rules
.\.venv\Scripts\python.exe dashboard.py --smoke-test
.\.venv\Scripts\python.exe test_ocr_dashboard.py
```

See [FIELD_MODEL_GUIDE.md](FIELD_MODEL_GUIDE.md) for model details. Training scripts are for development and need their generated datasets/checkpoints; they are not required for normal dashboard use. `app.py` and `inspection.py` retain the earlier OpenCV inspection method for comparison.

---

## Bahasa Melayu

### Tentang projek

Dashboard memeriksa lima medan: Parcel ID, nama penerima, alamat, poskod dan tarikh penghantaran. YOLO mengesan medan berisi atau kosong, manakala RapidOCR pralatih membaca teks secara automatik dan memaparkannya bersama status medan.

- Kotak hijau: `filled`. Kotak merah: `empty`.
- Nombor pada kotak ialah confidence YOLO (0 hingga 1), bukan ukuran ketepatan keseluruhan projek.
- **PASS:** lima medan dikesan dan semuanya berisi.
- **FAIL:** lima medan dikesan dan sekurang-kurangnya satu kosong.
- **RETAKE:** bilangan atau susunan medan tidak memenuhi template.

### Keperluan laptop Windows lain

1. Install **Git** dan **Python 3.12 versi 64-bit**. Pilih **Add Python to PATH** dan pasang Python launcher (`py`).
2. Sambungan internet diperlukan untuk muat turun awal dan pemasangan library.
3. Gunakan webcam built-in/USB, Qualcomm RB3 yang sudah dikonfigurasi, atau gambar demo.
4. Akaun GitHub mesti mempunyai akses kepada **repositori private** ini sebelum boleh clone atau pull.

GPU berasingan tidak diwajibkan kerana dashboard menggunakan OpenCV DNN pada CPU. Model YOLO terlatih sudah disertakan, jadi **tidak perlu train semula**.

### Setup kali pertama

Buka PowerShell atau terminal VS Code:

```powershell
git clone https://github.com/sitiradhiah/packaging-label-inspection.git
cd packaging-label-inspection
```

Sediakan persekitaran dashboard:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Sediakan persekitaran OCR 64-bit:

```powershell
py -3.12 -m venv .venv-train
.\.venv-train\Scripts\python.exe -m pip install -r requirements-ocr.txt
```

Nama folder `.venv-train` memang digunakan oleh kod OCR sekarang. **Tidak perlu install `requirements-training.txt` jika hanya mahu menjalankan dashboard.** Arahan activation tidak diperlukan kerana arahan di atas menggunakan laluan Python penuh.

### Jalankan dengan webcam laptop

```powershell
.\.venv\Scripts\python.exe dashboard.py --webcam
```

Klik **Mula Webcam**, atau **Buka Gambar Demo** dan pilih gambar dalam `templates` untuk mencuba tanpa kamera.

### Jalankan dengan Qualcomm RB3

Laptop perlu mempunyai Android SDK **Platform Tools (ADB)**, sambungan USB yang dibenarkan dan setup kamera/GStreamer yang serasi pada board. Kod semasa menggunakan `gst-launch-1.0`, `qtiqmmfsrc` dan kamera indeks 0. ADB dicari melalui PATH atau `%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe`.

Sambungkan hanya satu peranti ADB yang dibenarkan:

```powershell
adb devices
.\.venv\Scripts\python.exe dashboard.py --rb3
```

RB3 bermula secara automatik dalam mod ini. `dashboard.py` tanpa pilihan dan `run.bat` juga menggunakan RB3 secara lalai. Tekan **Henti** sebelum menukar sumber kamera.

### Pemeriksaan dan simpanan

1. Tunjukkan satu label tegak dengan lima medan dan empat penanda sudut yang jelas.
2. Kotak YOLO serta status medan dipaparkan pada kamera dan panel kanan.
3. OCR membaca secara automatik tanpa menekan CHECK. Teks terkini dan masa tangkapan dipaparkan di kanan. Ujian demo mengambil sekitar 1-2 saat; kelajuan bergantung pada komputer dan gambar. OCR bukan dikemas kini pada setiap frame video.
4. Tekan **CHECK & SIMPAN** untuk menyimpan rekod. OCR membaca gambar yang sama disimpan. Bacaan automatik tidak menambah sejarah.
5. Tekan **Buka Excel (OCR)** untuk membuka CSV berisi teks OCR. **Folder Keputusan** membuka `results_fields` yang mengandungi gambar, JSON dan CSV.

Eksport OCR mengambil teks daripada rekod JSON, menggantikan perkataan seperti `FILLED` dalam lajur medan. Tutup CSV dalam Excel sebelum menyimpan ke fail yang sama. Jika fail eksport dikunci, butang eksport menghasilkan salinan dengan cap masa.

### Kemas kini projek yang sudah dimuat turun

Tutup dashboard, masuk folder projek dalam terminal dan jalankan:

```powershell
git pull
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-train\Scripts\python.exe -m pip install -r requirements-ocr.txt
.\.venv\Scripts\python.exe dashboard.py --webcam
```

Simpan perubahan kod tempatan sebelum menyelesaikan konflik Git. Buka semula dashboard selepas kemas kini supaya kod baharu digunakan.

### Kandungan GitHub

- Kod aplikasi, senarai library, template demo dan model `models/parcel_fields.onnx` disertakan.
- `.venv` dan `.venv-train` tidak dimuat naik; bina semula menggunakan langkah setup.
- Rekod kamera, log, dataset yang dijana dan hasil latihan tidak dimuat naik. Fail tersebut kekal pada laptop asal.

### Batasan dan ujian

Model YOLO dilatih dengan gambar sintetik daripada satu keluarga template. Semua 32 kombinasi demo berisi/kosong lulus ujian, tetapi ketepatan menggunakan set ujian kamera sebenar yang bebas belum diukur. Kabur, pantulan, tulisan kecil dan sudut kamera boleh mempengaruhi keputusan. OCR boleh kehilangan jarak antara perkataan atau tersalah baca aksara. Ia tidak mengesahkan kesahihan ID, alamat atau tarikh. Empat penanda sudut diperlukan untuk penjajaran OCR semasa; OCR boleh berjalan walaupun YOLO belum mengesan kelima-lima medan.

Ujian asas tanpa membuka kamera:

```powershell
.\.venv\Scripts\python.exe -m unittest test_fields test_yolo_field_rules
.\.venv\Scripts\python.exe dashboard.py --smoke-test
.\.venv\Scripts\python.exe test_ocr_dashboard.py
```

Rujuk [FIELD_MODEL_GUIDE.md](FIELD_MODEL_GUIDE.md) untuk butiran model. Skrip latihan memerlukan dataset/checkpoint berkaitan dan tidak diperlukan untuk penggunaan biasa. `app.py` dan `inspection.py` mengekalkan kaedah pemeriksaan OpenCV terdahulu untuk perbandingan.
