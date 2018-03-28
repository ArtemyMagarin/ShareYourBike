import config
import keyboard
import db
import json
from sqlalchemy import desc
from telebot import types

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
    currentEditors[message.chat.id].ownerUsername = message.from_user.username


    if message.from_user.username:
        currentEditors[message.chat.id].published = True
        session = db.Session()
        session.add(currentEditors[message.chat.id])
        session.commit()
        session.close()

        del currentEditors[message.chat.id]


        bot.send_message(
            message.chat.id, 
            """Спасибо!\nВаше объявление опубликовано!
            """, 
            reply_markup=keyboard.MAIN_KEYBOARD)
    else:
        msg = bot.send_message(
        message.chat.id, 
        """Спасибо!\nА как с вами связаться?\nПришлите мне ваш номер телефона или ссылку на профиль в VK
        """, 
        reply_markup=keyboard.CANCEL_BUTTON)
        bot.register_next_step_handler(msg, new_ad_step_4)


def new_ad_step_4(message):
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
            "Кажется, что-то пошло не так. Пришлите мне ваш номер телефона или ссылку на профиль в VK.", 
            reply_markup=keyboard.CANCEL_BUTTON)
        bot.register_next_step_handler(msg, new_ad_step_4)
        return

    currentEditors[message.chat.id].ownerContact = message.text.strip()
    currentEditors[message.chat.id].published = True
    session = db.Session()
    session.add(currentEditors[message.chat.id])
    session.commit()
    session.close()

    del currentEditors[message.chat.id]


    bot.send_message(
        message.chat.id, 
        """Спасибо!\nВаше объявление опубликовано!
        """, 
        reply_markup=keyboard.MAIN_KEYBOARD)





@bot.message_handler(func=lambda message: message.text=='Мои объявления', content_types=['text'])
def show_my_ads(msg):
    session = db.Session()
    ad = session.query(db.Ad).filter(db.Ad.ownerId==msg.chat.id).filter(db.Ad.deleted==False).first()
    session.close()

    if not ad:
        response_message_text = 'Объявлений пока нет.'
        bot.send_message(msg.chat.id, response_message_text, parse_mode='HTML', reply_markup=keyboard.MAIN_KEYBOARD)
        return

    response_message_text = '<b>{title}</b>\nЦена: {price}\n\n'.format(
        title=ad.title.capitalize(), 
        price=ad.price)


    k = keyboard.OWNER_INLINE_KEYBOARD(ad)

    bot.send_message(msg.chat.id, response_message_text, parse_mode='HTML', reply_markup=k)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline_my(call):
    data = json.loads(call.data)
    session = db.Session()

    if data['type'] == "my_next":
        ad = session.query(db.Ad).filter(db.Ad.ownerId==call.message.chat.id).filter(db.Ad.deleted==False).filter(db.Ad.id > data['id']).first()

        if not ad:
            ad = session.query(db.Ad).filter(db.Ad.ownerId==call.message.chat.id).filter(db.Ad.deleted==False).first()
 
        session.close()
        response_message_text = '<b>{title}</b>\nЦена: {price}\n\n'.format(
        title=ad.title.capitalize(), 
        price=ad.price)

        k = keyboard.OWNER_INLINE_KEYBOARD(ad)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", text=response_message_text, reply_markup=k)

    if data['type'] == "my_prev":
        ad = session.query(db.Ad).filter(db.Ad.ownerId==call.message.chat.id).filter(db.Ad.deleted==False).order_by(desc(db.Ad.id)).filter(db.Ad.id < data['id']).first()

        if not ad:
            ad = session.query(db.Ad).filter(db.Ad.ownerId==call.message.chat.id).filter(db.Ad.deleted==False).order_by(desc(db.Ad.id)).first()


        session.close()
        response_message_text = '<b>{title}</b>\nЦена: {price}\n\n'.format(
        title=ad.title.capitalize(), 
        price=ad.price)

        k = keyboard.OWNER_INLINE_KEYBOARD(ad)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", text=response_message_text, reply_markup=k)


    if data['type'] == "edit":
        ad = session.query(db.Ad).filter(db.Ad.published==True).filter(db.Ad.deleted==False).filter(db.Ad.id == data['id']).first()
        session.close()

        
        response_message_text = '<b>В разработке</b>'
       
        k = keyboard.OWNER_INLINE_KEYBOARD(ad)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", text=response_message_text, reply_markup=k)

    if data['type'] == 'toggle_hide':
        ad = session.query(db.Ad).filter(db.Ad.id == data['id']).first()
        if ad.published:
            ad.published = False
        else:
            ad.published = True

        k = keyboard.OWNER_INLINE_KEYBOARD(ad)

        response_message_text = '<b>{title}</b>\nЦена: {price}\n\n'.format(
        title=ad.title.capitalize(), 
        price=ad.price)

        
        session.add(ad)
        session.commit()
        session.close()



        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", text=response_message_text, reply_markup=k)

    if data['type'] == 'delete':
        ad = session.query(db.Ad).filter(db.Ad.id == data['id']).first()
        ad.deleted = True
        k = keyboard.OWNER_INLINE_KEYBOARD(ad, True)

        session.add(ad)
        session.commit()
        session.close()

        response_message_text = '<b>Удалено</b>'


        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", text=response_message_text, reply_markup=k)


    if data['type'] == "next":
        ad = session.query(db.Ad).filter(db.Ad.published==True).filter(db.Ad.deleted==False).filter(db.Ad.id > data['id']).first()
        if not ad:
            ad = session.query(db.Ad).filter(db.Ad.deleted==False).filter(db.Ad.published==True).first() 
        session.close()
        response_message_text = '<b>{title}</b>\nЦена: {price}\n\n'.format(
        title=ad.title.capitalize(), 
        price=ad.price)

        k = keyboard.GLOBAL_INLINE_KEYBOARD(ad)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", text=response_message_text, reply_markup=k)

    if data['type'] == "prev":
        ad = session.query(db.Ad).filter(db.Ad.deleted==False).filter(db.Ad.published==True).order_by(desc(db.Ad.id)).filter(db.Ad.id < data['id']).first()
        if not ad:
            ad = session.query(db.Ad).filter(db.Ad.deleted==False).filter(db.Ad.published==True).order_by(desc(db.Ad.id)).first() 

        session.close()
        response_message_text = '<b>{title}</b>\nЦена: {price}\n\n'.format(
        title=ad.title.capitalize(), 
        price=ad.price)


        k = keyboard.GLOBAL_INLINE_KEYBOARD(ad)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", text=response_message_text, reply_markup=k)


    if data['type'] == "rent":
        ad = session.query(db.Ad).filter(db.Ad.deleted==False).filter(db.Ad.published==True).filter(db.Ad.id == data['id']).first()
        session.close()

        if not ad:
            response_message_text = '<b>Объявление удалено. Попробуйте подобрать что-то еще.</b>'
        else:
            # ТУТ ЛОГИКА УЧЕТА АКТИВНОСТИ

            if ad.ownerUsername:
                response_message_text="Для связи с владельцем велосипеда, перейдите к диалогу:\n\n t.me/"+ad.ownerUsername
            else:
                response_message_text="Для связи с владельцем велосипеда, воспользуйтесь этими контактными данными:\n\n"
                response_message_text+=ad.ownerContact

        k = keyboard.GLOBAL_INLINE_KEYBOARD(ad, remove_contact_btn=True):
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML", text=response_message_text, reply_markup=k)






@bot.message_handler(func=lambda message: message.text=='Взять напрокат', content_types=['text'])
def new_rent(msg):

    session = db.Session()
    ad = session.query(db.Ad).filter(db.Ad.deleted==False).filter(db.Ad.published==True).first()
    session.close()

    if not ad:
        response_message_text = 'Объявлений пока нет.'
        bot.send_message(msg.chat.id, response_message_text, parse_mode='HTML', reply_markup=keyboard.MAIN_KEYBOARD)
        return

    response_message_text = '<b>{title}</b>\nЦена: {price}\n\n'.format(
        title=ad.title.capitalize(), 
        price=ad.price)

    k = keyboard.GLOBAL_INLINE_KEYBOARD(ad)
    bot.send_message(msg.chat.id, response_message_text, parse_mode='HTML', reply_markup=k)




def main():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        main()


if __name__ == '__main__':
    main()
    # bot.polling(none_stop=True)

