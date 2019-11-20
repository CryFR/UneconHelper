from telebot.types import ReplyKeyboardMarkup as RplMarkup
from db_api import *


def start():
    mkp = RplMarkup(True, False)
    mkp.row('️️Расписание группы')
    mkp.row('Расписание преподавателя')
    mkp.row('Расписание аудитории')
    return mkp


def faculties():
    mkp = RplMarkup(True, False)
    print(get_faculties())
    for faculty in get_faculties():
        mkp.row(faculty[0])
    return mkp
