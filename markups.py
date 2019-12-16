from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from db_api import *
from datetime import datetime, timedelta
from constants import every_lesson_notification_options


def remove():
    mkp = ReplyKeyboardRemove()
    return mkp


def no_need():
    mkp = ReplyKeyboardMarkup(True, False)
    mkp.row('Не уведомлять')
    return mkp


def start():
    mkp = ReplyKeyboardMarkup(True, False)
    mkp.row('️️Расписание группы')
    mkp.row('Расписание преподавателя')
    mkp.row('Расписание аудитории')
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
    mkp = ReplyKeyboardMarkup(True, False, row_width=5)
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


def main():
    mkp = ReplyKeyboardMarkup(True, False, row_width=2)
    mkp.row('Menu')
    # TODO: menu markup
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
    print(date)
    date = datetime.strptime(date, '%d.%m.%y')
    day = timedelta(days=1)
    week = timedelta(weeks=1)
    mkp.row(InlineKeyboardButton((date-day).strftime('%d.%m %a'), callback_data=str((date-day).strftime('%d.%m.%y'))),
            InlineKeyboardButton((date+day).strftime('%d.%m %a'), callback_data=str((date+day).strftime('%d.%m.%y'))))
    mkp.row(InlineKeyboardButton((date-week).strftime('%d.%m %a'), callback_data=str((date-week).strftime('%d.%m.%y'))),
            InlineKeyboardButton((date+week).strftime('%d.%m %a'), callback_data=str((date+week).strftime('%d.%m.%y'))))
    return mkp


if __name__ =='__main__':
    print(str(datetime.now().strftime('%d%m%y')))
