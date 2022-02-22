import re
from .torcategory import cutExt


def isFullAscii(str):
    return re.fullmatch(r'[\x00-\x7F]*', str, re.A)


def containsCJK(str):
    return re.search(r'[\u4e00-\u9fa5\u3041-\u30fc]', str)

def containdCJKKeyword(str):
    return re.search(r'^(.迪士尼\b)', str)

def notTitle(str):
    return re.search(r'^(BDMV|1080[pi]|MOVIE|DISC|Vol)', str, re.A | re.I)


def cutAKA(titlestr):
    m = re.search(r'\s(/|AKA)\s', titlestr, re.I)
    if m:
        titlestr = titlestr.split(m.group(0))[0]
    return titlestr.strip()

def cutAKAJP(titlestr):
    m = re.search(r'(/|\bAKA\b)', titlestr, re.I)
    if m:
        titlestr = titlestr.split(m.group(0))[0]
    return titlestr.strip()


def getIndexItem(items, index):
    if index >= 0 and index < len(items):
        return items[index]
    else:
        return ''

def is0DayName(itemstr):
    # CoComelon.S03.1080p.NF.WEB-DL.DDP2.0.H.264-NPMS
    m = re.match(r'^\w+.*\b(BluRay|Blu-?ray|720p|1080[pi]|2160p|576i|WEB-DL|\.DVD\.|WEBRip|HDTV)\b.*', itemstr, flags=re.A | re.I)
    return m
        

def getNoBracketedStr(torName, items):
    ss = torName
    for s in items:
        ss = ss.replace('[' + s + ']', '')
    ss = ss.replace('[', '')
    ss = ss.replace(']', '')
    ss = ss.strip()

    return ss

def cutBracketedTail(sstr):
    m = re.search(r'^\w+.*(\[[^]]*\]?)', sstr)
    if m:
        sstr = sstr[:m.span(1)[0]]
    return sstr


def parseJpAniName(torName):
    yearstr, yearspan = parseYear(torName)

    items = re.findall(r'\[([^]]*[^[]*)\]', torName)

    if len(items) < 2:
        return parse0DayMovieName(torName)

    for s in items:
        if is0DayName(s):
            return parse0DayMovieName(s)

    strLeft = getNoBracketedStr(torName, items)
    if len(strLeft) > 0:
        # yearstr, titlestr = getYearStr(torName)
        titlestr = bracketToBlank(strLeft)
        return cutAKAJP(titlestr), yearstr, '', '', ''

    jptitles = []
    titlestrs = []
    jptitle = ''
    titlestr = ''
    for item in items:
        if re.match(r'^(BDMV|EAC|XLD|1080[pi]|MOVIE|DISC|Vol\.?\d+|MPEG|合集|ALBUM|SBCV|FLAC|SINGLE|V\.A|VVCL)\b', item, re.A | re.I):
            continue
        if re.match(r'^\d+$', item):
            continue
        
        if containsCJK(item):
            jptitles.append(item) 
        else:
            titlestrs.append(item)

    if len(titlestrs) > 0:
        titlestr = titlestrs[0]
        # titlestr = max(titlestrs, key=len)
        if jptitles:
            jptitle = max(jptitles, key=len)
    else:
        if jptitles:
            # jptitle = jptitles[0]
            jptitle = max(jptitles, key=len)
            titlestr = jptitle
        else:
            pass
            # raise 'Some thing Wrong'

    titlestr = cutBracketedTail(titlestr)
    titlestr = bracketToBlank(titlestr)

    return cutAKAJP(titlestr), yearstr, '', '', jptitle


def bracketToBlank(sstr):
    dilimers = ['(', ')', '-', '–', '_', '+']
    for dchar in dilimers:
        sstr = sstr.replace(dchar, ' ')
    return re.sub(r' +', ' ', sstr).strip()

def delimerToBlank(sstr):
    dilimers = ['[', ']', '.', '{', '}', '_', ',']
    for dchar in dilimers:
        sstr = sstr.replace(dchar, ' ')
    return sstr

def parseMovieName(torName):
    if torName.startswith('[') and torName.endswith('SP'):
        m = re.search(r'\]([^]]*\+.?SP)$', torName, flags=re.I)
        if m:
            namestr = torName[:m.span(1)[0]]
            return parseJpAniName(namestr)
            
    if torName.startswith('[') and torName.endswith(']'):
        return parseJpAniName(torName)
    else:
        return parse0DayMovieName(torName)

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

    m2 = re.search(r'(\b(S\d+)([\. ]?Ep?\d+)?)\b', sstr, flags=re.A | re.I)
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


    mcns = re.search(r'(第?\s*((\d+)|([一二三四五六七八九十]))(-\d+)?季)(\s*第\s*((\d+)|([一二三四五六七八九十]))集)?', sstr, flags=re.I)
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
        r'\b((19\d{2}\b|20\d{2})(-19\d{2}|-20\d{2})?)\b(?!.*\b\d{4}\b.*)',
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
    if (ifrom >= 0) and (len(sstr) > ito):
        sstr = sstr[0 : ifrom: ] + sstr[ito + 1 : :]
    return sstr


def parse0DayMovieName(torName):
    sstr = cutExt(torName)

    failsafeTitle = sstr

    sstr = re.sub(
        r'\b((UHD)?\s+BluRay|Blu-?ray|720p|1080[pi]|2160p|576i|WEB-DL|\.DVD\.|WEBRip|HDTV|Director(\'s)?[ .]Cut|REMASTERED|LIMITED|Complete(?=[. -]\d+)|SUBBED|TV Series).*$',
        '',
        sstr,
        flags=re.I)
    sstr = re.sub(r'\[Vol.*\]$', '', sstr, flags=re.I)

    sstr = re.sub(r'\W?(IMAX|Extended Cut|\d+CD|APE整轨)\b.*$', '', sstr, flags=re.I)
    sstr = re.sub(r'[\[\(](BD\d+|WAV\d*|(CD\-)?FLAC|Live|DSD\s?\d*)\b.*$', '', sstr, flags=re.I)
    sstr = re.sub(r'^\W?(BDMV|\BDRemux|\bCCTV\d(HD)?|BD\-?\d*|[A-Z]{1,5}TV)\W*', '', sstr, flags=re.I)

    sstr = re.sub(r'\{[^\}]*\}.*$', '', sstr, flags=re.I)
    sstr = re.sub(r'([\s\.-](\d+)?CD[\.-]WEB|[\s\.-](\d+)?CD[\.-]FLAC|[\s\.-][\[\(\{]FLAC[\]\)\}]).*$', '', sstr, flags=re.I)
    sstr = re.sub(r'\bFLAC\b.*$', '', sstr, flags=re.I)
    sstr = re.sub(r'^[\[\(]\d+[^\)\]]*[\)\]]', '', sstr, flags=re.I)


    sstr = re.sub(r'^\W?CC_?\b', '', sstr, flags=re.I)
    if sstr and sstr[-1] in ['(', '[', '{']:
        sstr = sstr[:-1]

    sstr = delimerToBlank(sstr)
    if sstr:
        failsafeTitle = sstr

    seasonstr, seasonspan, episodestr = parseSeason(sstr)
    yearstr, yearspan = parseYear(sstr)
    if not yearstr:
        yearstr, yearspan = parseYear(torName)
        yearspan = [-1, -1]

    if seasonspan[0] > yearspan[0]:
        syspan = seasonspan
        systr = seasonstr
    else:
        syspan = yearspan
        systr = yearstr

    skipcut = False
    if syspan and syspan[0] > 1 :
        spanstrs = sstr.split(systr)
        if containdCJKKeyword(sstr[:syspan[0]]):
            sstr = sstr[syspan[1]:]
            skipcut = True
        else:
            sstr = sstr[:syspan[0]]

    if not skipcut:
        sstr = cutspan(sstr, seasonspan[0], seasonspan[1])
        sstr = cutspan(sstr, yearspan[0], yearspan[1])

    sstr = re.sub(r'\b(剧集|全\d集|\d集全|国语|BD\d*)$', '', sstr, flags=re.I)

    if sstr and sstr[-1] in ['(', '[', '{', '（', '【']:
        sstr = sstr[:-1]

    # if titlestr.endswith(')'):
    #     titlestr = re.sub(r'\(.*$', '', sstr).strip()

    cntitle = sstr
    # m = re.search(r'^.*[^\x00-\x7F](S\d+|\s|\.|\d|-|\))*\b(?=[a-zA-Z])', sstr, flags=re.A)
    # m = re.search( r'^.*[^a-zA-Z_\- &0-9](S\d+|\s|\.|\d|-)*\b(?=[A-Z])', titlestr, flags=re.A)
    m = re.search(r'^.*[\u4e00-\u9fa5\u3041-\u30fc](S\d+|\s|\.|\d|-|\))*\b(?=[a-zA-Z])',
                  sstr, flags=re.A)
    if m:
        # ['(', ')', '-', '–', '_', '+']
        cntitle = m.group(0)
        if not re.search(r'\s[\-\+]\s', cntitle):
            # if len(sstr)-len(cntitle) > 4:
            sstr = sstr.replace(cntitle, '')

    titlestr = bracketToBlank(sstr)
    titlestr = cutAKA(titlestr)
    if len(titlestr) == 0:
        titlestr = bracketToBlank(failsafeTitle)

    return titlestr, yearstr, seasonstr, episodestr, cntitle
