# VERSION: 1.01
# AUTHORS: iordic (iordicdev@gmail.com)

import re
import urllib.parse
from datetime import datetime
from html.parser import HTMLParser

from novaprinter import prettyPrinter
from helpers import download_file, retrieve_url

MAX_PAGES = 10

class mejortorrent(object):
    url = 'https://www36.mejortorrent.eu'
    name = 'MejorTorrent'
    supported_categories = {'all': '0', 'movies': 'pelicula', 'tv': 'serie'}

    class SeriesHtmlParser(HTMLParser):
        def __init__(self, domain):
            HTMLParser.__init__(self)
            self.domain = domain
        
        def init(self, link):
            self.path = link
            self.title = ""
            self.title_found = False
            self.table_found = False
            self.item_found = False
            self.field_found = False
            self.key_found = False
            self.column_number = 0
            self.item = {}

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            if tag == "p":
                if "class" in params and "text-blue-900" in params["class"]:
                    self.title_found = True
                elif self.field_found:
                    self.key_found = True
            if self.table_found:
                if tag == "tr":
                    self.item_found = True
                elif tag == "td":
                    self.field_found = True
                elif tag == "a" and self.field_found and "href" in params:
                    self.item['link'] = params["href"]
            else:
                if tag == "tbody":
                    self.table_found = True
                    
        def handle_data(self, data):
            data = data.strip()
            if self.title_found:
                self.title = data
            if self.field_found:
                if self.column_number == 0:
                    self.item['id'] = data
                elif self.column_number == 1:
                    self.item['episodes'] = data
                elif self.column_number == 2:
                    self.item['date'] = round(datetime.timestamp(datetime.strptime(data, "%Y-%m-%d")))
                elif self.column_number == 3 and self.key_found:
                    self.item['key'] = data

        def handle_endtag(self, tag):
            if tag == "p": 
                if self.title_found:
                    self.title_found = False
                elif self.key_found:
                    self.key_found = False
            if tag == "td" and self.field_found:
                self.field_found = False
                self.column_number += 1
            if tag == "tr" and self.item_found:
                info = {
                    'name': "{title} ({episodes}){key}" \
                            .format(title=self.title, episodes=self.item['episodes'], key=", password: " + self.item['key'] if self.item['key'] != "Sin clave" else ""),
                    'size': -1,
                    'link': '{domain}{path}'.format(domain=self.domain, path=self.item['link']),
                    'desc_link': self.path,
                    'engine_url': self.domain,
                    'seeds': -1,
                    'leech': -1,
                    'pub_date': self.item['date']
                }
                prettyPrinter(info)
                self.item_found = False
                self.item = {}
                self.column_number = 0

    def __init__(self):
        self.tv_parser = self.SeriesHtmlParser(self.url)
    
    def download_torrent(self, info):
        print(download_file(info))

    def search(self, what, cat='all'):
        # Search example: https://www21.mejortorrent.zip/busqueda?q=godzilla
        search_url = "{domain}/busqueda?q={query}".format(domain=self.url, query=what)
        html = retrieve_url(search_url)
        num_pages = self.get_num_pages(html)
        items = []
        items.extend(self.parse_page(html, cat))
        for p in range(2, self.get_num_pages(html) + 1):
            if p > MAX_PAGES:
                break
            # Search page example: https://www21.mejortorrent.zip/busqueda/page/3?q=paco
            search_url = "{domain}/busqueda/page/{page}?q={query}".format(domain=self.url, page=p, query=what)
            html = retrieve_url(search_url)
            items.extend(self.parse_page(html, cat))
        
        for i in items:
            if self.supported_categories['movies'] in i:
                self.parse_film(i)
            elif self.supported_categories['tv'] in i:
                self.parse_tv_season(i)

    def get_num_pages(self, html):
        pages = re.findall(r'"go to page [0-9]+"', html)
        if not pages:
            return 1
        else:
            # map to array of integers and calculate max value
            return max(list(map(lambda n: int(n.strip('"').split(" ")[-1]), pages)))

    def parse_page(self, html, category):
        all_categories = dict(self.supported_categories)  # create a copy
        all_categories.pop('all')
        category_patterns = map(lambda e: "{domain}/{category}/[0-9]+/[^\"]+".format(domain=self.url, category=e), list(all_categories.values()))
        pattern = r"({})".format("|".join(category_patterns)) if category == "all" \
            else r'{domain}/{category}/[0-9]+/[^\"]+'.format(domain=self.url, category=self.supported_categories[category])
        return re.findall(pattern, html)

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
    
    def parse_tv_season(self, link):
        html = retrieve_url(link)
        self.tv_parser.init(link)
        self.tv_parser.feed(html)
