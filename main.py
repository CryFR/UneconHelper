# _*_ coding: utf-8 _*_

import telebot
from db_api import *
from constants import TOKEN, states, every_lesson_notification_options
from locale import setlocale, LC_TIME
from datetime import datetime
import markups
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
setlocale(LC_TIME, locale="ru_RU")
bot = telebot.TeleBot(TOKEN, threaded=False)


@bot.message_handler(commands=['start', 'reset'])
@connect_and_run
def handle_command(message, cursor):
    user_id = message.from_user.id
    print(user_id, 'started')
    reset_user(user_id, cursor)
    answer = 'Привет, я могу выводить расписание, а также, если нужно, напоминать о парах.\nИ так, расписание чего нужно выводить?'
    bot.send_message(user_id, answer, reply_markup=markups.start())
    change_state(user_id, states['start'], cursor)


@bot.message_handler(content_types=['text'])
@connect_and_run
def handle_command(message, cursor):
    print('get')
    now = datetime.now()
    answer = 'Не понял вас'
    markup = False
    user_id = message.from_user.id
    bot.send_chat_action(user_id, 'typing')
    try:
        state = get_state(user_id, cursor)
    except Exception as e:
        print(e)
        change_state(user_id, states['start'], cursor)
        state = states['start']
    text = message.text
    print(f'{state} {user_id}: {text} ')
    if state == states['start']:
        if text == '️️Расписание группы':
            answer = 'Выберите свой факультет, или введи номер группы'
            markup = markups.faculties()
            state = states['waiting_for_faculty/group']
        elif text == 'Расписание преподавателя':
            answer = 'Введите часть имени преподавателя'
            markup = markups.remove()
            state = states['waiting_for_teacher']
        elif text == 'Расписание аудитории':
            answer = 'Выберите задние:'
            markup = markups.buildings()
            state = states['waiting_for_building']
    elif state == states['waiting_for_faculty/group']:
        if text in get_all_groups(cursor):
            if len(get_tracking_names(user_id, cursor)) == 0:
                set_tracking(user_id, 'group', get_group_id(text, cursor), True, text, cursor)
                answer = f'Выбрана группа:\n\n{text}\n\nБот может отсылать вам уведомления о предстоящих занятиях, есть три вида уведомлений:\n\n1)Уведомления перед каждой парой - такие уведомления будут приходить за выбранное время до начала пары\n\n2)Уведомление перед первой парой - для первой пары можно выставить отдельное время\n\n3)Уведомление о парах на день - позволяет получать расписание всех занятий на предстоящий учебный день'
                bot.send_message(user_id, answer, reply_markup=markup)
                answer = 'Уведомления перед каждой парой:'
                markup = markups.every_lesson_notification()
                state = states['every_lesson_notification']
            else:
                set_tracking(user_id, 'group', get_group_id(text, cursor), False, text, cursor)
                answer = f'''Выбрана группа:\n\n{text}\n\nТеперь в главном меню вы можете найти кнопку для вывода её расписания\n\nУведомления о парах приходят только для главного расписания, сделать расписание главным:\n\nНастройки → Главное расписание'''
                bot.send_message(user_id, answer, reply_markup=markups.remove())
                main_type, main_id = get_main_tracking(294821600, cursor)[1:3]
                answer = get_schedule(now.strftime('%d.%m.%y'), main_type, main_id, cursor)
                markup = markups.inline_schedule_controls()
        elif text in get_faculties(cursor):
            set_buffer(user_id, text, cursor)
            answer = 'Теперь выберите направление'
            markup = markups.specialities(text)
            state = states['waiting_for_speciality']
        elif text.find('курс') == -1:
            answer = 'Не могу найти такую группу, выберите факультет'
            markup = markups.faculties()
    elif state == states['waiting_for_speciality']:
        if text in get_specialities('%', cursor):
            answer = 'Найдите свою группу'
            markup = markups.groups(get_buffer(user_id, cursor), text)
            state = states['waiting_for_faculty/group']
    elif state == states['waiting_for_teacher']:
        if len(text) >= 3:
            teachers = get_teachers(text, cursor)
            number_of_teachers = len(teachers)
            if number_of_teachers == 1:
                if len(get_tracking_names(user_id, cursor)) == 0:
                    set_tracking(user_id, 'teacher', get_teacher_id(teachers[0], cursor), True, text, cursor)
                    answer = f'''Выбран преподаватель:\n\n{teachers[0]}\n\nБот может отсылать вам уведомления о предстоящих занятиях, есть три вида уведомлений:\n\n1)Уведомления перед каждой парой - такие уведомления будут приходить за выбранное время до начала пары\n\n2)Уведомление перед первой парой - для первой пары можно выставить отдельное время\n\n3)Уведомление о парах на день - позволяет получать расписание всех занятий на предстоящий день'''
                    bot.send_message(user_id, answer, reply_markup=markup)
                    answer = 'Уведомления перед каждой парой:'
                    markup = markups.every_lesson_notification()
                    state = states['every_lesson_notification']
                else:
                    set_tracking(user_id, 'teacher', get_teacher_id(text, cursor), False, text, cursor)
                    answer = f'''Выбран преподаватель:\n\n{teachers[0]}\n\nТеперь в главном меню вы можете найти кнопку для вывода расписания для данного преподавателя\n\nУведомления о парах приходят только для главного расписания, сделать расписание главным:\n\nНастройки → Главное расписание'''
                    bot.send_message(user_id, answer, reply_markup=markups.remove())
                    main_type, main_id = get_main_tracking(294821600, cursor)[1:3]
                    answer = get_schedule(now.strftime('%d.%m.%y'), main_type, main_id, cursor)
                    markup = markups.inline_schedule_controls()
            elif number_of_teachers > 1:
                answer = 'Выберите преподавателя из списка'
                markup = markups.teachers(text)
            else:
                answer = 'Преподаватель не найден, попробуйте изменить запрос'
                markup = markups.remove()
        else:
            answer = 'Введите хотя-бы три символа'
            markup = markups.remove()
    elif state == states['waiting_for_building']:
        if text in get_buildings(cursor):
            set_buffer(user_id, text, cursor)
            answer = 'Выберите аудиторию или введите её номер'
            markup = markups.room_numbers('%', text)
            state = states['waiting_for_room']
    elif state == states['waiting_for_room']:
        number_of_rooms = len(get_rooms(text, get_buffer(user_id, cursor), cursor))
        if number_of_rooms == 1:
            if len(get_tracking_names(user_id, cursor)) == 0:
                set_tracking(user_id, 'room', get_room_id(text, get_buffer(user_id, cursor), cursor), True, text,
                             cursor)
                answer = f'''Выбрана аудитория:\n\n{text}\n\nБот может отсылать вам уведомления о предстоящих занятиях, есть три вида уведомлений:\n\n1)Уведомления перед каждой парой - такие уведомления будут приходить за выбранное время до начала пары\n\n2)Уведомление перед первой парой - для первой пары можно выставить отдельное время\n\n3)Уведомление о парах на день - позволяет получать расписание всех занятий на предстоящий день'''
                bot.send_message(user_id, answer, reply_markup=markup)
                answer = 'Уведомления перед каждой парой:'
                markup = markups.every_lesson_notification()
                state = states['every_lesson_notification']
            else:
                set_tracking(user_id, 'room', get_room_id(text, get_buffer(user_id, cursor), cursor), False, text,
                             cursor)
                answer = f'''Выбрана аудитория:\n\n{text}\n\nТеперь в главном меню вы можете найти кнопку для вывода расписания для данной аудитории\n\nУведомления о парах приходят только для главного расписания, сделать расписание главным:\n\nНастройки → Главное расписание'''
                bot.send_message(user_id, answer, reply_markup=markups.remove())
                main_type, main_id = get_main_tracking(294821600, cursor)[1:3]
                answer = get_schedule(now.strftime('%d.%m.%y'), main_type, main_id, cursor)
                markup = markups.inline_schedule_controls()
        elif number_of_rooms > 1:
            answer = 'По запросу найдено несколько аудиторий:'
            markup = markups.room_numbers(text, get_buffer(user_id, cursor))
        else:
            answer = 'Неизвестная аудитория, попробуйте найти её в списке'
            markup = markups.room_numbers('%', get_buffer(user_id, cursor))
    elif state == states['every_lesson_notification']:
        if text in every_lesson_notification_options.keys():
            time = every_lesson_notification_options[text]
            set_every_lesson_notification(user_id, time, cursor)
            if time is not None:
                answer = f'Уведомление будет приходить {text.lower()}'
            else:
                answer = 'Уведомления о начале каждой пары приходить не будут'
            bot.send_message(user_id, answer, reply_markup=markups.remove())
            answer = 'Введите время, за которое вас уведомить о начале первой пары:'
            markup = markups.inline_timer()
            state = states['first_lesson_notification']
    elif state == states['first_lesson_notification']:
        if text.isdigit() and 0 <= int(text) <= 360:
            set_first_lesson_notification(user_id, int(text) * 60, cursor)
            answer = f'Уведомление будет приходить за {text} '
            if int(text) % 10 == 1:
                answer += 'минуту'
            elif int(text) % 10 in [2, 3, 4]:
                answer += 'минуты'
            else:
                answer += 'минут'
            bot.send_message(user_id, answer, reply_markup=markups.remove())
            answer = 'Укажите время, в которое присылать расписание на предстоящий день:'
            markup = markups.inline_timer()
            state = states['day_notification']
        elif text == 'Не уведомлять':
            bot.send_message(user_id, answer, reply_markup=markups.remove())
            set_first_lesson_notification(user_id, None, cursor)
            answer = 'Укажите время, в которое присылать расписание на предстоящий день:'
            markup = markups.inline_timer()
            state = states['day_notification']
    bot.send_message(user_id, answer, reply_markup=markup)
    change_state(user_id, state, cursor)
    print(f'{state} {user_id}: {text} | executed in {datetime.now() - now}')


@bot.callback_query_handler(func=lambda call: True)
@connect_and_run
def callback_query(call, cursor):
    user_id = call.from_user.id
    state = get_state(user_id, cursor)
    now = datetime.now()
    edit = True
    if state == states['first_lesson_notification']:
        button, time = timer_handler(call)
        if button == 'Submit' or button == 'Cancel':
            edit = False
            if timer_handler(call)[0] == 'Submit':
                set_first_lesson_notification(user_id, time, cursor)
                answer = f'Расписание будет за {time} до начала первой пары'
            else:
                answer = 'Специальное уведомление о начале первой пары приходить не будет'
            if get_buffer(user_id, cursor) == 'In settings':
                # TODO: go to settings
                pass
            else:
                bot.send_message(user_id, answer, reply_markup=markups.remove())
                bot.send_chat_action(user_id, 'typing')
                answer = 'Укажите время, в которое присылать расписание на предстоящий день:'
                markup = markups.inline_timer()
                state = states['day_notification']
    elif state == states['day_notification']:
        button, time = timer_handler(call)
        if button == 'Submit' or button == 'Cancel':
            edit = False
            if button == 'Submit':
                set_day_notification(user_id, time, cursor)
                answer = f'Расписание будет приходить в {time}'
            else:
                answer = 'Уведомление с расписанием на предстоящий день приходить не будет'
            if get_buffer(user_id, cursor) == 'In settings':
                # TODO: go to settings
                pass
            else:
                bot.send_message(user_id, answer, reply_markup=markups.remove())
                main_type, main_id = get_main_tracking(294821600, cursor)[1:3]
                answer = get_schedule(now.strftime('%d.%m.%y'), main_type, main_id, cursor)
                markup = markups.inline_schedule_controls()
                state = states['main']
    elif state == states['main']:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        main_type, main_id = get_main_tracking(294821600, cursor)[1:3]
        bot.edit_message_text(get_schedule(call.data, main_type, main_id, cursor), chat_id, message_id, reply_markup=markups.inline_schedule_controls(date=call.data))
    if not edit:
        change_state(user_id, state, cursor)
        bot.send_message(user_id, answer, reply_markup=markup)


def timer_handler(call):
    text = call.message.text
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    hours = [0, 0]
    minutes = [0, 0]
    button, hours[0], hours[1], minutes[0], minutes[1] = call.data.split()
    hours = list(map(int, hours))
    minutes = list(map(int, minutes))
    time = f'{hours[0]}{hours[1]}:{minutes[0]}{minutes[1]}'
    if button[0] == 'h' or button[0] == 'm':
        if button[0] == 'h':
            if button[1] == '0':
                if button[2] == '+':
                    if hours[0] == 1 and hours[1] not in [1, 2, 3, 4] or hours[0] == 2:
                        hours[0] = 0
                    else:
                        hours[0] += 1
                else:
                    if hours[0] == 0:
                        if hours[1] in [1, 2, 3, 4]:
                            hours[0] = 2
                        else:
                            hours[0] = 1
                    else:
                        hours[0] -= 1
            else:
                if button[2] == '+':
                    if hours[0] == 2 and hours[1] == 4 or hours[1] == 9:
                        hours[1] = 0
                    else:
                        hours[1] += 1
                else:
                    if hours[1] == 0:
                        if hours[0] == 2:
                            hours[1] = 4
                        else:
                            hours[1] = 9
                    else:
                        hours[1] -= 1
        elif button[0] == 'm':
            if button[1] == '0':
                if button[2] == '+':
                    minutes[0] = (minutes[0] + 1) % 10
                else:
                    minutes[0] = (minutes[0] - 1) % 10
            else:
                if button[2] == '+':
                    minutes[1] = (minutes[1] + 5) % 10
                else:
                    minutes[1] = (minutes[1] - 5) % 10
        markup = markups.inline_timer(hours, minutes)
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    return button, time


if __name__ == '__main__':
    try:
        print(bot.get_me())
        bot.polling(none_stop=True, interval=0.5)
    except Exception as e:
        print(e)
