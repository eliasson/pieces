#
# pieces - An experimental BitTorrent client
#
# Copyright 2016 markus.eliasson@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from collections import OrderedDict

from pieces.bencoding import Decoder, Encoder


class DecodingTests(unittest.TestCase):
    def test_peek_iis_idempotent(self):
        decoder = Decoder(b'12')

        self.assertEqual(b'1', decoder._peek())
        self.assertEqual(b'1', decoder._peek())

    def test_peek_should_handle_end(self):
        decoder = Decoder(b'1')
        decoder._index = 1

        self.assertEqual(None, decoder._peek())

    def test_read_until_found(self):
        decoder = Decoder(b'123456')

        self.assertEqual(b'123', decoder._read_until(b'4'))

    def test_read_until_not_found(self):
        decoder = Decoder(b'123456')

        with self.assertRaises(RuntimeError):
            decoder._read_until(b'7')

    def test_empty_string(self):
        with self.assertRaises(EOFError):
            Decoder(b'').decode()

    def test_not_a_string(self):
        with self.assertRaises(TypeError):
            Decoder(123).decode()
        with self.assertRaises(TypeError):
            Decoder({'a': 1}).decode()

    def test_integer(self):
        res = Decoder(b'i123e').decode()

        self.assertEqual(int(res), 123)

    def test_string(self):
        res = Decoder(b'4:name').decode()

        self.assertEqual(res, b'name')

    def test_min_string(self):
        res = Decoder(b'1:a').decode()

        self.assertEqual(res, b'a')

    def test_string_with_space(self):
        res = Decoder(b'12:Middle Earth').decode()

        self.assertEqual(res, b'Middle Earth')

    def test_list(self):
        res = Decoder(b'l4:spam4:eggsi123ee').decode()

        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], b'spam')
        self.assertEqual(res[1], b'eggs')
        self.assertEqual(res[2], 123)

    def test_dict(self):
        res = Decoder(b'd3:cow3:moo4:spam4:eggse').decode()

        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res[b'cow'], b'moo')
        self.assertEqual(res[b'spam'], b'eggs')

    def test_malformed_key_in_dict_should_failed(self):
        with self.assertRaises(EOFError):
            Decoder(b'd3:moo4:spam4:eggse').decode()


class EncodingTests(unittest.TestCase):
    def test_empty_encoding(self):
        res = Encoder(None).encode()

        self.assertEqual(res, None)

    def test_integer(self):
        res = Encoder(123).encode()

        self.assertEqual(b'i123e', res)

    def test_string(self):
        res = Encoder('Middle Earth').encode()

        self.assertEqual(b'12:Middle Earth', res)

    def test_list(self):
        res = Encoder(['spam', 'eggs', 123]).encode()

        self.assertEqual(b'l4:spam4:eggsi123ee', res)

    def test_dict(self):

        d = OrderedDict()
        d['cow'] = 'moo'
        d['spam'] = 'eggs'
        res = Encoder(d).encode()

        self.assertEqual(b'd3:cow3:moo4:spam4:eggse', res)

    def test_nested_structure(self):
        outer = OrderedDict()
        b = OrderedDict()
        b['ba'] = 'foo'
        b['bb'] = 'bar'
        outer['a'] = 123
        outer['b'] = b
        outer['c'] = [['a', 'b'], 'z']
        res = Encoder(outer).encode()

        self.assertEqual(res,
                         b'd1:ai123e1:bd2:ba3:foo2:bb3:bare1:cll1:a1:be1:zee')
