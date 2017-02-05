import re
import requests
from bs4 import BeautifulSoup
from models import Torrent
from abc import ABCMeta, abstractmethod


class TorrentApi(object):
    __metaclass__ = ABCMeta

    def __init__(self, base_url):
        protocol_match = re.match(r'^https?://', base_url)
        if not protocol_match:
            base_url = 'https://' + base_url

        self.base_url = base_url if not base_url.endswith('/') else base_url[:-1]

    @abstractmethod
    def search(self, query):
        raise NotImplementedError("Should implement search()!")


class KickAssTorrentApi(TorrentApi):

    def __init__(self, base_url='http://kickass.to'):
        TorrentApi.__init__(self, base_url)

    def search(self, query, page=1):
        if page == 1:
            search_url = self.base_url + '/search/{}/'.format(query)
        else:
            search_url = self.base_url + '/search/{}/{}/'.format(query, page)

        request = requests.get(search_url)
        soup = BeautifulSoup(request.text, "lxml")

        error_page = soup.find(name='div', class_='errorpage')

        torrents = []
        num_pages = 0
        if not error_page:
            for row in soup.find_all(name='tr', id=re.compile('torrent_')):
                torrents.append(self._row_to_torrent(row))
            pagination = soup.find(name='div', class_='pages')
            num_pages = int(pagination.find_all('a')[-1].find('span').text)

        return torrents, num_pages

    def _row_to_torrent(self, row):
        torrent = Torrent()
        torrent.name = row.find(class_='torrentname').find_all('a')[1].text
        torrent.magnet_link = row.find(name='a', class_='imagnet').get('href')
        torrent.torrent_link = row.find(name='a', class_='idownload').get('href')
        tds = row.find_all('td')
        torrent.seeders = int(tds[4].text)
        torrent.leechers = int(tds[5].text)
        torrent.size = 'UNKNOWN'  # TODO
        return torrent


class PirateBayApi(TorrentApi):

    def __init__(self, base_url='https://thepiratebay.org'):
        TorrentApi.__init__(self, base_url)
        self.size_regex = re.compile('Size (\d+\.?\d*)[^MGK]+([^,]*)')

    # page numbers are 0-based for TPB, but we make them 1-based for consistency
    def search(self, query, page=1):
        search_url = self.base_url + '/search/{}/{}/7/0'.format(query, page - 1)
        request = requests.get(search_url)
        soup = BeautifulSoup(request.text, "lxml")

        table = soup.find(name='table', id='searchResult')
        pagination = soup.find(id='main-content').find_next_sibling('div')
        num_pages = len(pagination.find_all('a'))
        if num_pages == 0:  # no pagination links means there is only one page
            num_pages = 1

        torrents = []
        for row in table.find_all('tr', recursive=False):
            torrents.append(self._row_to_torrent(row))

        return torrents, num_pages

    def _row_to_torrent(self, row):
        torrent = Torrent()
        torrent_name_tag = row.find(class_='detName')
        description = row.find(class_='detDesc').text
        torrent.name = torrent_name_tag.find(class_='detLink').text
        torrent.magnet_link = torrent_name_tag.find_next_sibling('a').get('href')
        tds = row.find_all('td')
        torrent.seeders = int(tds[2].text)
        torrent.leechers = int(tds[3].text)
        torrent.size = ' '.join(self.size_regex.search(description).groups())
        return torrent
