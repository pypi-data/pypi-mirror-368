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

    @staticmethod
    def go_to_frame(
        reader: cv2.VideoCapture,
        frame_index: int
    ) -> cv2.VideoCapture:
        """
        Move the opencv 'reader' to the 'frame_index' frame
        position to start reading from there.
        """
        ParameterValidator.validate_mandatory_instance_of('reader', reader, cv2.VideoCapture)

        reader.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

        return reader

    @staticmethod
    def read_frame(
        reader: cv2.VideoCapture,
        frame_index: Union[None, int] = None,
        do_rollback: bool = False
    ) -> Union['np.ndarray', None]:
        """
        Read the frame at the current frame index or at
        the given 'frame_index' if it is not None. If the
        'do_rollback' parameter is True, the pointer will
        read the current frame but will not move on to 
        the next position.

        This method will return None if no frame available.

        The OpenCV reading process is complex and involves
        decompressing códecs for the different frames. It
        is cheaper to read the frames consecutively and
        discard the ones we don't want than moving to the
        one we need before reading it, and then doing the
        same to the next one.
        """
        ParameterValidator.validate_mandatory_instance_of('reader', reader, cv2.VideoCapture)

        current_frame_index = reader.get(cv2.CAP_PROP_POS_FRAMES)

        # This will move the pointer to the next frame
        if frame_index is not None:
            OpencvUtils.go_to_frame(reader, frame_index)

        ret, frame = reader.read()

        if do_rollback:
            OpencvUtils.go_to_frame(reader, current_frame_index)

        return (
            None
            if not ret else
            frame
        )
    
    @staticmethod
    def iterate_frames_by_indexes(
        reader: cv2.VideoCapture,
        frame_indexes: list[int]
        # TODO: What is the return type (?)
    ):
        """
        Iterator that iterates over all the video
        frames, reading them as a sequence, 
        skipping the ones we don't need, using
        cache of the previous one if needed to
        repeat (maybe due to slowing down the
        video).

        This is supposed to be the best method to
        read frames by tehri indexes, in terms of
        performance.

        Return a tuple containing the frame as a
        numpy array, and the frame index as an int.
        """
        last_index_to_read = max(frame_indexes)
        frame_indexes = set(frame_indexes)

        # Hold information about repeated ones
        last_frame_read_index = -1
        last_frame_read = None

        # Try to read the smaller amount possible
        current_index = min(frame_indexes)
        OpencvUtils.go_to_frame(reader, current_index)

        while current_index <= last_index_to_read:
            if current_index == last_frame_read_index:
                frame = last_frame_read
                # Go to next frame but less expensive
                reader.grab()
            else:
                ret, frame = reader.read()
                # TODO: This below should not happen...
                if not ret:
                    break

            if current_index in frame_indexes:
                yield frame, current_index

            last_frame_read_index = current_index
            last_frame_read = frame
            current_index += 1

    