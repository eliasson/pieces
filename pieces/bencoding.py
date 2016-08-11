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

from collections import OrderedDict


# Indicates start of integers
TOKEN_INTEGER = b'i'

# Indicates start of list
TOKEN_LIST = b'l'

# Indicates start of dict
TOKEN_DICT = b'd'

# Indicate end of lists, dicts and integer values
TOKEN_END = b'e'

# Delimits string length from string data
TOKEN_STRING_SEPARATOR = b':'


class Decoder:
    """
    Decodes a bencoded sequence of bytes.
    """
    def __init__(self, data: bytes):
        if not isinstance(data, bytes):
            raise TypeError('Argument "data" must be of type bytes')
        self._data = data
        self._index = 0

    def decode(self):
        """
        Decodes the bencoded data and return the matching python object.

        :return A python object representing the bencoded data
        """
        c = self._peek()
        if c is None:
            raise EOFError('Unexpected end-of-file')
        elif c == TOKEN_INTEGER:
            self._consume()  # The token
            return self._decode_int()
        elif c == TOKEN_LIST:
            self._consume()  # The token
            return self._decode_list()
        elif c == TOKEN_DICT:
            self._consume()  # The token
            return self._decode_dict()
        elif c == TOKEN_END:
            return None
        elif c in b'01234567899':
            return self._decode_string()
        else:
            raise RuntimeError('Invalid token read at {0}'.format(
                str(self._index)))

    def _peek(self):
        """
        Return the next character from the bencoded data or None
        """
        if self._index + 1 >= len(self._data):
            return None
        return self._data[self._index:self._index + 1]

    def _consume(self) -> bytes:
        """
        Read (and therefore consume) the next character from the data
        """
        self._index += 1

    def _read(self, length: int) -> bytes:
        """
        Read the `length` number of bytes from data and return the result
        """
        if self._index + length > len(self._data):
            raise IndexError('Cannot read {0} bytes from current position {1}'
                             .format(str(length), str(self._index)))
        res = self._data[self._index:self._index+length]
        self._index += length
        return res

    def _read_until(self, token: bytes) -> bytes:
        """
        Read from the bencoded data until the given token is found and return
        the characters read.
        """
        try:
            occurrence = self._data.index(token, self._index)
            result = self._data[self._index:occurrence]
            self._index = occurrence + 1
            return result
        except ValueError:
            raise RuntimeError('Unable to find token {0}'.format(
                str(token)))

    def _decode_int(self):
        return int(self._read_until(TOKEN_END))

    def _decode_list(self):
        res = []
        # Recursive decode the content of the list
        while self._data[self._index: self._index + 1] != TOKEN_END:
            res.append(self.decode())
        self._consume()  # The END token
        return res

    def _decode_dict(self):
        res = OrderedDict()
        while self._data[self._index: self._index + 1] != TOKEN_END:
            key = self.decode()
            obj = self.decode()
            res[key] = obj
        self._consume()  # The END token
        return res

    def _decode_string(self):
        bytes_to_read = int(self._read_until(TOKEN_STRING_SEPARATOR))
        data = self._read(bytes_to_read)
        return data


class Encoder:
    """
    Encodes a python object to a bencoded sequence of bytes.

    Supported python types is:
        - str
        - int
        - list
        - dict
        - bytes

    Any other type will simply be ignored.
    """
    def __init__(self, data):
        self._data = data

    def encode(self) -> bytes:
        """
        Encode a python object to a bencoded binary string

        :return The bencoded binary data
        """
        return self.encode_next(self._data)

    def encode_next(self, data):
        if type(data) == str:
            return self._encode_string(data)
        elif type(data) == int:
            return self._encode_int(data)
        elif type(data) == list:
            return self._encode_list(data)
        elif type(data) == dict or type(data) == OrderedDict:
            return self._encode_dict(data)
        elif type(data) == bytes:
            return self._encode_bytes(data)
        else:
            return None

    def _encode_int(self, value):
        return str.encode('i' + str(value) + 'e')

    def _encode_string(self, value: str):
        res = str(len(value)) + ':' + value
        return str.encode(res)

    def _encode_bytes(self, value: str):
        result = bytearray()
        result += str.encode(str(len(value)))
        result += b':'
        result += value
        return result

    def _encode_list(self, data):
        result = bytearray('l', 'utf-8')
        result += b''.join([self.encode_next(item) for item in data])
        result += b'e'
        return result

    def _encode_dict(self, data: dict) -> bytes:
        result = bytearray('d', 'utf-8')
        for k, v in data.items():
            key = self.encode_next(k)
            value = self.encode_next(v)
            if key and value:
                result += key
                result += value
            else:
                raise RuntimeError('Bad dict')
        result += b'e'
        return result
