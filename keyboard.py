from telebot import types


MAIN_KEYBOARD = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
MAIN_KEYBOARD.add(*['Подать объявление', 'Взять напрокат'])


CANCEL_BUTTON = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
CANCEL_BUTTON.add('Отмена')


HIDE_KEYBOARD = types.ReplyKeyboardRemove()
