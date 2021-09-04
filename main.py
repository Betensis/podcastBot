import datetime

from conf.settings import LOGGING_SETTINGS, TELEGRAM_TOKEN
from libs.validators import is_url
from libs.youtube import install_file, send_file
from libs.file_system import FileSystem
from loguru import logger
from aiogram import Bot, Dispatcher, executor, types


file_sys = FileSystem()
file_sys.create_file_struct()

bot_log_dir = file_sys.LOG_DIR.joinpath(f"bot{datetime.date.today()}")

bot_log_dir.mkdir(exist_ok=True)

logger.add(bot_log_dir / "bot.json", **LOGGING_SETTINGS)

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
    file_path = await install_file(mes)
    if file_path:
        await send_file(mes, file_path)
    else:
        mes.answer_photo(
            "https://cdn.pixabay.com/photo/2014/11/30/14/11/cat-551554_960_720.jpg"
        )


if __name__ == "__main__":
    print("---START---")
    executor.start_polling(dp)
