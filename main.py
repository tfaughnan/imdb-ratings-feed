#!/usr/bin/env python3

import datetime
import logging
import re
import sys

import bs4
import feedgen.feed
import requests

USERNAME_REGEX = re.compile(r"^(?P<username>[a-zA-Z0-9_-]+)'s Ratings$")
DATE_REGEX = re.compile(r'^Rated on (?P<date_string>[0-9]{2} [a-zA-Z]{3} [0-9]{4})$')

def main() -> int:
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    if len(sys.argv) != 2:
        logging.error(f'Usage: {sys.argv[0]} IMDB_RATINGS_URL')
        return 1
    ratings_url = sys.argv[1]
    try:
        r = requests.get(ratings_url)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return 1

    soup = bs4.BeautifulSoup(r.text, 'lxml')
    username_line = soup.find('h1').text
    m = USERNAME_REGEX.match(username_line)
    if not m:
        logging.error(f'Failed to match username regex in "{username_line}"')
        return 1
    username = m.group('username')

    fg = feedgen.feed.FeedGenerator()
    fg.id(ratings_url)
    fg.title(f'{username}\'s IMDb ratings')
    fg.author(name=username)
    fg.link(href=ratings_url, rel='alternate')
    fg.language('en')

    for tag in soup.find_all('div', {'class': 'mode-detail'}):
        movie_img_url = tag.find('img')['loadlate']
        movie_title_tag = tag.find('h3', {
            'class': 'lister-item-header'
        }).find('a')
        movie_title = movie_title_tag.text
        movie_url = movie_title_tag['href']
        movie_year = tag.find('span', {'class': 'lister-item-year'}).text
        rating_stars = tag.find('div', {
            'class': 'ipl-rating-star--other-user'
        }).find('span', {
            'class': 'ipl-rating-star__rating'
        }).text
        date_line = tag.find('p', string=re.compile(DATE_REGEX)).text
        m = DATE_REGEX.match(date_line)
        if not m:
            logging.error(f'Failed to match date regex in "{date_line}"')
            return 1
        date_string = m.group('date_string')
        try:
            rating_date = datetime.datetime.strptime(date_string, '%d %b %Y')
        except ValueError as e:
            logging.error(e)
            return 1
        rating_date = rating_date.replace(tzinfo=datetime.timezone.utc)

        fe = fg.add_entry()
        fe.id(movie_url)
        fe.title(f'{movie_title} {movie_year} \u2605 {rating_stars}/10')
        fe.author(name=username)
        fe.published(rating_date)
        fe.updated(rating_date)
        fe.link(href=ratings_url, rel='alternate')
        fe.content(f'<p>{username} rated <a href="{movie_url}">{movie_title} '
                   f'{movie_year}</a></p><img src="{movie_img_url}">',
                   type='html')

    atomfeed = fg.atom_str(pretty=True)
    print(atomfeed.decode())
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
