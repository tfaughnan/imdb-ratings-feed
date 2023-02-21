# IMDb ratings feed

Given the URL to an IMDb user's ratings page, this script scrapes their rating
entries, generates an Atom feed, and prints it to standard output.

Intended use case is in a cron job writing to a file which is served
by an HTTP server. Point your feed reader to the generated file's URL.

Example crontab, refreshing once per hour:

```bash
MAILTO=me@example.com
0 * * * * /path/to/main.py https://www.imdb.com/user/ur1337/ratings > /var/www/example.com/ratings.atom
```

Requires Python3, Requests, Beautiful Soup, lxml, and feedgen.
