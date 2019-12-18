from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from db_api import *
from datetime import datetime, timedelta
from constants import every_lesson_notification_options


def remove():
    return ReplyKeyboardRemove()


def yes_no():
    mkp = ReplyKeyboardMarkup(True, False)
    mkp.row('Да', 'Нет')
    return mkp


def add_schedule(returnable=True):
    mkp = ReplyKeyboardMarkup(True, False)
    mkp.row('️️Расписание группы')
    mkp.row('Расписание преподавателя')
    mkp.row('Расписание аудитории')
    if returnable:
        mkp.row('Назад')
    return mkp


@connect_and_run
def faculties(cursor):
    mkp = ReplyKeyboardMarkup(True, False)
    for faculty in get_faculties(cursor):
        mkp.row(faculty)
    return mkp


@connect_and_run
def specialities(faculty, cursor):
    mkp = ReplyKeyboardMarkup(True, False)
    for speciality in get_specialities(faculty, cursor):
        mkp.row(speciality)
    return mkp


@connect_and_run
def groups(faculty, speciality, cursor):
    mkp = ReplyKeyboardMarkup(True, False, row_width=4)
    buttons = []
    last_course = 0
    for group in get_groups(faculty, speciality, cursor):
        if group['course'] > last_course:
            mkp.add(*buttons)
            mkp.row(f"{group['course']} курс")
            last_course = group['course']
            buttons = []
        buttons.append(KeyboardButton(group['number']))
    mkp.add(*buttons)
    return mkp


@connect_and_run
def teachers(name, cursor):
    mkp = ReplyKeyboardMarkup(True, False)
    for teacher in get_teachers(name, cursor):
        mkp.row(teacher)
    return mkp


@connect_and_run
def buildings(cursor):
    mkp = ReplyKeyboardMarkup(True, False)
    for _building in get_buildings(cursor):
        mkp.row(_building)
    return mkp


@connect_and_run
def room_numbers(number, building, cursor):
    mkp = ReplyKeyboardMarkup(True, False, row_width=4)
    buttons = []
    for room in get_rooms(number, building, cursor):
        buttons.append(room)
    mkp.add(*buttons)
    return mkp


def every_lesson_notification():
    mkp = ReplyKeyboardMarkup(True, False, row_width=2)
    for button in every_lesson_notification_options.keys():
        mkp.add(KeyboardButton(button))
    return mkp


def notification_choose(returnable=True):
    mkp = ReplyKeyboardMarkup(True, False)
    mkp.row('Установить время уведомлений перед каждой парой')
    mkp.row('Установить время уведомления перед первой парой')
    mkp.row('Установить время уведомления с расписанием предстоящих пар')
    if returnable:
        mkp.row('Назад')
    return mkp


def set_main_schedule(user_id, cursor):
    mkp = ReplyKeyboardMarkup(True, False)
    main = get_main_tracking(user_id, cursor)[5]
    for name in get_tracking_names(user_id, cursor):
        if name != main:
            mkp.row(name)
    mkp.row('Назад')
    return mkp


@connect_and_run
def main_menu(user_id, cursor):
    mkp = ReplyKeyboardMarkup(True, False)
    for name in get_tracking_names(user_id, cursor):
        mkp.row(name)
    mkp.row('Настройки')
    return mkp


def settings():
    mkp = ReplyKeyboardMarkup(True, False)
    mkp.row('Добавить расписание')
    mkp.row('Изменить главное расписание')
    mkp.row('Установить/изменить врямя уведомлений')
    mkp.row('Назад')
    return mkp


def inline_timer(hours=None, minutes=None):
    if minutes is None:
        minutes = [0, 0]
    if hours is None:
        hours = [0, 0]
    mkp = InlineKeyboardMarkup()
    data = f' {hours[0]} {hours[1]} {minutes[0]} {minutes[1]}'
    timer_mkp = ((InlineKeyboardButton('▲', callback_data='h0+' + data),
                  InlineKeyboardButton('▲', callback_data='h1+' + data),
                  InlineKeyboardButton('-', callback_data='None' + data),
                  InlineKeyboardButton('▲', callback_data='m0+' + data),
                  InlineKeyboardButton('▲', callback_data='m1+' + data)),
                 (InlineKeyboardButton(hours[0], callback_data='None' + data),
                  InlineKeyboardButton(hours[1], callback_data='None' + data),
                  InlineKeyboardButton(':', callback_data='None' + data),
                  InlineKeyboardButton(minutes[0], callback_data='None' + data),
                  InlineKeyboardButton(minutes[1], callback_data='None' + data)),
                 (InlineKeyboardButton('▼', callback_data='h0-' + data),
                  InlineKeyboardButton('▼', callback_data='h1-' + data),
                  InlineKeyboardButton('-', callback_data='None' + data),
                  InlineKeyboardButton('▼', callback_data='m0-' + data),
                  InlineKeyboardButton('▼', callback_data='m1-' + data)),
                 (InlineKeyboardButton('Не уведомлять', callback_data='Cancel' + data),
                  InlineKeyboardButton('Подтвердить', callback_data='Submit' + data)))
    for row in timer_mkp:
        mkp.row(*row)
    return mkp


def inline_schedule_controls(date=datetime.now().strftime('%d.%m.%y')):
    mkp = InlineKeyboardMarkup()
    date = datetime.strptime(date, '%d.%m.%y')
    day = timedelta(days=1)
    week = timedelta(weeks=1)
    mkp.row(
        InlineKeyboardButton((date - day).strftime('%d.%m %a'), callback_data=str((date - day).strftime('%d.%m.%y'))),
        InlineKeyboardButton((date + day).strftime('%d.%m %a'), callback_data=str((date + day).strftime('%d.%m.%y'))))
    mkp.row(
        InlineKeyboardButton((date - week).strftime('%d.%m %a'), callback_data=str((date - week).strftime('%d.%m.%y'))),
        InlineKeyboardButton((date + week).strftime('%d.%m %a'), callback_data=str((date + week).strftime('%d.%m.%y'))))
    return mkp


if __name__ == '__main__':
    print(str(datetime.now().strftime('%d%m%y')))
