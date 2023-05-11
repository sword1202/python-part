import unittest

import config
import contentstack

_preview = {
    'enable': True,
    'live_preview': '#*#*#*#*#',
    'host': 'cdn.contentstack.io',
    'content_type_uid': 'product',
    'entry_uid': 'blt909u787843',
    'authorization': 'management_token@fake@testing'
}

API_KEY = config.APIKEY
DELIVERY_TOKEN = config.DELIVERYTOKEN
ENVIRONMENT = config.ENVIRONMENT
HOST = config.HOST
ENTRY_UID = config.APIKEY


class TestLivePreviewConfig(unittest.TestCase):

    def setUp(self):
        self.stack = contentstack.Stack(
            API_KEY, DELIVERY_TOKEN,
            ENVIRONMENT, host=HOST)

    def test_01_live_preview_enabled_(self):
        self.stack = contentstack.Stack(
            API_KEY,
            DELIVERY_TOKEN,
            ENVIRONMENT,
            live_preview=_preview)
        self.stack.content_type(
            'live_content_type').entry('live_entry_uid')
        self.assertEqual(3, len(self.stack.get_live_preview))
        self.assertTrue(self.stack.get_live_preview['enable'])
        self.assertTrue(self.stack.get_live_preview['authorization'])

    def test_021_live_preview_enabled_(self):
        self.stack = contentstack.Stack(
            API_KEY,
            DELIVERY_TOKEN,
            ENVIRONMENT,
            live_preview=_preview)
        self.assertEqual(_preview['authorization'],
                         self.stack.live_preview['authorization'])

    def test_03_set_host(self):
        self.stack = contentstack.Stack(
            API_KEY,
            DELIVERY_TOKEN,
            ENVIRONMENT,
            live_preview=_preview)
        self.assertEqual(3, len(self.stack.live_preview))
        self.assertEqual(True, self.stack.live_preview['enable'])

    def test_031_set_host_value(self):
        self.stack = contentstack.Stack(
            API_KEY,
            DELIVERY_TOKEN,
            ENVIRONMENT,
            live_preview=_preview)
        self.assertEqual(3, len(self.stack.live_preview))
        self.assertEqual(_preview['host'],
                         self.stack.live_preview['host'])

    def test_06_live_preview_query(self):
        _live_preview = {
            'include_edit_tags': True,
            'edit_tags_type': object,
        }
        _preview.update(_live_preview)
        self.stack = contentstack.Stack(
            API_KEY,
            DELIVERY_TOKEN,
            ENVIRONMENT,
            live_preview=_preview
        )
        self.assertEqual(5, len(self.stack.live_preview))

    def test_07_branching(self):
        stack = contentstack.Stack(
            'api_key', 'delivery_token', 'environment', branch='dev_branch')
        stack.content_type('product')
        self.assertEqual('dev_branch', stack.get_branch)

    def test_08_live_preview_query_hash_included(self):
        self.stack = contentstack.Stack(
            API_KEY,
            DELIVERY_TOKEN,
            ENVIRONMENT,
            live_preview=_preview
        )
        self.stack.live_preview_query(
            hash='live_preview',
            content_type_uid='fake@content_type')
        self.assertEqual(7, len(self.stack.live_preview))

    def test_09_live_preview_query_hash_excluded(self):
        self.stack = contentstack.Stack(
            API_KEY,
            DELIVERY_TOKEN,
            ENVIRONMENT,
            live_preview=_preview
        )
        self.stack.live_preview_query(live_preview=_preview)
        self.stack.content_type('product').entry(entry_uid='blt43434433432')
        self.assertEqual(3, len(self.stack.headers))
        self.assertEqual(True, 'access_token' in self.stack.headers)
        self.assertEqual(True, 'api_key' in self.stack.headers)

    def test_10_live_preview_check_hash_value(self):
        self.stack = contentstack.Stack(
            API_KEY,
            DELIVERY_TOKEN,
            ENVIRONMENT,
            live_preview=_preview
        )
        self.stack.live_preview_query(live_preview={
            'enable': True,
            'live_preview': 'B0B)B)B)BB)B',
            'host': 'cdn.contentstack.io',
            'content_type_uid': 'producto',
            'entry_uid': 'blt909u787843',
            'authorization': 'management_token@fake@testing'
        })
        entry = self.stack.content_type('product').entry(entry_uid=ENTRY_UID)
        response = entry.fetch()
        self.assertEqual(2, len(self.stack.headers))
        self.assertEqual(API_KEY, self.stack.headers['api_key'])

    def test_11_live_preview(self):
        stack = contentstack.Stack(
            'api_key',
            'delivery_token',
            'development',
            live_preview=_preview).live_preview_query(
            entry_uid='entry_uid',
            content_type_uid='bugfixes',
            hash='#Just_fake_it'
        )
        result = stack.content_type(content_type_uid='bugfixes').query().find()


if __name__ == '__main__':
    unittest.main()
