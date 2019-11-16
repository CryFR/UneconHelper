import urllib.request
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
main_url = 'https://rasp.unecon.ru/raspisanie.php'
group_url = 'https://rasp.unecon.ru/raspisanie_grp.php'


def get_soup(url):
    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response, 'html.parser')
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
    table = soup.find('table')
    rows = table.find_all('tr')
    days = []
    for element in rows[1:]:
        content = element.find_all('td')
        try:
            days.append({
                'time': content[1].span.text,
                'dates': content[1].find('span', {'class': 'dates'}).text,
                'even_odd': content[1].find('span', {'class': 'even_odd'}).text,
                'room': content[2].span.text,
                'lesson': content[3].find('span', {'class': 'predmet'}).text,
                'teacher': content[3].find('span', {'class': 'prepod'}).text
            })
        except:
            try:
                days.append({
                    'time': content[1].span.text,
                    'dates': content[1].find('span', {'class': 'dates'}).text,
                    'room': content[2].span.text,
                    'lesson': content[3].find('span', {'class': 'predmet'}).text,
                    'teacher': content[3].find('span', {'class': 'prepod'}).text
                })
            except:
                pass
    return days
