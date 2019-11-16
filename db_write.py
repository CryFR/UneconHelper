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

def fill_groups(course, fac_id):
    sql = "REPLACE INTO groups (group_id, group_number, group_speciality_name, group_speciality_code, faculty_id, course) VALUES (%s, %s, %s, %s, %s, %s)"
    keys_grp, values_grp = zip(*schedule_parser.get_groups(fac_id, course).items())
    for i in range(0,len(keys_grp)):
        data = (keys_grp[i], values_grp[i][0], values_grp[i][2], values_grp[i][1], fac_id, course)
        cursor.execute(sql, data)
        i += 1

if __name__ == '__main__':
    conn = pymysql.connect(host=MYSQL_IP,
                           database=MYSQL_BD_NAME,
                           user=MYSQL_USER,
                           password=MYSQL_PASSWORD)
    cursor = conn.cursor()
    fill_faculties()
    fill_groups(2, 18)
    conn.commit()
    cursor.close()
