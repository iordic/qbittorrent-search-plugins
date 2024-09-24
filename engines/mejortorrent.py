#VERSION: 1.00
# AUTHORS: iordic (iordicdev@gmail.com)

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter

from datetime import datetime
import urllib.parse
import re

class mejortorrent(object):
    url = 'https://www21.mejortorrent.zip'
    name = 'MejorTorrent'
    supported_categories = {
        'all': '0',
        'movies': 'pelicula',
        'tv': 'serie'
    }

    def __init__(self):
        """
        Some initialization
        """

    def download_torrent(self, info):
        print(download_file(info))

    def search(self, what, cat='all'):
        #Search example: https://www21.mejortorrent.zip/busqueda?q=godzilla
        #TODO: pagination: search_url = "{domain}/page/{page}/?s={query}".format(domain=self.url, page=page, query=what.replace('%20', '+'))
        search_url = "{domain}/busqueda?q={query}".format(domain=self.url, query=urllib.parse.quote(what))
        html = retrieve_url(search_url)
        all_categories = dict(self.supported_categories)  # create a copy
        all_categories.pop('all')
        category_patterns = map(lambda e: "{domain}/{category}/[0-9]+/[^\"]+".format(domain=self.url, category=e), list(all_categories.values()))
        pattern = r"({})".format("|".join(category_patterns)) if cat == "all" \
            else r'{domain}/{category}/[0-9]+/[^\"]+'.format(domain=self.url, category=self.supported_categories[cat])
        items = re.findall(pattern, html)
        for i in items:
            if self.supported_categories['movies'] in i:
                self.parse_film(i)
            elif self.supported_categories['tv'] in i:
                self.parse_tv_season(i)

    def parse_film(self, url):
        html = retrieve_url(url)
        title = re.search(r'text-blue-900">[^\<]+', html).group(0).split('>')[-1]
        quality = re.search(r'/quality/[^\"]+', html).group(0).split('/')[-1]
        
        info = {
            'name': '{title} ({quality})'.format(title=title, quality=quality),
            'size': -1,
            'link': '{domain}{path}'.format(domain=self.url, path=re.search(r'/torrents/.+\.torrent', html).group(0)),
            'desc_link': url,
            'engine_url': self.url,
            'seeds': -1,
            'leech': -1,
            'pub_date': round(datetime.timestamp(datetime.strptime(re.search(r'[0-9]{2}/[0-9]{2}/[0-9]{4}', html).group(0), "%d/%m/%Y")))
        }
        prettyPrinter(info)
    
    def parse_tv_season(self, url):
        None
