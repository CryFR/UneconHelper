from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from db_api import *


def remove():
    mkp = ReplyKeyboardRemove()
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


def groups(speciality):
    mkp = ReplyKeyboardMarkup(True, False, row_width=4)
    buttons = []
    for group in get_groups(speciality):
        buttons.append(KeyboardButton(group))
    mkp.add(*buttons)
    return mkp


def teachers(name):
    mkp = ReplyKeyboardMarkup(True, False)
    for teacher in get_teachers(name):
        mkp.row(teacher)
    return mkp


def buildings():
    mkp = ReplyKeyboardMarkup(True, False)
    for _building in get_buildings():\
        mkp.row(_building)
    return mkp


def room_numbers(number, _building):
    mkp = ReplyKeyboardMarkup(True, False, row_width=5)
    buttons = []
    for room in get_rooms(number, _building):
        buttons.append(room)
    mkp.add(*buttons)
    return mkp


def lesson_notifications():
    mkp = ReplyKeyboardMarkup(True, False)
    mkp.row('️️За 5 минут', 'За 10 минут')
    mkp.row('️️За 15 минут', 'Не уведомлять')
    return mkp


def day_notifications():
    mkp = ReplyKeyboardMarkup(True, False)
    mkp.row('️️Вечером', 'Утром')
    mkp.row('Не уведомлять')


if __name__ == '__main__':
    print(building())
