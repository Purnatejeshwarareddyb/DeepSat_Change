import cv2
import numpy as np


def align_images(before_bgr, after_bgr, max_features=1000, good_match_percent=0.2):
    try:
        gray_before = cv2.cvtColor(before_bgr, cv2.COLOR_BGR2GRAY)
        gray_after = cv2.cvtColor(after_bgr, cv2.COLOR_BGR2GRAY)

        orb = cv2.ORB_create(max_features)
        kp1, des1 = orb.detectAndCompute(gray_before, None)
        kp2, des2 = orb.detectAndCompute(gray_after, None)

        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            return after_bgr, False, "Not enough features detected for alignment."

        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(des1, des2)
        matches = sorted(matches, key=lambda m: m.distance)

        num_good = max(4, int(len(matches) * good_match_percent))
        matches = matches[:num_good]

        if len(matches) < 4:
            return after_bgr, False, "Not enough matching features for alignment."

        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)
        for i, m in enumerate(matches):
            points1[i, :] = kp1[m.queryIdx].pt
            points2[i, :] = kp2[m.trainIdx].pt

        h_matrix, mask = cv2.findHomography(points2, points1, cv2.RANSAC)
        if h_matrix is None:
            return after_bgr, False, "Homography estimation failed."

        height, width = before_bgr.shape[:2]
        aligned = cv2.warpPerspective(after_bgr, h_matrix, (width, height))
        return aligned, True, "Alignment succeeded."
    except Exception as exc:
        return after_bgr, False, f"Alignment failed: {exc}"
