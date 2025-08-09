"""
Temporary module to include all the effects
and modifications we can apply on a single
video frame.
"""
import numpy as np
import cv2


class FrameEffect:
    """
    Class to wrap the effects we can apply to a
    video single frame.
    """

    @staticmethod
    def grayscale(
        frame: 'np.ndarray'
    ) -> 'np.ndarray':
        """
        Transform the frame to a gray scale.
        """
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    @staticmethod
    def invert(
        frame: 'np.ndarray'
    ) -> 'np.ndarray':
        """
        Invert the colors of the frame.
        """
        return 255 - frame
    
    @staticmethod
    def blur(
        frame: 'np.ndarray'
    ) -> 'np.ndarray':
        """
        Apply a blur on the frame.
        """
        # TODO: This can be customized
        return cv2.GaussianBlur(frame, (15, 15), 0)
    
    @staticmethod
    def sepia(
        frame: 'np.ndarray'
    ) -> 'np.ndarray':
        """
        Transform the frame to a sepia color frame.
        """
        sepia_filter = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ])
        sepia = cv2.transform(frame, sepia_filter)

        return np.clip(sepia, 0, 255).astype(np.uint8)
    
    @staticmethod
    def canny(
        frame: 'np.ndarray'
    ) -> 'np.ndarray':
        """
        Detect the borders of the frame.
        """
        return cv2.Canny(frame, 100, 200)

    @staticmethod
    def zoom_at(
        frame: 'np.ndarray',
        zoom: float,
        center: tuple[int, int] = None
    ):
        """
        Apply the provided 'zoom' to the given 'frame',
        using the 'center' also provided as the center
        position within the 'frame'. Any missing pixel
        will be fulfilled with a black one.
        """
        h, w = frame.shape[:2]
        center = (
            (w // 2, h // 2)
            if center is None else
            center
        )
        out_w, out_h = w, h

        zoomed = cv2.resize(frame, None, fx = zoom, fy = zoom, interpolation = cv2.INTER_LINEAR)
        zh, zw = zoomed.shape[:2]

        # Focus on the center
        x_center, y_center = center
        new_x_center = int(x_center * zoom)
        new_y_center = int(y_center * zoom)

        # Cut where we need
        x1 = new_x_center - out_w // 2
        y1 = new_y_center - out_h // 2
        x2 = x1 + out_w
        y2 = y1 + out_h

        # Fulfill with black background
        # output = np.zeros((out_h, out_w, 3), dtype = np.uint8)
        # Fulfil with white blackground
        output = np.full((out_h, out_w, 3), 255, dtype = np.uint8)

        # Zoomed coordinates we need
        x1_src = max(0, x1)
        y1_src = max(0, y1)
        x2_src = min(zw, x2)
        y2_src = min(zh, y2)

        # Coordinates but in output
        x1_dst = x1_src - x1
        y1_dst = y1_src - y1
        x2_dst = x1_dst + (x2_src - x1_src)
        y2_dst = y1_dst + (y2_src - y1_src)

        output[y1_dst:y2_dst, x1_dst:x2_dst] = zoomed[y1_src:y2_src, x1_src:x2_src]

        return output