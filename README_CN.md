# 外站辅种软件 SeedCross

* 对下载器(Deluge/qBittorrent/Transmission)中的种子，通过Jackett在各外站上寻找匹配的种子，以暂停状态加入到下载器，供进一步检查完成辅种
* 参考 [CrossSeedAutoDL](https://github.com/BC44/Cross-Seed-AutoDL)

![screenshot](screenshot/seedcross1.png)

## 前置条件
* [Jackett](https://github.com/Jackett/Jackett) : 外站众多，形态各异，Jackett作了相对统一的适配，因此，这里通过 Jackett 进行种子搜索。如果你还没有安装，可参考：[这里](https://github.com/ccf-2012/ptnote/blob/main/CrossSeed.md#jackett-%E5%AE%89%E8%A3%85)
* Deluge/qBittorrent/Transmission：略
* Docker：可以是任何支持Docker的环境，比如 nas，seedbox, 你的笔记本也行，它运行起来没什么负担

## 安装
* 在装有Docker的环境中，运行以下命令即可：
```sh
docker run -d --name seedcross -p 8019:8019 ccf2012/seedcross:latest
```
* 所需要的就是映射 `8019` 端口出来，以便浏览器访问。


## 开始使用
1. 浏览器中打开 `http://<your-ip>:8019` 
2. 用户名:密码  `admin`:`admin`

## 设置参数
* 首先进`Settings`页面，这里的每个参数都要小心填写：
1. Download Client Setting: 
  * 下载器的 `Type`, `Host`, `Port`, `Username`, `Password` , 注意 `Host` 都是IP地址，而不是带 `http://` 和端口的 url。
2. Jackett Setting: 
  * `Jackett Url` 填写 `http://<server ip>:<port>/`, 即前面有`http://` 后面到 端口号 为止, 打开你已经配置好的 Jackett 网页，拷贝右上角的 `Jackett Api key`
  * Trackers / Indexers in Jackett: 留空就会搜索全部配置的tracker。如果你想只搜单个tracker, 这里要填的就是在Jackett中 `torznab feed URL` 里面 `indexers/` 和 `/results` 中间那个单词。
3. Flow Control Setting: 
  * Flow control: Count limit: 如果你下载器中有几千种子，持续搜索将会对tracker服务器带来负担，所以把这个值设置为一个你觉得安全的上限。SeedCross会管理搜索的历史，下次搜索时会跳过那些已经搜过的种子。
  * Flow control: Interval: 查询间隔，每次查询之后暂停几秒。
4. 填完上述信息后，点击 `Save Settings`, 明显的错误如url/ip格式不符，界面会停在设置页面，并有错误信息提示，否则就会转到 `Start Cross` 页面。

## Start Crossing
1. 点击 `Start Cross` 按钮, SeedCross就会开始:
    1. 从下载器中读入种子
    2. 解析种子名字以获得 title,year,episode 等， 以这些信息通过Jackett去到各站进行搜索
    3. 对搜索结果进行筛选
    4. 将筛选出的种子，其下载链接加入到下载器，并确保是暂停状态，不论下载器设置中全局设置是否暂停，注意如果相同的种子已经在下载器中，就会忽略
* 已经查过的种子将不会提交搜索
* 含有 CJK 字符和种子将不会提交搜索
* 如果点击 `Start Cross` 按钮时，还没有设置好必要信息，就会转到 `Settings` 页. 

2.  在处理过程中，会显示一个进度面板，其中包括:
  * Total/Searched: 在下载器中的种子总数 / 到现在已经处理的种子数，包括跳过的
  * Flow-Limit/Searched of this session: 你所设置的流控数量 / 本次搜索已经发起的查询次数
  * Downloaded torrent in this session：本次搜索中，找到的匹配。需要说明的是，如果你已经对这批种子作过多次辅种，有可能找到的匹配是已经在下载器中了，所以这里的列表和下载器中不一定会一一对应
  * 有一个滚动的 text box 显示 info/error 消息。这消息就用来看看的，出现错误时可以试着猜猜发生了什么，如果刷新页面，前面的消息是会消失的

3. 一次辅种处理过程将会在下列情况停止:
  * 配置错误：下载器连不上，下载器登陆密码错，Jackett地址错或Api key填错
  * 查询次数达到 Flow limit count
  * 下载器中的种子已经全部遍历
  * 用户点击了 Cancel 按钮
* 如果没有活动的cross任务，进度面板在页面刷新时会消失

## Search History
* 查过的种子会被存在一个History表中，这些种子在下次查询时将会跳过，即使你已经开始在另一个下载器进行辅种查询.
* 如果你又收了个新站，你可能会想重新进行搜索，点击菜单中的 `Clear Search History` 就会删除所有记录.

## 数据库备份与恢复
* 有些麻烦预警
1. 先进入docker后台，把db拷出一份到 `/backup`
```sh
docker exec -it seedcross /bin/bash


mkdir /backup
cp -R /code/seedcross/db /backup/ 
```
2. 停止docker，将`/backup` 映射出来，比如映射到 `/volume1/docker/backup`
3. 再启动docker，就可以主机中的 `/volume1/docker/backup` 看到 `db` 目录，备份这个目录

* 更新docker后恢复数据 
1. 重新 pull 了新image后，在建 container时要映射一个目录到主机
2. 备份的数据拷到这个目录
3. 然后将备份的目录拷到程序目录中替换
```
docker exec -it seedcross /bin/bash

cp -R /backup/db  /code/seedcross/
```

## 近期计划
* Scheduler: 实现定期运行，就像iyuu那样
* Seperate tracker to search different media: 对音乐站不停地搜索Episode，和对影视站不停地搜索FLAC，后面看看能作到什么样
* Hardlink tweaks of file/folder to get more crossed：那些诱人的 `FraMeSToR.mkv` 和 `FraMeSToR/` ，以及 `CultFilms™` 和 `CultFilms`....
* Open to you Dai-lo's suggestions.


## Acknowledgement
1. Aruba@hutongyouwu 
2. [CrossSeedAutoDL](https://github.com/BC44/Cross-Seed-AutoDL)

