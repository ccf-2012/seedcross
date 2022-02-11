from distutils.spawn import spawn
import re
from .torcategory import cutExt


def isFullAscii(str):
    return re.fullmatch(r'[\x00-\x7F]*', str, re.A)


def containsCJK(str):
    return re.search(r'[\u4e00-\u9fa5\u3041-\u30fc]', str)


def notTitle(str):
    return re.search(r'^(BDMV|1080[pi]|MOVIE|DISC|Vol)', str, re.A | re.I)


def cutAKA(titlestr):
    m = re.search(r'\s(/|AKA)\s', titlestr, re.I)
    if m:
        titlestr = titlestr.split(m.group(0))[0].strip()
    return titlestr


def getIndexItem(items, index):
    if index >= 0 and index < len(items):
        return items[index]
    else:
        return ''


def getNoBracketedStr(torName, items):
    ss = torName
    for s in items:
        ss = ss.replace('[' + s + ']', '')
    ss = ss.replace('[', '')
    ss = ss.replace(']', '')
    ss = ss.strip()

    return ss


def parseJpAniName(torName):
    items = re.findall(r'\[([^]]*)\]', torName)
    if len(items) < 2:
        return parseMovieName2(torName)

    strLeft = getNoBracketedStr(torName, items)

    if items[0] in ['BDMV', 'EAC', 'XLD']:
        items.pop(0)
    if len(strLeft) > 0:
        return getUnbracketedTitle(strLeft, items)
    else:
        titleIndex = -1
        if isFullAscii(items[0]):
            titleIndex = 0
        elif isFullAscii(items[1]) and not notTitle(items[1]):
            titleIndex = 1

    if titleIndex >= 0:
        return get3SectionJpAniName(items, titleIndex)
    else:
        return get1SectionJpAniName(items)


def getUnbracketedTitle(strLeft, items):
    yearstr, titlestr = getYearStr(strLeft)

    return cutAKA(titlestr), yearstr, '', '', ''


def get1SectionJpAniName(items):
    m = re.search(r'\(([\x00-\x7F]*)\)', items[0], re.A)
    if m:
        titlestr = m[1]
        yearstr, titlestr = getYearStr(titlestr)
    else:
        titlestr = items[0]

    return cutAKA(titlestr), yearstr, '', '', ''


def getYearStr(str):
    myear = re.search(r'\b((19\d{2}\b|20\d{2})-?(19\d{2}|20\d{2})?)\b', str)
    if myear:
        yearstr = myear.group(1)
        titlestr = re.sub(r'\(?' + yearstr + r'\)?', '', str)
    else:
        yearstr = ''
        titlestr = str
    return yearstr, titlestr


def get3SectionJpAniName(items, titleIndex):
    prevstr = getIndexItem(items, titleIndex - 1)
    if prevstr and containsCJK(prevstr):
        cntitle = prevstr
    else:
        cntitle = ''

    titlestr = getIndexItem(items, titleIndex)

    nextstr = getIndexItem(items, titleIndex + 1)
    if nextstr and containsCJK(nextstr):
        jptitle = nextstr
        jptitleIndex = titleIndex + 1
    else:
        jptitle = ''
        jptitleIndex = titleIndex

    nextstr2 = getIndexItem(items, jptitleIndex + 1)
    if re.search(r'\b((19\d{2}\b|20\d{2})-?(19\d{2}|20\d{2})?)\b', nextstr2):
        yearstr = nextstr2
        # seasonstr = getIndexItem(items, jptitleIndex+2)
    else:
        yearstr, titlestr = getYearStr(titlestr)
        # seasonstr = getIndexItem(items, jptitleIndex+1)
    seasonstr = ''
    episodestr = ''

    return cutAKA(titlestr), yearstr, seasonstr, episodestr, cntitle


def parseMovieName(torName):
    if torName.startswith('[') and torName.endswith('SP'):
        m = re.search(r'\]([^]]*\+.?SP)$', torName, flags=re.I)
        if m:
            namestr = torName[:m.span(1)[0]]
            return parseJpAniName(namestr)
            
    if torName.startswith('[') and torName.endswith(']'):
        return parseJpAniName(torName)
    else:
        return parseMovieName2(torName)

def parseSeason(sstr):
    seasonstr = ''
    seasonspan = [-1, -1]
    episodestr = ''

    # m1 = None
    # for m1 in re.finditer(r'(\bS\d+(-S\d+)?)\b', sstr, flags=re.A | re.I):
    #     pass
    m1 = re.search(r'(\bS\d+(-S?\d+))\s(?!.*\bS\d+)', sstr, flags=re.A | re.I)
    if m1:
        seasonstr = m1.group(1)
        seasonspan = m1.span(1)
        sstr = sstr.replace(seasonstr, '')
        return seasonstr, seasonspan, episodestr

    m2 = re.search(r'(\b(S\d+)(E\d+)?)\b', sstr, flags=re.A | re.I)
    if m2:
        seasonstr = m2.group(1)
        seasonspan = m2.span(1)
        if m2.group(3):
            seasonstr = m2.group(2)
            episodestr = m2.group(3)
        return seasonstr, seasonspan, episodestr

        # seasonsapn = mcns.span(1)
        # sstr = sstr.replace(mcns.group(1), '')
    mep = re.search(r'(Ep?\d+(-Ep?\d+)?)\b', sstr, flags=re.A | re.I)
    if mep:
        seasonstr = 'S01'
        episodestr = mep.group(1)
        seasonspan = mep.span(1)
        # if mep.group(2):
        #     seasonstr = mep.group(2)
        #     seasonspan = mep.span(2)
        return seasonstr, seasonspan, episodestr


    mcns = re.search(r'(第\s*((\d+)|([一二三四五六七八九十]))(-\d+)?季)(\s*第\s*((\d+)|([一二三四五六七八九十]))集)?', sstr, flags=re.I)
    if mcns:
        # origin_seasonstr = mcns.group(1)
        seasonspan = mcns.span(1)
        ssi = mcns.group(2)
        iss = '一二三四五六七八九'.find(ssi)
        if iss >= 0:
            ssi = str(iss+1).zfill(2)
        seasonstr = 'S' + ssi
        if mcns.group(6):
            episodestr = 'E' + mcns.group(7)

        return seasonstr, seasonspan, episodestr


    return seasonstr, seasonspan, episodestr

def parseYear(sstr):
    yearstr = ''
    yearspan = [-1, -1]
    m2 = re.search(
        r'\b((19\d{2}\b|20\d{2})-?(19\d{2}|20\d{2})?)\b(?!.*\b\d{4}\b.*)',
        sstr,
        flags=re.A | re.I)
    if m2:
        yearstr = m2.group(1)
        yearspan = m2.span(1)
        if re.search(r'[\(\[\{]' + yearstr+r'\b', sstr):
            # sstr = sstr[:yearspan[0] - 1]
            yearspan = [yearspan[0]-1, yearspan[1]+1 ]
        # elif re.search(r'\w.*' + yearstr+r'\b', sstr):
        #     sstr = sstr[:yearspan[0]]

    return yearstr, yearspan

def cutspan(sstr, ifrom, ito):
    if (ifrom > 0) and (len(sstr) > ito):
        sstr = sstr[0 : ifrom: ] + sstr[ito + 1 : :]
    return sstr


def parseMovieName2(torName):
    sstr = cutExt(torName)

    sstr = re.sub(
        r'\b((UHD)?\s+BluRay|Blu-?ray|720p|1080[pi]|2160p|576i|WEB-DL|\.DVD\.|WEBRip|HDTV|Director(\'s)?[ .]Cut|REMASTERED|LIMITED|Complete(?=[. -]\d+)|SUBBED|TV Series).*$',
        '',
        sstr,
        flags=re.I)
    sstr = re.sub(r'\[Vol.*\]$', '', sstr, flags=re.I)

    sstr = re.sub(r'\W?(IMAX|Extended Cut)\s*$', '', sstr, flags=re.I)

    if sstr[-1] in ['(', '[', '{']:
        sstr = sstr[:-1]

    dilimers = ['[', ']', '.', '{', '}', '_', ',']
    for dchar in dilimers:
        sstr = sstr.replace(dchar, ' ')

    sstr = re.sub(r'^\W?(BDMV|\BDRemux|\bCCTV\d(HD)?|[A-Z]{1,5}TV)\W*',
                  '',
                  sstr,
                  flags=re.I)

    seasonstr, seasonspan, episodestr = parseSeason(sstr)
    yearstr, yearspan = parseYear(sstr)

    t = max(seasonspan[0], yearspan[0])
    if t > 0:
        sstr = sstr[:t]

    sstr = cutspan(sstr, seasonspan[0], seasonspan[1])
    sstr = cutspan(sstr, yearspan[0], yearspan[1])
    # if seasonstr:
    #     sstr = re.sub(origin_seasonstr+r'.*$', '', sstr)
    sstr = re.sub(r'\b(剧集|全\d集|\d集全)\b', '', sstr, flags=re.I)

    titlestr = re.sub(r' +', ' ', sstr).strip()

    if titlestr.endswith(')'):
        titlestr = re.sub(r'\(.*$', '', sstr).strip()

    cntitle = titlestr
    m = re.search(
        r'^.*[^a-zA-Z_\- &0-9](S\d+|\s|\.|\d|-)*\b(?=[A-Z])',
        # m = re.search(r'^.*[^\x00-\x7F](S\d+|\s|\.|\d|-)*\b(?=[A-Z])',
        titlestr,
        flags=re.A)
    # m = re.search(r'^.*[\u4e00-\u9fa5\u3041-\u30fc](S\d+| |\.|\d|-)*(?=[A-Z])',
    #               titlestr)
    if m:
        cntitle = m.group(0)
        titlestr = titlestr.replace(cntitle, '')
    # if titlestr.endswith(' JP'):
    #     titlestr = titlestr.replace(' JP', '')

    return cutAKA(titlestr), yearstr, seasonstr, episodestr, cntitle
