from mock import patch, Mock
import unittest
from os import path
from flood import PirateBayApi
from flood import KickAssTorrentApi
from flood.models import Torrent

class TestFlood(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        FIXTURES_DIR = path.join(path.dirname(__file__), 'fixtures')
        with open(path.join(FIXTURES_DIR, "kat_response.html"), "r") as f:
            cls.kat_response = f.read()

        with open(path.join(FIXTURES_DIR, "piratebay_response.html"), "r") as f:
            cls.tpb_response = f.read()

    @patch('requests.get')
    def testTPB(self, mock_get):
        mock_response = Mock()
        mock_response.text = self.tpb_response
        mock_get.return_value = mock_response

        api = PirateBayApi()
        torrents = api.search("Dexter")
        self.assertEqual(len(torrents), 30, "30 torrents are found on the first page")
        self.assertIsInstance(torrents[0], Torrent, "PirateBayApi.search returns a list of Torrent objects")
        expected_first_torrent_name = "Dexter S08E12 HDTV x264-EVOLVE[ettv]"
        self.assertEqual(torrents[0].name, expected_first_torrent_name, "First Torrent object in list matches expected Torrent object")

    @patch('requests.get')
    def testKAT(self, mock_get):
        mock_response = Mock()
        mock_response.text = self.kat_response
        mock_get.return_value = mock_response
        api = KickAssTorrentApi()
        torrents = api.search("Dexter")
        self.assertEqual(len(torrents), 25, "25 torrents are found on the first page")
        self.assertIsInstance(torrents[0], Torrent, "KickAssTorrentApi.search returns a list of Torrent objects")
        expected_first_torrent_name = "Dexter S08E11 HDTV x264-ASAP[rartv]"
        self.assertEqual(torrents[0].name, expected_first_torrent_name, "Torrent name of the first found torrents matches expected name")



