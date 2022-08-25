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

from hashlib import sha1
from collections import namedtuple
import os

from . import bencoding

# Represents the files within the torrent (i.e. the files to write to disk)
TorrentFile = namedtuple('TorrentFile', ['path', 'length'])


class Torrent:
    """
    Represent the torrent meta-data that is kept within a .torrent file. It is
    basically just a wrapper around the bencoded data with utility functions.

    This class does not contain any session state as part of the download.
    """
    def __init__(self, filename):
        self.filename = filename
        self.files = []

        with open(self.filename, 'rb') as f:
            meta_info = f.read()
            self.meta_info = bencoding.Decoder(meta_info).decode()
            info = bencoding.Encoder(self.meta_info[b'info']).encode()
            self.info_hash = sha1(info).digest()
            self._identify_files()

    def _identify_files(self):
        """
        Identifies the files included in this torrent
        """
        if self.multi_file:
            name = self.meta_info[b'info'][b'name'].decode('utf-8')
            if not os.path.exists(name):
                os.mkdir(name); 
            for file in self.meta_info[b'info'][b'files']:
                curr_path = (b'/'.join(file[b'path'])).decode('utf-8')
                curr_path = os.path.join(self.meta_info[b'info'][b'name'].decode('utf-8'), curr_path)
                self.files.append(TorrentFile(curr_path, file[b'length'])) 
        else:
            self.files.append(
                TorrentFile(
                    self.meta_info[b'info'][b'name'].decode('utf-8'),
                    self.meta_info[b'info'][b'length']))

    @property
    def announce(self) -> str:
        """
        The announce URL to the tracker.
        """
        return self.meta_info[b'announce'].decode('utf-8')
    
    @property
    def announce_list(self) -> list:
        """ 
        Returns announce list of trackers. 
        """
        if b'announce-list' in self.meta_info.keys():
            return [[a.decode('utf-8') for a in x] for x in self.meta_info[b'announce-list']]
        else:
            return None

    @property
    def multi_file(self) -> bool:
        """
        Does this torrent contain multiple files?
        """
        # If the info dict contains a files element then it is a multi-file
        return b'files' in self.meta_info[b'info']

    @property
    def piece_length(self) -> int:
        """
        Get the length in bytes for each piece
        """
        return self.meta_info[b'info'][b'piece length']

    @property
    def total_size(self) -> int:
        """
        The total size (in bytes) for all the files in this torrent. For a
        single file torrent this is the only file, for a multi-file torrent
        this is the sum of all files.

        :return: The total size (in bytes) for this torrent's data.
        """
        if self.multi_file:
            return sum(file.length for file in self.files) 
        else:
            return self.files[0].length

    @property
    def pieces(self):
        # The info pieces is a string representing all pieces SHA1 hashes
        # (each 20 bytes long). Read that data and slice it up into the
        # actual pieces
        data = self.meta_info[b'info'][b'pieces']
        pieces = []
        offset = 0
        length = len(data)

        while offset < length:
            pieces.append(data[offset:offset + 20])
            offset += 20
        return pieces

    @property
    def output_file(self):
        if self.multi_file:
            if not os.path.exists('.pieces_tmp'):
                os.mkdir('.pieces_tmp')
            return os.path.join('.pieces_tmp', 'tmp')
        else:
            return self.meta_info[b'info'][b'name'].decode('utf-8')

    def __str__(self):
        return 'Filename: {0}\n' \
               'File length: {1}\n' \
               'Announce URL: {2}\n' \
               'Hash: {3}'.format(self.meta_info[b'info'][b'name'],
                                  self.meta_info[b'info'][b'length'],
                                  self.meta_info[b'announce'],
                                  self.info_hash)
