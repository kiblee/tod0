import os
import unittest

from todocli.graphapi import wrapper


class GraphWrapperTest(unittest.TestCase):

    CLIENT_ID = os.environ['client_id']
    CLIENT_SECRET = os.environ['client_secret']

    def test_all_lists(self):
        result = wrapper.get_lists()
        self.assertGreater(len(result), 1)


if __name__ == '__main__':
    unittest.main()