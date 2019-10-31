import sqlite3
import rasp_parser

conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()
keys_fac, values_fac = zip(*rasp_parser.get_faculties().items())
keys_grp, values_grp  = zip(*rasp_parser.get_groups(18, 2).items())
# keys_time, value_time = zip(*rasp_parser.parse().items())
cursor.executescript("""DROP TABLE IF EXISTS facults;
                CREATE TABLE facults(fac_num , fac_name);
                DROP TABLE IF EXISTS groups;
                CREATE TABLE groups(grp_kod, grp_nomer, grp_spec_name, grp_spec_kod);
                DROP TABLE IF EXISTS timetable;
                CREATE TABLE timetable(date, day, time, room, lesson, teacher)
                """)

for i in range(0,len(keys_fac)):
    cursor.execute('''REPLACE INTO facults(fac_num, fac_name) VALUES (?, ?)''', (keys_fac[i],values_fac[i]))
    i += 1
for i in range(0,len(keys_grp)):
    cursor.execute('''REPLACE INTO groups(grp_kod, grp_nomer, grp_spec_name, grp_spec_kod) VALUES (?, ?, ?, ?)''', (keys_grp[i], values_grp[i][0], values_grp[i][2], values_grp[i][1]))
    i += 1

conn.commit()



