from telebot import types


MAIN_KEYBOARD = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
MAIN_KEYBOARD.add(*['Взять напрокат'])
MAIN_KEYBOARD.add(*['Подать объявление','Мои объявления'])



CANCEL_BUTTON = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
CANCEL_BUTTON.add('Отмена')


HIDE_KEYBOARD = types.ReplyKeyboardRemove()
