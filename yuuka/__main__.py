# from io import BytesIO
import logging
import toml

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, ParseMode, message, \
    InputTextMessageContent, InlineQueryResultPhoto

from lib.eflora import search_cvh, species_info_cvh, cvh_base_url, iplant_base_url, iplant_value_from_latin
from lib.plantcv import photo_to_species


# Configure logging
logging.basicConfig(filename="./yuuka_bot.log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Initialize bot and dispatcher
config = toml.load("./yuuka.toml")
try:
    bot = Bot(token=config["telegram"]["token"], proxy=config["telegram"]["proxy"])
except KeyError:
    bot = Bot(token=config["telegram"]["token"])
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message):
    await message.reply("Plant recognition is in testing, send tg compressed image to get result.") 

@dp.message_handler(content_types="photo")
async def plant_recognition(message):
    """
    powered by quarrying-plant-id(https://github.com/quarrying/quarrying-plant-id)
    """
    # TODO bytesio for image
    # buf = BytesIO()
    # await message.photo[-1].download(buf)
    # buf.seek(0)
    await message.photo[-1].download(destination_file="./photo.jpg", make_dirs=False)
    msg = ""
    if (results := photo_to_species('./photo.jpg')) is None:
        msg = "Failed to recognize"
    else:
        for species in results:
            msg += "[{}]({}) _{}_ ({:.3f})\n".format(species['taxon_chinese'].replace('_', ' '), 
                                                     iplant_base_url.format(value=iplant_value_from_latin(species['value'])),
                                                     species['value'], 
                                                     species['probability'])
    await message.reply(msg, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['search'])
async def search(message):
    logging.info(f'{message.text}')
    try:
        keyword = message.text.split(' ', 1)[1]
    except IndexError:
        raise
    results = search_cvh(keyword)

    keyboard_markup = types.InlineKeyboardMarkup()
    for plant in results:
        plant_name = plant['desc'] + " {}".format(plant['value'])
        keyboard_markup.row(types.InlineKeyboardButton(plant_name, callback_data=' '.join(filter(None, ['/info', plant['value']]))))
    # add exit button
    keyboard_markup.row(types.InlineKeyboardButton('exit', callback_data='exit'))
    await message.reply("Find {} in CVH 植物物种名录".format(keyword), reply_markup=keyboard_markup)

@dp.message_handler(commands=['info'])
async def info(message, query=None):
    logging.info(f'{message.text}')
    species = message.text.split(' ', 1)[1]
    species_info = species_info_cvh(species)
    species_taxon = ' -> '.join([species_info['taxon']['family_c']+"<em>{}</em>".format(species_info['taxon']['family']), 
                                 species_info['taxon']['genus_c']])
    species_links = ' '.join(["more info:", 
                              '<a href="{}">iplant</a>'.format(iplant_base_url.format(value=iplant_value_from_latin(species_info['canName']))), 
                              '<a href="{}">CVH</a>'.format(cvh_base_url.format(value=species_info['canName']))])
    try:
        species_text = '\n'.join([species_taxon, 
                                species_info['chName']+' '+species_info['sciName'], 
                                species_links])
    except KeyError:
        species_text = '\n'.join([species_taxon, 
                                species_info['sciName'], 
                                species_links])
    await query.message.answer(species_text, parse_mode=ParseMode.HTML)

@dp.callback_query_handler(lambda cb: '/info' in cb.data)
@dp.callback_query_handler(text='exit')
async def inline_search_answer_callback_handler(query):
    logging.info(f'{query.inline_message_id}: {query.data}')
    if query.data == 'exit':
        await query.message.delete()
        return 1
    # await search(message.Message(text=query.data), query=query)
    await info(message.Message(text=query.data), query=query)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
