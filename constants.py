TOKEN = '860115005:AAEJ4zeXMpANPc1KEmxS1GRCTjoUZ7WLW70'

IP = '128.199.50.189'
PORT = 8443
URL = f"https://{IP}:{PORT}"
PATH = f"/{TOKEN}/"
LISTEN = '0.0.0.0'
SSL_CERTIFICATE = './unecon_helper.crt'
SSL_KEY = './unecon_helper.key'

MYSQL_IP = '128.199.50.189'
MYSQL_USER = 'uneconBot'
MYSQL_PASSWORD = 'G2o7qBBPEvN550EjTLCv'
MYSQL_BD_NAME = 'unecon_bot'

states = {'add_schedule': 0,
          'waiting_for_faculty/group': 1,
          'waiting_for_speciality': 2,
          'waiting_for_teacher': 3,
          'waiting_for_building': 4,
          'waiting_for_room': 5,
          'notifications': 6,
          'every_lesson_notification': 7,
          'first_lesson_notification': 8,
          'day_notification': 9,
          'main': 10,
          'settings': 11,
          'set_main_schedule': 13,
          'is_notifications_needed': 14
          }

every_lesson_notification_options = {'С началом пары': '0',
                                     '️️За 5 минут': '00:05',
                                     'За 10 минут': '00:10',
                                     '️️За 15 минут': '00:15',
                                     'Не уведомлять': None
                                     }
