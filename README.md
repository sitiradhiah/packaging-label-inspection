# Parcel Label Inspection Dashboard

YOLO, OpenCV and automatic OCR for a fixed parcel label template.

## English

### ZIP / WhatsApp setup (no Git required)

1. Install Python 3.12 (64-bit) with the Python launcher (`py`).
2. Right-click the ZIP and select **Extract All**. Open the extracted folder containing `setup.bat`.
3. Run `setup.bat` once. Internet is needed to install dashboard and OCR libraries.
4. Wait for **YOLO: PASS** and **OCR: PASS**.
5. Open `run-webcam.bat`, then click **Mula Webcam**. Use **Buka Gambar Demo** to test without a camera.

Do not run the program inside the ZIP. Git and a GitHub account are not required for a ZIP received through WhatsApp. No model training is needed.

If `run-webcam.bat` is unavailable, open a terminal in the extracted folder and run:

```powershell
.\.venv\Scripts\python.exe dashboard.py --webcam
```

### GitHub clone setup (alternative)

Install **Git** and **Python 3.12 (64-bit)**, including the Python launcher (`py`). Internet access is needed for installation. This repository is private; your GitHub account needs access before cloning.

Run in PowerShell or the VS Code terminal:

```powershell
git clone https://github.com/sitiradhiah/packaging-label-inspection.git
cd packaging-label-inspection
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
py -3.12 -m venv .venv-train
.\.venv-train\Scripts\python.exe -m pip install -r requirements-ocr.txt
```

Alternatively, after cloning and entering the folder, run `setup.bat` instead of the manual environment commands. It installs both dashboard and OCR libraries, then checks the model and OCR. These setup steps are needed once. The current OCR code requires the folder name `.venv-train`. The trained YOLO model is included; **training and `requirements-training.txt` are not needed to run the dashboard**.

**Missing OCR or model error after using an older setup?** Follow the update method below for your ZIP or Git copy, then rerun `setup.bat`. Existing environments are reused. Setup only reports success after YOLO and OCR checks pass. If it fails, copy the full terminal error. You can rerun the check with `.\.venv\Scripts\python.exe check_setup.py`.

### Run

For a laptop webcam:

```powershell
.\.venv\Scripts\python.exe dashboard.py --webcam
```

Click **Mula Webcam**, or **Buka Gambar Demo** to select an image from `templates` without a camera.

`run.bat` opens the dashboard with **RB3 selected by default**. If it is already open, no extra launch command is needed. Click **Henti** before changing the camera selection.

For RB3:

```powershell
adb devices
.\.venv\Scripts\python.exe dashboard.py --rb3
```

RB3 requires Android SDK Platform Tools (ADB), exactly one authorised USB device, and a compatible camera setup on the board with `gst-launch-1.0` and `qtiqmmfsrc` (camera index 0). ADB must be on PATH or in `%LOCALAPPDATA%\Android\Sdk\platform-tools`. RB3 connects automatically when launched in this mode.

### Inspect and save

- Show one upright supplied label template with all five fields and four corner markers visible.
- Green `filled` boxes indicate filled fields; red `empty` boxes indicate empty fields. Box scores are YOLO confidence, not measured accuracy.
- **PASS:** five fields detected and all filled. **FAIL:** five detected with at least one empty. **RETAKE:** the detected count or arrangement does not match the template.
- OCR automatically displays text beside each field. It updates periodically, not on every video frame. No CHECK click is needed to read text.
- **CHECK & SIMPAN** saves the image, inspection result and OCR text from that image. Automatic OCR does not save history.
- **Buka Excel (OCR)** opens a CSV with recognised text instead of `FILLED`/`EMPTY`. **Folder Keputusan** opens `results_fields`, containing CSV, JSON and image records.
- Close a CSV in Excel before writing to the same file. A locked OCR export is saved as a timestamped copy.

### Update

**ZIP users:** obtain the latest ZIP and extract it into a new folder. Run its `setup.bat` and then `run-webcam.bat`. Keep the old folder if it contains inspection records; ZIP updates do not transfer those records automatically. Do not use `git pull` for a ZIP copy.

**Git clone users:** close the dashboard. In the project folder, run:

```powershell
git pull
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-train\Scripts\python.exe -m pip install -r requirements-ocr.txt
.\.venv\Scripts\python.exe dashboard.py --webcam
```

Preserve local code changes before resolving any Git conflicts. Restart after an update to load the new code.

### Project structure

- Root Python files: dashboard, camera, detection, OCR and record storage. Existing launch commands are unchanged.
- `models/` and `templates/`: active model and demo labels.
- `tools/training/`: dataset generators and field-model training scripts.
- `tools/legacy/`: earlier whole-label training and checkpoint experiments; not used by the dashboard.
- Root `test_*.py`, `verify_*.py` and `check_setup.py`: existing checks, kept at their original paths.
- Local environments and `results_fields/` remain in place.

See [Development tools](tools/README.md) for the relocated commands.

### Notes

- Python environments and camera records are not included in GitHub. Setup recreates the environments; inspections create local records.
- This prototype uses synthetic training images and a fixed template. Real-world camera accuracy has not been independently measured.
- Blur, glare and small text affect results. OCR can misread characters or spaces and does not validate addresses, IDs or dates.
- See [Model details](FIELD_MODEL_GUIDE.md) for detection rules and checks, and [Model sources](models/SOURCE.txt) for provenance.

---

## Bahasa Melayu

### Setup ZIP / WhatsApp (tidak perlu Git)

1. Install Python 3.12 (64-bit) bersama Python launcher (`py`).
2. Klik kanan ZIP dan pilih **Extract All**. Buka folder hasil extract yang mengandungi `setup.bat`.
3. Jalankan `setup.bat` sekali. Internet diperlukan untuk memasang library dashboard dan OCR.
4. Tunggu **YOLO: PASS** dan **OCR: PASS**.
5. Buka `run-webcam.bat`, kemudian klik **Mula Webcam**. Pilih **Buka Gambar Demo** untuk mencuba tanpa kamera.

Jangan jalankan program dari dalam ZIP. Git dan akaun GitHub tidak diperlukan untuk ZIP yang diterima melalui WhatsApp. Model tidak perlu dilatih semula.

Jika `run-webcam.bat` tiada, buka terminal dalam folder hasil extract dan jalankan:

```powershell
.\.venv\Scripts\python.exe dashboard.py --webcam
```

### Setup melalui GitHub clone (alternatif)

Install **Git** dan **Python 3.12 (64-bit)** bersama Python launcher (`py`). Internet diperlukan semasa pemasangan. Repositori ini private; akaun GitHub anda perlu diberi akses sebelum clone.

Jalankan dalam PowerShell atau terminal VS Code:

```powershell
git clone https://github.com/sitiradhiah/packaging-label-inspection.git
cd packaging-label-inspection
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
py -3.12 -m venv .venv-train
.\.venv-train\Scripts\python.exe -m pip install -r requirements-ocr.txt
```

Sebagai alternatif selepas clone dan masuk folder, jalankan `setup.bat` menggantikan arahan persekitaran manual. Ia memasang library dashboard dan OCR, kemudian menguji model serta OCR. Setup ini hanya diperlukan sekali. Kod OCR semasa memerlukan nama folder `.venv-train`. Model YOLO terlatih sudah disertakan; **tidak perlu train atau install `requirements-training.txt` untuk menjalankan dashboard**.

**OCR tiada atau model gagal selepas menggunakan setup lama?** Ikut cara kemas kini ZIP atau Git di bawah, kemudian jalankan semula `setup.bat`. Persekitaran sedia ada digunakan semula. Setup hanya melaporkan berjaya selepas ujian YOLO dan OCR lulus. Jika gagal, salin ralat penuh terminal. Ujian boleh diulang dengan `.\.venv\Scripts\python.exe check_setup.py`.

### Jalankan

Untuk webcam laptop:

```powershell
.\.venv\Scripts\python.exe dashboard.py --webcam
```

Klik **Mula Webcam**, atau **Buka Gambar Demo** untuk memilih gambar dalam `templates` tanpa kamera.

`run.bat` membuka dashboard dengan **RB3 sebagai pilihan lalai**. Jika dashboard sudah terbuka, tidak perlu arahan tambahan untuk membukanya lagi. Tekan **Henti** sebelum menukar pilihan kamera.

Untuk RB3:

```powershell
adb devices
.\.venv\Scripts\python.exe dashboard.py --rb3
```

RB3 memerlukan Android SDK Platform Tools (ADB), hanya satu peranti USB yang dibenarkan, dan setup kamera serasi pada board dengan `gst-launch-1.0` serta `qtiqmmfsrc` (kamera indeks 0). ADB mesti berada dalam PATH atau `%LOCALAPPDATA%\Android\Sdk\platform-tools`. Sambungan RB3 bermula automatik dalam mod ini.

### Pemeriksaan dan simpanan

- Tunjukkan satu template label yang dibekalkan secara tegak, dengan lima medan dan empat penanda sudut kelihatan.
- Kotak hijau `filled` menunjukkan medan berisi; kotak merah `empty` menunjukkan medan kosong. Nombor kotak ialah confidence YOLO, bukan ukuran ketepatan projek.
- **PASS:** lima medan dikesan dan semuanya berisi. **FAIL:** lima medan dikesan dengan sekurang-kurangnya satu kosong. **RETAKE:** bilangan atau susunan medan tidak memenuhi template.
- OCR memaparkan teks di sebelah setiap medan secara automatik dan berkala, bukan pada setiap frame video. Tidak perlu tekan CHECK untuk membaca teks.
- **CHECK & SIMPAN** menyimpan gambar, keputusan pemeriksaan dan teks OCR daripada gambar itu. Bacaan automatik tidak menyimpan sejarah.
- **Buka Excel (OCR)** membuka CSV dengan teks bacaan menggantikan `FILLED`/`EMPTY`. **Folder Keputusan** membuka `results_fields` yang mengandungi CSV, JSON dan gambar.
- Tutup CSV dalam Excel sebelum menyimpan ke fail yang sama. Eksport OCR yang dikunci akan disimpan sebagai salinan dengan cap masa.

### Kemas kini

**Pengguna ZIP:** dapatkan ZIP terkini dan extract ke folder baharu. Jalankan `setup.bat`, kemudian `run-webcam.bat`. Simpan folder lama jika ada rekod pemeriksaan; rekod tidak dipindahkan secara automatik. Jangan gunakan `git pull` untuk salinan ZIP.

**Pengguna Git clone:** tutup dashboard. Dalam folder projek, jalankan:

```powershell
git pull
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-train\Scripts\python.exe -m pip install -r requirements-ocr.txt
.\.venv\Scripts\python.exe dashboard.py --webcam
```

Simpan perubahan kod tempatan sebelum menyelesaikan konflik Git. Buka semula dashboard selepas kemas kini supaya kod baharu digunakan.

### Struktur projek

- Fail Python utama: dashboard, kamera, pengesanan, OCR dan simpanan rekod. Arahan membuka dashboard tidak berubah.
- `models/` dan `templates/`: model aktif dan label demo.
- `tools/training/`: penjana dataset dan latihan model medan.
- `tools/legacy/`: eksperimen checkpoint dan latihan pengesanan seluruh label terdahulu; tidak digunakan dashboard.
- `test_*.py`, `verify_*.py` dan `check_setup.py`: ujian sedia ada kekal di lokasi asal.
- Persekitaran Python dan `results_fields/` tempatan dikekalkan.

Rujuk [Alat pembangunan](tools/README.md) untuk arahan skrip yang dipindahkan.

### Nota

- Persekitaran Python dan rekod kamera tidak dimuat naik ke GitHub. Setup membina semula persekitaran; pemeriksaan menghasilkan rekod tempatan.
- Prototaip ini menggunakan gambar latihan sintetik dan template tetap. Ketepatan kamera sebenar belum diukur melalui set ujian bebas.
- Kabur, pantulan dan tulisan kecil mempengaruhi keputusan. OCR boleh tersalah baca aksara atau jarak perkataan dan tidak mengesahkan kesahihan alamat, ID atau tarikh.
- Rujuk [Butiran model](FIELD_MODEL_GUIDE.md) untuk peraturan pengesanan dan ujian, serta [Sumber model](models/SOURCE.txt).
