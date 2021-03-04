# Unofficial qBittorrent search engines
Search engines implemented by me to integrate with qBittorrent GUI (used in the search tab). This engines are basically scrappers to retrieve torrents from different web pages. All the related info is [here](https://github.com/qbittorrent/search-plugins/wiki/Unofficial-search-plugins).

## Engines implemented here
* **Elitetorrent**. 
  * Available categories: (all, movies, tv)

### Installation
Copy [raw link](https://raw.githubusercontent.com/iordic/qbittorrent-search-plugins/master/engines/elitetorrent.py) into your qbittorrent client. Then follow this steps:

![Show search section](/images/enable_search.png)
![Install engine](/images/instalacion_engine.png)

### Testing
```
$ git clone https://github.com/iordic/qbittorrent-search-plugins.git
$ cd qbittorrent-search-plugins
$ python3 nova2.py <engine> <category> <query>

Example:
$ python3 nova2.py elitetorrent all godzilla
```
