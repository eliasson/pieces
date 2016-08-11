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

from pieces.torrent import Torrent


class UbuntuTorrentTests(unittest.TestCase):
    def setUp(self):
        self.t = Torrent('tests/data/ubuntu-16.04-desktop-amd64.iso.torrent')

    def test_instantiate(self):
        self.assertIsNotNone(self.t)

    def test_is_single_file(self):
        self.assertFalse(self.t.multi_file)

    def test_announce(self):
        self.assertEqual(
            'http://torrent.ubuntu.com:6969/announce', self.t.announce)

    def test_piece_length(self):
        self.assertEqual(
            524288, self.t.piece_length)

    def test_file(self):
        self.assertEqual(1, len(self.t.files))
        self.assertEqual(
            'ubuntu-16.04-desktop-amd64.iso', self.t.files[0].name)
        self.assertEqual(1485881344, self.t.files[0].length)

    def test_hash_value(self):
        # hexdigest of the SHA1 '4344503b7e797ebf31582327a5baae35b11bda01',
        self.assertEqual(
            b"CDP;~y~\xbf1X#'\xa5\xba\xae5\xb1\x1b\xda\x01",
            self.t.info_hash)

    def test_total_size(self):
        self.assertEqual(1485881344, self.t.total_size)

    def test_pieces(self):
        self.assertEqual(2835, len(self.t.pieces))


class SXSWTorrentTests(unittest.TestCase):
    """
    Represents a multi-file torrent which is not supported
    """
    def test_instantiate(self):
        with self.assertRaises(RuntimeError):
            Torrent('tests/data/SXSW_2016_Showcasing_Artists_Part1.torrent')
