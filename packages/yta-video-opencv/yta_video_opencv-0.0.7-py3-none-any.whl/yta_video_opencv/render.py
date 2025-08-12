from yta_video_opencv import Video
from yta_video_opencv import OpencvWriter
from yta_video_opencv.canvas import Canvas
from yta_video_frame_time import T
from yta_constants.multimedia import DEFAULT_SCENE_SIZE


class Render:
    """
    Class to render a project that is made of
    different videos.
    """

    @property
    def fps(
        self
    ) -> float:
        """
        The frames per second that will be used in
        the composition, which is the maximum fps
        value of all the videos that are on it.
        """
        return max(self.videos, key = lambda video: video.fps).fps
    
    @property
    def t_end(
        self
    ) -> float:
        """
        The time moment in which the last video 
        must end.
        """
        return max(self.videos, key = lambda video: video._composition_end_t)._composition_end_t

    def __init__(
        self,
        size: tuple[int, int] = DEFAULT_SCENE_SIZE
    ):
        self.size: tuple[int, int] = size
        """
        The size of the canvas in which we will put
        all the videos together and render.
        """
        self.videos: list[Video] = []

    def add_video(
        self,
        video: Video
    ) -> 'Render':
        """
        Add a video to the render.
        """
        # TODO: This has to be with tracks, not videos
        # directly
        self.videos.append(video)

        return self

    def _process(
        self
    ):
        """
        Iterator to process all the frames of the
        different videos and return the final
        composition
        """
        # TODO: Need the 't_end' of the project
        # TODO: Need the max 'fps' of the project
        canvas = Canvas(size = self.size)

        print(f'Rendering to {str(self.t_end)}')
        # TODO: What is the fastest way to access to the
        # video frames, one by one, but as I do here? Is
        # this one?
        for t in T.get_frame_time_moments(self.t_end, self.fps):
            # We put the background on the base
            frame = canvas.empty_frame
            # TODO: We need to read in the opposite order of priority
            for video in self.videos:
                # TODO: We need to check if it is playing something
                # or not actually, and with layers, no videos
                if video.is_playing(t):
                    # TODO: We need to add the frame to the previous frame
                    # considering the pixeles outside as alpha pixels
                    # TODO: This 't' conversion should be done in the video
                    frame = video.frames.get(t - video._composition_start_t, do_process = True, do_rollback = False)
                    print(f'Video ({str(video._composition_start_t)}) playing at {str(t)}')
            
            # Here we have the definitive frame
            yield(frame)
        
    def save_as(
        self,
        output_filename: str
    ):
        # TODO: This should be done using tracks that
        # include videos and audios with hierarchy
        from yta_video_opencv import Video
        from yta_general_utils.math.progression import Progression

        test_input_video_filename = 'test_files/test_1.mp4'
        video_1 = Video(test_input_video_filename)
        video_1.rotation_values = Progression(0, 360, video_1.number_of_frames).values
        video_1.resize_values = Progression(0.2, 0.4, video_1.number_of_frames).values
        video_1.position_values = list(zip(
            Progression(500, 700, video_1.number_of_frames).values,
            Progression(300, 350, video_1.number_of_frames).values
        ))
        video_1._composition_start_t = 1.0

        video_2 = Video(test_input_video_filename)
        video_2.rotation_values = Progression(0, 360, video_1.number_of_frames).values
        video_2.resize_values = Progression(0.2, 0.4, video_1.number_of_frames).values
        video_2.position_values = list(zip(
            Progression(700, 800, video_1.number_of_frames).values,
            Progression(300, 350, video_1.number_of_frames).values
        ))
        video_2._composition_start_t = 0.5

        self.add_video(video_1).add_video(video_2)

        output_writer = OpencvWriter.auto_detected(self.fps, self.size, 'test_files/render_composition.mp4')
        
        for frame in self._process():
            output_writer.write(frame)

        output_writer.release()

        return