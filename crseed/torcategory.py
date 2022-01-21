import re
import os


class CategoryItem:
    def __init__(label, number):
        label = label
        number = number
        # size = 0


class GuessCategoryUtils:
    # 有些组生产 TV Series，但是在种子名上不显示 S01 这些
    TV_GROUPS = ['CMCTV', 'FLTTH']
    WEB_GROUPS = ['CHDWEB', 'PTERWEB', 'HARESWEB', 'DBTV', 'QHSTUDIO', 
                 'LEAGUEWEB', 'HDCTV', '52KHD', 'PTHWEB', 'OURTV', 'ILOVETV']

    # 有些组专门生产 MV
    MV_GROUPS = ['PTERMV', 'FHDMV', 'MELON', 'HARESMV', 'BUGS!']
    # 有些组专门生产 Audio
    AUDIO_GROUPS = ['PTHAUDIO', 'HDSAB']
    # 有些组专门作压制，但是不在种子名上标记
    MOVIE_ENCODE_GROUPS = ['CMCT', 'FRDS']

    CATEGORIES = {
        'TV': ['TV', '32', 0, 'TV'],
        'MV': ['MV', '31;1', 0, 'MV'],
        'Audio': ['Audio', '32;1', 0, 'Audio'],
        'Music': ['Music', '31', 0, 'Music'],
        'eBook': ['eBook', '34', 0, 'eBook'],
        # 压制 1080p and lower, 适合emby
        'MovieEncode': ['MovieEncode', '36', 0, 'MovieEncode'],
        # Remux 1080p and lower, 适合emby
        'MovieRemux': ['MovieRemux', '36', 0, 'MovieRemux'],
        'Movie4K': ['Movie4K', '36', 0, 'Movie4K'],  # 压制和Remux 4K，适合emby
        'MovieWebdl': ['MovieWebdl', '36', 0, 'MovieWebdl'],  # Web DL，适合emby
        'MovieWeb4K': ['MovieWeb4K', '36', 0, 'MovieWeb4K'],  # Web DL，适合emby
        'MovieBDMV': ['MovieBDMV', '35', 0, 'MovieBDMV'],  # 原盘, 适合播放机 & kodi
        # 原盘 4K, 适合播放机 & kodi
        'MovieBDMV4K': ['MovieBDMV4K', '35', 0, 'MovieBDMV4K'],
        'HDTV': ['HDTV', '33', 0, 'HDTV'],
        'Other': ['Other', '33', 0, 'Others']
    }

    category = ''
    group = ''
    CategorySummary = []

    def setCategory(category):
        GuessCategoryUtils.category = category
        GuessCategoryUtils.CATEGORIES[category][2] += 1

    def categoryByExt(torName):
        if re.search(
                r'(pdf|epub|mobi|txt|chm|azw3|CatEDU|eBook-\w{4,8}|mobi|doc|docx).?$',
                torName, re.I):
            GuessCategoryUtils.setCategory('eBook')
        elif re.search(r'\.(mpg)\b', torName, re.I):
            GuessCategoryUtils.setCategory('MV')
        elif re.search(r'\b(FLAC.{0,3}|DSD(\d{1,3})?)$', torName, re.I):
            GuessCategoryUtils.setCategory('Music')
        else:
            return False
        return True

    def categoryByKeyword(torName):
        if re.search(r'(上下册|全.{1,4}册|精装版|修订版|第\d版|共\d本|文集|新修版|PDF版|课本|课件|出版社)',
                     torName):
            GuessCategoryUtils.setCategory('eBook')
        elif re.search(r'(\d+册|\d+期|\d+版|\d+本|\d+年|\d+月|系列|全集|作品集).?$',
                       torName):
            GuessCategoryUtils.setCategory('eBook')
        elif re.search(r'(\bConcert|演唱会|音乐会|\bLive[. ]At)\b', torName, re.A | re.I):
            GuessCategoryUtils.setCategory('MV')
        elif re.search(r'\bBugs!.?\.mp4', torName, re.I):
            GuessCategoryUtils.setCategory('MV')
        elif re.search(r'(\bVarious Artists|\bMQA\b|整轨|\b分轨|\b无损|\bLPCD|\bSACD|XRCD\d{1,3})',
                       torName, re.A | re.I):
            GuessCategoryUtils.setCategory('Music')
        elif re.search(r'(\b\d+ ?CD|24-96|24\-192|24\-44\.1|FLAC.*24bit|FLAC.*44|FLAC.*48|WAV.*CUE|FLAC.*CUE|\[FLAC\]|FLAC.+WEB\b|FLAC.*Album|CD[\s-]+FLAC|FLAC[\s-]+CD)', torName, re.A | re.I):
            GuessCategoryUtils.setCategory('Music')
        elif re.search(r'(乐团|交响曲|协奏曲|二重奏|专辑\b)', torName):
            GuessCategoryUtils.setCategory('Music')
        else:
            return False
        return True

    def categoryTvByName(torName):
        if re.search(r'\bHDTV\b', torName):
            GuessCategoryUtils.setCategory('HDTV')
        elif re.search(r'\W[ES]\d+\W|EP\d+\W|\d+季|第\w{1,3}季\W', torName, re.A | re.I):
            GuessCategoryUtils.setCategory('TV')
        elif re.search(r'Full.Season|全\d+集|\d+集全', torName, re.A | re.I):
            GuessCategoryUtils.setCategory('TV')
        else:
            return False
        return True

    def categoryByGroup(group):
        if group in GuessCategoryUtils.MV_GROUPS:
            GuessCategoryUtils.setCategory('MV')
        elif group in GuessCategoryUtils.AUDIO_GROUPS:
            GuessCategoryUtils.setCategory('Audio')
        elif group in GuessCategoryUtils.TV_GROUPS:
            GuessCategoryUtils.setCategory('TV')
        elif group in GuessCategoryUtils.WEB_GROUPS:
            GuessCategoryUtils.setCategory('TV')
        elif group in GuessCategoryUtils.MOVIE_ENCODE_GROUPS:
            GuessCategoryUtils.setCategory('MovieEncode')
        else:
            return False
        return True


    def cutExt(torName):
        tortup = os.path.splitext(torName)
        torext = tortup[1].lower()
        mvext = ['.mkv', '.ts', '.m2ts', '.vob', '.mpg', '.mp4', '.3gp', '.mov', '.tp']
        if torext in mvext:
            return tortup[0].strip()
        else:
            return torName

    def parseGroup(torName):
        sstr = GuessCategoryUtils.cutExt(torName)
        match = re.search(r'[@\-￡]\s?(\w{3,12})\b(?!.*[@\-￡].*)$', sstr, re.I)
        if match:
            groupName = match.group(1).strip().upper()
            if groupName.startswith('CMCT'):
                if not groupName.startswith('CMCTV'):
                    groupName = 'CMCT'
            return groupName

        return None

    def getResolution(torName):
        match = re.search(r'\b(2160p|1080[pi]|720p|576p|480p)\b', torName, re.A | re.I)
        if match:
            return match.group(0).strip().lower()
        else:
            return ''

    def getQuality(torName):
        match = re.search(r'\b(Blu[\-\. ]?Ray|WEB[\-\. ]?DL)\b', torName, re.A | re.I)
        if match:
            groupstr = match.group(0).strip().lower()
            if 'blu' in groupstr:
                return 'BLURAY'
            else:
                return 'WEBDL'
        else:
            return ''

    def categoryByQuality(torName):
        quality = GuessCategoryUtils.getQuality(torName)
        resolution = GuessCategoryUtils.getResolution(torName)
        if quality:
            # 来源为原盘的
            if quality == 'BLURAY':
                # Remux, 压制 还是 原盘
                if re.search(r'\WREMUX\W', torName, re.I):
                    if resolution == '2160p':
                        GuessCategoryUtils.setCategory('Movie4K')
                    else:
                        GuessCategoryUtils.setCategory('MovieRemux')
                elif re.search(r'\b(x265|x264)\b', torName, re.I):
                    if resolution == '2160p':
                        GuessCategoryUtils.setCategory('Movie4K')
                    else:
                        GuessCategoryUtils.setCategory('MovieEncode')
                else:
                    if resolution == '2160p':
                        GuessCategoryUtils.setCategory('MovieBDMV4K')
                    else:
                        GuessCategoryUtils.setCategory('MovieBDMV')
            # 来源是 WEB-DL
            elif quality == 'WEBDL': 
                if resolution == '2160p':
                    GuessCategoryUtils.setCategory('MovieWeb4K')
                else:
                    GuessCategoryUtils.setCategory('MovieWebdl')
            else:
                return False
            return True
        return False

    @staticmethod
    def guessByName(torName):
        GuessCategoryUtils.group = GuessCategoryUtils.parseGroup(torName)
        if GuessCategoryUtils.categoryByExt(torName):
            return GuessCategoryUtils.category, GuessCategoryUtils.group

        if GuessCategoryUtils.categoryTvByName(torName):
            return GuessCategoryUtils.category, GuessCategoryUtils.group

        if GuessCategoryUtils.categoryByKeyword(torName):
            return GuessCategoryUtils.category, GuessCategoryUtils.group

        if GuessCategoryUtils.categoryByGroup(GuessCategoryUtils.group):
            return GuessCategoryUtils.category, GuessCategoryUtils.group

        # 非web组出的
        if GuessCategoryUtils.categoryByQuality(torName):
            return GuessCategoryUtils.category, GuessCategoryUtils.group
        else:
            # Other的条件： TV/MV/Audio都匹配不上，quality没标记，各种压制组也对不上
            GuessCategoryUtils.setCategory('Other')
            return GuessCategoryUtils.category, GuessCategoryUtils.group

    def getSummary():
        for cat in GuessCategoryUtils.CATEGORIES.keys():
            ic = CategoryItem(GuessCategoryUtils.CATEGORIES[cat][0],
                              GuessCategoryUtils.CATEGORIES[cat][2])
            GuessCategoryUtils.CategorySummary.append(ic)
        return GuessCategoryUtils.CategorySummary
