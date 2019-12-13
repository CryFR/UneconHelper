from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from db_api import *
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


def faculties():
    mkp = ReplyKeyboardMarkup(True, False)
    for faculty in get_faculties():
        mkp.row(faculty)
    return mkp


def specialities(faculty):
    mkp = ReplyKeyboardMarkup(True, False)
    for speciality in get_specialities(faculty):
        mkp.row(speciality)
    return mkp


def groups(faculty, speciality):
    mkp = ReplyKeyboardMarkup(True, False, row_width=4)
    buttons = []
    last_course = 0
    for group in get_groups(faculty, speciality):
        if group['course'] > last_course:
            mkp.add(*buttons)
            mkp.row(f"{group['course']} курс")
            last_course = group['course']
            buttons = []
        buttons.append(KeyboardButton(group['number']))
    mkp.add(*buttons)
    return mkp


def teachers(name):
    mkp = ReplyKeyboardMarkup(True, False)
    for teacher in get_teachers(name):
        mkp.row(teacher)
    return mkp


def buildings():
    mkp = ReplyKeyboardMarkup(True, False)
    for _building in get_buildings():
        mkp.row(_building)
    return mkp


def room_numbers(number, building):
    mkp = ReplyKeyboardMarkup(True, False, row_width=5)
    buttons = []
    for room in get_rooms(number, building):
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


def get_day_notification_inline(hours=None, minutes=None):
    if minutes is None:
        minutes = [0, 0]
    if hours is None:
        hours = [0, 0]
    mkp = InlineKeyboardMarkup()
    data = f' {hours[0]} {hours[1]} {minutes[0]} {minutes[1]}'
    timer_mkp = inline_timer(hours, minutes, data)
    for row in timer_mkp:
        mkp.row(*row)
    mkp.row(InlineKeyboardButton('Не уведомлять', callback_data='Cancel' + data),
            InlineKeyboardButton('Подтвердить', callback_data='Submit' + data))
    return mkp


def inline_timer(hours, minutes, data):
    mkp = ((InlineKeyboardButton('▲', callback_data='h0+' + data),
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
            InlineKeyboardButton('▼', callback_data='m1-' + data)))
    return mkp


if __name__ == '__main__':
    print(groups(get_buffer(294821600), 'Информационная безопасность'))
