from yta_validation.parameter import ParameterValidator
from yta_programming.output import Output
from yta_constants.file import FileType
from moviepy import VideoClip
from typing import Union


class MoviepyWriter:
    """
    Class to write moviepy video and audio
    files.
    """

    def write_video(
        video: VideoClip,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Write the provided video as a local
        file with the given 'output_filename'.
        """
        ParameterValidator.validate_mandatory_instance_of('video', video, VideoClip)

        output_filename = Output.get_filename(output_filename, FileType.VIDEO)

        video.write_videofile(output_filename)

        return output_filename

    def write_video_audio(
        video: VideoClip,
        output_filename: Union[str, None] = None
    ) -> Union[str, None]:
        """
        Write the provided video audio as a
        local file with the given
        'output_filename'.
        """
        ParameterValidator.validate_mandatory_instance_of('video', video, VideoClip)

        if video.audio is None:
            return None

        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        video.audio.write_audiofile(output_filename)
        
        return output_filename