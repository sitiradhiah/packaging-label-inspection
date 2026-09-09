# Model details

## Detection

The dashboard loads `models/parcel_fields.onnx`, a YOLO11n model with two classes: `filled` and `empty`. Inference uses OpenCV DNN on the CPU with a 640-pixel input, confidence threshold 0.65 and class-agnostic NMS IoU threshold 0.45.

Exactly five separated rows with similar widths are required. Names are assigned from top to bottom: Parcel ID, recipient name, address, postcode and shipping date. All filled means PASS; any empty means FAIL. An unmatched count or arrangement means RETAKE. A missing detection is not classified as empty. When the count is not five but four template markers are visible, individual detections are mapped to their fixed field positions. Missing fields show NOT_DETECTED and ambiguous matches show UNCERTAIN; the overall result remains RETAKE. OCR continues reading fixed field contents without reading the headings.

For labels filling almost the whole image, ArUco markers guide the addition of a margin before inference. Boxes are mapped back to the original image. Class labels and confidence still come from YOLO.

## OCR and records

RapidOCR uses pretrained models to read the five single-line fields automatically in a background process. Four ArUco corner markers align the label. OCR does not require five successful YOLO detections and does not determine PASS/FAIL.

CHECK & SIMPAN reads and saves the same image. JSON records retain field states, confidence, detections and OCR text. The Excel-readable OCR export uses those saved text readings. An empty OCR reading does not prove an empty field.

## Training and limitations

The model was fine-tuned from pretrained YOLO11n using synthetic label images. Each training stage used 200 training and 40 validation scenes, including negative backgrounds. The second stage varied all 32 filled/empty combinations.

Validation shared the same template family and is not an independent measure of camera accuracy. Use one upright supplied template. Blur, glare, small text and different layouts can affect detection and OCR. Text recognition does not verify the validity of the information.

Training is optional for development. The repository includes the inference model, but excludes generated datasets, training checkpoints and runs. Training scripts require those inputs; they are not part of normal setup. Model provenance is recorded in [models/SOURCE.txt](models/SOURCE.txt).

## Checks without a camera

After completing the README setup, run:

```powershell
.\.venv\Scripts\python.exe -m unittest test_fields test_yolo_field_rules
.\.venv\Scripts\python.exe dashboard.py --smoke-test
.\.venv\Scripts\python.exe test_ocr_dashboard.py
```

These checks cover inspection rules, dashboard rendering, automatic OCR, text clearing and saving the correct image. They do not measure live camera performance.
