import pymysql
import schedule_parser
from constants import MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_BD_NAME


def fill_faculties():
    keys_fac, values_fac = zip(*schedule_parser.get_faculties().items())
    sql = "REPLACE INTO faculties (faculty_id, faculty_name_ru, number_of_courses) VALUES (%s, %s, %s)"
    for i in range(0, len(keys_fac)):
        data = (keys_fac[i], values_fac[i], len(schedule_parser.get_courses(keys_fac[i])))
        cursor.execute(sql, data)
        i += 1


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
