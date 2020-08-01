import logging
from urllib.parse import urlencode

import aiohttp

from pieces.bencoding import Decoder
from pieces.torrent import Torrent
from pieces.trackers.base import BaseTracker, _calculate_peer_id, TrackerResponse


class HTTPTracker(BaseTracker):
    """
    Represents the connection to a tracker for a given Torrent that is either
    under download or seeding state.
    """

    def __init__(self, torrent: Torrent):
        self.torrent = torrent
        self.peer_id = _calculate_peer_id()
        self.http_client = aiohttp.ClientSession()

    async def connect(self, first: bool = None, uploaded: int = 0, downloaded: int = 0) -> TrackerResponse:
        """
        Makes the announce call to the tracker to update with our statistics
        as well as get a list of available peers to connect to.

        If the call was successful, the list of peers will be updated as a
        result of calling this function.

        :param first: Whether or not this is the first announce call
        :param uploaded: The total number of bytes uploaded
        :param downloaded: The total number of bytes downloaded
        """
        params = {
            'info_hash': self.torrent.info_hash,
            'peer_id': self.peer_id,
            'port': 6889,
            'uploaded': uploaded,
            'downloaded': downloaded,
            'left': self.torrent.total_size - downloaded,
            'compact': 1}
        if first:
            params['event'] = 'started'

        url = self.torrent.announce + '?' + urlencode(params)
        logging.info('Connecting to tracker at: ' + url)

        async with self.http_client.get(url) as response:
            if not response.status == 200:
                raise ConnectionError('Unable to connect to tracker: status code {}'.format(response.status))
            data = await response.read()
            # TODO: Process tracker errors when response status is 200 OK.
            return TrackerResponse(Decoder(data).decode())

    def close(self):
        self.http_client.close()

    def _construct_tracker_parameters(self):
        """
        Constructs the URL parameters used when issuing the announce call
        to the tracker.
        """
        return {
            'info_hash': self.torrent.info_hash,
            'peer_id': self.peer_id,
            'port': 6889,
            # TODO Update stats when communicating with tracker
            'uploaded': 0,
            'downloaded': 0,
            'left': 0,
            'compact': 1
        }
