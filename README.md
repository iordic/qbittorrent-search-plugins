# Unofficial qBittorrent search engines
All related info at [unofficial search plugins wiki](https://github.com/qbittorrent/search-plugins/wiki/Unofficial-search-plugins).

## Engines implemented here
* **Elitetorrent**
  * Available categories: movies and tv series.
* **MejorTorrent**
  * Available categories: movies and tv series.

## Installation
Copy [raw link](https://raw.githubusercontent.com/iordic/qbittorrent-search-plugins/master/engines/elitetorrent.py) into your qbittorrent client. Then follow this steps:

![Show search section](/images/enable_search.png)
![Install engine](/images/instalacion_engine.png)

### (Optional) Install engine icons
If you want to add icons at search engines' menu you have to (unfortunately) follow additional steps.

![search engine icons](/images/added_icons.jpg)

Copy icon files from `engines/*.ico` files to the engines folder:
* Windows path: %localappdata%\qBittorrent\nova3\engines\
* Linux path: ~/.local/share/data/qBittorrent/nova3/engines/

![Install icons](/images/install_icons.png)

> :warning: {name}.ico files must have same name as {name}.py