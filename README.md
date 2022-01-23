# SeedCross
* A Web app to Cross-Seed torrents in Deluge/qBittorrent/Transmission
* based on [CrossSeedAutoDL](https://github.com/BC44/Cross-Seed-AutoDL)

![screenshot](screenshot/seedcross1.png)

## Require
* [Jackett](https://github.com/Jackett/Jackett) 
* Deluge/qBittorrent/Transmission
* Docker
  
## Installation
```sh
docker run -d --name seedcross -p 8019:8019 ccf2012/seedcross:latest
```

## Login
1. open `http://<your-ip>:8019` in browser
2. login with `admin:admin`

## Settings
* Start from `Settings` tab, fill the fields carefully:
1. Download Client Setting: 
   1. `Type`, `Host`, `Port`, `Username`, `Password` as usual, note the `Host` must be an IP address, not url.
2. Jackett Setting: 
   1. you should have started a proper configured Jackett server, thus you can get the  `Jackett Url` and `Jackett Api key`, 
   2. Trackers / Indexers in Jackett: the only optional field, leave it blank if you would seach all the trackers; when you want to search specific tracker, you should find the exact word between `indexers/` and `/results` in the `torznab feed URL` in Jackett
3. Flow Control Setting: 
   1. Flow control: Count limit: every search query will lead load to the tracker server, limit this count as your feel safe, SeedCross will manage the search history and find the next un-searched torrent when you start cross next time.
   2. Flow control: Interval: time delay between 2 search query.
4. After you fill the form, press `Save Settings`, if no error detected, it will redirect to the `Start Cross` page, otherwise there will be error message next to the field.

## Start Crossing
1. press `Start Cross` button, seedcross will start to:
    1. load the torrents from the download client.
    2. parse the name to get the title,year,episode etc, with these keyword ask Jackett server to search torrents in your pre-configured trackers.
    3. check if there's match by title and size.
    4. add the download link to the download client, in `paused` state.
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

 
## Search History
* Torrents that has been searched will be recorded, they won't bother the trackers for the next process.
* but when you add new trackers you may want to redo the search, click the `Clear Search History` will delete all the records.

## Plans
* Scheduler to run the task periodically
* Seperate tracker to search different media
* Hardlink tweaks of file/folder to get more crossed.
* Open to you Dai-lo's suggestions.


## Acknowledgement
1. Aruba@hutongyouwu 
2. [CrossSeedAutoDL](https://github.com/BC44/Cross-Seed-AutoDL)

