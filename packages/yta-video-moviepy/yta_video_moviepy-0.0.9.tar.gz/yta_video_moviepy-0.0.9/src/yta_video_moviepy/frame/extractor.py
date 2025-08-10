from yta_video_moviepy.t import T, get_number_of_frames
from yta_constants.video import FrameExtractionType
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from yta_validation.number import NumberValidator
from moviepy import VideoFileClip, VideoClip
from typing import Union

import numpy as np


class MoviepyVideoFrameExtractor:
    """
    Class to simplify the process of extracting
    video frames by time or frame number.

    A moviepy clip is built by consecutive
    frames. The first frame is on t = 0, and the
    next frames are obtained by applying a (a, b]
    interval. This means that if we a have a
    video of 10 fps, each frame will last 0.1s.
    So, considering the previous condition, the
    second frame will be at 0.1s, so you will be
    able to access it by providing a time between
    (0.000000000001, 0.1].
    """

    # TODO: You can use imageio 'imsave'
    # to save the numpy frame as an image

    @staticmethod
    def get_frame_by_index(
        video: VideoClip,
        index: int = 0
    ):
        """
        Get the frame numpy array 
        corresponding to the given time
        frame 'index' of the also provided
        'video'.
        """
        ParameterValidator.validate_mandatory_positive_int('index', index, do_include_zero = True)

        return MoviepyVideoFrameExtractor.get_frame(video, FrameExtractionType.FRAME_INDEX, index)

    @staticmethod
    def get_frames_by_index(
        video: VideoClip,
        indexes: list[float] = [0],
        do_use_concurrency: bool = False
    ):
        """
        Get all the frame numpy arrays 
        corresponding to the frame indexes
        given as 'indexes' for the provided
        'video'. 
        """
        if not PythonValidator.is_list(indexes):
            if NumberValidator.is_positive_number(indexes, do_include_zero = True):
                indexes = [indexes]
            else:
                raise Exception('The provided "indexes" is not an array of frame numbers nor a single one.')
            
        if do_use_concurrency:
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor() as executor:
                frames = list(executor.map(
                    lambda index: MoviepyVideoFrameExtractor.get_frame(video, FrameExtractionType.FRAME_INDEX, index),
                    indexes
                ))

            return frames
        else:
            return list(map(
                lambda index: MoviepyVideoFrameExtractor.get_frame(video, FrameExtractionType.FRAME_INDEX, index),
                indexes
            ))
    
    @staticmethod
    def get_frame_by_t(
        video: VideoClip,
        t: float = 0.0
    ):
        """
        Get the frame numpy array 
        corresponding to the given time
        moment 't' of the also provided
        'video'. The frame time must be
        a valid value between 0 and the
        video duration.
        """
        ParameterValidator.validate_mandatory_positive_number('t', t, do_include_zero = True)

        return MoviepyVideoFrameExtractor.get_frame(video, FrameExtractionType.FRAME_INDEX, t)

    @staticmethod
    def get_frames_by_t(
        video: VideoClip,
        t: list[float] = [0.0],
        do_use_concurrency: bool = False
    ):
        """
        Get all the frame numpy arrays
        corresponding to the time moments
        given as 't' for the provided
        'video'. All frame times must be
        valid, between 0 and the video
        duration.

        Set the flag 'do_use_concurrency'
        as True if you want to use an
        experimental method that uses
        concurrency.
        """
        if not PythonValidator.is_list(t):
            if NumberValidator.is_positive_number(t, do_include_zero = True):
                t = [t]
            else:
                raise Exception('The provided "t" is not an array of frame times nor a single one.')
            
        if do_use_concurrency:
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor() as executor:
                frames = list(executor.map(
                    lambda t_: MoviepyVideoFrameExtractor.get_frame(video, FrameExtractionType.FRAME_TIME_MOMENT, t_),
                    t
                ))

            return frames
        else:
            return list(map(
                lambda t_: MoviepyVideoFrameExtractor.get_frame(video, FrameExtractionType.FRAME_TIME_MOMENT, t_),
                t
            ))
    
    @staticmethod
    def get_frame(
        video: VideoClip,
        mode: FrameExtractionType = FrameExtractionType.FRAME_INDEX,
        t: Union[float, int] = 0
    ):
        """
        Get the frame numpy array 
        corresponding to the provided 
        't' frame number or time moment.
        
        This is my own method due to 
        some problems with the original
        moviepy '.get_frame()' and 
        because of its laxity. Feel free
        to use the moviepy '.get_frame()'
        method instead.
        """
        mode = FrameExtractionType.to_enum(mode)
        ParameterValidator.validate_mandatory_positive_number('t', t, do_include_zero = True)

        t = {
            FrameExtractionType.FRAME_INDEX: lambda: T.frame_index_to_frame_time(int(t), video.fps),
            FrameExtractionType.FRAME_TIME_MOMENT: lambda: float(t)
        }[mode]()

        return video.get_frame(t)

    @staticmethod
    def get_all_frames(
        video: VideoClip
    ):
        """
        Get all the frame numpy arrays
        of the given 'video'.
        """
        return list(video.iter_frames())
    
    @staticmethod
    def get_first_frame(
        video: VideoClip
    ):
        """
        Get the first frame numpy array
        of the provided 'video'.
        """
        return MoviepyVideoFrameExtractor.get_frame_by_index(video, 0)
    
    @staticmethod
    def get_last_frame(
        video: VideoClip
    ):
        """
        Get the last frame numpy array
        of the provided 'video'.
        """
        return MoviepyVideoFrameExtractor.get_frame_by_index(
            get_number_of_frames(video.duration, video.fps) - 1
        )
    
    # TODO: Would be perfect to have some methods to turn frames into
    # RGBA denormalized (0, 255) or normalized (0, 1) easier because
    # it is needed to work with images and other libraries. Those 
    # methods would iterate over the values and notice if they are in
    # an specific range so they need to be change or even if they are
    # invalid values (not even in [0, 255] range because they are not
    # rgb or rgba colors but math calculations).
    # This is actually being done by the VideoMaskHandler
    @staticmethod
    def get_frame_as_rgba_by_t(
        video: VideoClip,
        t: float,
        do_normalize: bool = False,
        #output_filename: str = None
    ):
        """
        Gets the frame of the requested
        't' time moment of the provided
        'video' as a normalized RGBA
        numpy array that is built by
        joining the rgb frame (from main
        clip) and the alpha (from .mask
        clip), useful to detect
        transparent regions.
        """
        # TODO: We don't use VideoParser to avoid
        # a cyclic import but it should be good
        video = VideoFileClip(video, has_mask = True)

        # We first normalize the clips
        main_frame = MoviepyVideoFrameExtractor.get_frame_by_t(video, t) / 255  # RGB numpy array normalized 3d <= r,g,b
        mask_frame = MoviepyVideoFrameExtractor.get_frame_by_t(video.mask, t)[:, :, np.newaxis]  # Alpha numpy array normalized 1d <= alpha
        # Combine RGB of frame and A from mask to RGBA numpy array (it is normalized)
        frame_rgba = np.concatenate((main_frame, mask_frame), axis = 2) # 4d <= r,g,b,alpha

        # if output_filename:
        #     # TODO: Check extension
        #     ImageConverter.numpy_image_to_pil(frame_rgba).save(output_filename)
        #     # TODO: Write numpy as file image
        #     # Video mask is written as 0 or 1 (1 is transparent)
        #     # but main frame is written as 0 to 255, and the
        #     # 'numpy_image_to_pil' is expecting from 0 to 1
        #     # (normalized) instead of from 0 to 255 so it won't
        #     # work

        return (
            frame_rgba * 255
            if not do_normalize else
            frame_rgba
        )
    