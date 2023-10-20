import asyncio
import base64
import hashlib
import json
import logging
import os
import re
import sys
from io import BytesIO
from typing import io

import aiogram
import dotenv
from aiogram import Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InputFile, BotCommand
from aiogram.types.input_media_photo import InputMediaPhoto

from draw_things_api_wrapper import DrawThingApiWrapper
from prompt_generator import PromptGenerator
from templater import ParamsTemplate
from tg_status_wrapper import TgStatusWrapper

# Load .env file
dotenv.load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

telegram_wrapper = TgStatusWrapper()
api_url = os.getenv("PROMPT_GENERATOR_ENDPOINT")
generator = PromptGenerator(api_url=api_url)

bot = aiogram.Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(bot=bot)
tg_router = Router()

txt2img_endpoint = os.getenv("TXT2IMG_ENDPOINT")
templater = ParamsTemplate()
api_wrapper = DrawThingApiWrapper(txt2img_endpoint, generator, templater)


def tg_command_args(msg: str):
    _, *args = msg.split(maxsplit=1)
    return "".join(args)


async def send_welcome(message: Message):
    await message.answer("Hello! I'm image genertion bot. Type /help to see what I can do.")


async def send_api_example(message: Message):
    await message.answer(json.dumps(templater.render_api_params({}), indent=4, sort_keys=True))


async def send_help(message: Message):
    await message.answer(templater.render_help(), parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)


async def on_generate_long(message: Message):
    await on_generate(message=message, long_message=True)


async def on_generate(message: Message, long_message: bool = False):
    msg_text = tg_command_args(message.text)
    logger.info(f"Received message: {msg_text}")
    to_del = await message.reply(f"Received message, generating prompts...")
    payloads = api_wrapper.get_generation_request_json(msg_text)

    # Initializing generation_results object
    generation_results = [{'payload': payload, 'images': [], 'message_ids': []} for payload in payloads]

    try:
        await to_del.delete()
        for index, gen_result in enumerate(generation_results):
            await process_single_payload(message, index, generation_results, long_message)
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await message.reply(f"An error occurred. Please try again later. Error: {e}")


tg_router.message.register(send_welcome, CommandStart())
tg_router.message.register(send_help, Command("help"))
tg_router.message.register(on_generate, Command("gen"))
tg_router.message.register(on_generate_long, Command("gen_long"))
tg_router.message.register(send_api_example, Command("api_def"))


async def process_single_payload(message: Message, index: int, generation_results: list, long_message: bool = False):
    gen_result = generation_results[index]
    processing_message = None
    txt_msg = f'🔄 Generating with parameters for payload {index + 1} out of {len(generation_results)}: ' \
              f'{json.dumps(gen_result["payload"], indent=4, sort_keys=True)}' \
        if long_message else f'🔄Generating image {index + 1} out of {len(generation_results)}'
    processing_message = await message.reply(txt_msg)

    images_data_base64_list = api_wrapper.send_request(gen_result['payload'])

    if images_data_base64_list:
        gen_result['images'].extend(images_data_base64_list)
        await send_images_incrementally_in_gallery(message, index, generation_results)
        await processing_message.delete()
    else:
        await processing_message.edit_text("Failed to generate images.")


async def send_images_incrementally_in_gallery(message: Message, index: int, generation_results: list):
    gen_result = generation_results[index]

    # Aggregate all previously sent message_ids
    all_previous_message_ids = [
        msg_id
        for result in generation_results[:index + 1]
        for msg_id in result['message_ids']
    ]

    # Delete previous media groups if they exist
    for msg_id in all_previous_message_ids:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            logger.info(f"Deleted message with ID: {msg_id}")
        except Exception as e:
            logger.error(f"Failed to delete message with ID: {msg_id}. Error: {str(e)}")

    media = []

    # Initialize a counter for unique image identifiers across all payloads
    img_counter = 0

    # Loop over all relevant generation_results entries
    for i, result in enumerate(generation_results[:index + 1]):
        prompt = result['payload']['prompt']
        for img_data in result['images']:
            image_data_binary = base64.b64decode(img_data)
            photo = InputMediaPhoto(
                media=aiogram.types.input_file.BufferedInputFile(image_data_binary, f"{prompt} batch# {img_counter}"),
                caption=f"{prompt} batch# {img_counter}")
            media.append(photo)
            img_counter += 1  # Increment the counter after using its value

    # Send new media group and update message_ids in generation_results
    try:
        sent_messages = await bot.send_media_group(chat_id=message.chat.id, media=media)
        generation_results[index]['message_ids'] = [msg.message_id for msg in sent_messages]
        logger.info(f"Sent media group with IDs: {[msg.message_id for msg in sent_messages]}")
    except Exception as e:
        logger.error(f"Failed to send media group. Error: {str(e)}")


async def main() -> None:
    dp.include_router(tg_router)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
