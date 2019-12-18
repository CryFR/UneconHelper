import pymysql
from constants import MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_BD_NAME


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


def change_state(user_id, new_state, cursor):
    sql = '''INSERT INTO `users` (`user_id`, `state`) 
             VALUES (%s, %s)
             ON DUPLICATE KEY UPDATE `previous_state`=state,  `state`=%s'''
    data = [user_id, new_state, new_state]
    cursor.execute(sql, data)


def get_state(user_id, cursor):
    sql = '''SELECT `state` 
             FROM `users` 
             WHERE `user_id`=%s'''
    cursor.execute(sql, user_id)
    return cursor.fetchall()[0][0]


def get_previous_state(user_id, cursor):
    sql = '''SELECT `previous_state` 
             FROM `users` 
             WHERE `user_id`=%s'''
    cursor.execute(sql, user_id)
    return cursor.fetchall()[0][0]


def set_tracking(user_id, tracking_type, tracked_id, is_main, name, cursor):
    sql = '''INSERT INTO `trackings` (user_id, type, tracked_id, is_main, name)
             VALUES (%s, %s, %s, %s, %s)'''
    data = [user_id, tracking_type, tracked_id, is_main, name]
    cursor.execute(sql, data)


def get_tracking_names(user_id, cursor):
    sql = '''SELECT `name` 
             FROM `trackings`
             WHERE  `user_id`= %s'''
    cursor.execute(sql, user_id)
    return [tracking[0] for tracking in cursor.fetchall()]


def get_tracking_info_by_name(user_id, name, cursor):
    sql = '''SELECT `tracked_id`, `type` 
             FROM `trackings`
             WHERE  `user_id`= %s
             AND `name` = %s'''
    data = [user_id, name]
    cursor.execute(sql, data)
    return cursor.fetchall()[0][:2]


def get_main_tracking(user_id, cursor):
    sql = '''SELECT *
             FROM `trackings`
             WHERE  `user_id`= %s
             AND `is_main` = 1'''
    cursor.execute(sql, user_id)
    return cursor.fetchall()[0]


def change_main_tracking(user_id, name, cursor):
    sql = ['''UPDATE `trackings`
            SET `is_main` = 0
            WHERE `is_main` = 1
            AND `user_id` = %s
            AND `name`!= %s''',
           '''UPDATE `trackings`
            SET `is_main` = 1
            WHERE `user_id` = %s
            AND `name` =  %s''']
    data = [user_id, name]
    for query in sql:
        cursor.execute(query, data)


def remove_tracking(user_id, name, cursor):
    sql = '''DELETE FROM `trackings`
             WHERE `user_id` = %s
             AND `name` = %s'''
    data = [user_id, name]
    cursor.execute(sql, data)


def set_every_lesson_notification(user_id, time, cursor):
    sql = '''UPDATE `users`
             SET `every_lesson_notification` = %s
             WHERE `user_id` = %s'''
    data = [time, user_id]
    cursor.execute(sql, data)


def set_first_lesson_notification(user_id, time, cursor):
    sql = '''UPDATE `users`
             SET `first_lesson_notification` = %s
             WHERE `user_id` = %s'''
    data = [time, user_id]
    cursor.execute(sql, data)


def set_day_notification(user_id, time, cursor):
    sql = '''UPDATE `users`
             SET `day_notification` = %s
             WHERE `user_id` = %s'''
    data = [time, user_id]
    cursor.execute(sql, data)


def get_notification_data(user_id, cursor):
    sql = '''SELECT `first_lesson_notification`, `every_lesson_notification`, `day_notification`
    FROM `users`
    WHERE user_id = %s'''
    cursor.execute(sql, user_id)
    return cursor.fetchall()[0]


def set_buffer(user_id, buffer, cursor):
    sql = '''UPDATE `users` 
             SET `buffer`=%s
             WHERE `user_id`=%s'''
    data = [buffer, user_id]
    cursor.execute(sql, data)


def get_buffer(user_id, cursor):
    sql = '''SELECT `buffer` 
                 FROM `users` 
                 WHERE `user_id`=%s'''
    cursor.execute(sql, user_id)
    return cursor.fetchall()[0][0]


def get_faculties(cursor):
    sql = '''SELECT `faculty_name` 
             FROM `faculties`
             GROUP BY  `faculty_name`'''
    cursor.execute(sql)
    return [faculty[0] for faculty in cursor.fetchall()]


def get_specialities(faculty, cursor):
    sql = '''SELECT `group_speciality_name` 
             FROM `groups` 
             JOIN `faculties` ON `groups`.`faculty_id`=`faculties`.`faculty_id`
             WHERE `faculties`.`faculty_name` LIKE %s
             GROUP BY `group_speciality_name` 
             ORDER BY `group_speciality_name`'''
    cursor.execute(sql, faculty)
    return [speciality[0] for speciality in cursor.fetchall()]


def get_groups(faculty, speciality, cursor):
    sql = '''SELECT `course`, `group_number` 
             FROM `groups` g
             JOIN faculties f on g.faculty_id = f.faculty_id
             WHERE f.`faculty_name` = %s
             AND g.`group_speciality_name` = %s
             ORDER BY `course`, `group_number`'''
    data = [faculty, speciality]
    cursor.execute(sql, data)
    return [{'course': group[0],
             'number': group[1]}
            for group in cursor.fetchall()]


def get_all_groups(cursor):
    sql = '''SELECT `group_number`
             FROM `groups`'''
    cursor.execute(sql)
    return [group[0] for group in cursor.fetchall()]


def get_teachers(name, cursor):
    sql = '''SELECT concat_ws(' ' ,`surname`, `first_name`, `patronymic`),
             MATCH(`surname`, `first_name`, `patronymic`) 
             AGAINST (%s IN BOOLEAN MODE) AS RES
             FROM `teachers`
             WHERE MATCH(`surname`, `first_name`, `patronymic`) 
             AGAINST (%s IN BOOLEAN MODE)>0
             ORDER BY RES DESC, `surname`, `first_name`, `patronymic`'''
    data = [''.join([f'+{part}* ' for part in name.split()]) + ''.join([f'>{part} ' for part in name.split()])] * 2
    cursor.execute(sql, data)
    return [teacher[0] for teacher in cursor.fetchall()]


def get_buildings(cursor):
    sql = '''SELECT `building` 
             FROM `rooms`
             GROUP BY  `building`
             ORDER BY  `building`'''
    cursor.execute(sql)
    return [building[0] for building in cursor.fetchall() if building[0] != '']


def get_rooms(number, building, cursor):
    sql = '''SELECT `number` 
             FROM `rooms` 
             WHERE `building`=%s 
             AND `number` LIKE %s
             ORDER BY `number`'''
    data = [building, f'%{number}%']
    cursor.execute(sql, data)
    return [room[0] for room in cursor.fetchall()]


def get_teacher_id(name, cursor):
    sql = '''SELECT `teacher_id` 
                 FROM `teachers` 
                 WHERE `surname` = %s 
                 AND `first_name` = %s
                 AND `patronymic` = %s'''
    data = name.split(maxsplit=2)
    cursor.execute(sql, data)
    return cursor.fetchall()[0][0]


def get_group_id(group, cursor):
    sql = '''SELECT `group_id` 
                 FROM `groups` 
                 WHERE `group_number` = %s'''
    cursor.execute(sql, group)
    return cursor.fetchall()[0][0]


def get_room_id(number, building, cursor):
    sql = '''SELECT `room_id` 
             FROM `rooms` 
             WHERE `building`= %s 
             AND `number` LIKE %s'''
    data = [building, f'{number}']
    cursor.execute(sql, data)
    return cursor.fetchall()[0][0]


def get_name(id, type, cursor):
    if type == 'group':
        sql = '''SELECT `group_number`
                 FROM  `groups`
                 where group_id = %s'''
    elif type == 'room':
        sql = '''SELECT `building`, `number`
                 FROM  `rooms`
                 where room_id = %s'''
    elif type == 'teacher':
        sql = '''SELECT concat_ws(' ', `surname`, `first_name`, `patronymic`)
                 FROM  `teachers`
                 where teacher_id = %s'''
    cursor.execute(sql, id)
    return cursor.fetchall()[0]


def get_schedule(date, type, id, cursor):
    from datetime import datetime
    data = [id, f'%{date}%']
    date = datetime.strptime(date, '%d.%m.%y')
    schedule = {'date': f"{date.strftime('%A, %d %b %Y')}".capitalize()}
    sql = '''SELECT `lesson_number`, `start_time`, `end_time`, `subject_name`, `type`, concat_ws(' ', `surname`, `first_name`, `patronymic`), `groups`.`group_number`, `building`, `rooms`.`number`
            FROM `lessons`
            JOIN `timings`  ON `timings`.`number`       = `lessons`.`lesson_number`
            JOIN `subjects` ON `subjects`.`subject_id`  = `lessons`.`subject_id`
            JOIN `teachers` ON `teachers`.`teacher_id`  = `lessons`.`teacher_id`
            JOIN `groups`   ON `groups`.`group_id`      = `lessons`.`group_id`
            JOIN `rooms`    ON `rooms`.`room_id`        = `lessons`.`room_id`'''
    postfix = ''
    if type == 'group':
        schedule['type'] = 'Группа'
        schedule['group'] = get_name(id, type, cursor)[0]
        postfix = '''WHERE  `groups`.`group_id`= %s
                     AND dates LIKE %s
                     ORDER BY `timings`.`number`'''
    elif type == 'room':
        schedule['type'] = 'Аудитория'
        schedule['building'], schedule['room'] = get_name(id, type, cursor)
        postfix = '''WHERE  `rooms`.`room_id`= %s
                 AND dates LIKE %s
                 ORDER BY `timings`.`number`'''
    elif type == 'teacher':
        schedule['type'] = 'Преподаватель'
        schedule['teacher'] = get_name(id, type, cursor)[0]
        postfix = '''WHERE  `teachers`.`teacher_id`= %s
                 AND dates LIKE %s
                 ORDER BY `timings`.`number`'''
    sql = f'{sql}\n{postfix}'
    cursor.execute(sql, data)
    schedule['lessons'] = []
    for lesson in cursor.fetchall():
        schedule['lessons'].append({'number': lesson[0],
                                    'start_time': lesson[1],
                                    'end_time': lesson[2],
                                    'subject': lesson[3],
                                    'type': lesson[4],
                                    'teacher': lesson[5],
                                    'groups': [lesson[6]],
                                    'building': lesson[7],
                                    'room': lesson[8]})
    if type == 'group':
        for lesson in schedule['lessons']:
            del lesson['groups']
    else:
        for lesson in schedule['lessons']:
            for _lesson in schedule['lessons']:
                if lesson['number'] == _lesson['number'] and lesson['groups'] != _lesson['groups']:
                    lesson['groups'].append(*_lesson['groups'])
                    schedule['lessons'].remove(_lesson)
        if type == 'room':
            for lesson in schedule['lessons']:
                del lesson['building']
                del lesson['room']
        elif type == 'teacher':
            for lesson in schedule['lessons']:
                del lesson['teacher']
    return schedule


def get_nearest_lesson(date, time, tracked_type, tracked_id, cursor):
    pass


def reset_user(user_id, cursor):
    sql = ['''DELETE FROM `trackings`
              WHERE `user_id` = %s''',
           '''DELETE FROM `users`
              WHERE `user_id` = %s''']
    for query in sql:
        cursor.execute(query, user_id)


if __name__ == '__main__':
    from datetime import datetime
    from locale import setlocale, LC_TIME

    setlocale(LC_TIME, locale="ru_RU")
    _start_time = datetime.now()
    _conn = pymysql.connect(host=MYSQL_IP,
                            database=MYSQL_BD_NAME,
                            user=MYSQL_USER,
                            password=MYSQL_PASSWORD)
    _cursor = _conn.cursor()
    # reset_user(294821600, _cursor)
    from format import format_schedule

    # print(get_tracking_names(294821600, _cursor))
    # print(get_schedule('18.12.19', 'teacher', 14578, _cursor))
    # print(get_schedule('19.12.19', 'group', 12244, _cursor))
    # print(get_main_tracking(294821600, _cursor))
    print(get_name(15, 'room', _cursor))
    _conn.commit()
    _cursor.close()
    print((datetime.now() - _start_time))
