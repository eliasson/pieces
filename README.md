# pieces

An experimental BitTorrent client implemented in Python 3 using asyncio.

The client is not a practical BitTorrent client, it lacks too many
features to really be useful. It was implemented for fun in order to
learn more about BitTorrent as well as Python's asyncio library.

See http://markuseliasson.se/article/bittorrent-in-python/ for a walkthrough
on the BitTorrent protocol and how pieces works under the hood.

The client currently only support downloading of data, although adding
the remaining features regarding seeding and multi-file should not be
that hard.

Current features:

- [x] Download pieces (leeching)
- [x] Contact tracker periodically
- [ ] Seed (upload) pieces
- [ ] Support multi-file torrents
- [ ] Resume a download

Even though it's not practical at this point, feel free to learn from
it, steal from it, improve it, laugh at it or just ignore it.

Known issues:

* Sometimes the client hangs at startup. It seems to relate to the
  number of concurrent peer connections.


## Getting started

Install the needed dependencies and run the unit tests with:

    $ make init
    $ make test

In order to download a torrent file, run this command:

    $ python pieces.py -v tests/data/bootfloppy-utils.img.torrent

If everything goes well, your torrent should be downloaded and the
program terminated. You can stop the client using `Ctrl + C`.


## Design considerations

The purpose with implementing this client was to learn myself some
`asyncio` (and other Python 3.5 features, such as _type hinting_)
together with my old itch of implementing the BitTorrent protocol.

Thus, the code have been written to be as clear and simple as possible,
not bothering about efficiency or performance. E.g. the pieces are all
requested in order, not implementing a _rares first_ algorithm, and the
pieces are all kept in memory until the entire torrent is downloaded.


### Code walkthrough

The `pieces.client.TorrentClient` is the center piece, it:

* Connects to the tracker in order to receive the peers to connect to.

* Based on that result, creates a Queue of peers that can be connected
  to.

* Determine the order in which the pieces should be requested from the
  remote peers.

* Shuts down the client once the download is complete.


The strategy on which piece to request next and the assembly of
retrieved pieces is implemented in the `pieces.client.PieceManager`. As
previously stated, the strategy implemented is the simplest one
possible.

Notice, the file writing is synchronous something that could be
improved.

The BitTorrent specifics is implemented in the `pieces.protocol` module
where the `pieces.protocol.PeerConnection` sets up a connection to one
of the remote peers retrieved from the tracker. This class handles the
control flow of messages between the two peers.

BitTorrent is a binary protocol, and all decoding of messages is
implemented as a _async iterator_ under he name
`pieces.protocol.PeerStreamIterator`. The async part is that this
iterator will keep reading and parsing the raw data received from the
socket until the connection is closed.

Each of BitTorrents messages is implemented as separate classes, each
with a `encode` and a `decode` method. However, since this client
currently does not support seeding - not all of the messages goes in
both ways.


## References

There is plenty of information on how to write a BitTorrent client
available on the Internet. These two articles were the real enablers
for my implementation:

* http://www.kristenwidman.com/blog/33/how-to-write-a-bittorrent-client-part-1/

* https://wiki.theory.org/BitTorrentSpecification

Asyncio is fairly new and I have not seen that many articles about it,
at least not where the code examples are a little bit more elaborate
than having a few coroutines sleep. Out of the ones I read and can
recommend these are on the top of my list:

* http://www.snarky.ca/how-the-heck-does-async-await-work-in-python-3-5

* http://www.pythonsandbarracudas.com/blog/2015/11/22/developing-a-computational-pipeline-using-the-asyncio-module-in-python-3

* http://dabeaz.com/coroutines/Coroutines.pdf


# License

The client is released under the Apache v2 license, see LICENCE.
