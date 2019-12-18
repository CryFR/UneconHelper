from datetime import datetime, time


def format_schedule(schedule):
    message = schedule['type']
    if 'group' in schedule:
        message += f" <b>{schedule['group']}</b>\n"
    elif 'teacher' in schedule:
        message += f" <b>{schedule['teacher']}</b>\n"
    elif 'room' in schedule:
        message += f" <b>{schedule['room']}, {schedule['building']}</b>\n"
    message += f"{schedule['date']}\n\n\n"
    if schedule['lessons']:
        for lesson in schedule['lessons']:
            message += f"{(datetime(1900,1,1)+lesson['start_time']).strftime('%H.%M')}-{(datetime(1900,1,1)+lesson['end_time']).strftime('%H.%M')}\n"
            if 'room' not in schedule:
                message += f"   {lesson['building']}, <b>{lesson['room']}</b>\n"
            message += f"   {lesson['subject']} - <i>{lesson['type']}</i>\n"
            if 'teacher' not in schedule:
                message += f"   {lesson['teacher']}\n"
            if 'group' not in schedule:
                message += f"    {', '.join(lesson['groups'])}\n"
            message += '\n'
    else:
        message += 'Пар нет, можно прередохнуть\n\n'
    return message
