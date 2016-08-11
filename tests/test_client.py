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

from . import no_logging
from pieces.client import Piece, Block


class PieceTests(unittest.TestCase):
    def test_empty_piece(self):
        p = Piece(0, blocks=[], hash_value=None)
        self.assertIsNone(p.next_request())

    def test_request_ok(self):
        blocks = [Block(0, offset, length=10) for offset in range(0, 100, 10)]
        p = Piece(0, blocks, hash_value=None)

        block = p.next_request()
        missing_blocks = [b for b in p.blocks if b.status is Block.Missing]
        pending_blocks = [b for b in p.blocks if b.status is Block.Pending]

        self.assertEqual(1, len(pending_blocks))
        self.assertEqual(9, len(missing_blocks))
        self.assertEqual(block, pending_blocks[0])

    def test_reset_missing_block(self):
        p = Piece(0, blocks=[], hash_value=None)
        with no_logging:
            p.block_received(123, b'')   # Should not throw

    def test_reset_block(self):
        blocks = [Block(0, offset, length=10) for offset in range(0, 100, 10)]
        p = Piece(0, blocks, hash_value=None)

        p.block_received(10, b'')

        self.assertEqual(1, len([b for b in p.blocks
                                if b.status is Block.Retrieved]))
        self.assertEqual(9, len([b for b in p.blocks
                                if b.status is Block.Missing]))
