import urllib.request
from bs4 import BeautifulSoup
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
main_url = 'https://rasp.unecon.ru/raspisanie.php'
group_url = 'https://rasp.unecon.ru/raspisanie_grp.php'


def get_soup(url):
    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response, 'lxml')
    return soup


def get_faculties():
    soup = get_soup(main_url)
    faculties = eval(soup.body.main.script.get_text().split('\n')[1][17:-2])
    return faculties


def get_courses(faculty_num):
    soup = get_soup(main_url)
    courses = eval(soup.body.main.script.get_text().split('\n')[2][23:-2])[str(faculty_num)]
    return courses


def get_groups(faculty_num, course):
    soup = get_soup(main_url)
    groups = {}
    group_list = eval(soup.body.main.script.get_text().split('\n')[3][25:-2])[str(faculty_num)][str(course)]
    for group_dict in group_list:
        groups.update({group_dict.get('grp_kod'): [group_dict.get('grp_nomer'), group_dict.get('grp_spec_kod'), group_dict.get('grp_spec_name')]})
    return groups


def parse_semester(group_id):
    soup = get_soup(group_url+f'?g={group_id}&semestr')
    semester_period= re.findall('\d{2}\.\d{2}\.\d{4}', soup.find('div', class_='rasp').h1.text)
    table = soup.find('table')
    rows = table('tr')
    lessons = []
    for row in rows:
        if row['class'] != ['new_day_border']:
            if row.find('span', class_='prepod').text != '':
                teacher = row.find('span', class_='prepod').text
                teacher_id = re.findall('\d+', row.find('a', {'title': 'Преподаватель'})['href'])
            else:
                teacher = teacher_id = ''
            if row.find('td', class_='aud').find('span', class_='aud').text + row.find('span', class_='korpus').text != '':
                room = row.find('td', class_='aud').find('span', class_='aud').text
                building = row.find('span', class_='korpus').text
            elif row.find('span', class_='prim').text != '':
                room = row.find('span', class_='prim').text.rpartition(',')[2].strip()
                building = row.find('span', class_='prim').text.rpartition(',')[0].strip()
            else:
                room = building = ''
            if row.find('span', class_='predmet').find('span', class_='vibor') is None:
                subject = row.find('span', class_='predmet').text.partition('(')[0].strip()
                is_chosable = False
            else:
                subject = row.find('span', class_='predmet').text.partition('(')[0].strip()[6:]
                is_chosable = True
            time = row.find('span', class_='time').text
            dates = row.find('span', class_='dates').text
            even_odd = row.find('span', class_='even_odd').text
            lesson_type = row.find('span', class_='predmet').text.rpartition('(')[2].rstrip(')')
            lessons.append({'time': time,
                           'dates': dates,
                            'even_odd': even_odd,
                            'room': room,
                            'building': building,
                            'subject': subject,
                            'is_choosable': is_chosable,
                            'type': lesson_type,
                            'teacher': teacher,
                            'teacher_id': teacher_id,
                            'semester_period': semester_period
                            })
    return lessons

