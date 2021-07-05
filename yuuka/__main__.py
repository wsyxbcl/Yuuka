import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, ParseMode, message, \
    InputTextMessageContent, InlineQueryResultPhoto

from .lib.eflora import search_iplant

# Configure logging
logging.basicConfig(filename="./yuuka_bot.log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Initialize bot and dispatcher
config = toml.load("yuuka.toml")
bot = Bot(token=config["telegram"]["token"])
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message):
    await message.reply("Still under construction, currently a iplant.cn forward bot.\n"
                        "/help if you need, contribute or build your own from https://github.com/wsyxbcl/Yuuka") 

@dp.message_handler(commands=['search'])
async def search(message):
    logging.info(f'{message.text}')
    try:
        keyword = message.text.split()[1]
    except IndexError:
        raise
    results = search_iplant(keyword)
    if len(results) == 1:
        await message_reply(results[0]['url'])
    else:
        keyboard_markup = types.InlineKeyboardMarkup()
        for plant in results:
            keyboard_markup.row(types.InlineKeyboardButton(plant['data'], url=plant['url']))
        # add exit button
        keyboard_markup.row(types.InlineKeyboardButton('exit', callback_data='exit'))
        await message.reply("Multiple results", reply_markup=keyboard_markup)

    