"""
The opencv reader has a pointer that is the
last frame that was read, and can be obtained
with the 'reader.get(cv2.CAP_PROP_POS_FRAMES)'
property. If you use the read method, which is
'ret, frame = reader.read()', it will move to
the next frame to read it. So, as you can see,
the pointer is not pointing to the frame that
will be read but to the previous one.
"""
from yta_validation.parameter import ParameterValidator
from typing import Union

import numpy as np
import cv2


class _Image:
    """
    *For internal use only*

    Utils related to image management.
    """

    @staticmethod
    def show(
        image: 'np.ndarray'
    ) -> None:
        """
        Show the 'image' provided on a display.
        """
        cv2.imshow('video_display', cv2.resize(image, (int(image.shape[1] / 2), int(image.shape[0] / 2))))
        cv2.waitKey(0)

class OpencvUtils:
    """
    Class to wrap some utils related to video 
    and video frame management.
    """

    images: _Image = _Image
    """
    Shortcut to the image utils.
    """