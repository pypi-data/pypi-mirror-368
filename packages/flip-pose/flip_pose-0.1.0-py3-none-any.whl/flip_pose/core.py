import cv2
import numpy as np
from typing import List, Tuple, Optional

def flip_pose_frame(
    frame: np.ndarray,
    keypoints: Optional[List[Tuple[float, float]]] = None,
    connections: Optional[List[Tuple[int, int]]] = None,
    flip_points: bool = False
):
    """
    Flip a video frame horizontally, optionally flipping keypoints & connections.

    Args:
        frame (np.ndarray): Input BGR image.
        keypoints: List of (x, y) pixel coordinates.
        connections: List of (start_idx, end_idx) pairs.
        flip_points: False = only flip image, True = flip image and points.

    Returns:
        flipped_frame, flipped_keypoints
    """
    flipped_frame = cv2.flip(frame, 1)

    if keypoints is None:
        return flipped_frame, None

    h, w = frame.shape[:2]
    if flip_points:
        flipped_keypoints = [(w - x, y) for (x, y) in keypoints]
    else:
        flipped_keypoints = keypoints

    # Draw connections
    if connections:
        for start, end in connections:
            cv2.line(flipped_frame,
                     (int(flipped_keypoints[start][0]), int(flipped_keypoints[start][1])),
                     (int(flipped_keypoints[end][0]), int(flipped_keypoints[end][1])),
                     (0, 255, 0), 2)

    # Draw points
    for (x, y) in flipped_keypoints:
        cv2.circle(flipped_frame, (int(x), int(y)), 3, (0, 0, 255), -1)

    return flipped_frame, flipped_keypoints
