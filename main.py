#!/usr/bin/python3
# _*_ coding: utf-8 _*_

import telebot
import cherrypy
from db_api import *
from format import *
from constants import *
from locale import setlocale, LC_TIME
from datetime import datetime
import markups


setlocale(LC_TIME, locale="ru_RU")
bot = telebot.TeleBot(TOKEN, threaded=False)


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                'content-type' in cherrypy.request.headers and \
                cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


@bot.message_handler(commands=['start', 'reset'])
@connect_and_run
def handle_command(message, cursor):
    user_id = message.from_user.id
    print(user_id, 'started')
    reset_user(user_id, cursor)
    answer = 'Привет, я могу выводить расписание, а также, если нужно, напоминать о парах.\nИ так, расписание чего нужно выводить?'
    bot.send_message(user_id, answer, reply_markup=markups.add_schedule(returnable=False))
    change_state(user_id, states['add_schedule'], cursor)


@bot.message_handler(content_types=['text'])
@connect_and_run
def handle_command(message, cursor):
    now = datetime.now()
    answer = 'Не понял вас'
    markup = None
    parse_mode = None
    user_id = message.from_user.id
    bot.send_chat_action(user_id, 'typing')
    try:
        state = get_state(user_id, cursor)
    except IndexError:
        change_state(user_id, states['add_schedule'], cursor)
        state = states['add_schedule']
    text = message.text
    if state == states['add_schedule']:
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
        elif text == 'Назад' and get_buffer(user_id, cursor) == 'In settings':
            state = states['settings']
            answer = 'Настройки'
            markup = markups.settings()
    elif state == states['waiting_for_faculty/group']:
        if text in get_all_groups(cursor):
            if len(get_tracking_names(user_id, cursor)) == 0:
                set_tracking(user_id, 'group', get_group_id(text, cursor), True, text, cursor)
                answer = f'Выбрана группа:\n\n{text}\n\nХотите получать уведомления о предстоящих занятиях?'
                markup = markups.yes_no()
                state = states['is_notifications_needed']
            else:
                set_tracking(user_id, 'group', get_group_id(text, cursor), False, text, cursor)
                answer = f'''Выбрана группа:\n\n{text}\n\nТеперь в главном меню вы можете найти кнопку для вывода её расписания\n\nУведомления о парах приходят только для главного расписания, сделать расписание главным:\n\nНастройки → Главное расписание'''
                state = states['settings']
                markup = markups.settings()
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
                    answer = f'''Выбран преподаватель:\n\n{teachers[0]}\n\nХотите получать уведомления о предстоящих занятиях?'''
                    markup = markups.yes_no()
                    state = states['is_notifications_needed']
                else:
                    set_tracking(user_id, 'teacher', get_teacher_id(text, cursor), False, text, cursor)
                    answer = f'''Выбран преподаватель:\n\n{teachers[0]}\n\nТеперь в главном меню вы можете найти кнопку для вывода расписания для данного преподавателя\n\nУведомления о парах приходят только для главного расписания, сделать расписание главным:\n\nНастройки → Главное расписание'''
                    state = states['settings']
                    markup = markups.settings()
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
                answer = f'''Выбрана аудитория:\n\n{text}\n\nХотите получать уведомления о предстоящих занятиях?'''
                markup = markups.yes_no()
                state = states['is_notifications_needed']
            else:
                set_tracking(user_id, 'room', get_room_id(text, get_buffer(user_id, cursor), cursor), False, text,
                             cursor)
                answer = f'''Выбрана аудитория:\n\n{text}\n\nТеперь в главном меню вы можете найти кнопку для вывода расписания для данной аудитории\n\nУведомления о парах приходят только для главного расписания, сделать расписание главным:\n\nНастройки → Главное расписание'''
                state = states['settings']
                markup = markups.settings()
        elif number_of_rooms > 1:
            answer = 'По запросу найдено несколько аудиторий:'
            markup = markups.room_numbers(text, get_buffer(user_id, cursor))
        else:
            answer = 'Неизвестная аудитория, попробуйте найти её в списке'
            markup = markups.room_numbers('%', get_buffer(user_id, cursor))
    elif state == states['is_notifications_needed']:
        if text == 'Да':
            answer = 'Есть три вида уведомлений:\n\n1)Уведомления перед каждой парой - такие уведомления будут приходить за выбранное время до начала пары\n\n2)Уведомление перед первой парой - для первой пары можно выставить отдельное время\n\n3)Уведомление о парах на день - позволяет получать расписание всех занятий на предстоящий учебный день'
            markup = markups.notification_choose(returnable=False)
            state = states['notifications']
        elif text == 'Нет':
            bot.send_message(user_id, 'Главное меню', reply_markup=markups.main_menu(user_id))
            main_type, main_id = get_main_tracking(user_id, cursor)[1:3]
            answer = format_schedule(get_schedule(now.strftime('%d.%m.%y'), main_type, main_id, cursor))
            markup = markups.inline_schedule_controls()
            parse_mode = 'HTML'
            state = states['main']
    elif state == states['notifications']:
        if text == 'Установить время уведомлений перед каждой парой':
            answer = 'Уведомления перед каждой парой:'
            markup = markups.every_lesson_notification()
            state = states['every_lesson_notification']
        elif text == 'Установить время уведомления перед первой парой':
            bot.send_message(user_id, answer, reply_markup=markups.remove())
            answer = 'Введите время, за которое вас уведомить о начале первой пары:'
            markup = markups.inline_timer()
            state = states['first_lesson_notification']
        elif text == 'Установить время уведомления с расписанием предстоящих пар':
            bot.send_message(user_id, answer, reply_markup=markups.remove())
            bot.send_chat_action(user_id, 'typing')
            answer = 'Укажите время, в которое присылать расписание на предстоящий день:'
            markup = markups.inline_timer()
            state = states['day_notification']
        elif text == 'Назад' and get_buffer(user_id, cursor) == 'In settings':
            state = states['settings']
            answer = 'Настройки'
            markup = markups.settings()
    elif state == states['every_lesson_notification']:
        if text in every_lesson_notification_options.keys():
            time = every_lesson_notification_options[text]
            set_every_lesson_notification(user_id, time, cursor)
            if time is not None:
                answer = f'Уведомление будет приходить {text.lower()}'
            else:
                answer = 'Уведомления о начале каждой пары приходить не будут'
            if get_buffer(user_id, cursor) == 'In settings':
                markup = markups.notification_choose()
                state = states['notifications']
            else:
                bot.send_message(user_id, answer, reply_markup=markups.remove())
                answer = 'Введите время, за которое вас уведомить о начале первой пары:'
                markup = markups.inline_timer()
                state = states['first_lesson_notification']
    elif state == states['main']:
        if text == 'Настройки':
            state = states['settings']
            answer = text
            markup = markups.settings()
            set_buffer(user_id, "In settings", cursor)
        elif text in get_tracking_names(user_id, cursor):
            schedule_id, schedule_type = get_tracking_info_by_name(user_id, text, cursor)
            answer = format_schedule(get_schedule(now.strftime('%d.%m.%y'), schedule_type, schedule_id, cursor))
            markup = markups.inline_schedule_controls(now.strftime('%d.%m.%y'))
            parse_mode = 'HTML'
    elif state == states['settings']:
        if text == 'Добавить расписание':
            answer = 'Какое расписание добавить?'
            markup = markups.add_schedule()
            state = states['add_schedule']
        elif text == 'Установить/изменить врямя уведомлений':
            answer = 'Есть три вида уведомлений:\n\n1)Уведомления перед каждой парой - такие уведомления будут приходить за выбранное время до начала пары\n\n2)Уведомление перед первой парой - для первой пары можно выставить отдельное время\n\n3)Уведомление о парах на день - позволяет получать расписание всех занятий на предстоящий учебный день'
            markup = markups.notification_choose()
            state = states['notifications']
        elif text == 'Изменить главное расписание':
            answer = 'Здесь можно установить ваше главное расписание- оно будет автоматически отображаться в главном меню и только для него приходят уведомления'
            markup = markups.set_main_schedule(user_id, cursor)
            state = states['set_main_schedule']
        elif text == 'Назад':
            bot.send_message(user_id, 'Главное меню', reply_markup=markups.main_menu(user_id))
            schedule_type, schedule_id = get_main_tracking(user_id, cursor)[1:3]
            answer = format_schedule(get_schedule(now.strftime('%d.%m.%y'), schedule_type, schedule_id, cursor))
            markup = markups.inline_schedule_controls(now.strftime('%d.%m.%y'))
            set_buffer(user_id, None, cursor)
            parse_mode = 'HTML'
            state = states['main']
    elif state == states['set_main_schedule']:
        if text in get_tracking_names(user_id, cursor):
            change_main_tracking(user_id, text, cursor)
            answer = f'Новое главное расписание - {text}'
            markup = markups.settings()
            state = states['settings']
        elif text == 'Назад':
            state = states['settings']
            answer = 'Настройки'
            markup = markups.settings()

    bot.send_message(user_id, answer, reply_markup=markup, parse_mode=parse_mode)
    change_state(user_id, state, cursor)
    print(f'{state} {user_id}: {text} | executed in {datetime.now() - now}')


@bot.callback_query_handler(func=lambda call: True)
@connect_and_run
def callback_query(call, cursor):
    answer = call.message.text
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id
    try:
        state = get_state(user_id, cursor)
    except IndexError:
        change_state(user_id, states['add_schedule'], cursor)
        state = states['add_schedule']
    markup = None
    parse_mode = None
    now = datetime.now()
    edit = True
    send = True
    if state == states['first_lesson_notification']:
        send, markup, button, time = timer_handler(call)
        if button == 'Submit' or button == 'Cancel':
            edit = False
            if button == 'Submit':
                set_first_lesson_notification(user_id, time, cursor)
                answer = f'Расписание будет за {time} до начала первой пары'
            else:
                answer = 'Специальное уведомление о начале первой пары приходить не будет'
            if get_buffer(user_id, cursor) == 'In settings':
                markup = markups.notification_choose()
                state = states['notifications']
            else:
                bot.send_message(user_id, answer, reply_markup=markups.remove())
                bot.send_chat_action(user_id, 'typing')
                answer = 'Укажите время, в которое присылать расписание на предстоящий день:'
                markup = markups.inline_timer()
                state = states['day_notification']
    elif state == states['day_notification']:
        send, markup, button, time = timer_handler(call)
        if button == 'Submit' or button == 'Cancel':
            edit = False
            if button == 'Submit':
                set_day_notification(user_id, time, cursor)
                answer = f'Расписание будет приходить в {time}'
            else:
                answer = 'Уведомление с расписанием на предстоящий день приходить не будет'
            if get_buffer(user_id, cursor) == 'In settings':
                markup = markups.notification_choose()
                state = states['notifications']
            else:
                main_type, main_id = get_main_tracking(user_id, cursor)[1:3]
                try:
                    bot.send_message(user_id, 'Главное меню', reply_markup=markups.main_menu(user_id))
                    answer = format_schedule(get_schedule(now.strftime('%d.%m.%y'), main_type, main_id, cursor))
                    markup = markups.inline_schedule_controls()
                    parse_mode = 'HTML'
                    state = states['main']
                except ValueError:
                    send = False
    elif state == states['main']:
        try:
            main_type, main_id = get_main_tracking(user_id, cursor)[1:3]
            answer = format_schedule(get_schedule(call.data, main_type, main_id, cursor))
            markup = markups.inline_schedule_controls(date=call.data)
            parse_mode = 'HTML'
        except ValueError:
            send = False
    if send:
        if edit:
            bot.edit_message_text(answer, chat_id, message_id, reply_markup=markup, parse_mode=parse_mode)
        else:
            change_state(user_id, state, cursor)
            bot.send_message(user_id, answer, reply_markup=markup, parse_mode=parse_mode)


def timer_handler(call):
    hours = [0, 0]
    minutes = [0, 0]
    markup = None
    send = True
    button, hours[0], hours[1], minutes[0], minutes[1] = call.data.split()
    hours = list(map(int, hours))
    minutes = list(map(int, minutes))
    time = f'{hours[0]}{hours[1]}:{minutes[0]}{minutes[1]}'
    if button[0] == 'h' or button[0] == 'm':
        if button[0] == 'h':
            if hours[0] == 2 and hours[1] == 4:
                if minutes[0] != 0 and minutes[1] != 0:
                    minutes[0] = minutes[1] = 0
            if button[1] == '0':
                if button[2] == '+':
                    if hours[0] == 1 and hours[1] not in [1, 2, 3, 4] or hours[0] == 2:
                        hours[0] = 0
                    else:
                        hours[0] += 1
                else:
                    if hours[0] == 0:
                        if hours[1] in [0, 1, 2, 3, 4]:
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
            if hours[0] == 2 and hours[1] == 4:
                if minutes[0] == minutes[1] == 0:
                    send = False
                else:
                    minutes[0] = minutes[1] = 0
            else:
                if button[1] == '0':
                    if button[2] == '+':
                        minutes[0] = (minutes[0] + 1) % 6
                    else:
                        minutes[0] = (minutes[0] - 1) % 6
                else:
                    if button[2] == '+':
                        minutes[1] = (minutes[1] + 5) % 10
                    else:
                        minutes[1] = (minutes[1] - 5) % 10
        markup = markups.inline_timer(hours, minutes)
    elif button == 'None':
        send = False
    return send, markup, button, time


bot.remove_webhook()
print(bot.get_me())
bot.set_webhook(URL + PATH, open(SSL_CERTIFICATE))
access_log = cherrypy.log.access_log
for handler in tuple(access_log.handlers):
    access_log.removeHandler(handler)
cherrypy.config.update({
    'server.socket_host': LISTEN,
    'server.socket_port': PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': SSL_CERTIFICATE,
    'server.ssl_private_key': SSL_KEY
})
cherrypy.quickstart(WebhookServer(), PATH, {'/': {}})
