import urllib.request
from bs4 import BeautifulSoup


def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def get_faculties():
    html = get_html('https://rasp.unecon.ru/raspisanie.php')
    soup = BeautifulSoup(html, 'html.parser')
    faculties = eval(soup.body.main.script.get_text().split('\n')[1][17:-2])
    return faculties


def get_courses(faculty_num):
    html = get_html('https://rasp.unecon.ru/raspisanie.php')
    soup = BeautifulSoup(html, 'html.parser')
    courses = eval(soup.body.main.script.get_text().split('\n')[2][23:-2])[str(faculty_num)]
    return courses


def get_groups(faculty_num, course):
    html = get_html('https://rasp.unecon.ru/raspisanie.php')
    soup = BeautifulSoup(html, 'html.parser')
    groups = {}
    group_list = eval(soup.body.main.script.get_text().split('\n')[3][25:-2])[str(faculty_num)][str(course)]
    for group_dict in group_list:
        groups.update({group_dict.get('grp_kod'): [group_dict.get('grp_nomer'), group_dict.get('grp_spec_name')]})
        groups.update({group_dict.get('grp_kod'): [group_dict.get('grp_nomer'), group_dict.get('grp_spec_kod'), group_dict.get('grp_spec_name')]})
    return groups


def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
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

print(get_groups(18, 2))
