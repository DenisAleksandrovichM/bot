import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile
from config import tg_bot_key
from db import fetchall, insert
from messages import get_message_function
from order_processing import check_order_update, get_response

bot = Bot(token=tg_bot_key, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


class User(StatesGroup):
    token = State()


@dp.message_handler(Command('start'), state=None)
async def start(message: types.Message):
    user = fetchall('user', ('id', 'wb_key'), f'id = {message.from_user.id}')
    if len(user):
        await message.answer(f'Вы уже привязали к вашему пользователю Api-ключ {user[0]["wb_key"]}')
    else:
        await message.answer('Введите Ваш ключ для работы с API статистики x64:')
        await User.token.set()


@dp.message_handler(state=User.token)
async def process_key(message: types.Message, state: FSMContext):
    if len(message.text) == 48:
        for i in range(5):
            success = get_response(message.text).status_code == 200
            if success:
                await message.answer('Вы успешно привязали Ваш Api-ключ к боту')
                await state.finish()
                insert('user', {'id': message.from_user.id, 'wb_key': message.text})
                return

    await message.answer('Что-то пошло не так.')
    await start(message)


async def process_orders(user_data, mode):
    message = get_message_function(mode)
    if message is None:
        return

    fresh_orders = check_order_update(user_data, mode == 'O')
    if fresh_orders is None:
        return
    elif isinstance(fresh_orders, tuple):
        for item in fresh_orders:
            await send_orders(item, user_data, message)
    else:
        await send_orders(fresh_orders, user_data, message)

    await asyncio.sleep(10)


async def send_orders(fresh_orders, user_data, message):
    for value in fresh_orders:
        await bot.send_photo(
            user_data['id'],
            photo=InputFile.from_url(
                f'https://images.wbstatic.net/big/new/{str(value["nmId"])[:4]}0000/{value["nmId"]}-1.jpg'
            ),
            caption=message(value))
        await asyncio.sleep(0.3)


async def main():
    while True:
        users = fetchall('user', ('id', 'wb_key'))
        for user in users:
            for mode in ('O', 'S', 'R'):
                await process_orders(user, mode)
        await asyncio.sleep(60)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    executor.start_polling(dp, skip_updates=True)
