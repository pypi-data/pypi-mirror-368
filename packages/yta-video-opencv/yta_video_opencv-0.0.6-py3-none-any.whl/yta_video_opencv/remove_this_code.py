"""
Old code that was working but it is not the
final code I will keep. I don't want to 
remove it yet.
"""
def process_applying_complex_speed_factor_slow(
):
    # TODO: 'speed' must have the same number of
    # values than the amount of frames on this video
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