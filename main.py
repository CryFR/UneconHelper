# _*_ coding: utf-8 _*_

import telebot
from db_api import *
from constants import TOKEN
import markups


# try:
bot = telebot.TeleBot(TOKEN, threaded=False)
print(bot.get_me())


@bot.message_handler(commands=['start', 'reset'])
def handle_command(message):
    user_id = message.from_user.id
    print(user_id)
    answer = 'Привет, я могу выводить расписание, а также, если нужно, напоминать о парах.\nИ так, расписание чего нужно выводить?'
    bot.send_message(message.from_user.id, answer, reply_markup=markups.start())
    change_state(user_id, 0)


@bot.message_handler(content_types=['text'])
def handle_command(message):
    answer = markup = ''
    user_id = message.from_user.id
    state = get_state(user_id)
    text = message.text
    print(f'{state} {user_id}: {text}')
    if state == 0:
        if text == '️️Расписание группы':
            answer = 'Выберите свой факультет, или введи номер группы'
            markup = markups.faculties()
            state = 10
        elif text == 'Расписание преподавателя':
            answer = 'Введите часть имени преподавателя'
            markup = markups.remove()
            state = 20
        elif text == 'Расписание аудитории':
            answer = 'Выберите задние:'
            markup = markups.buildings()
            state = 30
    elif state == 10:
        if text in get_faculties():
            answer = 'Теперь выберите направление'
            markup = markups.specialities(text)
            state = 11
    elif state == 11:
        if text in get_specialities('%'):
            answer = 'Найдите свою группу'
            markup = markups.groups(text)
            state = 12
    elif state == 20:
        answer = 'Выберите преподавателя из списка'
        markup = markups.teachers(text)
        state = 21
    elif state == 30:
        if text in get_buildings():
            answer = 'Выберите аудиторию или введите её номер'
            markup = markups.room_numbers('%', text)
            state = 32
    elif state == 12:
        answer = f'Выбрана группа {text}'
        markup = markups.lesson_notifications()
        set_tracking(user_id, 'group', get_group_id(text), True)
    if answer != '':
        bot.send_message(message.from_user.id, answer, reply_markup=markup)
        change_state(user_id, state)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=2)

# except Exception as e:
#     print(e)
