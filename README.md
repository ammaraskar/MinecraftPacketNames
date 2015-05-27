# MinecraftPacketNames
An automatically updating git repo that scrapes wiki.vg to generate a list of minecraft 
packet names and IDs for each known protocol version. Grabbed from http://wiki.vg/Protocol_version_numbers

## Dependencies

* [requests](http://docs.python-requests.org/en/latest/)
* [beautifulsoup4](http://www.crummy.com/software/BeautifulSoup/)

Also noted in ``requirements.txt``, use ``pip install -r requirements.txt`` to install them.

## Auto generation

``update_repo.sh`` automatically updates a git repo after scraping and generating the latest
packets file, it can be added under cron to run at whatever time period you want.
