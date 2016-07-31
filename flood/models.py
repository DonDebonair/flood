from __future__ import division

class Torrent(object):

    def __init__(self, name=None, uploader=None, magnet_link=None, torrent_link=None, seeders=0, leechers=0, size=None):
        self.name = name
        self.uploader=None
        self.magnet_link = magnet_link
        self.torrent_link = torrent_link
        self.seeders = seeders
        self.leechers = leechers
        self.size = size

    @property
    def seeder_ratio(self):
        return self.seeders / self.leechers if self.leechers != 0 else float('inf')
