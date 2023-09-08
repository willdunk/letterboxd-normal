'''
Pretty printing reviews with a generator.
    => Generators are good for when there are requests to many different URLs.
    => A new requests session is created for the duration of the generator.
'''

import requests
from bs4 import BeautifulSoup
from rich import print as rprint
from time import time
from pprint import pprint
from collections import defaultdict

from lboxd import lboxdlist
import lboxd
from bs4 import BeautifulSoup as bs
from rich import print as rprint

# for review in lboxd.reviews(user='hahaveryfun', count=5):
#     title = review ['title']
#     review = review['review']
#     htmlPretty = bs.prettify(bs(review, 'html.parser'))

#     rprint(f'[yellow]Title:[/yellow] [red]{title}[/red]\n{htmlPretty}')

starChar = '★'
halfChar = '½'
previewChar = '…'
def getHtmlText(url='', session=''):

    httpGet = session.get(url).text
    return httpGet

def getPageUrls(user='', session='', url=''):
    url = url.strip('/')

    htmlText = getHtmlText(url=url, session=session)
    soup = BeautifulSoup(htmlText, 'html.parser')
    pageDiv = str(soup.find("div", {'class': "pagination"}))
    try:
        lastValidPage = int(pageDiv.split('/page/')[-1].split('/')[0])

        return [f'{url}/page/{str(i)}' for i in range(1, lastValidPage + 1)]

    except ValueError:

        return [f'{url}/page/1']

def lboxdlist(user='', onlyRated=False, count=None):
    url = f'https://letterboxd.com/{user}/films'
    reviewUrl = f'https://letterboxd.com/{user}/films/reviews'
    singleUrl = url[:-1]
    titleStr = 'data-film-slug="'

    session = requests.session()

    titleRating = {}
    ct = 0
    for url in getPageUrls(user=user, session=session, url=url):
        htmlText = getHtmlText(url=url, session=session)
        soup = BeautifulSoup(htmlText, 'html.parser')

        for topDiv in soup.find_all('ul', {'class':"poster-list -p70 -grid film-list clear"}):
            movies = [(x.split('"')[0], f'{x.count(starChar) + x.count(halfChar) / 2}'.replace('0.0', '')) for x in str(topDiv).split(titleStr) if x[0] != '<']

        if onlyRated:
            movies = [i for i in movies if i[1] != '']

        for movie in movies:
            if ct == count:
                return
            ct+=1
            yield {'title':movie[0], 'rating': movie[1]}

movies = lboxdlist(user='hahaveryfun')
count = 0
for movie in movies:
    count = count + 1
    title = movie ['title']
    rating = movie['rating']
    richTitle = f'[yellow]Title:[/yellow] [red]{title}[/red]'

    if rating:
        rprint(f'{richTitle} rating={rating}')
    else:
        rprint(richTitle)

print(count)