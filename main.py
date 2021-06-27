import os
import datetime

from conf.settings import LOGGING_SETTINGS, TELEGRAM_TOKEN
from libs.validators import is_url
from libs.youtube import download_yt_video
from libs.file_system import FileSystem

from pytube import exceptions as yt_exceptions
from loguru import logger
from aiogram import Bot, Dispatcher, executor, types
import aiogram

file_sys = FileSystem()
file_sys.create_file_struct()

bot_log_dir = file_sys.LOG_DIR.joinpath(f"bot{datetime.date.today()}")

bot_log_dir.mkdir(exist_ok=True)

logger.add(
    bot_log_dir / "bot.json",
    **LOGGING_SETTINGS
)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_message(mes: types.Message):
    await mes.reply("кинь ютуб ссылку")


@dp.message_handler()
async def common_message(mes: types.Message):
    if not is_url(mes.text):
        await mes.answer("Отправьте ссылку, а не вот это")
        return

    await mes.answer("Пытаюсь скачать youtube видео....")

    try:
        file_path = await download_yt_video(
            str(mes.text),
            f"media/{mes.chat.id}",
        )
    except KeyError as err:
        await mes.answer(
            "Видимо вы отправили ссылку на " + "трансляцию.... не надо так"
        )
        logger.info(f"Send stream link: |{mes.text=}|{err=}|{mes.chat.id=}")
        return
    except yt_exceptions.VideoPrivate as err:
        await mes.answer("Видео находится в приватном доступе")
        logger.info(f"Send private video: |{mes.text=}|{err=}|{mes.chat.id=}")
        return
    except yt_exceptions.VideoRegionBlocked as err:
        await mes.answer("Видео заблочено в моем регионе")
        logger.info(f"Blocked video: |{mes.text=}|{err=}|{mes.chat.id=}")
        return
    except yt_exceptions.VideoUnavailable as err:
        await mes.answer("Видео недоступно по хз какой причине")
        logger.info(f"Video Unavaible: |{mes.text=}|{err=}|{mes.chat.id=}")
        return

    await mes.answer("Видео скачано, отправляю...")

    try:
        await mes.answer_audio(types.InputFile(file_path))
    except aiogram.exceptions.NetworkError as err:
        await mes.answer(
            "Слишком длинное и тяжелое видео... " +
            "телеграм не может такое отправить"
        )
        logger.info(f'Video too large: |{mes.text=}|{err=}|{mes.chat.id=}')
    finally:
        # delete audio file
        try:
            os.remove(file_path)
            logger.info(f"{file_path=} was deleted")
        except OSError as err:
            logger.error(err)


if __name__ == "__main__":
    executor.start_polling(dp)
