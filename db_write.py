import pymysql
import schedule_parser
from constants import MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_BD_NAME


def fill_faculties():
    keys_fac, values_fac = zip(*schedule_parser.get_faculties().items())
    sql = "INSERT INTO faculties (faculty_id, faculty_name_ru, courses) VALUES (%s, %s, %s)"
    for i in range(0, len(keys_fac)):
        data = (keys_fac[i], values_fac[i], ','.join((schedule_parser.get_courses(keys_fac[i]).keys())))
        try:
            # print(data)
            cursor.execute(sql, data)
        except Exception as e:
            print(e)

        i += 1


def fill_groups():
    faculty_rows = cursor.execute("SELECT * FROM faculties")
    sql = "INSERT INTO `groups` (group_id, group_number, group_speciality_name, group_speciality_code, faculty_id, course) VALUES (%s, %s, %s, %s, %s, %s)"
    for j in range(0, faculty_rows):
        faculty_id = cursor.fetchall()
        courses_num = cursor.fetchall()
        courses = courses_num[0][0].split(',')
        print(faculty_id[0][0], courses)
        for course in courses:
            keys_grp, values_grp = zip(*schedule_parser.get_groups(faculty_id[0][0], course).items())
            for i in range(0, len(keys_grp)):
                data = (keys_grp[i], values_grp[i][0], values_grp[i][2], values_grp[i][1], faculty_id, course)
                try:
                    cursor.execute(sql, data)
                except Exception as e:
                    print(e)


# def fill_groups(faculty_id, course):
#     sql = "INSERT INTO `groups` (group_id, group_number, group_speciality_name, group_speciality_code, faculty_id, course) VALUES (%s, %s, %s, %s, %s, %s)"
#     keys_grp, values_grp = zip(*schedule_parser.get_groups(faculty_id, course).items())
#     for i in range(0, len(keys_grp)):
#         data = (keys_grp[i], values_grp[i][0], values_grp[i][2], values_grp[i][1], faculty_id, course)
#         try:
#             cursor.execute(sql, data)
#         except Exception as e:
#             print(e)


def fill_teachers(group_id):
    sql = "INSERT INTO teachers (surname_ru, first_name_ru, patronymic_ru) VALUES (%s, %s, %s)"
    group_teachers = set(lesson['teacher'] for lesson in schedule_parser.parse_semester(group_id))
    for teacher in group_teachers:
        data = teacher.split()
        try:
            cursor.execute(sql, data)
        except Exception as e:
            print(e)


def fill_subjects(group_id):
    sql = "INSERT INTO subjects (subject_name_ru) VALUES (%s)"
    group_subjects = set(lesson['subject'] for lesson in schedule_parser.parse_semester(group_id))
    for subject in group_subjects:
        subject = subject.partition('(')[0].rstrip()
        try:
            cursor.execute(sql, subject)
        except Exception as e:
            print(e)


def fill_rooms(group_id):
    sql = "INSERT INTO rooms (number, building_ru) VALUES (%s, %s)"
    group_rooms = set([lesson['room'], lesson['building']] for lesson in schedule_parser.parse_semester(group_id))
    for room in group_rooms:
        try:
            cursor.execute(sql, room)
        except Exception as e:
            print(e)
