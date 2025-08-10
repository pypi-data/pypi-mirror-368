"""
Module to manage and handle moviepy
video frames.

Imagine a video with fps = 30 and that lasts 1
second. That means that the video has 30 frames
and that each frame duration is 1 / 30 = 0.03333.

The frame times are the next:
frame 0: [0, 0.0333333) -> First frame
frame 1: [0.033333, 0.0666667)
...
frame 28: [0.933333, 0.966667)
frame 29: [0.966667, 1.0) -> Last frame

So, considering the previous details and a 't'
variable that is a specific time moment within
a video, when t=0.01, as you can see, the
interval hits the frame 0 because 0.01 / 0.03333
= 0, but when t=0.04, the interval hits the frame
1 because 0.04 / 0.03333 = 1.

When working with python, floating points and 
periodic numbers, we have to consider that we can
obtain results like 0.3333333333333326, which is
actually lower than 0.3333333333333333 due to
a bad precision, so when we do the division the
result will be wrong. We will use a small amount
we add in any situation to make sure we avoid
those errors when calculating something related
to a 't' time moment.

Each moviepy video is a sequence of
frames. Each frame can be normal or
can have a second related frame that
is a mask frame.

The normal frame is a 'np.uint8' and
has a (height, width, 3) shape. The
range of values is [0, 255] for each
color channel (R, G, B), where 0 
means no color and 255 full color.
For example, a frame of a 720p video
would have a (720, 1280, 3) shape.

The mask frame is a 'np.float32' or
'np.float64' and has a (height,
width) shape. The range of values is
[0.0, 1.0] for each value, where 0.0
means completely transparent and 1.0
means completely opaque. For example,
a frame of a 720p video would have 
(720, 1280) shape.

A mask frame can be attached to a 
normal frame but not viceversa. So,
a normal frame can (or cannot) have
a mask frame attached.

TODO: Copied from 'yta_multimedia'
Using the 'get_frame' in moviepy returns a numpy array of 3 or 1 
dimension depending on the type of clip. If the clip is a main 
clip, a 3d array with values between [0, 255] is returned (one
[255, 255, 255] array would be a white pixel). If the clip is a
mask clip, a 1d array with values between [0, 1] is returned (the
1 completely transparent, the 0 is not).

Thats why you need to normalize or denormalize those values to
work with them because they are different and turning frames into
an image would need you to have the same range [0, 1] or [0, 255].

Check the Pillow, ImageIO and other libraries to see what kind of
numpy arrays are needed to write (or read) images.

TODO: This was in the previous 'frames.py' file that was moved to
a whole module in a folder. Do I need this explanation here (?)
"""
from yta_numpy.video.moviepy.frame_handler import NumpyFrameHelper
from yta_constants.video import MoviepyFrameMaskingMethod
from dataclasses import dataclass

import numpy as np


@dataclass
class MoviepyVideoFrame:
    """
    Class to represent a video frame, to simplify the way
    we turn it into a mask and work with it. A mask frame
    is a numpy array with single values per pixel and 
    values between 0.0 and 1.0 (where 0.0 is full 
    full transparent and 1.0 is full opaque). A normal
    frame is a numpy array with 3 values per pixel
    (representing R, G, B) between 0 and 255 (where 0 is
    the absence of color and 255 the full presence of that
    color).

    This class has been created to work easily with frames
    and to verify them when creating a new instance.
    """
    
    @property
    def is_mask(
        self
    ):
        """
        Indicate if the 'frame' stored is a mask,
        which means that is a numpy array of single
        values between 0.0 and 1.0 (representing 
        the opacity: 0.0 is full transparent, 1.0 
        is full opaque).
        """
        return self._is_mask == True
    
    @property
    def is_normal(
        self
    ):
        """
        Indicate if the 'frame' stored is normal,
        which means that is a numpy array of 3 
        values (R, G, B) between 0 and 255 
        (representing the color presence: 0 is no
        color, 255 is full color).
        """
        return self._is_mask == False
    
    @property
    def inverted(
        self
    ):
        """
        Get the frame but inverted (each pixel
        will be transformed by substracting its
        value from the maximum value). This
        property does not modify the object
        itself.
        """
        return NumpyFrameHelper.invert(self.frame)
    
    @property
    def normalized(
        self
    ):
        """
        Get the frame but normalized (with values
        between 0.0 and 1.0). This property does
        not modify the object itself.
        """
        return NumpyFrameHelper.normalize(self.frame)
    
    @property
    def denormalized(
        self
    ):
        """
        Get the frame denormalized (with values
        between 0 and 255). This property does not
        modify the object itself.
        """
        return NumpyFrameHelper.denormalize(self.frame)

    def __init__(
        self,
        frame: np.ndarray
    ):
        if (
            not NumpyFrameHelper.is_rgb_not_normalized(frame) and
            not NumpyFrameHelper.is_rgb_normalized(frame) and
            not NumpyFrameHelper.is_alpha_normalized(frame) and
            not NumpyFrameHelper.is_alpha_not_normalized(frame)
        ):
            # TODO: Print properties to know why it is not valid
            raise Exception('The provided "frame" is not a valid frame.')

        is_mask = False
        if NumpyFrameHelper.is_alpha(frame):
            is_mask = True
            # We ensure it is a normalized alpha frame to store it
            frame = NumpyFrameHelper.as_alpha(frame)
        elif NumpyFrameHelper.is_rgb(frame):
            # We ensure it is a not normalized normal frame to store it
            frame = NumpyFrameHelper.as_rgb(frame)
        else:
            raise Exception('The provided "frame" is not an alpha nor a rgb frame.')

        self.frame: np.ndarray = frame
        """
        The frame information as a numpy array.
        This array can only contain frames in
        the format of not normalized RGB (array
        of 3 values from 0 to 255 per pixel) or
        normalized alpha (1 single value per
        pixel from 0.0 to 1.0).
        """
        self._is_mask = is_mask
        """
        Boolean value, autodetected internally,
        to indicate if the frame is a mask
        frame or is not.
        """

    def as_mask(
        self,
        masking_method: MoviepyFrameMaskingMethod = MoviepyFrameMaskingMethod.MEAN
    ):
        """
        Return the frame as a mask by applying
        the 'masking_method' if necessary.
        """
        masking_method = MoviepyFrameMaskingMethod.to_enum(masking_method)

        return normal_frame_to_mask(self.frame, masking_method)

# Utils below
def normal_frame_to_mask(
    frame: np.ndarray,
    masking_method: MoviepyFrameMaskingMethod = MoviepyFrameMaskingMethod.MEAN
) -> np.ndarray:
    """
    Transform the normal moviepy video
    'frame' provided to a mask frame by
    using the also given 'masking_method'.
    """
    return (
        frame
        if NumpyFrameHelper.is_alpha(frame) else
        NumpyFrameHelper.as_alpha(
            frame = frame,
            do_normalize = True,
            masking_method = masking_method
        )
    )