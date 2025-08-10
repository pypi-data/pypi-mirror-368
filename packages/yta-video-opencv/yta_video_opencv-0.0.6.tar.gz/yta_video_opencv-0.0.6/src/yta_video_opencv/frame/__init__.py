"""
When handling a frame that has been read 
with the opencv library, the first value
is the height and the second is the width.
"""
from yta_video_opencv.canvas import Canvas
from yta_video_opencv.frame.effects import FrameEffect
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from yta_validation.parameter import ParameterValidator
from typing import Union

import numpy as np
import cv2


class _Effects:
    """
    *For internal use only*

    Class to wrap effects that we can apply
    directly to our frames to transform them.

    This class has been created to simplify
    the way we use those effects.

    TODO: Implement all methods in FrameEffect.
    TODO: Careful with those methods that
    modify the frame dimensions and not only 
    the internal values... These are frame
    effects and not video effects.
    """

    @property
    def frame(
        self
    ) -> 'np.ndarray':
        """
        The frame numpy array of the Frame instance
        we are handling.

        This is a shortcut to make the operations
        easier.
        """
        return self._frame_instance.frame
    
    @frame.setter
    def frame(
        self,
        value: 'np.ndarray'
    ) -> None:
        """
        Set the Frame instance frame numpy array.
        """
        self._frame_instance.frame = value

    def __init__(
        self,
        frame: 'Frame'
    ):
        self._frame_instance: 'Frame' = frame
        """
        The frame instance we are handling.
        """

    def grayscale(
        self
    ) -> 'Frame':
        """
        Transform the frame to a gray scale.
        """
        self.frame = FrameEffect.grayscale(self.frame)

        return self._frame_instance

    def invert(
        self
    ) -> 'Frame':
        """
        Invert the colors of the frame.
        """
        self.frame = FrameEffect.invert(self.frame)

        return self._frame_instance
    
    def blur(
        self
    ) -> 'Frame':
        """
        Apply a blur on the frame.
        """
        self.frame = FrameEffect.blur(self.frame)

        return self._frame_instance
    
    def sepia(
        self
    ) -> 'Frame':
        """
        Transform the frame to a sepia color frame.
        """
        self.frame = FrameEffect.sepia(self.frame)

        return self._frame_instance
    
    def canny(
        self
    ) -> 'Frame':
        """
        Detect the borders of the frame.
        """
        self.frame = FrameEffect.canny(self.frame)
        
        return self._frame_instance

class Frame:
    """
    Class to wrap functionality related to a
    video frame to simplify the way we can 
    handle them.

    TODO: If we make a frame fit the canvas,
    the one returned will lose the extra info
    that was out of bounds, so we need to use
    the '.original_frame' to be able to know
    how it was before.
    """

    @property
    def original_size(
        self
    ) -> tuple[int, int]:
       """
       The size of the original frame.
       """
       return (self.original_frame.shape[1], self.original_frame.shape[0])
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the current frame, considering
        the modifications applied on it.
        """
        return (self.frame.shape[1], self.frame.shape[0])

    def __init__(
        self,
        frame: 'np.ndarray'
    ):
        self.original_frame: 'np.ndarray' = frame
        """
        The original frame.
        """
        self.frame: 'np.ndarray' = frame
        """
        The frame, with all the modifications
        applied.
        """
        self.effects: _Effects = _Effects(self)
        """
        Easy effects handler property to apply the
        effects you want calling a single method.

        Any method you use within this property 
        will return this Frame instance to be able
        to call any method again (even effects).
        """

    def resize(
        self,
        size: tuple[int, int]
    ) -> 'Frame':
        """
        Resize the frame to the given 'size'.
        """
        # TODO: Validate 'size'
        self.frame = resize_image(self.frame, size)

        return self
    
    def resize_factor(
        self,
        factor: float
    ) -> 'Frame':
        """
        Resize the frame multiplying its size with
        the given scale 'factor'.
        """
        ParameterValidator.validate_mandatory_number('factor', factor)

        return self.resize(
            size = (
                int(self.size[0] * float(factor)),
                int(self.size[1] * float(factor))
            )
        )
    
    def rotate(
        self,
        angle: float
    ) -> 'Frame':
        """
        Rotate the frame the given 'angle'.
        """
        self.frame = rotate_image(
            image = self.frame,
            angle = angle
        )

        return self

    def move(
        self,
        position: tuple[int, int] = (DEFAULT_SCENE_SIZE[0] / 2, DEFAULT_SCENE_SIZE[1] / 2),
        canvas_size: tuple[int, int] = DEFAULT_SCENE_SIZE
    ) -> 'Frame':
        """
        Put the center of the frame in the given
        'position', within a canvas of the given
        'canvas_size'.

        TODO: I think the movement is not here, because
        its not the frame by itself who moves. Is the 
        whole frame within the canvas. You can rotate and
        resize it, but to move it you have to do it in
        a specific canvas.
        """
        self.frame = place_on_canvas(
            image = self.frame,
            canvas_size = canvas_size,
            position = position
        )

        return self


# Utils below
def place_on_canvas(
    image: 'np.ndarray',
    canvas_size: tuple[int, int] = DEFAULT_SCENE_SIZE,
    position: Union[tuple[int, int], None] = None
) -> 'np.ndarray':
    """
    Place the provided 'image' on a canvas of the
    given 'canvas_size', placing the center of
    the image on the also provided 'position'.
    """
    return Canvas(size = canvas_size).fit_image_at(
        image = image,
        position = position
    )

def scale_image(
    image: 'np.ndarray',
    factor: float = 1.0,
) -> 'np.ndarray':
    """
    Resize the given 'image' by applying the also
    provided 'factor'.
    """
    return resize_image(
        image = image,
        size = (int(image.shape[1] * factor), int(image.shape[0] * factor))
    )

def resize_image(
    image: 'np.ndarray',
    size: tuple[int, int],
) -> 'np.ndarray':
    """
    Resize the given 'image' to the also provided
    'size'.
    """
    # TODO: What about aspect ratio (?)
    return cv2.resize(
        src = image,
        dsize = (int(size[0]), int(size[1])),
        interpolation = cv2.INTER_LINEAR
    )

def rotate_image(
    image: 'np.ndarray',
    angle: float
) -> 'np.ndarray':
    """
    Rotate the 'image' provided the also given
    'angle'. The image dimensions can be different
    from the original one.
    """
    size = (image.shape[1], image.shape[0])

    # Rotate without cropping (pad the image if needed
    center = (size[0] // 2, size[1] // 2)

    # TODO: Maybe we can make the 'center' adjustable
    rotation_matrix = cv2.getRotationMatrix2D(
        center = center,
        angle = float(angle),
        scale = 1.0
    )

    # Rotated image bounding box size
    cos = abs(rotation_matrix[0, 0])
    sin = abs(rotation_matrix[0, 1])
    new_w = int((size[0] * cos) + (size[1] * sin))
    new_h = int((size[0] * sin) + (size[1] * cos))

    # Adjust the matriz to center the image
    rotation_matrix[0, 2] += (new_w / 2) - center[0]
    rotation_matrix[1, 2] += (new_h / 2) - center[1]

    return cv2.warpAffine(
        src = image,
        M = rotation_matrix,
        dsize = (new_w, new_h),
        borderValue = (0, 0, 0)
    )

# These below are not needed but...
# def rotate_image_scipy(
#     image: 'np.ndarray',
#     angle: float
# ) -> 'np.ndarray':
#     """
#     Rotate, but with scipy. This is very slow
#     (3.0s) and result is not good.
#     """
#     # TODO: Remove or add 'requires_dependency'
#     from scipy.ndimage import rotate

#     return rotate(
#         input = image,
#         angle = angle
#     )

# def rotate_imutils(
#     image: 'np.ndarray',
#     angle: float
# ) -> 'np.ndarray':
#     """
#     Rotate, but with imutils. This is fast (0.05s) but
#     the result is not very good.
#     """
#     # TODO: Remove or add 'requires_dependency'
#     from imutils import rotate

#     return rotate(image, angle)