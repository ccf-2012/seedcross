import base64
from datetime import datetime
import glob, os
import qbittorrentapi
import transmission_rpc
import deluge_client
import logging
import pytz
import urllib.parse
from abc import abstractmethod, ABCMeta

logger = logging.getLogger(__name__)


def getDownloadClient(scsetting, log=None):
    if scsetting.clienttype == 'qb':
        scobj = QbDownloadClient(scsetting, log)
    elif scsetting.clienttype == 'tr':
        scobj = TrDownloadClient(scsetting, log)
    elif scsetting.clienttype == 'de':
        scobj = DeDownloadClient(scsetting, log)
    return scobj


class DownloadClientBase(metaclass=ABCMeta):
    def __init__(self, scsetting):
        self.scsetting = scsetting

    @abstractmethod
    def connect(self):
        pass


class TrDownloadClient(DownloadClientBase):
    def __init__(self, scsetting, log=None):
        self.scsetting = scsetting
        self.trClient = None
        self.log = log

    def connect(self):
        self.trClient = None
        try:
            self.trClient = transmission_rpc.Client(
                host=self.scsetting.host,
                port=self.scsetting.port,
                username=self.scsetting.username,
                password=self.scsetting.password)
        except transmission_rpc.error.TransmissionError as e:
            if self.log:
                self.log.message("TransmissionError: check settings")
            print(e)
            return None

        return self.trClient

    def mkSeedTor(self, trTor):
        if not trTor:
            return None
        st = SeedingTorrent(
            torrent_hash=trTor.hashString,
            name=trTor.name,
            size=trTor.total_size,
            tracker=self.abbrevTracker(trTor.trackers[0]),
            added_date=trTor.date_added,
            status=trTor.status,
            save_path=trTor.download_dir,
        )
        return st

    def abbrevTracker(self, trackerJson):
        hostnameList = urllib.parse.urlparse(
            trackerJson["announce"]).netloc.split('.')
        if len(hostnameList) == 2:
            abbrev = hostnameList[0]
        elif len(hostnameList) == 3:
            abbrev = hostnameList[1]
        else:
            abbrev = ''
        return abbrev

    def loadTorrents(self):
        self.trClient = self.connect()
        if not self.trClient:
            return []
        torList = self.trClient.get_torrents(arguments=[
            'id', 'name', 'hashString', 'downloadDir', 'totalSize', 'trackers',
            'addedDate', 'status'
        ])
        activeList = []
        for trTor in torList:
            st = self.mkSeedTor(trTor)
            activeList.append(st)
        return activeList

    def addTorrentUrl(self, tor_url, download_location):
        if not self.trClient:
            self.connect()
        newtor = None
        if self.trClient:
            try:
                newtor = self.trClient.add_torrent(
                    tor_url, paused=True, download_dir=download_location)
            except Exception as e:
                if self.log:
                    self.log.message('Torrent not added')
                logger.debug('Torrent not added')
                return None

        return self.getTorrent(newtor.hashString)

    def getTorrent(self, tor_hash):
        try:
            logger.info('Double checking that the torrent was added.')
            trTor = self.trClient.get_torrent(tor_hash,
                                              arguments=[
                                                  'id', 'name', 'hashString',
                                                  'downloadDir', 'totalSize',
                                                  'trackers', 'addedDate',
                                                  'status'
                                              ])

        except Exception as e:
            s = 'Torrent was not added! maybe exists.'
            logger.warn(s)
            if self.log:
                self.log.message(s)
            return None
        else:
            if trTor:
                s = 'Torrent successfully added!'
                logger.info(s)
                if self.log:
                    self.log.message(s)
                st = self.mkSeedTor(trTor)
                return st
            else:
                return None


class QbDownloadClient(DownloadClientBase):
    def __init__(self, scsetting, log=None):
        self.scsetting = scsetting
        self.qbClient = None
        self.log = log

    def connect(self):
        self.qbClient = qbittorrentapi.Client(
            host=self.scsetting.host,
            port=self.scsetting.port,
            username=self.scsetting.username,
            password=self.scsetting.password,
            #   VERIFY_WEBUI_CERTIFICATE = False,
        )
        try:
            self.qbClient.auth_log_in()
        except Exception as ex:
            s = 'There was an error during auth_log_in: ' + str(ex)
            if self.log:
                self.log.message(s)
            logger.error(s)
            return None

        return self.qbClient

    def abbrevTracker(self, trackerstr):
        if len(trackerstr) < 2:
            return ''
        hostnameList = urllib.parse.urlparse(trackerstr).netloc.split('.')
        if len(hostnameList) == 2:
            abbrev = hostnameList[0]
        elif len(hostnameList) == 3:
            abbrev = hostnameList[1]
        else:
            abbrev = ''
        return abbrev

    def mkSeedTor(self, tor):
        st = SeedingTorrent(
            torrent_hash=tor.hash,
            name=tor.name,
            size=tor.size,
            tracker=self.abbrevTracker(tor.tracker),
            added_date=datetime.utcfromtimestamp(
                tor.added_on).replace(tzinfo=pytz.utc),
            status=tor.state,
            save_path=tor.save_path,
        )
        return st

    def loadTorrents(self):
        if not self.qbClient:
            self.connect()
        if not self.qbClient:
            return []

        torList = self.qbClient.torrents_info()
        activeList = []
        for qbTor in torList:
            st = self.mkSeedTor(qbTor)
            activeList.append(st)
        return activeList

    def findJustAdded(self):
        torList = self.qbClient.torrents_info(status_filter='paused',
                                              sort='added_on')
        if torList:
            return torList[-1]
        else:
            return None

    def addTorrentUrl(self, tor_url, download_location, indexer):
        if not self.qbClient:
            self.connect()
        st = None
        if self.qbClient:
            try:
                result = self.qbClient.torrents_add(
                    urls=tor_url,
                    is_paused=True,
                    skip_checking=True,
                    tags="seedcross," + indexer,
                    autoTMM=False,
                    save_path=download_location )
                if 'OK' in result.upper():
                    qbTor = self.findJustAdded()
                    if qbTor:
                        st = self.mkSeedTor(qbTor)
            except Exception as e:
                self.log('Torrent not added! Torrent already in session.')
                return None

        return st

    def getTorrent(self, tor_hash):
        try:
            logger.info('Double checking that the torrent was added.')
            qbTor = self.qbClient.torrents_info(torrent_hashes=tor_hash)
        except Exception as e:
            logger.warn('Torrent was not added! maybe exists.')
            return None
        else:
            if qbTor:
                logger.info('Torrent successfully added!')
                st = self.mkSeedTor(qbTor)
                return st
            else:
                return None


class DeDownloadClient(DownloadClientBase):
    def __init__(self, scsetting, log=None):
        self.scsetting = scsetting
        self.deClient = None
        self.log = log

    def connect(self):
        if self.scsetting is None:
            return None

        s = 'Connecting to ' + self.scsetting.host + ':' + str(self.scsetting.port)
        logger.info(s)
        if self.log:
            self.log.message(s)
        try:
            self.deClient = deluge_client.DelugeRPCClient(
                self.scsetting.host, int(self.scsetting.port),
                self.scsetting.username, self.scsetting.password)
        except Exception as e:
            s = 'Could not create DelugeRPCClient Object' + str(e)
            logger.error(s)
            if self.log:
                self.log.message(s)
            return None
        else:
            try:
                self.deClient.connect()
            except Exception as e:
                s = 'Could not connect to Deluge ' + self.scsetting.host
                logger.error(s)
                if self.log:
                    self.log.message(s)
            else:
                return self.deClient

    def mkSeedTor(self, deTor):
        st = SeedingTorrent(
            torrent_hash=deTor[b'hash'].decode("utf-8"),
            name=deTor[b'name'].decode("utf-8"),
            size=deTor[b'total_size'],
            tracker=self.abbrevTracker(deTor[b'tracker_host'].decode("utf-8")),
            added_date=datetime.utcfromtimestamp(
                deTor[b'time_added']).replace(tzinfo=pytz.utc),
            status=deTor[b'state'].decode("utf-8"),
            save_path=deTor[b'download_location'].decode("utf-8"),
        )
        return st

    def getTorrent(self, tor_hash):
        try:
            s = 'Double checking that the torrent was added.'
            logger.info(s)
            if self.log:
                self.log.message(s)

            # deTor1 = self.get_torrent(tor_hash)
            deTor = self.deClient.call('core.get_torrent_status', tor_hash, [
                'name', 'hash', 'download_location', 'total_size',
                'tracker_host', 'time_added', 'state'
            ])

        except Exception as e:
            s = 'Torrent was not added! maybe exists.'
            logger.warn(s)
            if self.log:
                self.log.message(s)

            return None
        else:
            if deTor:
                s = 'Torrent successfully added!'
                logger.info(s)
                if self.log:
                    self.log.message(s)
                st = self.mkSeedTor(deTor)
                return st
            else:
                return None

    def addTorrentUrl(self, tor_url, download_location):
        if not self.deClient:
            self.connect()
        torhash = None
        if self.deClient:
            t_options = {}
            t_options['add_paused'] = True
            t_options['download_location'] = download_location
            try:
                torid = self.deClient.call('core.add_torrent_url', tor_url,
                                           t_options)
                torhash = torid.decode("utf-8")

            except Exception as e:
                s = 'Torrent not added'
                logger.debug(s)
                if self.log:
                    self.log.message(s)
                return None

        return self.getTorrent(torhash)

    def add_torrent_file(self, filepath, download_location):
        if not self.deClient:
            self.connect()
        torrent_id = False

        if self.deClient:
            # logger.info('Checking if Torrent Exists!')

            torrentcontent = open(filepath, 'rb').read()
            # Deluge expects a lower case hash
            #            hash = str.lower(self.get_the_hash(filepath))

            #            logger.debug('Torrent Hash (load_torrent): "' + hash + '"')
            s = 'FileName (load_torrent): ' + str(os.path.basename(filepath))
            logger.debug(s)
            if self.log:
                self.log.message(s)

            t_options = {}
            t_options['add_paused'] = True
            t_options['download_location'] = download_location

            try:
                torrent_id = self.deClient.call(
                    'core.add_torrent_file', str(os.path.basename(filepath)),
                    base64.encodestring(torrentcontent), t_options)
            except Exception as e:
                s = 'Torrent not added'
                logger.debug(s)
                if self.log:
                    self.log.message(s)
                return None

        return self.getTorrent(torrent_id)

    def find_torrent(self, hash):
        logger.debug('Finding Torrent hash: ' + hash)
        torrent_info = self.getTorrent(hash)
        if torrent_info:
            return True
        else:
            return False

    def abbrevTracker(self, trackerHost):
        if len(trackerHost) < 2:
            return ''
        hostnameList = trackerHost.split('.')
        if len(hostnameList) == 2:
            abbrev = hostnameList[0]
        elif len(hostnameList) == 3:
            abbrev = hostnameList[1]
        else:
            abbrev = ''
        return abbrev

    def loadTorrents(self):
        if not self.deClient:
            self.connect()
        if not self.deClient:
            return []
        torList = self.deClient.call(
            'core.get_torrents_status', {"state": "Seeding"}, [
                'name', 'hash', 'download_location', 'total_size',
                'tracker_host', 'time_added', 'state'
            ])
        activeList = []
        for deTor in torList.values():
            st = self.mkSeedTor(deTor)
            activeList.append(st)
        return activeList


class SeedingTorrent(object):
    def __init__(self, torrent_hash, name, size, tracker, added_date, status,
                 save_path):
        self.torrent_hash = torrent_hash
        self.name = name
        self.size = size
        self.tracker = tracker
        self.added_date = added_date
        self.status = status
        self.save_path = save_path