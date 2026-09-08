# YOLO Field Inspection

Model: YOLO11n, classes 0 filled and 1 empty. OpenCV DNN inference on CPU, fixed 640 input, confidence threshold 0.65 and class-agnostic NMS IoU 0.45. Confidence is the model score, not calibrated accuracy.

The dashboard prefers models/parcel_fields.onnx. Green boxes mean filled and red boxes mean empty. Exactly five separated rows with similar widths are required; otherwise RETAKE. Any detected empty row -> FAIL; five filled rows -> PASS. Missing detection is never automatically classified as empty.

Field names are assigned top-to-bottom for one upright supplied template. YOLO does not read or validate content. A separate pretrained OCR step now reads text on CHECK & SIMPAN; it does not change the YOLO verdict. Raw image, field states, confidence and detections are retained in the result JSON when saved.

Training environment: .venv-train (64-bit Python). Dashboard environment: .venv (original Python).
Stage 1: YOLO11n pretrained weights, datasets/parcel_fields_v1.
Stage 2: models/fields-stage1.pt, datasets/parcel_fields_v3, train_fields_v2.py.
Each dataset contains 200 training / 40 validation synthetic scenes, including negative backgrounds. Stage 2 varies all 32 filled/empty combinations. The validation set shares the template family, so metrics are training diagnostics, NOT independent real-camera accuracy.

Train/export: .venv-train\Scripts\python.exe train_fields_v2.py
Dashboard: .venv\Scripts\python.exe dashboard.py

Before a class demonstration, test complete and incomplete labels using the chosen camera. Keep all fields in focus and visible. Collect independently captured images under different lighting and distances before claiming real-world accuracy. Source pretrained YOLO11 weights and Ultralytics training software use their applicable Ultralytics licence; see models/SOURCE.txt.

For demo images whose corner markers span almost the full image, the detector adds a grey margin before YOLO inference and maps boxes back to original coordinates. ArUco only controls framing; the field class and confidence still come from YOLO.
