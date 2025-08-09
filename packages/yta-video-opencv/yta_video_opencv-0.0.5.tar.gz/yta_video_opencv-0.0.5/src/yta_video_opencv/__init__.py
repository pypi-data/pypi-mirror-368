"""
Module to include video handling with the
OpenCV library.

A video has its original size and properties,
but when placed on a canvas to be modified
and with other videos, the position is 
related to that canvas size, not its original.
"""
from yta_video_opencv.writer import OpenCVWriter
from yta_video_opencv.frame import Frame
from yta_video_opencv.utils import OpencvUtils
from yta_general_utils.math.progression import Progression
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from yta_validation.number import NumberValidator
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
# TODO: This 'yta_random' is for manual testing
from yta_random import Random
# TODO: This timer has to be removed soon...
from yta_timer import Timer
from typing import Union
from contextlib import nullcontext

import numpy as np
import cv2


SMALL_AMOUNT_TO_FIX = 0.000001
"""
A small amount to fix to the video frame
time moments 't' to fix errors related to
decimal values.
"""

class _Frames:
    """
    *For internal use only*

    Class to simplify the way we handle the video frames.
    """

    @property
    def fps(
        self
    ) -> float:
        return self.video_instance.fps
    
    @property
    def number_of_frames(
        self
    ) -> int:
        return self.video_instance.number_of_frames
    
    @property
    def speed(
        self
    ) -> list[float]:
        """
        The speed values we want to apply for each
        frame of the video.
        """
        return self.video_instance.speed

    @property
    def rotation_values(
        self
    ) -> list[float]:
        """
        The list of the rotation values for each of
        the video frames, ordered from first to last
        frame, by indexes.
        """
        return self.video_instance.rotation_values
    
    @property
    def resize_values(
        self
    ) -> list[float]:
        """
        The list of the resize values for each of the
        video frames, ordered from first to last frame,
        by indexes.
        """
        return self.video_instance.resize_values
    
    @property
    def position_values(
        self
    ) -> list[float]:
        """
        The list of the position values for each of the
        video frames, ordered from first to last frame,
        by indexes.
        """
        return self.video_instance.position_values
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The original size of the video.
        """
        return self.video_instance.size

    @property
    def width(
        self
    ) -> int:
        """
        The original width of the video.
        """
        return self.video_instance.width
    
    @property
    def height(
        self
    ) -> int:
        """
        The original height of the video.
        """
        return self.video_instance.height
    
    # TODO: What if we want to subclip (?)
    @property
    def indexes_with_speed_applied(
        self
    ) -> list[int]:
        """
        Get the list of the frame indexes we need to render
        to fit the speed factor values holded in the
        'speed' parameter.

        This was previously an iterator, but I think it is
        not necessary.

        Use it as a list doing this:
        - `list(frame_indexes_with_speed_applied(speed, self.number_of_frames))`
        """
        indexes = []

        index = 0.0
        while index < self.number_of_frames:
            # This below is to make a list
            indexes.append(int(index))
            # This below is to make an iterator, but why?
            # yield int(index)
            index += self.speed[int(index)]

        return indexes
    
    def __init__(
        self,
        video: 'Video'
    ):
        self.video_instance: 'Video' = video
        """
        The video this frames belong to.
        """

    def go_to(
        self,
        frame_index: int
    ) -> cv2.VideoCapture:
        """
        Move the opencv reader to the 'frame_index' frame
        position to start reading from there.
        """
        return OpencvUtils.go_to_frame(
            reader = self.video_instance._video,
            frame_index = frame_index
        )

    def get(
        self,
        frame_index_or_t: Union[float, int]
    ) -> 'np.ndarray':
        """
        Get the frame with the given 'frame_index_or_t'
        as a numpy array, or raise an exception if not
        possible.

        This frame is the original frame with no 
        modifications, as it is read from the source.

        This method can be used to extract one single 
        frame, but is not a good option in terms of
        performance if going to read more than one.

        The 'frame_index_or_t' must be:
        - `int` if frame 'index' provided
        - `float` if frame time moment 't' provided
        """
        ParameterValidator.validate_mandatory_positive_number('frame_index_or_t', frame_index_or_t, do_include_zero = True)

        frame_index = (
            int((frame_index_or_t + SMALL_AMOUNT_TO_FIX) * self.fps)
            if NumberValidator.is_float(frame_index_or_t) else
            int(frame_index_or_t)
        )

        ParameterValidator.validate_mandatory_number_between('frame_index', frame_index, 0, self.number_of_frames - 1)

        return OpencvUtils.read_frame(
            reader = self.video_instance._video,
            frame_index = frame_index,
            do_rollback = True
        )

    def iterate(
        self,
        frame_indexes_or_ts: Union[list[int], list[float], None]
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

        Each iteration returns a tuple containing
        the frame as a numpy array, and the frame 
        index as an int.
        """
        if (
            not PythonValidator.is_list_of_int(frame_indexes_or_ts) and
            not PythonValidator.is_list_of_float(frame_indexes_or_ts) and
            frame_indexes_or_ts is not None
        ):
            raise Exception('The "frame_indexes_or_ts" parameter must be a list of int or float numbers.')
        
        # By default, we iterate over all of them if None
        frame_indexes_or_ts = (
            list(range(self.number_of_frames))
            if frame_indexes_or_ts is None else
            frame_indexes_or_ts
        )
        
        # Force frame indexes
        frame_indexes = [
            int((frame_index_or_t + SMALL_AMOUNT_TO_FIX) * self.fps)
            if NumberValidator.is_float(frame_index_or_t) else
            int(frame_index_or_t)
            for frame_index_or_t in frame_indexes_or_ts
        ]
        
        return OpencvUtils.iterate_frames_by_indexes(
            reader = self.video_instance._video,
            frame_indexes = frame_indexes
        )
    
    def show(
        self,
        frame_index_or_t: Union[float, int]
    ) -> None:
        """
        Show the frame with the given 'frame_index_or_t'
        on a display, or raise an exception if not
        possible.

        The 'frame_index_or_t' must be:
        - `int` if frame 'index' provided
        - `float` if frame time moment 't' provided
        """
        OpencvUtils.images.show(self.get(frame_index_or_t))

    def process(
        self,
        frame: 'np.ndarray',
        frame_index: int
    ):
        """
        Apply the modifications to the provided 'frame'
        which has the also given 'frame_index'.

        The 'frame_index' is to be able to autodetect
        the specific modifications for that frame.
        """
        frame: Frame = Frame(frame)

        random_effects = [
            frame.effects.blur,
            frame.effects.canny,
            frame.effects.grayscale,
            frame.effects.invert,
            frame.effects.sepia
        ]

        # Frame content changes below
        frame = random_effects[Random.int_between(0, len(random_effects) - 1)]()

        # Basic changes below
        frame = frame.rotate(self.rotation_values[frame_index])
        frame = frame.resize_factor(self.resize_values[frame_index])
        frame = frame.move(self.position_values[frame_index])

        # Aditional changes (?)

        return frame.frame

# TODO: We fake, by now, the Canvas size, but
# this has to be passed when instantiated,
# from the canvas handler that will include
# the edited videos...
CANVAS_SIZE = (1920, 1080)

class Video:
    """
    Class to wrap the information about a video
    by using the opencv library.
    """

    @property
    def fps(
        self
    ) -> float:
        if not hasattr(self, '_fps'):
            self._fps = self._video.get(cv2.CAP_PROP_FPS)

        return self._fps
    
    @property
    def number_of_frames(
        self
    ) -> int:
        if not hasattr(self, '_number_of_frames'):
            self._number_of_frames = int(self._video.get(cv2.CAP_PROP_FRAME_COUNT))

        return self._number_of_frames
    
    @property
    def duration(
        self
    ) -> float:
        if not hasattr(self, '_duration'):
            self._duration = self.number_of_frames / self.fps

        return self._duration
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The original size of the video.
        """
        if not hasattr(self, '_size'):
            self._size = (
                int(self._video.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self._video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )

        return self._size

    @property
    def width(
        self
    ) -> int:
        """
        The original width of the video.
        """
        return self.size[0]
    
    @property
    def height(
        self
    ) -> int:
        """
        The original height of the video.
        """
        return self.size[1]
    
    def __init__(
        self,
        # TODO: Can I receive frames as numpys (?)
        filename: str
    ):
        self._video = cv2.VideoCapture(filename)

        if not self._video.isOpened():
            raise IOError('Unable to open/read the video.')
        
        self.frames = _Frames(self)
        """
        Shortcut to the frames handler.
        """
        self.rotation_values = [0] * self.number_of_frames
        """
        The list of the rotation values for each of
        the video frames, ordered from first to last
        frame, by indexes.
        """
        self.resize_values = [1] * self.number_of_frames
        """
        The list of the resize values for each of the
        video frames, ordered from first to last frame,
        by indexes.
        """
        self.position_values = [(DEFAULT_SCENE_SIZE[0] / 2, DEFAULT_SCENE_SIZE[1] / 2)] * self.number_of_frames
        """
        The list of the position values for each of
        the video frames, ordered from first to last
        frame, by indexes.
        """
        self.speed = [1.0] * self.number_of_frames
        """
        The speed values we want to apply for each
        frame of the video.
        """

    def __del__(
        self
    ):
        self._video.release()

    def _process(
        self,
        t_start: float = 0.0,
        t_end: float = 999999.9,
        do_debug: bool = False
    ):
        """
        Process all the frames, as an iterator, and
        return each of them once it's been processed
        and all the changes have been applied.
        """
        # TODO: This is hardcoded for manual testing
        self.rotation_values = Progression(0, 360, self.number_of_frames).values
        self.resize_values = Progression(0.2, 0.4, self.number_of_frames).values
        self.position_values = list(zip(
            Progression(700, 800, self.number_of_frames).values,
            Progression(300, 350, self.number_of_frames).values
        ))

        # Get start and end frame indexes
        # TODO: Set this as properties
        start_frame_index = int((t_start + SMALL_AMOUNT_TO_FIX) * self.fps)
        end_frame_index = min(
            int((t_end + SMALL_AMOUNT_TO_FIX) * self.fps),
            self.number_of_frames
        )

        context = (
            Timer()
            if do_debug else
            nullcontext()
        )
        
        with context:
            for frame, frame_index in self.frames.iterate(self.frames.indexes_with_speed_applied):
                # Skip frames not in the range requested
                if (
                    frame_index < start_frame_index or
                    frame_index >= end_frame_index
                ):
                    continue

                specific_context = (
                    Timer(True)
                    if do_debug else
                    nullcontext()
                )
                
                with specific_context as timer:
                    frame = self.frames.process(
                        frame = frame,
                        frame_index =  frame_index
                    )

                if do_debug:
                    print(f'Frame {str(frame_index)} - {timer.time_elapsed_str}')

                yield(frame)
                # output_writer.write(frame)
        
    def save_as(
        self,
        output_filename: str,
        t_start: float = 0.0,
        t_end: float = 999999.9,
        do_debug: bool = False
    ):
        """
        Renderiza cambiando la velocidad sin precargar todo (usa seek por frames).
        Más seguro en memoria, pero puede ser más lento por seeks frecuentes.
        """
        output_writer = OpenCVWriter.auto_detected(self.fps, self.size, output_filename)
        
        for frame in self._process(t_start, t_end, do_debug):
            output_writer.write(frame)

        output_writer.release()
        self._video.release()

    def __del__(
        self
    ):
        # Free resources
        self._video.release()

def main():
    test_input_video_filename = 'test_files/test_1.mp4'
    test_output_video_filename = 'test_files/output.mp4'

    video = Video(test_input_video_filename)
    #video.frames.show(3.3)
    #video.process_and_save(test_output_video_filename, 1.0, 1.5, do_debug = True)
    video.save_as(test_output_video_filename, do_debug = True)

if __name__ == '__main__':
    main()