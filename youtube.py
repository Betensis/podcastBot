import os
import logging
import datetime

import pytube
from pytube import exceptions as yt_exceptions
import asyncio
from loguru import logger

from config.config import BASE_DIR, LOG_DIR, LOGGING_LVL


logging_path = LOG_DIR.joinpath(f'youtube{datetime.date.today()}')
logging_path.mkdir(exist_ok=True)

logger.add(
    logging_path / "youtube.json",
    level=LOGGING_LVL,
    rotation="100 MB",
    serialize=True,
    compression="zip",
    backtrace=True,
    catch=True,
)


async def download_yt_video(url: str, output_path: str = "") -> str:
    """download youtube video

    Args:
        url (str): youtube link
        output_path (str, optional): Output path for writing media file. Defaults to current directory.

    Returns:
        str: absolute path to saved file
    """
    logger.info(f"Try download video from {url=}")
    yt_video = pytube.YouTube(url)
    
    try:
        yt_video.check_availability()
    except yt_exceptions.VideoPrivate as e:
        logger.info(f'Video: "{yt_video.title}" from "{url}" is privat. {e}')
        raise e
    except yt_exceptions.VideoRegionBlocked:
        logger.info(f'Video: "{yt_video.title}" from "{url}" is region blocked. {e}')
        raise e
    except yt_exceptions.VideoUnavailable:
        logger.info(f'Video: "{yt_video.title}" from "{url}" is unavailable. {e}')
        raise e

    return (
        yt_video.streams.filter(only_audio=True)
        .order_by("abr")
        .first()
        .download(output_path=output_path)
    )