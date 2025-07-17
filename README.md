# SeedCross
* A Web app to Cross-Seed torrents in Deluge/qBittorrent/Transmission
* based on [CrossSeedAutoDL](https://github.com/BC44/Cross-Seed-AutoDL)

## Last update
* 2025.7.17 update to latest Django
* 2023.8.30: setting, max size difference (bytes) when compare torrents
* 2022.5.5:  `Fix` path of crossed torrent to match local path, required your download client is running on the same machine as seedcross. you may set a path map for dockers.
* 2022.4.29: dev merge to main
* 2022.3.29: deluge client, download_location => save_path
* 2022.3.6: mount db dir (/code/seedcross/db) externally


![screenshot](screenshot/seedcross1.png)

## Require
* [Jackett](https://github.com/Jackett/Jackett) / [Prowlarr](https://github.com/Prowlarr/Prowlarr)
* Deluge/qBittorrent/Transmission
* Docker (optional)
  

## Install with source
* create a virtualenv
```sh
# install virtualenv with root
sudo pip install virtualenv

# create a virutalenv
virtualenv  seed
source seed/bin/activate

```

* clone the source
```sh
git clone https://github.com/ccf-2012/seedcross.git
```

* Install the requirements
```sh
# install requirements
pip install -r requirements.txt
```

* build the db
```sh
cd seedcross

mkdir db
python manage.py migrate

# create a admin user
python manage.py createsuperuser
```

* (optional) set db to wal mode, to reduce sqlite3's 'table is locked'.
```sh
cd db
sqlite3 db.sqlite3 'PRAGMA journal_mode=wal;'
cd ..
```

* run the server
```sh
# better with a screen or tmux
screen 
# under seedcross folder 
chmod +x start.sh
./start.sh
```


## Installation with docker
install with docker run command, replace `/somedir/in/host` with some dir in your host:
```sh
docker run -d --name seedcross -v /somedir/in/host:/code/seedcross/db -p 8019:8019 ccf2012/seedcross:latest
```


or with a docker-compose.yml, replace `/somedir/in/host` with some dir in your host

```yml
version: "3"
services:
  seedcross:
    container_name: seedcross
    image: ccf2012/seedcross
    volumes:
      - /somedir/in/host:/code/seedcross/db
    ports:
      - 8019:8019
    restart: unless-stopped
```


## Login
Open `http://<your-ip>:8019` in browser
Login with `admin`:`admin`

## Settings
Start from `Settings` tab, fill the fields carefully:

### Download Client Setting: 
Enter the `Type`, `Host`, `Port`, `Username`, `Password`, note the `Host` must be an IP address, not url.

### Jackett/Prowlarr Setting: 
You should have a configured Jackett/Prowlarr server with indexers in place, the `Jackett/Prowlarr Url` formatted as `http://IP:PORT` and `Jackett/Prowlarr Api key`, 

`Trackers / Indexers:` Leave blank if you would seach all the trackers

If you want to search specific trackers:
 - Jackett you should find the exact word between `indexers/` and `/results` in the `torznab feed URL`
 - Prowlarr uses an integer number known as ID within Prowlarr, you can find these from the indexer info. Click on the Indexer in the list and its ID will be shown under the `Indexer Details`
 - These are then entered in a comma separated format e.g `11, 32, 59`

### Search options

`Max size difference (bytes) when compare torrents.` Some trackers will include an additional text file within a release meaning the size of the torrent is slightly different however, the main file contents are the same, this setting will allow for those torrents to be grabbed. You can adjust this setting if required.

`Search CJK title` - This will include CJK symbols within the search https://en.wikipedia.org/wiki/CJK_Symbols_and_Punctuation

`Category indexers` (Categorise Indexers) - If enabled you can use the values entered in the Trackers / Indexers: section and assign them to specific categories, this is useful when you don't want to search for TV shows on a Music Tracker. 

### Flow Control Setting: 
`Flow control: Count limit:` This option defines how many torrents to search for each cycle, keep in mind that this will search all your defined indexers/trackers so limit this setting to avoid overloading them, SeedCross will manage the search history and find the next un-searched torrent when you start cross next time.

`Flow control: Interval:` This defines the number of seconds to wait between each search query

### Cycle run options

`Cycle run interval (minutes)` Enabling this option defines how many minutes to wait between each run, meaning SeedCross can be left to automatically perform it's duties without intervention. 

### Fix options

If your download client is running on a different machine to seedcross you can use this option to 'map' the correct paths for SeedCross to use.

After you fill the form, press `Save Settings`, if no error detected, it will redirect to the `Start Cross` page, otherwise there will be error message next to the field.

## Start Crossing
1. press `Start Cross` button, seedcross will start to:
    1. load the torrents from the download client.
    2. parse the name to get the title,year,episode etc, with these keyword ask Jackett server to search torrents in your pre-configured trackers.
    3. check if there's match by title and size.
    4. add the download link to the download client, in `paused` state, you will need to 'force recheck' in qBittorrent to scan the files and start seeding.
    5. and Yes, if the configuration haven't been set, it will redirect to the `Settings` page. 

2.  during the process, a progress panel will show up, with:
  * Total/Searched torrents in the download client
  * Flow-Limit/Searched of this session
  * Downloaded torrent in this session 
  * a log message box showing the info/error messages of the process
    * note: the log message is for monitoring the process, it will lost when page refresh.

3. the process will stop when:
  * configuration error: download client / jackett,
  * reach the Flow limit count,
  * all torrents in the client has been searched,
  * user click the Canel button.
  * the progress panel will disappear when page refreshed.


## Notes on the match

This cross seeding tool works as follows.

1. Get the list of torrents from the downloader, extract the movie name from the torrent title, use Jackett/Prowlarr to search for torrents with the same movie name at each site, (you can't search directly using the file name, you need to strip extra strings and search only for the movie name), and match the information returned by Jackett/Prowlarr by comparing the size.
2. The torrent download link sent to the downloader, which downloads it via Jackett/Prowlarr
3. The actual title and file name of the torrent are not known until the .torrent file are downloaded, so if we want to compare whether the torrent is exactly match, the torrents are already on the downloader (in pause state). currently the croos-seed keep the torrents and only mark whether they match on the ui, and let the user check whether it can be rescued.

* so it will download and keep some torrent that's not same.


## Notes on the fix

There are sometimes torrents with same content but not in same name, these torrents maybe rescued. In the recent update, I have add a 'Fix' button, to get some of them fixed (with symbolink):
1. both are files, or both folder, but with different name, e.g. :
```
Olympus.S01.1080p.GBR.Blu-ray.AVC.DTS-HD.MA.5.1-PzD
Olympus S01 1080p GBR Blu-ray AVC DTS-HD MA 5.1-PzD

Prometheus.2012.COMPLETE.UHD.BLURAY-TERMiNAL
Prometheus.2012.2160p.BluRay.HEVC.DTS-HD.MA.7.1-TERMiNAL

JET PILOT
Jet Pilot 1957 2in1 1080p Blu-ray AVC DTS-HD MA 2.0-MM
```

2. one is file, and the other is folder, e.g. :
```
Lost.Highway.1997.1080p.BluRay.DD+5.1.x264-LoRD/
Lost.Highway.1997.1080p.BluRay.DD+5.1.x264-LoRD.mkv
```

*  and, stil, if the files in subfolder isn't same, it won't detects and the rescue will still failed.


## Search History
* Torrents that has been searched will be recorded, they won't bother the trackers for the next process.
* but when you add new trackers you may want to redo the search, click the `Clear Search History` will delete all the records.

## Plans
* Scheduler to run the task periodically (A simple cyclic run is implemented, expect feedback)
* Seperate tracker to search different media  (done, expect feedback)
* Hardlink tweaks of file/folder to get more crossed. (check [tortweak](https://github.com/ccf-2012/tortweak))
* Open to you Dai-lo's suggestions.


## Acknowledgement
1. Aruba@hutongyouwu 
2. [CrossSeedAutoDL](https://github.com/BC44/Cross-Seed-AutoDL)


## Files to build docker

* the dir tree
```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── seedcross\
```

* Dockerfile
```
# syntax=docker/dockerfile:1
FROM python:slim
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY seedcross/requirements.txt /code/
COPY seedcross/dockerstart.sh /code/
RUN pip install -r requirements.txt
COPY . /code/

EXPOSE 8019
ENTRYPOINT ["/code/dockerstart.sh"]
```

* docker-compose.yml
```yml
version: "3.9"
   
services:
  seedcross:
    build: .
    command: bash -c "./dockerstart.sh"
    volumes:
      - ./seedcross:/code
      - ./dbdata:/code/seedcross/db
    ports:
      - "8019:8019"
```

* a `dockerstart.sh` in seedcross dir
```sh
#!/bin/sh
cd /code/seedcross
cp -n db_empty/* db/
python3 manage.py makemigrations && python3 manage.py migrate
python manage.py process_tasks &
python manage.py runserver 0.0.0.0:8019
```
