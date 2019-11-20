# _*_ coding: utf-8 _*_

import telebot
from constants import TOKEN
import schedule_parser

try:
    bot = telebot.TeleBot(TOKEN)
    print(bot.get_me())

    start_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    start_markup.row()

    faculty_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    for faculty in schedule_parser.get_faculties():
        faculty_markup.row(schedule_parser.get_faculties()[faculty])

    language_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    language_markup.row('English', 'Русский')

    hide_markup = telebot.types.ReplyKeyboardRemove()


    def stating(user_id):
        state = None
        states = open('Unecon_States.txt')
        for line in states:
            if line[:9] == str(user_id):
                state = int(line[9])
                states.close()
                break
        if state is None:
            states.close()
            states = open('Unecon_States.txt', 'a')
            states.write(str(user_id) + '0' + '\n')
            states.close()
        return state


    def change_state(new_state, user_id):
        line_of_user = 0
        with open('Unecon_States.txt') as local_state:
            for local_line in local_state:
                if local_line[:9] == str(user_id):
                    break
                else:
                    line_of_user += 1
        local_state = open('Unecon_States.txt')
        lines = local_state.readlines()
        new_line = lines[line_of_user]
        lines[line_of_user] = new_line[:9] + '{}'.format(str(new_state) + '\n')
        local_state.close()
        save_changes = open('Unecon_States.txt', 'w')
        save_changes.writelines(lines)
        save_changes.close()


    @bot.message_handler(commands=['start'])
    def handle_command(message):
        user_id = message.from_user.id
        print(user_id)
        stating(message.from_user.id)

        change_state(0, user_id)
        answer = "Привет, выбери факультет, или просто введи номер группы"
        bot.send_message(message.from_user.id, answer, reply_markup=faculty_markup)

except Exception as e:
    print(e)

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
