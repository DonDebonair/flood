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

        with open(path.join(FIXTURES_DIR, "piratebay_response_one_page.html"), "r") as f:
            cls.tpb_one_page_response = f.read()

    def test_add_protocol_when_needed(self):
        api = PirateBayApi("sometpbproxy.com")
        self.assertTrue(api.base_url.startswith("https://"), "Api object adds missing protocol during construction")

    def test_ratio(self):
        torrent_with_leechers = Torrent("Something", "John", None, None, 50, 25)
        torrent_without_leechers = Torrent("Something else", "John", None, None, 50, 0)
        self.assertEqual(torrent_with_leechers.seeder_ratio, 2, "Torrent with leechers has positive ratio")
        self.assertEqual(torrent_without_leechers.seeder_ratio, float('inf'), "Torrent without leechers has infinite ratio")

    @patch('requests.get')
    def test_tpb_search(self, mock_get):
        mock_response = Mock()
        mock_response.text = self.tpb_response
        mock_get.return_value = mock_response

        api = PirateBayApi()
        torrents, num_pages = api.search("Dexter")
        self.assertEqual(len(torrents), 30, "30 torrents are found on the first page")
        self.assertEqual(num_pages, 34, "There are 34 pages of results")
        self.assertIsInstance(torrents[0], Torrent, "PirateBayApi.search returns a list of Torrent objects")
        expected_first_torrent_name = "Dexter S08E12 HDTV x264-EVOLVE[ettv]"
        self.assertEqual(torrents[0].name, expected_first_torrent_name, "First Torrent object in list matches expected Torrent object")

    @patch('requests.get')
    def test_tpb_pagination(self, mock_get):
        mock_response = Mock()
        mock_response.text = self.tpb_response
        mock_get.return_value = mock_response

        api = PirateBayApi()
        torrents, page_num = api.search("Dexter")
        mock_get.assert_called_with('https://thepiratebay.org/search/Dexter/0/7/0')
        torrents, page_num = api.search("Dexter", page=4)
        mock_get.assert_called_with('https://thepiratebay.org/search/Dexter/3/7/0')

    @patch('requests.get')
    def test_tpb_one_page_result(self, mock_get):
        mock_response = Mock()
        mock_response.text = self.tpb_one_page_response
        mock_get.return_value = mock_response
        api = PirateBayApi()
        torrents, num_pages = api.search("big buck bunny")
        self.assertEqual(len(torrents), 22, "22 torrents are found on this page")
        self.assertEqual(num_pages, 1, "There is one page with results")
        expected_first_torrent_name = "Big Buck Bunny (Peach): 720p Stereo OGG Theora version"
        self.assertEqual(torrents[0].name, expected_first_torrent_name, "First Torrent object in list matches expected Torrent object")
        self.assertEqual(torrents[0].size, u"187.78 MiB", "incorrect file size")

    @patch('requests.get')
    def test_kat_search(self, mock_get):
        mock_response = Mock()
        mock_response.text = self.kat_response
        mock_get.return_value = mock_response
        api = KickAssTorrentApi()
        torrents, num_pages = api.search("Dexter")
        self.assertEqual(len(torrents), 25, "25 torrents are found on the first page")
        self.assertEqual(num_pages, 199, "There are 199 pages of results")
        self.assertIsInstance(torrents[0], Torrent, "KickAssTorrentApi.search returns a list of Torrent objects")
        expected_first_torrent_name = "Dexter S08E11 HDTV x264-ASAP[rartv]"
        self.assertEqual(torrents[0].name, expected_first_torrent_name, "Torrent name of the first found torrents matches expected name")

    @patch('requests.get')
    def test_kat_pagination(self, mock_get):
        mock_response = Mock()
        mock_response.text = self.kat_response
        mock_get.return_value = mock_response
        api = KickAssTorrentApi()
        torrents, num_pages = api.search("Dexter")
        mock_get.assert_called_with('http://kickass.to/search/Dexter/')
        torrents, num_pages = api.search("Dexter", 4)
        mock_get.assert_called_with('http://kickass.to/search/Dexter/4/')

if __name__ == '__main__':
    unittest.main()
