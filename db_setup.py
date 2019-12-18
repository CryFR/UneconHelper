import pymysql
from constants import MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD, MYSQL_BD_NAME

sql = ['''DROP TABLE IF EXISTS `users`;''',
       '''CREATE TABLE `users`(
               `user_id` INT UNSIGNED NOT NULL PRIMARY KEY,
               `lang` CHAR(2) DEFAULT 'ru',
               `first_lesson_notification` TIME NULL,
               `every_lesson_notification` TIME NULL,
               `day_notification` TIME NULL,
               `subscription` BOOL,
               `showing_settings` SET(''),
               `buffer` TINYTEXT,
               `previous_state` TINYINT UNSIGNED,
               `state` TINYINT UNSIGNED
               )COLLATE='utf8_general_ci';''',
       '''DROP TABLE IF EXISTS `groups`;''',
       '''CREATE TABLE `groups`(
               `group_id` INT UNSIGNED PRIMARY KEY,
               `faculty_id` SMALLINT UNSIGNED,
               `course` TINYINT(3),
               `group_number` CHAR(15),
               `group_speciality_name` TINYTEXT,
               `group_speciality_code` INT UNSIGNED
               ) COLLATE='utf8_general_ci';''',
       '''DROP TABLE IF EXISTS `faculties`;''',
       '''CREATE TABLE `faculties` (
               `faculty_id` SMALLINT UNSIGNED PRIMARY KEY,
               `courses` SET('1', '2', '3', '4', '5', '6'),
               `faculty_name` TINYTEXT
               )COLLATE='utf8_general_ci';''',
       '''DROP TABLE IF EXISTS `timings`;''',
       '''CREATE TABLE `timings`(
               `number` TINYINT(3) NOT NULL PRIMARY KEY,
               `time` TINYTEXT,
               `start_time` TIME,
               `end_time` TIME
       ) COLLATE='utf8_general_ci';''',
       '''DROP TABLE IF EXISTS `teachers`;''',
       '''CREATE TABLE `teachers`(
               `teacher_id` INT UNSIGNED NOT NULL PRIMARY KEY,
               `surname` TINYTEXT,
               `first_name` TINYTEXT,
               `patronymic` TINYTEXT,
               FULLTEXT KEY `full_name`(`first_name` (30),`surname`(30),`patronymic`(30))
               ) COLLATE='utf8_general_ci';''',
       '''DROP TABLE IF EXISTS lessons;''',
       '''CREATE TABLE lessons(
               `subject_id` SMALLINT UNSIGNED NOT NULL,
               `is_choosable` BOOL,
               `teacher_id` INT UNSIGNED,
               `room_id` SMALLINT UNSIGNED,
               `dates` JSON,
               `lesson_number` TINYINT(3),
               `type` TINYTEXT,
               `group_id` SMALLINT UNSIGNED
               ) COLLATE='utf8_general_ci';''',
       '''DROP TABLE IF EXISTS `rooms`;''',
       '''CREATE TABLE `rooms`(
               `room_id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
               `number` TINYTEXT,
               `building` TINYTEXT,
               UNIQUE INDEX full_number (number(10), building(30))
               ) COLLATE='utf8_general_ci';''',
       '''DROP TABLE IF EXISTS `subjects`;''',
       '''CREATE TABLE `subjects`(
               `subject_id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
               `subject_name` TINYTEXT,
               `shortcut` TINYTEXT,
               UNIQUE INDEX (subject_name(80))
               ) COLLATE='utf8_general_ci';''',
       '''DROP TABLE IF EXISTS `trackings`;''',
       '''CREATE TABLE `trackings`(
               `user_id` INT UNSIGNED NOT NULL,
               `name` TINYTEXT,
               `type` SET('room', 'teacher', 'group') NOT NULL,
               `tracked_id` INT UNSIGNED NOT NULL,
               `black_list` JSON,
               `is_main` BOOL NOT NULL 
               ) COLLATE='utf8_general_ci';'''
       ]


def reset():
    conn = pymysql.connect(host=MYSQL_IP,
                           database=MYSQL_BD_NAME,
                           user=MYSQL_USER,
                           password=MYSQL_PASSWORD)
    cursor = conn.cursor()
    if input('Next action will erase all data in tables y/n?') == 'y':
        for query in sql:
            print(query)
            cursor.execute(query)
    conn.commit()
    cursor.close()


if __name__ == '__main__':
    reset()
