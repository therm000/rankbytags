from nsed import NSED

# Normalized Google Search Distance
class NGD(NSED):

    def __google_strip(self, match):
        s = match.group().replace('about ','')
        return s[len('</b> of <b>'):-len('</b> for <b>')].replace(',','')

    def __init__(self):
        url = 'www.google.com'
        get = '/search?'
        params = {}
        params['num'] = '1'
        params['btnG'] = 'Search'
        qparam = 'q'
        regex = '</b> of .*</b> for <b>'
        strip = self.__google_strip
        super(NGD,self).__init__(url, get, regex, strip, params, qparam)
        self.__failures = 0

# Normalized Msn Search (now Live Search) Distance
class NMD(NSED):

    def __msn_strip(self, match):
        return match.group()[len('Page 1 of '):-len(' results</span>')].replace(',','')

    def __init__(self):
        url = 'search.live.com'
        get = '/results.aspx?'
        params = {}
        qparam = 'q'
        regex = 'Page 1 of .* results</span>'
        strip = self.__msn_strip
        super(NMD,self).__init__(url, get, regex, strip, params, qparam)
        self.__failures = 0

# Normalized Yahoo Search Distance
class NYD(NSED):

    def __yahoo_strip(self, match):
                return match.group()[len('"infototal">'):-len('</')].replace(',','')

    def __init__(self):
        url = 'search.yahoo.com'
        get = '/search?'
        params = {}
        qparam = 'p'
#        <span id="infototal">16900000000</span>
        regex = '"infototal">[0-9,]+</'
        strip = self.__yahoo_strip
        super(NYD,self).__init__(url, get, regex, strip, params, qparam)
        self.__failures = 0

# Fotolog Harvester
class Fotolog(NSED):

    def __fotolog_strip(self, match):
                return match.group()[len('www.fotolog.com/'):-len('/')].replace(',','')

    def __init__(self):
        url = 'ff.fotolog.com'
        get = '/all.html?p=%s'
        params = {}
        qparam = 'u'
        regex = 'www.fotolog.com\/[a-z0-9_-]+\/'
        strip = self.__yahoo_strip
        super(NYD,self).__init__(url, get, regex, strip)
        self.__failures = 0

