from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import constants

bot = Bot(token=constants.API_KEY)
dp = Dispatcher(bot, storage=MemoryStorage())


class Order(StatesGroup):
    size = State()
    payment_method = State()


sizes = ['большую', 'маленькую']
payment_methods = ['наличкой', 'по карте']


@dp.message_handler(commands='start')
async def start_command(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for s in sizes:
        buttons.append(types.InlineKeyboardButton(text=s, callback_data=s))

    keyboard.add(*buttons)

    await message.reply('Какую вы хотите пиццу? Большую или маленькую?', reply_markup=keyboard)


@dp.callback_query_handler(text=sizes)
async def set_payment(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['size'] = query.data

    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for p in payment_methods:
        buttons.append(types.InlineKeyboardButton(text=p, callback_data=p))

    keyboard.add(*buttons)

    await bot.send_message(chat_id=query.message.chat.id, text='Как вы будете платить?', reply_markup=keyboard)


@dp.callback_query_handler(text=payment_methods)
async def set_size(query: types.CallbackQuery, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text='да', callback_data='да'),
        types.InlineKeyboardButton(text='нет', callback_data='нет')
    ]

    keyboard.add(*buttons)

    async with state.proxy() as proxy:
        await bot.send_message(
            chat_id=query.message.chat.id,
            text=f'Вы хотите {proxy["size"]} пиццу, оплата - наличкой?',
            reply_markup=keyboard)


@dp.callback_query_handler(text=['да', 'нет'])
async def set_complete(query: types.CallbackQuery):
    await bot.send_message(chat_id=query.message.chat.id, text='Спасибо за заказ')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)