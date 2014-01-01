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
            base_url = 'http://' + base_url

        self.base_url = base_url if not base_url.endswith('/') else base_url[:-1]

    @abstractmethod
    def search(self, query):
        raise NotImplementedError("Should implement search()!")


class KickAssTorrentApi(TorrentApi):

    def __init__(self, base_url='http://kickass.to'):
        TorrentApi.__init__(self, base_url)

    def search(self, query):
        search_url = self.base_url + '/search/{}/'.format(query)
        request = requests.get(search_url)
        soup = BeautifulSoup(request.text)

        torrents = []
        for row in soup.find_all(name='tr', id=re.compile('torrent_')):
            torrents.append(self._row_to_torrent(row))

        return torrents

    def _row_to_torrent(self, row):
        torrent = Torrent()
        torrent.name = row.find(class_='torrentname').find_all('a')[1].text
        torrent.magnet_link = row.find(name='a', class_='imagnet').get('href')
        torrent.torrent_link = row.find(name='a', class_='idownload').get('href')
        tds = row.find_all('td')
        torrent.seeders = int(tds[4].text)
        torrent.leechers = int(tds[5].text)
        return torrent


class PirateBayApi(TorrentApi):

    def __init__(self, base_url='http://thepiratebay.se'):
        TorrentApi.__init__(self, base_url)

    def search(self, query):
        search_url = self.base_url + '/search/{}/0/7/0'.format(query)
        request = requests.get(search_url)
        soup = BeautifulSoup(request.text)

        table = soup.find(name='table', id='searchResult')

        torrents = []
        for row in table.find_all('tr', recursive=False):
            torrents.append(self._row_to_torrent(row))

        return torrents

    def _row_to_torrent(self, row):
        torrent = Torrent()
        torrent_name_tag = row.find(class_='detName')
        torrent.name = torrent_name_tag.find(class_='detLink').text
        torrent.magnet_link = torrent_name_tag.find_next_sibling('a').get('href')
        tds = row.find_all('td')
        torrent.seeders = int(tds[2].text)
        torrent.leechers = int(tds[3].text)
        return torrent
