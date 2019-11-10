# -- coding: utf-8 --
import MySQLdb
import rasp_parser
import base64

conn = MySQLdb.connect('128.199.50.189','uneconBot','G2o7qBBPEvN550EjTLCv', 'unecon_bot',use_unicode=True, charset="utf8mb4")
cursor = conn.cursor()
keys_fac, values_fac = zip(*rasp_parser.get_faculties().items())
keys_grp, values_grp  = zip(*rasp_parser.get_groups(18, 2).items())
# keys_time, value_time = zip(*rasp_parser.parse().items())
cursor.execute("""DROP TABLE IF EXISTS faculties;
                CREATE TABLE faculties (faculty_id SMALLINT UNSIGNED, fac_name TINYTEXT);""")
cursor.execute("""DROP TABLE IF EXISTS groups;
                CREATE TABLE groups(group_id INT UNSIGNED, group_number CHAR(15), direction TINYTEXT, grp_spec_code INT UNSIGNED);""")
cursor.execute(""" DROP TABLE IF EXISTS lessons;
                CREATE TABLE lessons(lesson_id SMALLINT UNSIGNED, teacher_id SMALLINT UNSIGNED, room_id SMALLINT UNSIGNED, datetime TIMESTAMP, type_ru TINYTEXT, type_en TINYTEXT, group_ids SMALLINT);""")
cursor.execute(""" DROP TABLE IF EXISTS users;
                CREATE TABLE users(user_id INT UNSIGNED, group_ids SMALLINT UNSIGNED, teacher_ids SMALLINT UNSIGNED, room_id SMALLINT UNSIGNED, is_en BOOL, notification_time VARCHAR(30), black_list_ids SMALLINT UNSIGNED, subscription BOOL, showing_settings SET('a'), state TINYINT UNSIGNED);""")
cursor.execute(""" DROP TABLE IF EXISTS teachers;
                CREATE TABLE teachers(teacher_id SMALLINT UNSIGNED, surname_ru TINYTEXT, firstname_ru TINYTEXT, pathronymic_ru TINYTEXT, surname_en TINYTEXT, firstname_en TINYTEXT, pathronymic_en TINYTEXT);""")
cursor.execute("""DROP TABLE IF EXISTS rooms;
                CREATE TABLE rooms(room_id SMALLINT UNSIGNED, number SMALLINT UNSIGNED, building_ru TINYTEXT, building_en TINYTEXT);""")

for i in range(0,len(keys_fac)):
    cursor.execute(f'''REPLACE INTO faculties (faculty_id, fac_name) VALUES ({keys_fac[i]}, TO_BASE64('{values_fac[i]}'))''')
    i += 1
for i in range(0,len(keys_grp)):
    cursor.execute(f'''REPLACE INTO groups(group_id, group_number, direction, grp_spec_code) VALUES ({keys_grp[i]}, TO_BASE64('{values_grp[i][0]}'), TO_BASE64('{values_grp[i][2]}'), {values_grp[i][1]})''')
    i += 1

conn.commit()
cursor.close()


