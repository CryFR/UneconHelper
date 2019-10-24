# Это шаблон датабазы когда структуру создадим прост значения поменяем на пока сойдет

import sqlite3
import rasp_parser

conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()
keys, values = zip(*rasp_parser.get_faculties().items())
cursor.executescript("""DROP TABLE IF EXISTS facults;
                CREATE TABLE facults(fac_num , fac_name)""")
for i in range(0,len(keys)):
    cursor.execute('''REPLACE INTO facults(fac_num, fac_name) VALUES (?, ?)''', (keys[i],values[i]))
    i += 1

conn.commit()



