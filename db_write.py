import datetime
import re
from json import dumps
from db_setup import reset
import pymysql

import schedule_parser
from constants import MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_BD_NAME

errors_found = 0


def fill_faculties():
    keys_fac, values_fac = zip(*schedule_parser.get_faculties().items())
    sql = "INSERT INTO `faculties` (`faculty_id`, `faculty_name`, `courses`) VALUES (%s, %s, %s)"
    for i in range(0, len(keys_fac)):
        data = (keys_fac[i], values_fac[i], ','.join((schedule_parser.get_courses(keys_fac[i]).keys())))
        try:
            cursor.execute(sql, data)
        except Exception as e:
            print(e)

        i += 1


def fill_groups():
    faculty_rows = cursor.execute("SELECT * FROM `faculties`")
    sql = "INSERT INTO `groups` (`group_id`, `group_number`, `group_speciality_name`, `group_speciality_code`, `faculty_id`, `course`) VALUES (%s, %s, %s, %s, %s, %s)"
    for j in range(0, faculty_rows):
        cursor.execute(f"SELECT `faculty_id` FROM `faculties` LIMIT {j}, 1")
        faculty_id = cursor.fetchall()
        cursor.execute(f"SELECT `courses` FROM `faculties` LIMIT {j}, 1")
        courses = cursor.fetchall()[0][0].split(',')
        for course in courses:
            keys_grp, values_grp = zip(*schedule_parser.get_groups(faculty_id[0][0], course).items())
            for i in range(0, len(keys_grp)):
                data = (keys_grp[i], values_grp[i][0], values_grp[i][2], values_grp[i][1], faculty_id, course)
                try:
                    cursor.execute(sql, data)
                except Exception as e:
                    print(e)


def fill_timings():
    timings = {
        '1': ['09:00 - 10:35'],
        '2': ['10:50 - 12:25'],
        '3': ['12:40 - 14:15'],
        '4': ['14:30 - 16:00'],
        '5': ['16:10 - 17:40'],
        '6': ['18:30 - 20:00'],
        '7': ['20:10 - 21:40']
    }
    sql = "INSERT INTO `timings` (`number`, `time`) VALUES (%s, %s)"
    for timing in timings:
        data = [timing, timings[timing]]
        try:
            cursor.execute(sql, data)
        except Exception as e:
            print(e)


def get_full_date(date_without_year, period):
    date_without_year = [int(i) for i in date_without_year]
    period_start = datetime.datetime.strptime(period[0], '%d.%m.%Y').date()
    period_end = datetime.datetime.strptime(period[1], '%d.%m.%Y').date()
    if period_end.year == period_start.year:
        full_date = datetime.date(period_start.year, date_without_year[1], date_without_year[0])
    elif datetime.date(period_end.year, 1, 1) <= datetime.date(period_end.year, date_without_year[1],
                                                               date_without_year[0]) <= period_end:
        full_date = datetime.date(period_end.year, date_without_year[1], date_without_year[0])
    else:
        full_date = datetime.date(period_start.year, date_without_year[1], date_without_year[0])
    return full_date


def dates_to_list(dates, period, even_odd='', date_format='%d.%m.%y'):
    list_of_dates = [re.findall('\d{2}', date) for date in re.findall('\d{2}\.\d{2}', dates)]
    if dates.find('-') != -1:
        first_date = get_full_date(list_of_dates[0], period)
        last_date = get_full_date(list_of_dates[1], period)
        if even_odd == '':
            delta = datetime.timedelta(weeks=1)
        else:
            delta = datetime.timedelta(weeks=2)
        list_of_dates = [last_date.strftime(date_format)]
        while last_date != first_date:
            last_date -= delta
            list_of_dates.append(last_date.strftime(date_format))
    else:
        list_of_dates = [get_full_date(date, period).strftime(date_format)
                         for date in list_of_dates
                         ]
    return list_of_dates


def group_fill_all(group_id):
    cursor.execute("SELECT `subject_id`, subject_name FROM `subjects`")
    subjects = {subject_name: subject_id for subject_id, subject_name in cursor.fetchall()}
    cursor.execute("SELECT `teacher_id`, `surname`, `first_name`, `patronymic` FROM teachers")
    teachers = {' '.join(full_name).strip(): teacher_id for teacher_id, *full_name in cursor.fetchall()}
    cursor.execute("SELECT `room_id`, `number`, `building` FROM `rooms`")
    rooms = {' '.join(full_address).strip(): room_id for room_id, *full_address in cursor.fetchall()}
    cursor.execute("SELECT `number`, `time` FROM `timings`")
    timings = {time: number for number, time in cursor.fetchall()}
    lesson_data = []
    print(teachers)
    for lesson in schedule_parser.parse_semester(group_id):
        global errors_found
        try:
            if lesson['teacher'] != '' and lesson['teacher_id'] not in teachers.values():
                surname = first_name = patronymic = ''
                surname, first_name, *patronymic = lesson['teacher'].split()
                cursor.execute(
                    "INSERT INTO `teachers` (`teacher_id`, `surname`, `first_name`, `patronymic`) VALUES (%s, %s, %s, %s)",
                    [lesson['teacher_id'], surname, first_name, ' '.join(patronymic)])
                cursor.execute("SELECT `teacher_id`, `surname`, `first_name`, `patronymic` FROM teachers")
                teachers = {' '.join(full_name).strip(): teacher_id for teacher_id, *full_name in cursor.fetchall()}
            if lesson['subject'] not in subjects.keys():
                cursor.execute("INSERT INTO `subjects` (subject_name) VALUES (%s)", lesson['subject'])
                cursor.execute("SELECT `subject_id`, subject_name FROM `subjects`")
                subjects = {subject_name: subject_id for subject_id, subject_name in cursor.fetchall()}
            if ' '.join([lesson['room'], lesson['building']]).strip() not in rooms.keys():
                cursor.execute("INSERT INTO `rooms` (`number`, `building`) VALUES (%s, %s)",
                               [lesson['room'], lesson['building']])
                cursor.execute("SELECT `room_id`, `number`, `building` FROM `rooms`")
                rooms = {' '.join(full_address).strip(): room_id for room_id, *full_address in cursor.fetchall()}
            new_lesson_data = [subjects.get(lesson['subject'], ''),
                               lesson['is_choosable'],
                               teachers.get(lesson['teacher'], '0'),
                               rooms.get(lesson['room'] + ' ' + lesson['building'], '0'),
                               timings.get(lesson['time'], ''),
                               lesson.get('type', ''),
                               group_id
                               ]
            try:
                index = [row[:4] + row[5:] for row in lesson_data].index(new_lesson_data)
                lesson_data[index][4].extend(
                    dates_to_list(lesson['dates'], lesson['semester_period'], lesson['even_odd']))
            except ValueError:
                new_lesson_data.insert(4, dates_to_list(lesson['dates'], lesson['semester_period'], lesson['even_odd']))
                lesson_data.append(new_lesson_data)
        except Exception as e:
            print('error in collecting lesson, group id:', group_id, '\n', lesson, '\n', e)
            errors_found += 1
    sql = "INSERT INTO `lessons` VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    for row in lesson_data:
        row[4] = dumps(row[4])
        try:
            cursor.execute(sql, row)
        except Exception as e:
            print('error in writing semester, group id:', group_id, '\n', row, '\n', e)
            errors_found += 1


def fill_all():
    reset()
    start_time = datetime.datetime.now()
    fill_timings()
    fill_faculties()
    fill_groups()
    cursor.execute("SELECT `group_id` FROM `groups`")
    groups_done = 0
    for group_id in cursor.fetchall():
        group_time_start = datetime.datetime.now()
        group_fill_all(group_id[0])
        groups_done += 1
        average_time = (datetime.datetime.now() - start_time) / groups_done
        print('last operation:', datetime.datetime.now() - group_time_start, '  average time:', average_time,
              '  time passed:', datetime.datetime.now() - start_time, '  estimated time:',
              average_time * (664 - groups_done), '  errors found:', errors_found)
    print('Tables filled for:', datetime.datetime.now() - start_time, 'errors found:', errors_found)


if __name__ == '__main__':
    conn = pymysql.connect(host=MYSQL_IP,
                           database=MYSQL_BD_NAME,
                           user=MYSQL_USER,
                           password=MYSQL_PASSWORD)
    cursor = conn.cursor()
    fill_all()
    conn.commit()
    cursor.close()
