"""
We have two different types of clips
related to moviepy:

- `static` - The clip doesn't change
along its duration time. Each frame
is exactly the same as the previous
and the next one.
- `dynamic` - The clip changes along
its duration time. Each frame can be
different to the previous and the 
next one.
"""
from yta_video_moviepy.frame import MoviepyVideoFrame
from yta_video_utils.validation import validate_duration, validate_fps, validate_opacity, validate_size
from yta_constants.multimedia import DEFAULT_SCENE_SIZE
from yta_validation.parameter import ParameterValidator
from yta_colors import Color
from moviepy import ColorClip, VideoClip
from typing import Union


class MoviepyMaskClipGenerator:
    """
    Class to wrap the functionality
    related to generate moviepy mask
    videos.

    We have two different types of clips
    related to moviepy:

    - `static` - The clip doesn't change
    along its duration time. Each frame
    is exactly the same as the previous
    and the next one.
    - `dynamic` - The clip changes along
    its duration time. Each frame can be
    different to the previous and the 
    next one.
    """

    @staticmethod
    def get_static_mask(
        size: tuple = DEFAULT_SCENE_SIZE,
        duration: float = 1 / 60,
        fps: float = 60.0,
        opacity: float = 1.0
    ):
        """
        Get a moviepy mask video clip by
        generating a ColorClip with the
        opacity provided, where 0.0 is
        full transparent and 1.0 full
        opaque.

        It is a 'static' mask because
        the clip doesn't change along
        its duration time. Each frame
        is identic to the previous and
        the next one.
        """
        validate_size(size)
        validate_duration(duration)
        validate_fps(fps)
        validate_opacity(opacity)
        
        return ColorClip(
            size = size,
            color = opacity,
            is_mask = True,
            duration = duration
        ).with_fps(fps)
    
    @staticmethod
    def get_static_transparent_mask(
        size: tuple = DEFAULT_SCENE_SIZE,
        duration: float = 1 / 60,
        fps: float = 60.0
    ):
        """
        Get a moviepy mask video clip by
        generating a ColorClip with the
        opacity as 0.0, that means full
        transparent.

        It is a 'static' mask because
        the clip doesn't change along
        its duration time. Each frame
        is identic to the previous and
        the next one.
        """
        return MoviepyMaskClipGenerator.get_static_mask(
            size = size,
            duration = duration,
            fps = fps,
            opacity = 0.0
        )
    
    @staticmethod
    def get_static_opaque_mask(
        size: tuple = DEFAULT_SCENE_SIZE,
        duration: float = 1 / 60,
        fps: float = 60.0
    ):
        """
        Get a moviepy mask video clip by
        generating a ColorClip with the
        opacity as 1.0, that means full
        opaque.

        It is a 'static' mask because
        the clip doesn't change along
        its duration time. Each frame
        is identic to the previous and
        the next one.
        """
        return MoviepyMaskClipGenerator.get_static_mask(
            size = size,
            duration = duration,
            fps = fps,
            opacity = 1.0
        )

    # TODO: This method below has been
    # migrated from 'yta_multimedia'
    # but need to be reviewed and
    # improved
    @staticmethod
    def video_to_mask(
        video: 'Clip'
    ):
        """
        Turn the 'video' provided into a
        moviepy mask video clip that can
        be set as the mask of any other
        normal moviepy video clip.
        """
        # TODO: This is ok but very slow I think...
        mask_clip_frames = [
            MoviepyVideoFrame(frame).as_mask()
            for frame in video.iter_frames()
        ]

        return VideoClip(
            lambda t: mask_clip_frames[int(t * video.fps)],
            is_mask = True
        ).with_fps(video.fps)
    
class MoviepyNormalClipGenerator:
    """
    Class to wrap the functionality
    related to generate moviepy normal
    videos.

    We have two different types of clips
    related to moviepy:

    - `static` - The clip doesn't change
    along its duration time. Each frame
    is exactly the same as the previous
    and the next one.
    - `dynamic` - The clip changes along
    its duration time. Each frame can be
    different to the previous and the 
    next one.
    """

    @staticmethod
    def get_static_color_background(
        size: tuple,
        color: Union[Color, 'ColorString', str],
        duration: float = 1 / 60,
        fps: float = 60.0,
        opacity: float = 1.0
    ):
        """
        Get a static color clip to be used
        as a background clip, of the given
        'color' and 'size', that lasts
        the 'duration' provided, having the
        also given 'fps' and with the 
        'opacity' passed as parameter.

        The clip will have a mask attached
        if the 'opacity' provided is lower
        than 1.0.

        It is a 'static' video because
        the clip doesn't change along
        its duration time. Each frame
        is identic to the previous and
        the next one.
        """
        color = Color.parse(color)
        validate_size(size)
        validate_duration(duration)
        validate_fps(fps)
        validate_opacity(opacity)
        
        color_clip: ColorClip = ColorClip(
            size = size,
            color = color.rgb_array_not_normalized,
            is_mask = False,
            duration = duration
        ).with_fps(fps)

        return (
            color_clip.with_mask(
                MoviepyMaskClipGenerator.get_static_mask(
                    size = color_clip.size,
                    duration = color_clip.duration,
                    fps = color_clip.fps,
                    opacity = opacity
                )
            )
            if opacity < 1.0 else
            # A full opaque clip doesn't need a mask because it is,
            # by definition, full opaque
            color_clip
        )

    @staticmethod
    def get_static_default_color_background(
        size: tuple = DEFAULT_SCENE_SIZE,
        duration: float = 1 / 60,
        fps: float = 60,
        is_transparent: bool = True
    ):
        """
        Get a static color clip, of the
        default color, to be used as a
        background clip, of the given
        'size', that lasts the 'duration'
        provided, having the also given
        'fps' and being full transparent
        if 'is_transparent' is True, or
        opaque if False.

        It is a 'static' mask because
        the clip doesn't change along
        its duration time. Each frame
        is identic to the previous and
        the next one.
        """
        ParameterValidator.validate_mandatory_bool('is_transparent', is_transparent)
        
        opacity = (
            0.0
            if is_transparent else
            1.0
        )

        return MoviepyNormalClipGenerator.get_static_color_background(
            size = size,
            # black
            color = [0, 0, 0],
            duration = duration,
            fps = fps,
            opacity = opacity
        )

    # TODO: Maybe add more methods or
    # create a specific background clip
    # generator