import pymysql
import rasp_parser
from constants import MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_BD_NAME

conn = pymysql.connect(host=MYSQL_IP,
                       database=MYSQL_BD_NAME,
                       user=MYSQL_USER,
                       password=MYSQL_PASSWORD)
cursor = conn.cursor()
sql = [" DROP TABLE IF EXISTS users;",
       "CREATE TABLE users(user_id INT UNSIGNED, group_ids SMALLINT UNSIGNED, teacher_ids SMALLINT UNSIGNED, room_id SMALLINT UNSIGNED, is_en BOOL, notification_time VARCHAR(30), black_list_ids JSON, subscription BOOL, showing_settings SET(''), state TINYINT UNSIGNED) COLLATE='utf8_general_ci';",
       "DROP TABLE IF EXISTS `groups`;",
       "CREATE TABLE `groups`(group_id INT UNSIGNED, group_number CHAR(15), direction TINYTEXT, grp_spec_code INT UNSIGNED) COLLATE='utf8_general_ci';",
       "DROP TABLE IF EXISTS faculties;",
       "CREATE TABLE faculties (faculty_id SMALLINT UNSIGNED, fac_name TINYTEXT) COLLATE='utf8_general_ci';",
       " DROP TABLE IF EXISTS teachers;",
       "CREATE TABLE teachers(teacher_id SMALLINT UNSIGNED, surname_ru TINYTEXT, first_name_ru TINYTEXT, patronymic_ru TINYTEXT, surname_en TINYTEXT, first_name_en TINYTEXT, patronymic_en TINYTEXT) COLLATE='utf8_general_ci';",
       " DROP TABLE IF EXISTS lessons;",
       "CREATE TABLE lessons(lesson_id SMALLINT UNSIGNED, teacher_id SMALLINT UNSIGNED, room_id SMALLINT UNSIGNED, dates JSON, lesson_time TINYINT(3), type_ru TINYTEXT, type_en TINYTEXT, group_ids JSON) COLLATE='utf8_general_ci';",
       "DROP TABLE IF EXISTS rooms;",
       "CREATE TABLE rooms(room_id SMALLINT UNSIGNED, number SMALLINT UNSIGNED, building_ru TINYTEXT, building_en TINYTEXT) COLLATE='utf8_general_ci';",
       "DROP TABLE IF EXISTS subjects;",
       "CREATE TABLE subjects(subject_id SMALLINT UNSIGNED, subject_name_ru	TINYTEXT, subject_name_en TINYTEXT, shortcut_ru TINYTEXT, shortcut_en TINYTEXT) COLLATE='utf8_general_ci';"
       ]
for query in sql:
    cursor.execute(query)
keys_fac, values_fac = zip(*rasp_parser.get_faculties().items())
keys_grp, values_grp = zip(*rasp_parser.get_groups(18, 2).items())
sql = "REPLACE INTO faculties (faculty_id, fac_name) VALUES (%s, %s)"
for i in range(0, len(keys_fac)):
    data = (keys_fac[i], values_fac[i])
    print(data)
    cursor.execute(sql, data)
    i += 1
conn.commit()
cursor.close()
