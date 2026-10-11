import time
import numpy as np
from app.preprocessing.preprocessing import preprocess_pair, resize_to_match
from app.preprocessing.image_registration import align_images
from app.detection.postprocessing import clean_mask
from app.detection.change_calculator import compute_change_stats
from app.detection.region_analysis import analyze_regions
from app.visualization.overlays import build_overlay
from app.utils.logger import log


class InferenceResult:
    def __init__(self):
        self.before_display = None
        self.after_display = None
        self.probability_map = None
        self.binary_mask = None
        self.overlay = None
        self.regions = []
        self.change_stats = {}
        self.timings = {}
        self.alignment_ok = None
        self.alignment_message = ""


def run_inference(model, before_bgr, after_bgr, image_size=256, threshold=0.5,
                   min_region_size=100, do_alignment=True):
    result = InferenceResult()
    t0 = time.time()

    if before_bgr.shape[:2] != after_bgr.shape[:2]:
        before_bgr, after_bgr = resize_to_match(before_bgr, after_bgr)

    if do_alignment:
        t_align = time.time()
        aligned_after, ok, msg = align_images(before_bgr, after_bgr)
        result.alignment_ok = ok
        result.alignment_message = msg
        if ok:
            after_bgr = aligned_after
        result.timings["alignment_time"] = round(time.time() - t_align, 3)

    t_pre = time.time()
    tensor, before_r, after_r = preprocess_pair(before_bgr, after_bgr, image_size)
    result.before_display = before_r
    result.after_display = after_r
    result.timings["preprocessing_time"] = round(time.time() - t_pre, 3)

    t_inf = time.time()
    prediction = model.predict(tensor, verbose=0)
    prob_map = prediction[0, :, :, 0]
    result.probability_map = prob_map
    result.timings["inference_time"] = round(time.time() - t_inf, 3)

    t_post = time.time()
    binary_mask = clean_mask(prob_map, threshold=threshold, min_size=min_region_size)
    result.binary_mask = binary_mask
    result.overlay = build_overlay(after_r, binary_mask)
    result.timings["postprocessing_time"] = round(time.time() - t_post, 3)

    result.regions = analyze_regions(binary_mask)
    result.change_stats = compute_change_stats(binary_mask)
    result.change_stats["confidence"] = float(np.mean(prob_map[binary_mask > 0])) if np.any(binary_mask) else 0.0

    result.timings["total_time"] = round(time.time() - t0, 3)
    log.info("Prediction completed")
    return result
