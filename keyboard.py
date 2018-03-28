from telebot import types
from json import dumps


MAIN_KEYBOARD = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
MAIN_KEYBOARD.add(*['Взять напрокат'])
MAIN_KEYBOARD.add(*['Подать объявление','Мои объявления'])


def GLOBAL_INLINE_KEYBOARD(ad, remove_contact_btn=False):
    k = types.InlineKeyboardMarkup(row_width=2)
    next_button = types.InlineKeyboardButton(text=">>", callback_data=json.dumps({"type":"next", "id":ad.id}))
    prev_button = types.InlineKeyboardButton(text="<<", callback_data=json.dumps({"type":"prev", "id":ad.id}))
    contact_button = types.InlineKeyboardButton(text="Взять напрокат", callback_data=json.dumps({"type":"rent", "id":ad.id}))
    k.add(prev_button, next_button)
    if not remove_contact_btn:
        k.add(contact_button)
    return k

def OWNER_INLINE_KEYBOARD(ad, remove_service_btns=False):
    k = types.InlineKeyboardMarkup(row_width=2)
    next_button = types.InlineKeyboardButton(text=">>", callback_data=json.dumps({"type":"my_next", "id":ad.id}))
    prev_button = types.InlineKeyboardButton(text="<<", callback_data=json.dumps({"type":"my_prev", "id":ad.id}))
    edit_button = types.InlineKeyboardButton(text="Редактировать", callback_data=json.dumps({"type":"edit", "id":ad.id}))
    hide_button = types.InlineKeyboardButton(text= "Скрыть" if ad.published else "Опубликовать", callback_data=json.dumps({"type":"toggle_hide", "id":ad.id}))
    delete_button = types.InlineKeyboardButton(text="Удалить", callback_data=json.dumps({"type":"delete", "id":ad.id}))
    k.add(prev_button, next_button)
    if not remove_service_btns:
        k.add(edit_button)
        k.add(delete_button, hide_button)
    return k


CANCEL_BUTTON = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
CANCEL_BUTTON.add('Отмена')


HIDE_KEYBOARD = types.ReplyKeyboardRemove()
