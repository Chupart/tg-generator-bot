import logging
import time
import asyncio
from aiolimiter import AsyncLimiter

def tg_disabled_check(func):
    """Decorator to check if telegram communication is disabled."""
    async def wrapper(instance, *args, **kwargs):
        # Determine which instance type we're dealing with
        is_disabled = instance.is_disabled if isinstance(instance, TgStatusWrapper) else instance.wrapper.is_disabled
        logger = instance.logger if isinstance(instance, TgStatusWrapper) else instance.wrapper.logger
        if is_disabled:
            class FakeMessage:
                async def reply(self, *args, **kwargs):
                    logger.info(f"TG DISABLED: {func.__name__} with args: {args} and kwargs: {kwargs}")

            logger.info(f"TG DISABLED: {func.__name__} with args: {args} and kwargs: {kwargs}")
            return WrappedMessage(FakeMessage(), instance)
        return await func(instance, *args, **kwargs)
    return wrapper



class TgStatusWrapper:
    # This means 1 request can be made every 0.5 seconds
    RATE = 1
    PER = 0.5

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.limiter = AsyncLimiter(self.RATE, self.PER)
        self.is_disabled = False

    def disable(self):
        self.is_disabled = True

    def enable(self):
        self.is_disabled = False

    async def truncate_message(self, message_text):
        if len(message_text) > 4000:
            self.logger.warning("Message truncated due to exceeding length limit.")
            return message_text[:4000] + "...(truncated)"
        return message_text

    @tg_disabled_check
    async def reply(self, message, text):
        async with self.limiter:
            text = await self.truncate_message(text)
            result = await message.reply(text)
            self.logger.info(text)
            return WrappedMessage(result, self)

    @tg_disabled_check
    async def _delete(self, message):
        async with self.limiter:
            await message.delete()

    @tg_disabled_check
    async def _edit(self, message, text, parse_mode):
        async with self.limiter:
            text = await self.truncate_message(text)
            await message.edit_text(text, parse_mode)


class WrappedMessage:
    def __init__(self, message, wrapper):
        self.message = message
        self.wrapper = wrapper

    @tg_disabled_check
    async def edit_text(self, text, parse_mode=None):
        self.wrapper.logger.info(text)
        await self.wrapper._edit(self.message, text, parse_mode=parse_mode)

    @tg_disabled_check
    async def delete(self):
        self.wrapper.logger.info(f"Deleting message with ID: {self.message.message_id}")
        await self.wrapper._delete(self.message)
