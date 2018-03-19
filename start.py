import config
import keyboard
import db

import telebot

# словарь тех, кто сейчас редактирует объявление
currentEditors = {}

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "hello", reply_markup=keyboard.MAIN_KEYBOARD)


@bot.message_handler(func=lambda message: message.text=='Подать объявление', content_types=['text'])
def new_ad(message):
    msg = bot.send_message(
        message.chat.id, 
        "Пришлите мне заголовок объявления", 
        reply_markup=keyboard.CANCEL_BUTTON)

    bot.register_next_step_handler(msg, new_ad_step_2)

def new_ad_step_2(message):
    if message.text == 'Отмена':
        bot.send_message(
            message.chat.id, 
            "Операция отменена", 
            reply_markup=keyboard.MAIN_KEYBOARD)
        return

    if message.text.strip() == '':
        msg = bot.send_message(
            message.chat.id, 
            "Кажется, что-то пошло не так. Пришлите мне заголовок объявления", 
            reply_markup=keyboard.CANCEL_BUTTON)
        bot.register_next_step_handler(msg, new_ad_step_2)
        return


    currentEditors[message.chat.id] = db.Ad(title=message.text.strip())

    msg = bot.send_message(
        message.chat.id, 
        """Спасибо!\nА теперь пришлите мне цену, за которую вы готовы отдать велосипед в аренду.\nЭто может быть не только цена в рублях, но и вещь или услуга.
        """, 
        reply_markup=keyboard.CANCEL_BUTTON)
    bot.register_next_step_handler(msg, new_ad_step_3)


def new_ad_step_3(message):
    if message.text == 'Отмена':
        bot.send_message(
            message.chat.id, 
            "Операция отменена", 
            reply_markup=keyboard.MAIN_KEYBOARD)
        del currentEditors[message.chat.id]
        return

    if message.text.strip() == '':
        msg = bot.send_message(
            message.chat.id, 
            "Кажется, что-то пошло не так. Пришлите мне цену.", 
            reply_markup=keyboard.CANCEL_BUTTON)
        bot.register_next_step_handler(msg, new_ad_step_3)
        return

    currentEditors[message.chat.id].price = message.text.strip()

    currentEditors[message.chat.id].ownerId = message.from_user.id
    currentEditors[message.chat.id].published = True
    session = db.Session()
    session.add(currentEditors[message.chat.id])
    session.commit()
    session.close()

    del currentEditors[message.chat.id]


    bot.send_message(
        message.chat.id, 
        """Спасибо!\nВаше объявление опубликовано!.
        """, 
        reply_markup=keyboard.MAIN_KEYBOARD)











@bot.message_handler(func=lambda message: message.text=='Взять напрокат', content_types=['text'])
def new_rent(msg):

    # тут нужна проверка авторизации
    session = db.Session()
    ads = session.query(db.Ad).filter(db.Ad.published==True).all()

    response_message_text = ''
    num = 0
    for ad in ads:
        num+=1
        response_message_text+='{num}. <b>{title}</b>\nЦена: {price}\n\n'.format(
            title=ad.title.capitalize(), 
            price=ad.price, 
            num=num)


    bot.send_message(msg.chat.id, response_message_text, parse_mode='HTML', reply_markup=keyboard.MAIN_KEYBOARD)

if __name__ == '__main__':
    bot.polling(none_stop=True)
