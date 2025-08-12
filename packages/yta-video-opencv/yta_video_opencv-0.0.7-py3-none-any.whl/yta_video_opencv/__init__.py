"""
Module to include video handling with the
OpenCV library.

A video has its original size and properties,
but when placed on a canvas to be modified
and with other videos, the position is 
related to that canvas size, not its original.
"""
from yta_video_opencv.reader import OpencvReader
from yta_video_opencv.writer import OpencvWriter
from yta_video_opencv.frame import Frame
from yta_video_opencv.utils import OpencvUtils
from yta_general_utils.math.progression import Progression
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from yta_validation.number import NumberValidator
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from yta_video_frame_time import T
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
        self._video_instance: 'Video' = video
        """
        The video this frames belong to.
        """

    def go_to(
        self,
        frame_index: int
    ) -> 'Video':
        """
        Move the opencv reader to the 'frame_index' frame
        position to start reading from there.
        """
        self._video_instance._reader.go_to_frame(frame_index)
    
        return self._video_instance

    def get(
        self,
        frame_index_or_t: Union[float, int],
        do_process: bool = False,
        do_rollback: bool = True,
        do_store_in_cache: bool = False,
    ) -> 'np.ndarray':
        """
        Get the frame with the given 'frame_index_or_t'
        as a numpy array, or raise an exception if not
        possible.

        This frame is the original frame with no 
        modifications, as it is read from the source,
        if the 'do_process' parameter is False, or with
        the changes applied if True.

        The pointer will be returned to the previous
        position if the 'do_rollback' parameter is True,
        which is not recommended and can make the process
        slow if reading consecutive frames.

        The frame obtained will be stored in cache if the
        'do_store_in_cache' parameter is set as True, 
        being able to access to it in a near future. Use
        this feature carefully, a huge cache could 
        decrease the performance.

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

        frame = self._video_instance._reader.read_frame(
            frame_index = frame_index,
            do_rollback = do_rollback,
            do_store_in_cache = do_store_in_cache
        )

        return (
            self.process(frame, frame_index)
            if do_process else
            frame
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

        return self._video_instance._reader.iterate_frames_by_indexes(
            frame_indexes = frame_indexes
        )
    
    def show(
        self,
        frame_index_or_t: Union[float, int],
        do_process: bool = False
    ) -> None:
        """
        Show the frame with the given 'frame_index_or_t'
        on a display, or raise an exception if not
        possible.

        The 'frame_index_or_t' must be:
        - `int` if frame 'index' provided
        - `float` if frame time moment 't' provided
        """
        OpencvUtils.images.show(self.get(frame_index_or_t, do_process = do_process))

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

        # TODO: Process the transformation changes as
        # it should be done, not as a random thing
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
            self._fps = self._reader.fps

        return self._fps
    
    @property
    def number_of_frames(
        self
    ) -> int:
        if not hasattr(self, '_number_of_frames'):
            self._number_of_frames = self._reader.number_of_frames

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
            self._size = self._reader.size

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
    
    # TODO: Maybe this has to be moved
    @property
    def _composition_end_t(
        self
    ) -> float:
        """
        The end time when being used in a
        composition.
        """
        return self._composition_start_t + self._composition_duration
    
    def __init__(
        self,
        # TODO: Can I receive frames as numpys (?)
        filename: str
    ):
        # TODO: This must be replaced as we want to
        # accept a virtual video as numpy array, not
        # only a file source
        self._filename: str = filename
        """
        The filename provided as the original source.
        """
        self._reader = OpencvReader(filename)
        """
        The OpenCV video reader instance.
        """

        # This below is for the source file
        self._start_frame = 0
        """
        The index of the first frame to process.
        """
        self._end_frame = 999999
        """
        The index of the last frame to process.
        """
        
        # TODO: Maybe this below has to be moved
        # This below is for when composing
        self._composition_start_t: float = 0.0
        """
        The time start moment of this video when
        being in a composition, which means the
        time moment in which the video must start
        being displayed.
        """
        self._composition_duration: float = self.duration
        """
        The time the video must last when being
        in a composition.
        """
        
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
        The speed factor values we want to apply for
        each frame of the video.
        """

    # TODO: This must me moved to a more general
    # class about the element when being in a
    # composition
    def is_playing(
        self,
        t: float
    ) -> bool:
        """
        Flag to indicate if the video is being at the
        provided 't' time moment or not. Being played
        means that it must be considered when rendering
        the composition.
        """
        return self._composition_start_t < t < self._composition_end_t

    def _process(
        self,
        do_debug: bool = False
    ):
        """
        Iterator to process all the frames and
        return each of them once processed and all
        the changes have been applied.
        """
        # # TODO: This is hardcoded for manual testing
        # self.rotation_values = Progression(0, 360, self.number_of_frames).values
        # self.resize_values = Progression(0.2, 0.4, self.number_of_frames).values
        # self.position_values = list(zip(
        #     Progression(700, 800, self.number_of_frames).values,
        #     Progression(300, 350, self.number_of_frames).values
        # ))

        # Time spent in the whole process
        context = (
            Timer()
            if do_debug else
            nullcontext()
        )
        
        with context:
            for frame, frame_index in self.frames.iterate(self.frames.indexes_with_speed_applied):
                # Skip frames not in the range requested
                if (
                    frame_index < self._start_frame or
                    frame_index >= self._end_frame
                ):
                    continue

                # Time spent per frame build
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

    # TODO: Should this return a copy (?)
    def subclip(
        self,
        t_start: float,
        t_end: float
        # TODO: Maybe a 'do_copy' parameter to work
        # on a copy instead of on the original one?
    ) -> 'Video':
        """
        Subclip the video to the part in between the
        provided 't_start' and 't_end' time moments.
        """
        # TODO: Transform time to frame index
        ParameterValidator.validate_mandatory_positive_float('t_start', t_start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_float('t_end', t_end, do_include_zero = False)

        if t_end <= t_start:
            raise Exception('The "t_end" cannot be greater or equal than the "t_start" parameter.')

        self._start_frame = T.video_frame_time_to_video_frame_index(t_start, self.fps)
        self._end_frame = min(
            T.video_frame_time_to_video_frame_index(t_end, self.fps),
            self.number_of_frames - 1
        )

        return self
        
    def save_as(
        self,
        output_filename: str,
        do_debug: bool = False
    ):
        """
        Renderiza cambiando la velocidad sin precargar todo (usa seek por frames).
        Más seguro en memoria, pero puede ser más lento por seeks frecuentes.
        """
        output_writer = OpencvWriter.auto_detected(self.fps, self.size, output_filename)
        
        for frame in self._process(do_debug):
            output_writer.write(frame)

        output_writer.release()

    def copy(
        self
    ) -> 'Video':
        """
        Get a manually handled copy of this Video instance.
        """
        video = Video(
            filename = self._filename
        )
        video._start_frame = self._start_frame
        video._end_frame = self._end_frame
        video.rotation_values = self.rotation_values.copy()
        video.resize_values = self.resize_values.copy()
        video.position_values = self.position_values.copy()
        video.speed = self.speed.copy()

        return video

def main():
    from yta_video_opencv.render import Render

    test_input_video_filename = 'test_files/test_1.mp4'
    test_output_video_filename = 'test_files/output.mp4'

    video = Video(test_input_video_filename)
    #video.frames.show(3.3)
    #video.process_and_save(test_output_video_filename, 1.0, 1.5, do_debug = True)
    #video.subclip(1.0, 1.5).save_as(test_output_video_filename, do_debug = True)
    Render().save_as(test_output_video_filename)

    return

if __name__ == '__main__':
    main()

# TODO: Maybe I can create a VideoFrameIterator class