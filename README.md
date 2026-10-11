# DeepSat-Change

**Deep Learning-Based Satellite Image Change Detection and Analysis System**
Course: INT422 – Deep Learning

A native Python desktop application (PySide6) that detects and analyzes changes
between two satellite images of the same area taken at different times, using a
lightweight U-Net trained for binary change-mask segmentation. Runs fully offline
on CPU — no GPU, no cloud, no paid API required.

## Features

- Text-only, icon-free dark-theme desktop UI (PySide6) matching the reference dashboard layout
- Dataset Manager: validate a local before/after/mask dataset, or download a supported dataset automatically
- Real CPU training pipeline: `tf.data` generators, augmentation, TensorBoard logging,
  early stopping, best/latest checkpoint saving
- Real inference pipeline: ORB-based image alignment, preprocessing, U-Net inference,
  morphological post-processing, connected-component region analysis
- Live metrics computed from real predictions: Accuracy, Precision, Recall, F1, IoU, Dice,
  confusion matrix
- Activation map viewer for any encoder convolution layer, with sharp zoomable tiles and PNG export
- Zoomable/pannable image viewer and a draggable before/after comparison slider
- SQLite-backed analysis history
- PDF / CSV / JSON export, using ReportLab (no MS Word dependency)
- 27 automated tests covering preprocessing, alignment, detection, metrics, dataset validation, and exports
- Nothing is hardcoded: all statistics, images, and logs are generated from actual
  data, actual inference, and actual database records

## System Requirements

- Windows 10/11 (or Linux/macOS — pure Python, no OS-specific code)
- Python 3.11
- No GPU / CUDA required
- Tested target hardware: AMD Ryzen 5 5500U, 8 GB RAM, integrated graphics

## Installation (PyCharm Community)

```text
Open PyCharm Community
File -> New Project -> DeepSat-Change
Select Python 3.11 interpreter, create a virtual environment
Open the Terminal tab inside PyCharm
pip install -r requirements.txt
```

Or from any terminal:

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

or in PyCharm: right-click `main.py` -> Run.

No command-line arguments are required.

## Dataset Setup — fully automatic, no manual downloads

Open **DATASET MANAGER** and click **DOWNLOAD DATASET**. That's the entire
setup step. The app will:

1. Connect to Hugging Face and stream a public satellite change-detection
   dataset (LEVIR-CD, pre-cropped to 256x256 tiles, real building-change
   masks — configured in `config/datasets.json`).
2. Save a subset of ~2,800 image pairs by default (2000 train / 400
   validation / 400 test — adjustable via `max_train_samples`,
   `max_val_samples`, `max_test_samples` in `config/settings.json`).
3. Organize everything automatically into the required folder structure
   below — no manual file moving, no zip extraction, no folder renaming.
4. Run dataset validation automatically so you can see it's ready.

No account, login, or manual file handling is required. You only need an
internet connection while the download runs. If you'd rather use your own
dataset, **USE LOCAL DATASET** still works and lets you point the app at any
folder matching the structure below.

The resulting structure under `dataset/`:

```text
dataset/
├── train/{before,after,mask}/
├── validation/{before,after,mask}/
└── test/{before,after,mask}/
```

Corresponding files share the same filename stem, e.g.
`train/before/00001.png`, `train/after/00001.png`, `train/mask/00001.png`
(mask is a single-channel PNG where 255 = changed pixel).

`config/datasets.json` also lists a second, higher-resolution (1024x1024)
version of the same dataset if you want more detail and have a fast
connection and more disk space — just swap which entry is first in the list,
or download it and use **USE LOCAL DATASET**.

## Training

Open the **TRAINING** page, set image size / batch size / epochs / learning
rate, and click **START TRAINING**. Training runs on a background thread so the
UI stays responsive. Progress, live loss/Dice curves, TensorBoard logs
(`logs/tensorboard/`), and checkpoints (`models/best_model.keras`,
`models/latest_model.keras`) are all produced from the real training run —
nothing is simulated.

**A note on time.** The default dataset is now ~2,800 image pairs (2000
train / 400 validation / 400 test) with 30 epochs — this gives noticeably
better accuracy than a small quick run, but on a CPU-only laptop (e.g. Ryzen
5 5500U, 8 GB RAM) a full run can take several hours. Plan to start it and
let it run in the background (overnight is fine) rather than waiting on it.
If you want a faster first pass to confirm everything works before committing
to a long run, lower `epochs` to ~10 and/or `max_train_samples` to ~500 in
the Training page or `config/settings.json`, then raise them back up for the
real run once you've confirmed the pipeline works end to end.

To view TensorBoard manually:

```bash
tensorboard --logdir logs/tensorboard
```

## Running Detection

1. **UPLOAD DATA** — load a before image and an after image.
2. **PREDICTION** — set the detection threshold and click **RUN ANALYSIS**.
3. **RESULTS** / **VISUALIZATION** — inspect the mask, probability heatmap,
   overlay, zoomable panels, and the before/after comparison slider.
4. **REPORT GENERATOR** — export the mask/overlay/heatmap as PNG, the region
   table as CSV/JSON, or a full PDF report.

## Evaluation

**METRICS** -> **EVALUATE ON TEST SET** runs the current model over
`dataset/test/` and computes Accuracy, Precision, Recall, F1, IoU, Dice, and a
confusion matrix from the actual predictions vs. ground-truth masks.

## Project Folder Structure

This is the actual, current structure of the project — every folder and file
that ships in the zip, with what it's for. Files marked **(runtime)** are
created automatically the first time you run the app and start out empty or
with placeholder `.gitkeep` files; you never need to create them by hand.

```text
DeepSat-Change/
│
├── main.py                        Application entry point — run this file to start the app
├── requirements.txt                Pinned Python dependencies for `pip install -r`
├── README.md                       This file
├── LICENSE                         MIT license text
│
├── config/
│   ├── settings.json                All tunable defaults: image size, batch size, epochs,
│   │                                 learning rate, threshold, min region size, paths,
│   │                                 dataset sample caps. Editable directly or via the
│   │                                 Settings page in the app.
│   └── datasets.json                 Registry of downloadable datasets (name, Hugging Face
│                                     id, size estimate, license note). Add an entry here to
│                                     offer another dataset in Dataset Manager.
│
├── app/
│   ├── __init__.py                  Marks `app` as a Python package (empty)
│   │
│   ├── ui/                          Everything the user sees and clicks (PySide6 widgets)
│   │   ├── main_window.py             Builds the window, wires the sidebar to the page
│   │   │                             stack, owns the shared `AppState`, routes results
│   │   │                             from Prediction into Results/Dashboard.
│   │   ├── sidebar.py                 Left-hand text-only navigation list and its
│   │   │                             active/inactive highlighting.
│   │   ├── header.py                  Top bar: page title, subtitle, live clock/date.
│   │   ├── dashboard.py               Home page: system/model/dataset status, summary
│   │   │                             stats, the 5-step workflow tracker, the four
│   │   │                             before/after/mask/overlay panels, metric cards,
│   │   │                             training curve, model info, system log feed.
│   │   ├── upload_view.py             Before/after image pickers, metadata display,
│   │   │                             pair validation (dimension mismatch handling).
│   │   ├── preprocessing_view.py      Runs and displays the load -> validate -> align ->
│   │   │                             resize -> normalize -> tensor pipeline step by step.
│   │   ├── prediction_view.py         Detection threshold control and the background
│   │   │                             inference worker trigger/status.
│   │   ├── results_view.py            The four large zoomable result panels plus change
│   │   │                             stats and the region table.
│   │   ├── visualization_view.py      Switches between change mask / probability heatmap /
│   │   │                             overlay (with opacity slider) / before-after
│   │   │                             comparison slider.
│   │   ├── activation_maps_view.py    Lets you pick an encoder conv layer, generates its
│   │   │                             feature maps (sharp, zoomable), and saves them as PNGs.
│   │   ├── metrics_view.py            Runs real test-set evaluation and displays
│   │   │                             Accuracy/Precision/Recall/F1/IoU/Dice + confusion matrix.
│   │   ├── training_view.py           Training configuration form, start/stop controls,
│   │   │                             live epoch/loss/Dice readout and chart.
│   │   ├── dataset_view.py            Dataset Manager: shows the registry entry, drives the
│   │   │                             automatic Hugging Face download, or lets you pick a
│   │   │                             local folder; shows the validation report.
│   │   ├── model_view.py              Model Information page: status, architecture details,
│   │   │                             training/validation metrics, manual model loading.
│   │   ├── report_view.py             All export buttons: mask/overlay/heatmap PNG,
│   │   │                             CSV, JSON, full PDF report (also logs to History).
│   │   ├── history_view.py            Table of past analyses from the database, with delete.
│   │   ├── settings_view.py           Editable form for every value in `config/settings.json`.
│   │   ├── about_view.py              Static project/course description page.
│   │   ├── widgets.py                 Shared building blocks: `ImagePanel`, `StatCard`
│   │   │                             (with animated count-up), `SectionPanel`.
│   │   ├── workflow.py                The 5-step animated status tracker used on Dashboard.
│   │   └── charts.py                  Thin re-export of the chart canvases so UI code can
│   │                                 `from app.ui.charts import ...` — the real
│   │                                 implementation lives in `app/visualization/charts.py`.
│   │
│   ├── visualization/                Rendering logic that isn't tied to one specific page
│   │   ├── charts.py                   Matplotlib canvases: training-loss line chart,
│   │   │                             change-distribution donut, confusion matrix.
│   │   ├── image_viewer.py             `ZoomableGraphicsView` / `ZoomableImagePanel` —
│   │   │                             mouse-wheel zoom, drag-pan, fit/reset buttons.
│   │   ├── comparison.py               `ComparisonSlider` — the draggable before/after
│   │   │                             divider widget.
│   │   ├── overlays.py                 `build_overlay()` — blends the change mask onto the
│   │   │                             after-image at a given opacity.
│   │   ├── heatmap.py                  `probability_to_heatmap()` — converts the raw
│   │   │                             probability map into a colored heatmap image.
│   │   └── activation_maps.py          `compose_grid()` — helper to tile many feature maps
│   │                                 into one image (available for custom exports).
│   │
│   ├── models/                       The neural network itself
│   │   ├── unet.py                     Lightweight U-Net architecture (encoder/decoder,
│   │   │                             skip connections, 6-channel before+after input).
│   │   ├── losses.py                   Binary cross-entropy + Dice combined loss.
│   │   ├── metrics.py                  IoU/Dice Keras metrics, confusion-matrix counting,
│   │   │                             and the Accuracy/Precision/Recall/F1/IoU/Dice formulas.
│   │   ├── model_manager.py            Builds, compiles, saves, loads the model and its
│   │   │                             `model_metadata.json`; used everywhere a page needs
│   │   │                             "the current model."
│   │   └── activation_extractor.py     Lists convolution layers and extracts their
│   │                                 feature-map activations for a given input.
│   │
│   ├── preprocessing/                Turning raw images into model-ready tensors
│   │   ├── image_loader.py             Safe image loading (handles non-ASCII paths) and
│   │   │                             metadata extraction (dimensions, size, format).
│   │   ├── image_validator.py          Checks a file exists, opens, isn't corrupted/empty/
│   │   │                             oversized, and that a before/after pair matches.
│   │   ├── image_registration.py       ORB feature matching + homography to align a
│   │   │                             misaligned after-image onto the before-image.
│   │   ├── preprocessing.py            Resize-to-match, RGB conversion, normalization,
│   │   │                             concatenation into the 6-channel model input.
│   │   └── augmentation.py             Flips/rotations/brightness/contrast applied
│   │                                 consistently across before/after/mask during training.
│   │
│   ├── detection/                    Turning a model prediction into a real answer
│   │   ├── inference.py                Runs the full predict pipeline (align, preprocess,
│   │   │                             predict, clean, analyze) and times every stage.
│   │   ├── postprocessing.py           Thresholding, morphological open/close, small-object
│   │   │                             removal on the raw probability map.
│   │   ├── change_calculator.py        Change-pixel counting, change %, severity label.
│   │   └── region_analysis.py          Connected-component analysis: per-region area,
│   │                                 bounding box, centroid, relative area.
│   │
│   ├── training/                     Everything used only while training
│   │   ├── dataset_loader.py           Builds a `tf.data` pipeline from matched dataset
│   │   │                             triplets, with optional augmentation and shuffling.
│   │   ├── data_validation.py          Checks a dataset has enough matched samples before
│   │   │                             training starts, and figures out where validation
│   │   │                             data should come from.
│   │   ├── trainer.py                  Orchestrates one full training run: builds the
│   │   │                             model, trains, evaluates fit, saves checkpoints,
│   │   │                             writes to the database and to `training_history.py`.
│   │   ├── callbacks.py                Keras callbacks: checkpointing (best + latest),
│   │   │                             early stopping, TensorBoard logging, live progress.
│   │   └── training_history.py         Saves each run's full history/config as a JSON file
│   │                                 under `logs/training_history/`, independent of the
│   │                                 SQLite database, as a second, file-based record.
│   │
│   ├── dataset/                      Getting a real dataset onto disk
│   │   ├── dataset_manager.py          Reads/writes the configured dataset path, runs
│   │   │                             validation, resolves before/after/mask file paths.
│   │   ├── dataset_validator.py        Scans a folder structure and reports matched/missing
│   │   │                             before/after/mask counts per split.
│   │   ├── dataset_downloader.py       Generic HTTPS zip/tar downloader with progress and
│   │   │                             safe (path-traversal-proof) extraction — used for any
│   │   │                             dataset with a direct download URL.
│   │   ├── dataset_extractor.py        The safe zip/tar extraction logic itself, shared by
│   │   │                             `dataset_downloader.py`.
│   │   └── hf_downloader.py            The default, fully-automatic path: streams a dataset
│   │                                 from Hugging Face, matches its column names to
│   │                                 before/after/mask regardless of naming convention,
│   │                                 resizes, and writes it straight into the required
│   │                                 folder structure with sample caps applied.
│   │
│   ├── database/
│   │   └── database.py                 SQLite schema and all read/write operations for
│   │                                 `analyses`, `training_runs`, and dashboard stats.
│   │
│   ├── reports/                      Turning a result into a file you can hand someone
│   │   ├── pdf_report.py               Builds the full PDF report with ReportLab.
│   │   ├── csv_export.py               Writes the region table to CSV.
│   │   └── json_export.py              Writes metadata + metrics + regions to JSON.
│   │
│   ├── workers/                      Background threads so the UI never freezes
│   │   ├── training_worker.py          Runs `trainer.py` on a `QThread`, emits epoch
│   │   │                             progress signals back to the Training page.
│   │   ├── inference_worker.py         Runs `detection/inference.py` on a `QThread`.
│   │   ├── download_worker.py          Runs the generic URL-based dataset download.
│   │   └── hf_dataset_worker.py        Runs the Hugging Face dataset download.
│   │
│   └── utils/                        Small helpers used across the whole app
│       ├── config.py                   Loads/saves `config/settings.json` and
│       │                             `config/datasets.json`; the single source of truth
│       │                             for every tunable value.
│       ├── logger.py                   Python logging setup, writes `logs/application.log`,
│       │                             and broadcasts log lines to the Dashboard's live
│       │                             System Logs panel.
│       ├── helpers.py                  Small pure functions: file sizes, timestamps,
│       │                             severity labeling, overfitting/underfitting analysis.
│       ├── theme.py                    All colors and the app-wide Qt stylesheet
│       │                             (dark navy/blue/purple theme, no icons).
│       ├── animations.py               Fade-in transitions, animated progress bars, and
│       │                             the count-up number animator used on Dashboard cards.
│       └── validators.py               Input validation for Settings page fields (image
│                                     size, batch size, epochs, learning rate, threshold,
│                                     min region size, folder paths).
│
├── tests/                           Automated tests (pytest) — 27 tests, all real,
│   │                                against synthetic before/after/mask fixtures
│   ├── conftest.py                    Shared fixtures: `synthetic_pair`, `synthetic_dataset`.
│   ├── test_preprocessing.py          Validation, resizing, tensor shape, augmentation.
│   ├── test_registration.py           ORB alignment doesn't crash and returns sane output.
│   ├── test_model.py                  U-Net builds, predicts in [0,1], losses compute.
│   ├── test_detection.py              Thresholding, small-object removal, change stats,
│   │                                 region analysis, overlay blending.
│   ├── test_metrics.py                Confusion-matrix counting and the Accuracy/
│   │                                 Precision/Recall/F1/IoU/Dice formulas.
│   ├── test_dataset.py                Dataset folder validation across splits.
│   └── test_exports.py                CSV, JSON, and PDF report generation produce
│                                     real, non-empty files.
│
├── docs/                             Short supplementary notes (README covers the rest)
│   ├── architecture.md                One-paragraph description of the U-Net design.
│   ├── dataset.md                     The required folder/filename format, restated.
│   ├── training.md                    The training workflow, restated.
│   └── usage.md                       The page-by-page usage flow, restated.
│
├── dataset/                (runtime) Your before/after/mask images live here after
│   ├── train/{before,after,mask}/       Dataset Manager download or manual placement.
│   ├── validation/{before,after,mask}/  Starts empty (just `.gitkeep` placeholders).
│   └── test/{before,after,mask}/
│
├── models/                 (runtime) `best_model.keras`, `latest_model.keras`, and
│                                     `model_metadata.json` are written here after training.
│
├── database/                (runtime) `deepsat.db` — created automatically on first run.
│
├── logs/                    (runtime)
│   ├── application.log                Full application log (Python `logging` output).
│   ├── tensorboard/                    One folder per training run, for `tensorboard --logdir`.
│   └── training_history/               One JSON file per training run (see `training_history.py`).
│
└── results/                 (runtime) Everything you export from the app lands here:
    ├── masks/, overlays/, heatmaps/      PNGs from Report Generator.
    ├── activation_maps/                  PNGs from the Activation Maps page's Save button.
    ├── charts/                           Reserved for saved chart images (not yet wired to
    │                                     a button — see "Known Gaps" below).
    ├── reports/                          PDF reports.
    └── exports/                          CSV/JSON exports.
```

## INT422 Course Mapping

| Topic | Where it appears |
|---|---|
| TensorFlow tensors / variables / optimizers | `app/models/unet.py`, `app/training/trainer.py` |
| Keras layers, models, save/load | `app/models/unet.py`, `app/models/model_manager.py` |
| CNN / convolution / pooling / encoder-decoder | Lightweight U-Net architecture |
| Image segmentation | Core change-detection task |
| Data augmentation | `app/preprocessing/augmentation.py` |
| TensorBoard | `app/training/callbacks.py`, `logs/tensorboard/` |
| Overfitting / underfitting analysis | `app/utils/helpers.fit_analysis`, Training page |
| Activation map visualization | `app/models/activation_extractor.py`, Activation Maps page |
| Hyperparameter tuning | Training/Settings pages (image size, batch size, epochs, LR, threshold) |

## Known Gaps — what's honestly not in here

To keep everything above genuinely working rather than half-built, the
following optional spec items were deliberately left out. None of them are
required for the core "detect and analyze change between two satellite
images" goal, and the app runs correctly and completely without them:

- **First-run welcome wizard** — the app opens straight to the Dashboard
  rather than a guided "download dataset / load model / demo" first-launch
  screen. Dataset Manager and Model Information cover the same ground
  manually.
- **Demo mode / sample data auto-load** — there's no built-in one-click demo
  pair; you supply your own before/after images (or use a couple of test
  images from your downloaded dataset).
- **Hyperparameter experiment comparison table** — you can change
  image size/batch size/epochs/learning rate and retrain, but there's no
  page that stores and compares multiple configurations side by side.
- **Transfer-learning comparison experiment** (Model A vs. Model B with a
  pretrained encoder) — only the single lightweight U-Net is implemented,
  as the spec marked this optional given 8 GB RAM / no GPU.
- **`results/charts/` export button** — the folder is created and reserved,
  but no page currently has a "save this chart as an image" button (you can
  screenshot the training/confusion-matrix charts in the meantime).
- **Animated background grid/scan-line effect** — the dashboard uses the
  specified dark navy/purple/cyan theme and panel styling, but not the
  optional decorative animated background texture.

If you want any of these added, ask — they're all straightforward additions
on top of the existing architecture, not redesigns.

## Dataset Download Requirements

Automated dataset download needs the `datasets` and `huggingface_hub`
packages (already in `requirements.txt`) and an internet connection. The
download itself uses Hugging Face's official streaming API — files are
fetched, resized if needed, converted to the required folder structure, and
validated, all in the background without freezing the UI. You can cancel a
download in progress from the Dataset Manager page.

## Troubleshooting

- **"MODEL STATUS: NOT TRAINED"** — train a model on the Training page, or load
  an existing `.keras` file from Model Information.
- **"No matching training samples found"** — check the Dataset Manager
  validation report; filenames must match across `before/after/mask`.
- **Slow training** — reduce image size (e.g. 128) and batch size (2 or 4);
  this is expected on integrated-graphics / CPU-only hardware.
- **Different image dimensions on upload** — the app offers to resize
  automatically; this does not require re-running preprocessing manually.

## Important Note on Accuracy

Model performance (IoU, Dice, F1, etc.) is entirely a function of the dataset
used for training and how long it is trained — it is not fixed or guaranteed.
The application never fabricates these numbers: all displayed metrics come
from actual evaluation against real data.
