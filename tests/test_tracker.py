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

from pieces.tracker import _calculate_peer_id, TrackerResponse


class TrackerTests(unittest.TestCase):
    def test_peer_id(self):
        peer_id = _calculate_peer_id()

        self.assertTrue(len(peer_id) == 20)


class TrackerResponseTest(unittest.TestCase):
    def setUp(self):
        self.ok_response = OrderedDict([
            (b'complete', 5500),
            (b'incomplete', 240),
            (b'interval', 1800),
            (b'peers', b"V\x04\x18s\xc8\xdb\xb0\x1fc\xb2\xc7\x98V=G\x95\xa4\x1dP\x1e\xbf\xb0\xc8\xd5%\xbb\x01=\\\x1e\xb2\xdaf\x1b\x1a\xe1Oq\xee+\xc8\xd5S\xe3\x89M\xcc\xc7U\x0fXe\xc8\xd5\xbc\xe8\xd5\xde\xc8\xd5\xb9\x15\xd9J\xfa\x00\x05'Y\x1f\x1e\xc9\xc0\x00\xab*\x1a\xe1\xbcI\xa0P\x84\x99P\xdb\xe3\xd5\xcd-P\xb1\xa5\x93\x1a\xe1\xc0\x83,\t\xe7\x86I\n\xdae\xc8\xd5\xcc\xbbd\x13\x9c\xbf.)F\x17\x1a\xe1k\xbc\xea\xed\xbe\xa0\xb0O\x9b\xf3Z$P\xea,Q\xee;\xc0\x83,\\\xe5\x07e\xb8\x80\r\xed2\xb7\x0e\xa2N\xc8\xd5\x1f\x19\x1f\xda\xc8\xd5\x05'T\r\xc8\xd5[\xc4\xc2%\xc8\xd5^\x17%F\xc8\xd5^\x17\xdd\xd5\xaf\xd5\x83\xf7\x13t\xdcV\xc3.\xbbA\xc8\xd5\x051N\xd9\xc8\xd5OxV\x80\x1a\xecO\xf3\x97\xf9\x1a\xe1\xa3\xac\x84\xe6(\xcc\xd9\xe0L2\xffE\xd9X[\xc2\x1a\xe1\x02\x1d\x160\xc8\xd5PG\x81t\xe3\xc1\xce\xe1R\xa1\xb3\x9f\xc5\x94a\xa2\xc8\xd5H\xb9\xe3}\xe7\xd3\xc2\xe2\x9bK\xde\xa7_\xb6/\xe6\xd1*Pc1k\x1a\xeaG\xcf.(\xc8\xd5\xc3\x9a\xf0\x03\xb4\x06^\xf5.\x9dL\x18")])  # noqa

    def test_failed_response(self):
        response = TrackerResponse(OrderedDict([(b'failure reason',
                                                 b'You failed!')]))

        self.assertEqual('You failed!', response.failure)

    def test_successful_response_no_failure(self):
        response = TrackerResponse(self.ok_response)

        self.assertIsNone(response.failure)

    def test_successful_response_complete(self):
        response = TrackerResponse(self.ok_response)

        self.assertEqual(5500, response.complete)

    def test_successful_response_incomplete(self):
        response = TrackerResponse(self.ok_response)

        self.assertEqual(240, response.incomplete)

    def test_successful_response_interval(self):
        response = TrackerResponse(self.ok_response)

        self.assertEqual(1800, response.interval)

    def test_successful_response_peer_string(self):
        response = TrackerResponse(self.ok_response)

        self.assertEqual(50, len(response.peers))
