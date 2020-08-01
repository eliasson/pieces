import logging
import random
import socket
from abc import ABC
from struct import unpack
from typing import Optional, List, Tuple, Union


def _calculate_peer_id() -> str:
    """
    Calculate and return a unique Peer ID.

    The `peer id` is a 20 byte long identifier. This implementation use the
    Azureus style `-PC1000-<random-characters>`.

    Read more:
        https://wiki.theory.org/BitTorrentSpecification#peer_id
    """
    return '-PC0001-' + ''.join(
        [str(random.randint(0, 9)) for _ in range(12)])


def _decode_port(port) -> int:
    """
    Converts a 32-bit packed binary port number to int
    """
    # Convert from C style big-endian encoded as unsigned short
    return unpack(">H", port)[0]


class TrackerResponse:
    """
    The response from the tracker after a successful connection to the
    trackers announce URL.

    Even though the connection was successful from a network point of view,
    the tracker might have returned an error (stated in the `failure` property).
    """

    def __init__(self, response: dict):
        self.response = response

    @property
    def failure(self) -> Optional[str]:
        """
        If this response was a failed response, this is the error message to
        why the tracker request failed.

        If no error occurred this will be None
        """
        if b'failure reason' in self.response:
            return self.response[b'failure reason'].decode('utf-8')
        return None

    @property
    def interval(self) -> int:
        """
        Interval in seconds that the client should wait between sending
        periodic requests to the tracker.
        """
        return self.response.get(b'interval', 0)

    @property
    def complete(self) -> int:
        """
        Number of peers with the entire file, i.e. seeders.
        """
        return self.response.get(b'complete', 0)

    @property
    def incomplete(self) -> int:
        """
        Number of non-seeder peers, aka "leechers".
        """
        return self.response.get(b'incomplete', 0)

    @property
    def peers(self) -> List[Tuple[str, int]]:
        """
        A list of tuples for each peer structured as (ip, port)
        """
        # The BitTorrent specification specifies two types of responses. One
        # where the peers field is a list of dictionaries and one where all
        # the peers are encoded in a single string
        peers: Union[bytes, list] = self.response[b'peers']
        if type(peers) == list:
            return self._parse_dict_peers(peers)
        else:
            return self._parse_string_peers(peers)

    @staticmethod
    def _parse_string_peers(peers_str: bytes) -> List[Tuple[str, int]]:
        logging.debug('Binary model peers are returned by tracker')

        # Split the string in pieces of length 6 bytes, where the first
        # 4 characters is the IP the last 2 is the TCP port.
        peers = [peers_str[i:i + 6] for i in range(0, len(peers_str), 6)]

        # Convert the encoded address to a list of tuples
        return [(socket.inet_ntoa(p[:4]), _decode_port(p[4:])) for p in peers]

    @staticmethod
    def _parse_dict_peers(peers_dicts: list) -> List[Tuple[str, int]]:
        # TODO: Implement dict model peers
        logging.debug('Dict model peers are returned by tracker')
        raise NotImplementedError

    def __str__(self):
        return "incomplete: {incomplete}\n" \
               "complete: {complete}\n" \
               "interval: {interval}\n" \
               "peers: {peers}\n".format(
                   incomplete=self.incomplete,
                   complete=self.complete,
                   interval=self.interval,
                   peers=", ".join([x for (x, _) in self.peers]))


class BaseTracker(ABC):
    async def connect(self, first: bool = None, uploaded: int = 0, downloaded: int = 0) -> TrackerResponse:
        pass

    def close(self):
        pass
