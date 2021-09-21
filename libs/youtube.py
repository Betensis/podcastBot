import datetime
import os
from typing import Optional
import aiogram

import pytube
from pytube import exceptions as yt_exceptions
from loguru import logger
from aiogram import types

from libs.file_system import FileSystem
from conf.settings import LOGGING_SETTINGS


file_sys = FileSystem()
file_sys.create_file_struct()

logging_path = file_sys.LOG_DIR.joinpath(f"youtube{datetime.date.today()}")
logging_path.mkdir(exist_ok=True)

logger.add(sink=logging_path / "youtube.json", **LOGGING_SETTINGS)


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
    except yt_exceptions.VideoRegionBlocked as e:
        logger.info(f'Video: "{yt_video.title}" from "{url}" is region blocked. {e}')
        raise e
    except yt_exceptions.VideoUnavailable as e:
        logger.info(f'Video: "{yt_video.title}" from "{url}" is unavailable. {e}')
        raise e

    return (
        yt_video.streams.filter(only_audio=True)
        .order_by("abr")
        .first()
        .download(output_path=output_path)
    )


async def install_file(mes: types.Message) -> Optional[str]:
    try:
        file_path = await download_yt_video(
            str(mes.text),
            f"media/{datetime.date.today()}",
        )
    except KeyError as err:
        await mes.answer(
            "Видимо вы отправили ссылку на " + "трансляцию.... не надо так"
        )
        logger.info(f"Send stream link: |{mes.text=}|{err=}|{mes.chat.id=}")
    except yt_exceptions.VideoPrivate as err:
        await mes.answer("Видео находится в приватном доступе")
        logger.info(f"Send private video: |{mes.text=}|{err=}|{mes.chat.id=}")
    except yt_exceptions.VideoRegionBlocked as err:
        await mes.answer("Видео заблочено в моем регионе")
        logger.info(f"Blocked video: |{mes.text=}|{err=}|{mes.chat.id=}")
    except yt_exceptions.VideoUnavailable as err:
        await mes.answer("Видео недоступно по хз какой причине")
        logger.info(f"Video Unavaible: |{mes.text=}|{err=}|{mes.chat.id=}")

    await mes.answer("Видео скачано, отправляю...")
    return file_path or None


async def send_file(mes, file_path: str):
    try:
        await mes.answer_audio(types.InputFile(file_path))
    except aiogram.exceptions.NetworkError as err:
        await mes.answer(
            "Слишком длинное и тяжелое видео... " + "телеграм не может такое отправить"
        )
        logger.info(f"Video too large: |{mes.text=}|{err=}|{mes.chat.id=}")
    finally:
        # delete audio file
        try:
            os.remove(file_path)
            logger.info(f"{file_path=} was deleted")
        except OSError as err:
            logger.error(err)
