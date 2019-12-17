import pymysql
from constants import MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_BD_NAME, TOKEN
from datetime import datetime, timedelta
from format import format_schedule
import telebot

bot = telebot.TeleBot(TOKEN, threaded=False)


def connect_and_run(func):
    def wrap(*args, **kwargs):
        conn = pymysql.connect(host=MYSQL_IP,
                               database=MYSQL_BD_NAME,
                               user=MYSQL_USER,
                               password=MYSQL_PASSWORD)
        cursor = conn.cursor()
        result = func(*args, **kwargs, cursor=cursor)
        conn.commit()
        cursor.close()
        return result
    return wrap

@connect_and_run
def time_day_notificator(user_id, cursor):
    sql = '''SELECT `day_notification`
            FROM `users`
            WHERE `user_id`=%s
            '''
    cursor.execute(sql, user_id)
    return cursor.fetchall()[0][0]

@connect_and_run
def time_first_lesson(user_id, cursor):
    sql = '''SELECT `first_lesson_notification`
            FROM `users`
            WHERE `user_id`=%s
            '''
    cursor.execute(sql, user_id)
    return cursor.fetchall()[0][0]

@connect_and_run
def find_subject(date, tracked_type, tracked_id, cursor):
    sql = '''FROM `lessons`
                JOIN `timings` ON `timings`.`number` = `lessons`.`lesson_number`
                JOIN `subjects` ON `subjects`.`subject_id` = `lessons`.`subject_id`
                JOIN `teachers` ON `teachers`.`teacher_id` = `lessons`.`teacher_id`
                JOIN `groups` ON `groups`.`group_id` = `lessons`.`group_id`
                JOIN `rooms` ON `rooms`.`room_id` = `lessons`.`room_id`'''
    if tracked_type == 'group':
        prefix = '''SELECT `time`, `subject_name`, `type`, concat_ws(' ', `surname`, `first_name`, `patronymic`), `building`, `rooms`.`number`'''
        postfix = '''WHERE  `groups`.`group_id`= %s
                         AND dates LIKE %s
                         ORDER BY `timings`.`number`'''
    elif tracked_type == 'room':
        prefix = '''SELECT `time`, `subject_name`, `type`, concat_ws(' ', `surname`, `first_name`, `patronymic`), `groups`.`group_number`'''
        postfix = '''WHERE  `rooms`.`room_id`= %s
                     AND dates LIKE %s
                     ORDER BY `timings`.`number`'''
    elif tracked_type == 'teacher':
        prefix = '''SELECT `time`, `subject_name`, `type`, `groups`.`group_number`, `building`, `rooms`.`number`'''
        postfix = '''WHERE  `teachers`.`teacher_id`= %s
                     AND dates LIKE %s
                     ORDER BY `timings`.`number`'''
    sql = f'{prefix}\n{sql}\n{postfix}'
    data = [tracked_id, f'%{date}%']
    cursor.execute(sql, data)
    schedule = cursor.fetchall()
    if schedule:
        answer = ''
        for lesson in schedule[0]:
            answer += ''.join(lesson)
            answer += '\n'
        return answer

@connect_and_run
def find_track(user_id, cursor):
    sql = '''SELECT `type`, `tracked_id`
            FROM `trackings`
            WHERE `user_id`=%s
            '''
    cursor.execute(sql, user_id)
    return cursor.fetchall()[0]

@connect_and_run
def every_lesson(user_id, cursor):
    sql = '''SELECT `day_notification`
               FROM `users`
               WHERE `user_id`=%s
               '''
    cursor.execute(sql, user_id)
    return cursor.fetchall()[0][0]

@connect_and_run
def main(cursor):
    sql = '''SELECT `user_id`
            FROM `users`
            '''
    cursor.execute(sql)
    users = cursor.fetchall()

    for ids in users:
        id = ids[0]
        now = datetime.now()
        now = now.strftime("%H:%M:%S")
        now = datetime.strptime(now, '%H:%M:%S')
        now_str = datetime.now().strftime("%d.%m.%y")

        try:
            # time_every = every_lesson(id)
            time_day = datetime.strptime(str(time_day_notificator(id)), '%H:%M:%S')
            time_first = datetime.strptime(find_subject(now_str, find_track(id)[0], find_track(id)[1])[0:5], '%H:%M') - time_first_lesson(id)
            if now - timedelta(minutes=2) <= time_day <= now + timedelta(minutes=2):
                bot.send_message(id, text=format_schedule(get_next_day(date, time, tracked_type, tracked_id, cursor)))
            if  now - timedelta(minutes=2) <= time_first <= now + timedelta(minutes=2):
                bot.send_message(id, text=find_subject(now_str, find_track(id)[0], find_track(id)[1]))
            # if now - timedelta(minutes=2) <= time_every <= now + timedelta(minutes=2):
            #     bot.send_message(id, text=format_schedule(get_nearest_lesson(date, time, tracked_type, tracked_id, cursor)))
        except:
            pass

main()