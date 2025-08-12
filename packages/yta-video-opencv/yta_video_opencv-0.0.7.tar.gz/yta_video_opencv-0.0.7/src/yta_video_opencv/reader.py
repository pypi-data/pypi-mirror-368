from yta_validation.parameter import ParameterValidator
from typing import Union

import cv2


class _Cache:
    """
    Class to wrap the reader cache functionality.
    """

    def __init__(
        self,
        reader: 'OpencvReader'
    ):
        self._reader_instance: OpencvReader = reader
        """
        The OpencvReader instance this cache belongs
        to.
        """
        self._frames: dict = {}
        """
        Dictionary to store frames in a small cache
        by their frame indexes.
        """

    def clear(
        self
    ) -> 'OpencvReader':
        """
        Clear the cache by emptying the dictionary.
        """
        self._frames = {}

        return self._reader_instance

    def get(
        self,
        frame_index: int
        # TODO: Add 'default_value' (?)
    ) -> Union['np.ndarray', None]:
        """
        Get the frame with the given 'frame_index' key
        from the cache, only if available.
        """
        ParameterValidator.validate_mandatory_positive_number('frame_index', frame_index, do_include_zero = True)

        return self._frames.get(int(frame_index), None)

    def save(
        self,
        frame: 'np.ndarray',
        frame_index: int
    ) -> 'OpencvReader':
        """
        Save the provided 'frame' in the cache, using
        the 'frame_index' provided as its key.
        """
        ParameterValidator.validate_mandatory_numpy_array('frame', frame)
        ParameterValidator.validate_mandatory_positive_number('frame_index', frame_index, do_include_zero = True)

        self._frames[int(frame_index)] = frame

        return self._reader_instance

class OpencvReader:
    """
    Class to simplify the way we read files with
    the OpenCV library.
    """

    @property
    def fps(
        self
    ) -> float:
        """
        The frames per second of the video.
        """
        return self._reader.get(cv2.CAP_PROP_FPS)
    
    @property
    def number_of_frames(
        self
    ) -> int:
        """
        The number of frames of the video.
        """
        return int(self._reader.get(cv2.CAP_PROP_FRAME_COUNT))
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video read, in a (width, height) 
        format.
        """
        return  (
            int(self._reader.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self._reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
        )

    @property
    def current_frame_index(
        self
    ) -> float:
        """
        Get the current frame, which is the frame that
        will be read the next because the pointer is
        pointing to it.
        """
        return self._reader.get(cv2.CAP_PROP_POS_FRAMES)

    def __init__(
        self,
        filename: str
    ):
        self._filename: str = filename
        """
        The filename provided as the original source.
        """
        self._reader = cv2.VideoCapture(filename)
        """
        The OpenCV video reader instance.
        """

        if not self._reader.isOpened():
            raise IOError(f'Unable to open/read the video "{filename}".')
        
        # TODO: Should this be private as we use it
        # internally only (?)
        self.cache: _Cache = _Cache(self)
        """
        The cache that keeps the frames stored to access
        faster to them, if requested and needed.
        """
        
    def go_to_frame(
        self,
        frame_index: int
    ) -> 'OpencvReader':
        """
        Set the 'frame_index' provided as the next frame
        to be read, making the pointer point to that
        frame (only if it is not pointing to it already).
        """
        if frame_index == (self.current_frame_index + 1):
            self._reader.grab()
        elif frame_index != self.current_frame_index:
            # TODO: If going forward, is it faster if I do
            # the .grab() as many times as needed instead
            # of this below (?)
            self._reader.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

        return self     

    def read_frame(
        self,
        frame_index: Union[None, int] = None,
        do_rollback: bool = False,
        do_store_in_cache: bool = False
    ) -> Union['np.ndarray', None]:
        """
        Read the frame at the current frame index or at
        the given 'frame_index' if it is not None. If the
        'do_rollback' parameter is True, the pointer will
        read the current frame but will not move on to 
        the next position. If 'do_store_in_cache' is True,
        the frame will be stored in cache for a future
        faster access. Be careful, storing too many frames
        in cache can be a bad idea.

        This method will return None if no frame available.

        The OpenCV reading process is complex and involves
        decompressing códecs for the different frames. It
        is cheaper to read the frames consecutively and
        discard the ones we don't want than moving to the
        one we need before reading it, and then doing the
        same to the next one.
        """
        # First check in cache
        frame_in_cache = self.cache.get(frame_index)
        if frame_in_cache is not None:
            return frame_in_cache
        
        current_frame_index = self.current_frame_index

        # This will move the pointer to the next frame
        if frame_index is not None:
            self.go_to_frame(frame_index)

        ret, frame = self._reader.read()

        if do_rollback:
            self.go_to_frame(current_frame_index)

        # Store in cache if requested
        if (
            ret is not None and
            do_store_in_cache
        ):
            self.cache.save(frame, frame_index)

        return (
            None
            if not ret else
            frame
        )   
    
    def iterate_frames_by_indexes(
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

        # TODO: Maybe check if all of them are
        # stored in cache, to return without any
        # iteration (?)

        # Hold information about repeated ones
        last_frame_read_index = -1
        last_frame_read = None

        # Try to read the smaller amount possible
        current_index = min(frame_indexes)
        self.go_to_frame(current_index)

        while current_index <= last_index_to_read:
            if current_index == last_frame_read_index:
                frame = last_frame_read
                # Go to next frame but less expensive
                self._reader.grab()
            else:
                ret, frame = self._reader.read()
                # TODO: This below should not happen...
                if not ret:
                    break

            if current_index in frame_indexes:
                yield frame, current_index

            last_frame_read_index = current_index
            last_frame_read = frame
            current_index += 1
        
    def __del__(
        self
    ):
        self._reader.release()