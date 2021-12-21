import re
import requests
from bs4 import BeautifulSoup
import json

from datetime import datetime

link = 'https://www.instagram.com/accounts/login/'
login_url = 'https://www.instagram.com/accounts/login/ajax/'
home = 'https://www.instagram.com/'
search_url = 'https://www.instagram.com/explore/tags/tuborg/'
sections_url = 'https://www.instagram.com/api/v1/tags/tuborg/sections/'

time = int(datetime.now().timestamp())

payload = {
    'username': '',
    'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:',
    # <-- note the '0' - that means we want to use plain passwords
    'queryParams': {},
    'optIntoOneTap': 'false'
}

with requests.Session() as s:
    r = s.get(link)
    csrf = re.findall(r"csrf_token\":\"(.*?)\"", r.text)[0]
    r = s.post(login_url, data=payload, headers={
        "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": csrf
    })
    print(r.status_code)
    print(r.url)
    print(r.text)
with open('index.html', 'w') as f:
    f.write(r.text)

r = s.get(search_url)
soup = BeautifulSoup(r.text, 'html.parser')
data = soup.find('script', text=re.compile("window._sharedData")).text
data = data[data.find('{') - 1:-1]
data = json.loads(data)
# print ()
data = data['entry_data']['TagPage'][0]['data']
sections = data['top']['sections']
posts = []
posts_in_tag = []
for section in sections:
    medias = section['layout_content']['medias']
    for media in medias:
        media = media['media']
        user_name = media['user']['username']
        url = f'https://www.instagram.com/p/{media["code"]}'
        posts.append(url)
        posts_in_tag.append(media)
        print('**********************')
        print(user_name)
        print(url)

post = s.get(posts[4])
soup = BeautifulSoup(post.text, 'html.parser')
data = soup.findAll('script', text=re.compile("window.__additionalDataLoaded"))[1].text
# data = soup.find('script', text=re.compile("window.__additionalDataLoaded")).text
data = data[data.find('{'):-2]
data = json.loads(data)

with open('tag_data.json', 'w', encoding='utf-8') as f:
    json.dump(posts_in_tag[4], f, ensure_ascii=False)
print(s.cookies)
for cookie in s.cookies:
    print(cookie)
r = s.post(sections_url, cookies=s.cookies)
soup = BeautifulSoup(r.text, 'html.parser')
# data = soup.findAll('script')
data = soup.find('script', text=re.compile("window._sharedData")).text
data = data[data.find('{') - 1:-1]
data = json.loads(data)
# with open('tags.json', 'w', encoding='utf-8') as f:
#     json.dump(data, f,ensure_ascii=False)
# print ()
data = data['entry_data']['TagPage'][0]['data']
sections = data['top']['sections']
medias = sections[2]['layout_content']['medias']
media = medias[0]['media']
user_name = media['user']['username']
url = f'https://www.instagram.com/p/{media["code"]}'
print(url)
