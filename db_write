import pymysql
import schedule_parser
from constants import MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_BD_NAME


def fill_faculties():
    keys_fac, values_fac = zip(*schedule_parser.get_faculties().items())
    sql = "REPLACE INTO faculties (faculty_id, fac_name) VALUES (%s, %s)"
    for i in range(0, len(keys_fac)):
        data = (keys_fac[i], values_fac[i])
        cursor.execute(sql, data)
        i += 1


if __name__ == '__main__':
    conn = pymysql.connect(host=MYSQL_IP,
                           database=MYSQL_BD_NAME,
                           user=MYSQL_USER,
                           password=MYSQL_PASSWORD)
    cursor = conn.cursor()
    fill_faculties()
    conn.commit()
    cursor.close()
