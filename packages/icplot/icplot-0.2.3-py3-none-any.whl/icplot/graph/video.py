"""
Module for handling videos
"""

from pathlib import Path

from moviepy.video.io import ImageSequenceClip

from iccore.filesystem import get_files


def images_to_video(
    image_path: Path,
    output_path: Path,
    filename: str,
    fps: int = 5,
    image_format: str = "png",
    video_format: str = "mp4",
):
    """
    Convert an image to a video
    """

    images = get_files(image_path, image_format)

    def key(x):
        return int(x.stem)

    image_paths = sorted(images, key=key)
    images = [str(image) for image in image_paths]
    clip = ImageSequenceClip.ImageSequenceClip(images, fps=fps)
    clip.write_videofile(str(output_path / f"{filename}.{video_format}"))

    for image in image_paths:
        image.unlink()
