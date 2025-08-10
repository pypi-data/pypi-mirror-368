from yta_video_moviepy.generator import MoviepyNormalClipGenerator
from yta_video_moviepy.t import T, get_frame_duration, SMALL_AMOUNT_TO_FIX
from yta_constants.multimedia import DEFAULT_SCENE_SIZE, DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT
from moviepy import CompositeVideoClip, VideoClip
from copy import copy


def wrap_video_with_transparent_background(
    video: VideoClip
):
    """
    Put a full transparent background behind the video
    if its size is not our default scene (1920x1080) and
    places the video on the center of this background.

    This method works with a copy of the original video so
    only the returned one is changed.
    """
    video = copy(video)
    # TODO: Is this changing the variable value or do I
    # need to do by position (?)
    # TODO: What if the size is bigger than the scene
    # size?
    if video.size != DEFAULT_SCENE_SIZE:
        # I place the video at the center of the new background but
        # I reposition it to place with its center in the same place
        # as the original one
        original_center_positions = []
        frame_duration = get_frame_duration(video.fps)
        # TODO: Careful with this t
        for t in T.get_frame_time_moments(video.duration, video.fps):
            pos = video.pos(t)
            original_center_positions.append((pos[0], pos[1]))
        video = CompositeVideoClip([
            MoviepyNormalClipGenerator.get_static_default_color_background(
                duration = video.duration,
                fps = video.fps
            ),
            video.with_position(('center', 'center'))
        ]).with_position(lambda t: (
            original_center_positions[T.frame_time_to_frame_index(t, frame_duration)][0] - DEFAULT_SCENE_WIDTH / 2,
            original_center_positions[T.frame_time_to_frame_index(t, frame_duration)][1] - DEFAULT_SCENE_HEIGHT / 2
        ))

    return video

def calculate_real_video_duration(
    video: 'Clip'
):
    """
    Process the provided 'video' and obtain the real
    duration by trying to access to the last frames
    according to its duration attribute.

    This method will return the real duration, which
    is determined by the last accessible frame plus
    the frame duration and a small amount to avoid
    decimal issues.

    This method was created due to a bug in the 
    moviepy library related to some frames that were
    unreadable.
    """
    import warnings
    
    #video = VideoParser.to_moviepy(video)

    # Moviepy library is throwing a warning when a 
    # frame is not accessible through its 
    # ffmpeg_reader, but will return the previous
    # valid frame and throw no Exceptions. As we
    # are trying to determine its real duration,
    # that warning is saying that the frame is not
    # valid, so it is not part of its real duration
    # so we must avoid it and continue with the
    # previous one until we find the first (last)
    # valid frame.
    warnings.filterwarnings('error')
    
    for t in T.get_frame_time_moments(video.duration, video.fps)[::-1]:
        try:
            # How to catch warnings: https://stackoverflow.com/a/30368735
            video.get_frame(t = t)
            last_frame = t
            break
        except:
            pass

    warnings.resetwarnings()

    frame_duration = get_frame_duration(video.fps)
    # I sum a small amount to ensure it is over the
    # duration that guarantees the expected amount
    # of frames when calculating
    # Use this below to fix the video duration:
    # video = video.with_subclip(0, calculate_real_video_duration(video))#.with_fps(60)
    return ((last_frame + frame_duration + SMALL_AMOUNT_TO_FIX) // frame_duration) * frame_duration + SMALL_AMOUNT_TO_FIX