# Development tools

These scripts are optional development tools, not dashboard setup steps. Their contents were retained when moved from the project root. Dataset, model and training output paths still point to the project root.

## Field-model training

Run from the project root using the appropriate Python environment:

```powershell
.\.venv\Scripts\python.exe tools/training/make_field_dataset.py
.\.venv\Scripts\python.exe tools/training/make_field_dataset_v2.py
.\.venv-train\Scripts\python.exe tools/training/train_fields.py
.\.venv-train\Scripts\python.exe tools/training/train_fields_v2.py
```

Training requires `requirements-training.txt`. Generators refuse to overwrite an existing dataset. Despite its filename, `make_field_dataset_v2.py` produces `datasets/parcel_fields_v3`, as before. The second training script requires `models/fields-stage1.pt`, a local checkpoint that is not included in GitHub. These commands are not a complete automatic training pipeline. Training/export scripts can replace the active model, so run them only when developing a new model.

## Legacy experiments

`legacy/` contains the three `evaluate_fields*` scripts, `export_field_candidate.py`, `make_yolo_images.py` and `train_yolo.py`. They depend on their original datasets/checkpoints and are retained for reference. `train_yolo.py` trains the earlier single-class `parcel_label` model, not the current filled/empty model.

## Bahasa Melayu

Folder ini hanya untuk pembangunan dan latihan pilihan. Dashboard tidak memerlukan skrip ini. Laluan dataset, model dan output latihan masih merujuk kepada folder utama projek.

Gunakan arahan di atas jika mahu menjalankan skrip latihan yang dipindahkan. Dataset sedia ada tidak ditimpa oleh penjana. Latihan peringkat kedua memerlukan checkpoint tempatan `models/fields-stage1.pt` yang tidak disertakan dalam GitHub. Skrip latihan/eksport boleh menggantikan model aktif.

Folder `legacy/` menyimpan eksperimen lama untuk rujukan. Semua arahan menjalankan dashboard, setup dan ujian di folder utama kekal sama.
