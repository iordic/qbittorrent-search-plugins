#VERSION: 2.12
#AUTHORS: Diego de las Heras (diegodelasheras@gmail.com)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
from html.parser import HTMLParser
from urllib.parse import urlencode

class torrentz(object):
    # mandatory properties
    url  = 'https://torrentz.eu'
    name = 'Torrentz'
    supported_categories = {'all': ''}

    trackers_list = ['udp://open.demonii.com:1337/announce',
                    'udp://tracker.leechers-paradise.org:6969',
                    'udp://exodus.desync.com:6969',
                    'udp://tracker.coppersurfer.tk:6969',
                    'udp://9.rarbg.com:2710/announce']

    class MyHtmlParser(HTMLParser):
        def __init__(self, results, url, trackers):
            HTMLParser.__init__(self)
            self.results = results
            self.url = url
            self.trackers = trackers
            self.td_counter = None
            self.current_item = None

        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                params = dict(attrs)
                if 'href' in params:
                    self.current_item = {}
                    self.td_counter = 0
                    self.current_item['link'] = 'magnet:?xt=urn:btih:' + \
                        params['href'].strip(' /') + self.trackers
                    self.current_item['desc_link'] = self.url + params['href'].strip()
            elif tag == 'span':
                if isinstance(self.td_counter,int):
                    self.td_counter += 1
                    if self.td_counter > 6: # safety
                        self.td_counter = None

        def handle_data(self, data):
            if self.td_counter == 0:
                if 'name' not in self.current_item:
                    self.current_item['name'] = ''
                self.current_item['name'] += data
            elif self.td_counter == 4:
                if 'size' not in self.current_item:
                    self.current_item['size'] = data.strip()
            elif self.td_counter == 5:
                if 'seeds' not in self.current_item:
                    self.current_item['seeds'] = data.strip().replace(',', '')
            elif self.td_counter == 6:
                if 'leech' not in self.current_item:
                    self.current_item['leech'] = data.strip().replace(',', '')

                # display item
                self.td_counter = None
                self.current_item['engine_url'] = self.url
                if self.current_item['name'].find(' »'):
                    self.current_item['name'] = self.current_item['name'].split(' »')[0]
                self.current_item['link'] += '&' + urlencode({'dn' : self.current_item['name']})
                if not self.current_item['seeds'].isdigit():
                    self.current_item['seeds'] = 0
                if not self.current_item['leech'].isdigit():
                    self.current_item['leech'] = 0
                prettyPrinter(self.current_item)
                self.results.append('a')

    def download_torrent(self, info):
        print(download_file(info))

    def search(self, what, cat='all'):
        # initialize trackers for magnet links
        trackers = '&' + '&'.join(urlencode({'tr' : tracker}) for tracker in self.trackers_list)

        i = 0
        while i < 6:
            results_list = []
            # "what" is already urlencoded
            html = retrieve_url(self.url + '/search?f=%s&p=%d' % (what, i))
            parser = self.MyHtmlParser(results_list, self.url, trackers)
            parser.feed(html)
            parser.close()
            if len(results_list) < 1:
                break
            i += 1
