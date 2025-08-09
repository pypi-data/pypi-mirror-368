from yta_constants.file import VideoFileExtension
from typing import Union

import cv2


class OpenCVWriter:
    """
    Class to wrap the different video writers we
    have when using OpenCV.
    """

    @staticmethod
    def mp4(
        fps: float,
        size: tuple[int, int],
        output_filename: str
    ) -> cv2.VideoWriter:
        """
        Get an opencv output handler instance for
        '.mp4' videos.
        """
        return cv2.VideoWriter(output_filename, cv2.VideoWriter.fourcc('m','p','4','v'), fps, size)
    
    @staticmethod
    def auto_detected(
        fps: float,
        size: tuple[int, int],
        output_filename: str
    ) -> Union[cv2.VideoWriter, None]:
        """
        Get an opencv output handler instance for
        the extension that is auto detected from 
        the given 'output_filename'.
        """
        # TODO: Process and validate extension using 'yta_file'
        extension = output_filename.split('.')[1].lower()
        
        return {
            VideoFileExtension.MP4.value: lambda: OpenCVWriter.mp4(fps, size, output_filename)
        }[extension]()