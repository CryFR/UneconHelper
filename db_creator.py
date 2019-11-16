import pymysql
from constants import MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_BD_NAME

conn = pymysql.connect(host=MYSQL_IP,
                       database=MYSQL_BD_NAME,
                       user=MYSQL_USER,
                       password=MYSQL_PASSWORD)
cursor = conn.cursor()
sql = [" DROP TABLE IF EXISTS users;",
       "CREATE TABLE users(user_id INT UNSIGNED, group_ids SMALLINT UNSIGNED, teacher_ids SMALLINT UNSIGNED, room_id SMALLINT UNSIGNED, is_en BOOL, notification_time VARCHAR(30), black_list_ids JSON, subscription BOOL, showing_settings SET(''), state TINYINT UNSIGNED) COLLATE='utf8_general_ci';",
       "DROP TABLE IF EXISTS `groups`;",
       "CREATE TABLE `groups`(group_id INT UNSIGNED, faculty_id SMALLINT UNSIGNED, course TINYINT(3), group_number CHAR(15), group_speciality_name TINYTEXT, group_speciality_code INT UNSIGNED) COLLATE='utf8_general_ci';",
       "DROP TABLE IF EXISTS faculties;",
       "CREATE TABLE faculties (faculty_id SMALLINT UNSIGNED, number_of_courses TINYINT(3), faculty_name_ru TINYTEXT, faculty_name_en TINYTEXT) COLLATE='utf8_general_ci';",
       " DROP TABLE IF EXISTS teachers;",
       "CREATE TABLE teachers(teacher_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, surname_ru TINYTEXT, first_name_ru TINYTEXT, patronymic_ru TINYTEXT, surname_en TINYTEXT, first_name_en TINYTEXT, patronymic_en TINYTEXT) COLLATE='utf8_general_ci';",
       " DROP TABLE IF EXISTS lessons;",
       "CREATE TABLE lessons(subject_id SMALLINT UNSIGNED, teacher_id SMALLINT UNSIGNED, room_id SMALLINT UNSIGNED, dates JSON, lesson_number TINYINT(3), type_ru TINYTEXT, type_en TINYTEXT, group_ids JSON) COLLATE='utf8_general_ci';",
       "DROP TABLE IF EXISTS rooms;",
       "CREATE TABLE rooms(room_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, number SMALLINT UNSIGNED, building_ru TINYTEXT, building_en TINYTEXT) COLLATE='utf8_general_ci';",
       "DROP TABLE IF EXISTS subjects;",
       "CREATE TABLE subjects(subject_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, subject_name_ru	TINYTEXT, subject_name_en TINYTEXT, shortcut_ru TINYTEXT, shortcut_en TINYTEXT) COLLATE='utf8_general_ci';"
       ]
for query in sql:
    cursor.execute(query)
conn.commit()
cursor.close()
