"""
The canvas in which we position the different
frames to render them as a final video.
"""
from yta_colors import Colors, Color
from yta_validation.parameter import ParameterValidator
from typing import Union

import numpy as np


class Canvas:
    """
    Class to represent the camvas in which the
    videos are positioned and everything is
    shown and happening.
    """

    def __init__(
        self,
        color: Color = Colors.BLACK,
        size: tuple[int, int] = (1920, 1080)
    ):
        ParameterValidator.validate_mandatory_instance_of('color', color, Color)
        # TODO: Validate 'size'

        self.color: Color = color
        """
        The color of the background of the canvas,
        that will be visible when the images on it
        are not fitting the size.
        """
        self.size: tuple[int, int] = size
        """
        The size of the canvas.
        """
        self.canvas: 'np.ndarray' = Canvas.get(self.color, self.size)
        """
        The canvas itself as a numpy array. All the
        changes must be done in a copy of this one.
        """

    def fit_image_at(
        self,
        image: 'np.ndarray',
        position: Union[tuple[int, int], None] = None,
    ) -> 'np.ndarray':
        """
        Place the provided 'image' in this canvas with
        the center of the image in the also provided
        'position'. The position, by default, is the
        center of the canvas (if None provided).
        """
        ParameterValidator.validate_mandatory_numpy_array('image', image)
        # TODO: Validate 'position'

        image_size = (image.shape[1], image.shape[0])
        canvas = self.canvas.copy()

        # Calculate the position in which we need to place
        # the center of the image (center by default)
        position = (
            (self.size[0] // 2, self.size[1] // 2)
            if position is None else
            (int(position[0]), int(position[1]))
        )
        x = position[0] - (image_size[0] // 2)
        y = position[1] - (image_size[1] // 2)

        # Fit the image in the canvas
        x1, y1 = max(x, 0), max(y, 0)
        x2, y2 = min(x + image_size[0], self.size[0]), min(y + image_size[1], self.size[1])

        # Region of interest (ROI)
        roi_w = x2 - x1
        roi_h = y2 - y1

        if (
            roi_w > 0 and
            roi_h > 0
        ):
            canvas[y1:y1 + roi_h, x1:x1 + roi_w] = image[y1 - y:y1 - y + roi_h, x1 - x:x1 - x + roi_w]

        return canvas

    # TODO: Maybe move this to helper methods instead (?)
    @staticmethod
    def get(
        color: Color,
        size: tuple[int, int] = (1920, 1080),
    ) -> 'np.ndarray':
        """
        Generate a canvas of the given 'size' with pixels
        of the given 'color'.
        """
        ParameterValidator.validate_mandatory_instance_of('color', color, Color)

        return np.full((size[1], size[0], 3), color.for_opencv, dtype = np.uint8)
    
    @staticmethod
    def default(
        size: tuple[int, int] = (1920, 1080),
    ) -> 'np.ndarray':
        """
        Generate a canvas of the given 'size' with black
        pixels.
        """
        return np.full((size[1], size[0], 3), Colors.BLACK.for_opencv, dtype = np.uint8)