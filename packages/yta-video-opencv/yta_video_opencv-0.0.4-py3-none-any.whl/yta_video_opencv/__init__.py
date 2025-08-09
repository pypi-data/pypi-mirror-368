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
from yta_general_utils.math.progression import Progression
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from yta_validation.number import NumberValidator
from yta_validation.parameter import ParameterValidator
from typing import Union

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
        return self.video.fps
    
    @property
    def number_of_frames(
        self
    ) -> int:
        return self.video.number_of_frames
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The original size of the video.
        """
        return self.video.size

    @property
    def width(
        self
    ) -> int:
        """
        The original width of the video.
        """
        return self.video.width
    
    @property
    def height(
        self
    ) -> int:
        """
        The original height of the video.
        """
        return self.video.height

    def __init__(
        self,
        video: 'Video'
    ):
        self.video: 'Video' = video

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

        self.video._video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

        ret, frame = self.video._video.read()

        if ret is None:
            raise Exception(f'Something went wrong when reading the "{str(frame_index)}" frame of the video.')
        
        # TODO: Maybe return as 'Frame' instance (?)
        return frame
    
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
        frame = self.get(frame_index_or_t)
        cv2.imshow('video_display', cv2.resize(frame, (int(self.width / 2), int(self.height / 2))))
        cv2.waitKey(0)

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

        #cv2.putText(frame, "Hola!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # This is to export it
        #self.out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, (self.width, self.height))
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

    def __del__(
        self
    ):
        self._video.release()

    def _go_to_frame(
        self,
        frame_index: int
    ):
        """
        Move the opencv reader to the 'frame_index' frame
        position to start reading from there.
        """
        self._video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

    def _read_frame(
        self,
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
        current_frame_index = self._video.get(cv2.CAP_PROP_POS_FRAMES)

        # This will move the pointer to the next frame
        if frame_index is not None:
            self._go_to_frame(frame_index)

        ret, frame = self._video.read()

        if do_rollback:
            self._go_to_frame(current_frame_index)

        return (
            None
            if not ret else
            frame
        )
    
    def _iter_frames_by_indexes(
        self,
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
        self._go_to_frame(current_index)

        while current_index <= last_index_to_read:
            if current_index == last_frame_read_index:
                frame = last_frame_read
                # Go to next frame but less expensive
                self._video.grab()
            else:
                ret, frame = self._video.read()
                # TODO: This below should not happen...
                if not ret:
                    break

            if current_index in frame_indexes:
                yield frame, current_index

            last_frame_read_index = current_index
            last_frame_read = frame
            current_index += 1

    def process_and_save(
        self,
        output_filename: str,
        # TODO: Implement this below
        t_start: float = 0.0,
        t_end: float = 999999.9
    ):
        """
        Renderiza cambiando la velocidad sin precargar todo (usa seek por frames).
        Más seguro en memoria, pero puede ser más lento por seeks frecuentes.
        """
        output_writer = OpenCVWriter.auto_detected(self.fps, self.size, output_filename)
        if not output_writer.isOpened():
            self._video.release()
            raise IOError(f"No se pudo crear writer para ese vídeo")

        # TODO: Precalculate some random values to test
        self.rotation_values = Progression(0, 360, self.number_of_frames).values
        self.resize_values = Progression(0.2, 0.4, self.number_of_frames).values
        self.position_values = list(zip(
            Progression(700, 800, self.number_of_frames).values,
            Progression(300, 350, self.number_of_frames).values
        ))

        # Get the index of the frames we need to use
        # to build the video output
        # TODO: Set this as a property maybe (?)
        # TODO: What if we want to subclip (?)
        def frame_indexes_with_speed_applied(
            speed,
            total_frames
        ):
            """
            Get the list of the frame indexes we need to render
            to fit the speed factor values holded in the
            'speed' parameter.

            Use it as a list doing this:
            - `list(frame_indexes_with_speed_applied(speed, self.number_of_frames))`
            """
            index = 0.0
            while index < total_frames:
                yield int(index)
                index += speed[int(index)]

        def process_applying_complex_speed_factor(
        ):
            speed = Progression(0.5, 5, self.number_of_frames).values

            from yta_timer import Timer
            timer = Timer()

            # Get start and end frame indexes
            start_frame_index = int((t_start + SMALL_AMOUNT_TO_FIX) * self.fps)
            end_frame_index = min(
                int((t_end + SMALL_AMOUNT_TO_FIX) * self.fps),
                self.number_of_frames
            )

            # Save time if repeating
            last_frame_index = -1
            last_frame = None
            for current_frame_index in list(frame_indexes_with_speed_applied(speed, self.number_of_frames)):
                # Skip frames not in the range requested
                if (
                    current_frame_index < start_frame_index or
                    current_frame_index >= end_frame_index
                ):
                    continue
                
                timer.start()
                frame = (
                    last_frame
                    if current_frame_index == last_frame_index else
                    self.modify_frame(
                        frame = self._read_frame(current_frame_index),
                        frame_index =  current_frame_index
                    )
                )
                timer.stop()
                print(f'Frame {str(current_frame_index)} - {timer.time_elapsed_str}')

                output_writer.write(frame)
                last_frame_index = current_frame_index
                last_frame = frame

        def process_applying_complex_speed_factor_and_performance(
        ):
            """
            Process the video applying a complex speed
            factor but also using the best method to
            read frames, in terms of performance.
            """
            speed = Progression(0.5, 5, self.number_of_frames).values

            from yta_timer import Timer
            general_timer = Timer()
            timer = Timer()

            # Get start and end frame indexes
            start_frame_index = int((t_start + SMALL_AMOUNT_TO_FIX) * self.fps)
            end_frame_index = min(
                int((t_end + SMALL_AMOUNT_TO_FIX) * self.fps),
                self.number_of_frames
            )

            general_timer.start()
            for frame, frame_index in self._iter_frames_by_indexes(list(frame_indexes_with_speed_applied(speed, self.number_of_frames))):
                # Skip frames not in the range requested
                if (
                    frame_index < start_frame_index or
                    frame_index >= end_frame_index
                ):
                    continue
                
                timer.start()
                frame = self.modify_frame(
                    frame = frame,
                    frame_index =  frame_index
                )
                timer.stop()
                print(f'Frame {str(frame_index)} - {timer.time_elapsed_str}')

                output_writer.write(frame)
            
            general_timer.stop()
            general_timer.print()

        #process_applying_complex_speed_factor()
        process_applying_complex_speed_factor_and_performance()

        output_writer.release()
        self._video.release()

    def process_and_savex(
        self,
        output_filename: str,
        t_start: float = 0.0,
        t_end: float = 999999.9
    ):
        """
        Process the part of the video between the
        't_start' and the 't_end' and save it as
        the 'output_filename' file name provided.
        """
        # TODO: What if 't_start' is invalid (?)
        output_writer = OpenCVWriter.auto_detected(self.fps, self.size, output_filename)

        # Get start and end frame
        start_frame = int((t_start + SMALL_AMOUNT_TO_FIX) * self.fps)
        end_frame = min(
            int((t_end + SMALL_AMOUNT_TO_FIX) * self.fps),
            self.number_of_frames
        )

        self._go_to_frame(start_frame)

        from yta_timer import Timer
        timer = Timer()

        # TODO: Precalculate some random values to test
        self.rotation_values = Progression(0, 360, self.number_of_frames).values
        self.resize_values = Progression(0.2, 0.4, self.number_of_frames).values
        self.position_values = list(zip(
            Progression(700, 800, self.number_of_frames).values,
            Progression(300, 350, self.number_of_frames).values
        ))

        # TODO: I need to see the way to speed up,
        # slow down, etc. the video by playing with
        # the frame indexes, and this '.read()' is
        # not enough for that
        for frame_index in range(start_frame, end_frame):
            ret, frame = self._video.read()
            if not ret:
                break

            timer.start()
            frame = self.modify_frame(frame, frame_index)
            timer.stop()
            print(f'Frame {str(frame_index)} - {timer.time_elapsed_str}')
            # frame = self.place_video_frame_on_scene(
            #     frame = frame,
            #     zoom = 0.2 + 0.2 * (frame_index / self.number_of_frames),
            #     target_center = (300, 300),
            #     scene_size = self.size
            # )

            output_writer.write(frame)

        self._video.release()
        output_writer.release()

    def modify_frame(
        self,
        frame,
        frame_index: int
    ):
        """
        Apply the modifications to the provided 'frame'
        which has the also given 'frame_index'.

        The 'frame_index' is to be able to autodetect
        the specific modifications for that frame.
        """

        #resized = FrameEffect.zoom_at(frame, zoom)
        

        #return Frame(frame).transform_and_place(rotation, (300, 300)).frame#.fit_size(CANVAS_SIZE)
        return Frame(frame).effects.invert().rotate(self.rotation_values[frame_index]).resize_factor(self.resize_values[frame_index]).move(self.position_values[frame_index]).frame

        
        return resized
        return 255 - frame
        return frame



def main():
    test_input_video_filename = 'test_files/test_1.mp4'
    test_output_video_filename = 'test_files/output.mp4'

    video = Video(test_input_video_filename)
    #video.frames.show(3.3)
    #video.process_and_save(test_output_video_filename, 1.0, 1.5)
    video.process_and_save(test_output_video_filename)

if __name__ == '__main__':
    main()