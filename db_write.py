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
