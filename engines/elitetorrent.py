#VERSION: 1.5
# AUTHORS: iordic (iordicdev@gmail.com)
import re
import base64
import codecs

from html.parser import HTMLParser
from novaprinter import prettyPrinter
from helpers import download_file, retrieve_url

MAX_DEPTH = 10

def deobfuscate_magnet(obfuscated):
    try:
        for i in range(MAX_DEPTH):
            obfuscated = base64.b64decode(obfuscated)
            decoded_value = codecs.decode(obfuscated.decode(encoding='utf-8'), 'rot_13')
            if 'magnet' in decoded_value:
                return decoded_value
    except:
        return None


class elitetorrent(object):
    url = 'https://www.elitetorrent.com'
    name = 'Elitetorrent'
    # Page has only movies and tv series. Search box has no filters
    supported_categories = {'all': '0', 'movies': 'peliculas', 'tv': 'series'}

    def __init__(self):
        self.pages_limit = 2     # Limit of pages, more pages increase the time it takes

    def download_torrent(self, info):
        """ Unused :( """
        print(download_file(info))

    def search(self, what, cat='all'):
        search_url = "{}/?s={}".format(self.url, what.replace('%20', '+'))
        html = retrieve_url(search_url)

        # Get number of pages
        if "paginacion" in html:
            pages = re.findall(r'<a.*?class="pagina.*?</a>', html)
            if len(pages) > 0:
                last_page = pages[-1]
                last_page = re.findall(r'page/.*?/', last_page)[0]
                last_page = last_page.replace('/', '').replace('page', '')
                number_pages = int(last_page)

        # Only one page but there are results
        elif "Resultado de buscar" in html:
            number_pages = 1
        else:
            # A little trick to avoid entering the pages loop
            number_pages = 0

        # Set number of pages depending by limit
        number_pages = number_pages if number_pages < self.pages_limit else self.pages_limit

        links = []
        
        for page in range(1, number_pages + 1):
            # Each page's url looks like: https://www.example.com/page/[1-9]*/?s=WHAT
            url = "{}/page/{}/?s={}".format(self.url, page, what.replace('%20', '+'))
            html = retrieve_url(url).replace('\n','')   # Replace newline to help the regex
            # I hate regex, check if selected category is films or tv, if its 'all' get both
            pattern = r'({0}/series/.*?/|{0}/peliculas/.*?/)'.format(self.url) if cat == "all" \
                        else r'{0}/{1}/.*?/'.format(self.url, self.supported_categories[cat])
            # Get all ocurrencies
            items = re.findall(pattern, html)
            for item in items:
                if item not in links:
                    links.append(item)

        for i in links:
            # Visiting individual results to get its attributes makes it so slow
            data = retrieve_url(i).replace('\n','')
            item = {}
            # Unable to obtain info about leechers and seaders
            item['seeds'] = '-1'
            item['leech'] = '-1'
            item['name'] = i.split("/")[-2]
            item['size'] = re.search("Tama.?o:</b> [0-9\.]+[\ GM]+B", data).group(0).split("</b>")[1].strip()
            item['desc_link'] = i
            item['engine_url'] = self.url
            item['link'] = deobfuscate_magnet(re.findall(r'i=[-A-Za-z0-9+/]+\={0,3}\"', data)[1].lstrip('i=').rstrip('"'))
            if item['link'] is None:
                continue    # decoding has failed, skip
            # Prints in this format: link|name|size|seeds|leech|engine_url|desc_link
            prettyPrinter(item)
