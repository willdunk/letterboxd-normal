'''
Pretty printing reviews with a generator.
    => Generators are good for when there are requests to many different URLs.
    => A new requests session is created for the duration of the generator.
'''

import requests
from bs4 import BeautifulSoup
from rich import print as rprint
from lboxd import lboxdlist
from bs4 import BeautifulSoup as bs
from rich import print as rprint
import math
import csv
from datetime import datetime

starChar = '★'
halfChar = '½'
previewChar = '…'
def get_html_text(url='', session=''):
    return session.get(url).text

def get_film_page_urls(user='', session='', url=''):
    url = url.strip('/')

    html_text = get_html_text(url=url, session=session)
    soup = BeautifulSoup(html_text, 'html.parser')
    page_div = str(soup.find("div", {'class': "pagination"}))
    try:
        last_valid_page = int(page_div.split('/page/')[-1].split('/')[0])
        return [f'{url}/page/{str(i)}' for i in range(1, last_valid_page + 1)]

    except ValueError:
        return [f'{url}/page/1']

def rating_list(user='', onlyRated=False, count=None):
    url = f'https://letterboxd.com/{user}/films'
    title_str = 'data-film-slug="'

    session = requests.session()

    ct = 0
    for url in get_film_page_urls(user=user, session=session, url=url):
        html_text = get_html_text(url=url, session=session)
        soup = BeautifulSoup(html_text, 'html.parser')

        for topDiv in soup.find_all('ul', {'class':"poster-list -p70 -grid film-list clear"}):
            movies = [(x.split('"')[0], f'{x.count(starChar) + x.count(halfChar) / 2}'.replace('0.0', '')) for x in str(topDiv).split(title_str) if x[0] != '<']

        if onlyRated:
            movies = [i for i in movies if i[1] != '']

        for movie in movies:
            if ct == count:
                return
            ct+=1
            yield {'title':movie[0], 'rating': movie[1]}

MAX_NUM_PAGES = 256
NUM_USERS_PER_PAGE = 30

def get_user_page_urls(time_range, page_count):
    url = f'https://letterboxd.com/members/popular/this/{time_range}'

    for number in range(1, min(page_count, MAX_NUM_PAGES)+1):
        yield f'{url}/page/{number}'

def user_list(time_range='all-time', user_count=None):
    target_user_count = MAX_NUM_PAGES * NUM_USERS_PER_PAGE if user_count == None else user_count

    page_count = math.ceil(target_user_count / NUM_USERS_PER_PAGE)

    page_urls = get_user_page_urls(time_range, page_count)

    session = requests.session()

    users = []

    for page_url in page_urls:
        html_text = get_html_text(url=page_url, session=session)
        soup = BeautifulSoup(html_text, 'html.parser')
        for element in soup.find('table', {'class': 'person-table'}).find_all('a', {'class':"avatar -a40"}): 
            if (len(users) < target_user_count):
                users.append(element['href'].strip("/"))

    return users

def zip_users_and_their_movie_ratings(users):
    result = {}
    for user in users:
        print(f'Getting ratings for user: {user}')
        movie_ratings = rating_list(user=user)
        for movie_rating in movie_ratings:
            if user not in result:
                result[user] = []
            result[user] = result[user] + [movie_rating]
    return result

def sanitize_zipped_data(zipped_data):
    result = []
    for user, movie_ratings in zipped_data.items():
        this_line = {"user": user, "rating_string": ""}
        for movie_rating in movie_ratings:
            this_line['rating_string'] = this_line['rating_string'] + '/' + movie_rating['rating']
        result.append(this_line)
    return result

users = user_list(time_range="all-time", user_count=5)
zipped_data = zip_users_and_their_movie_ratings(users)
sanitized_data = sanitize_zipped_data(zipped_data)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

filename = f"data_{timestamp}.csv"

fieldnames = sanitized_data[0].keys()  # Assuming all dictionaries have the same keys
with open(filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()  # Write the header row
    writer.writerows(sanitized_data)