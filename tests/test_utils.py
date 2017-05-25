from .config import MeguTestCase

from megumegu.utils import filter_schedule, merge_url

class MeguUtilsTests(MeguTestCase):

    def testscheduleOK(self):
        data = [{'schedule': '* * * * *', 'title': 'UnitTest'}]
        self.assertEqual(data, filter_schedule(data))

    def testscheduleNG(self):
        data = [{'schedule': '0 0 0 0 0', 'title': 'UnitTest'}]
        self.assertNotEqual(data, filter_schedule(data))

    def testmergeurl(self):
        base_url = 'https://example.com/'
        path = './path/to/example.jpg'
        self.assertEqual(merge_url(base_url, path), 'https://example.com/path/to/example.jpg')
