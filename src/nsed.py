
import httplib, urllib
import re
import math
import time

# thread imports
from nsedthread import NSEDThread


# Normalized Search Engine Distance
class NSED(object):

    def __search_engine_strip(self):
        return ''

    def __init__(self, url, get, regex, strip, snippet_regex, snippet_strip, params, qparam, cache={}):
#        super(NMD,self).__init__(url, get, regex, strip, snippet_regex, snippet_strip, params, qparam, {}, proxy)
        self.__base = 2
        self.__url = url
        self.__get = get
        self.__regex = regex
        self.__strip = strip
	self.__snippet_regex = snippet_regex
	self.__snippet_strip = snippet_strip
        self.__params = params
        self.__qparam = qparam
        self.__cache = cache
        self.__failures = 0
        self.set_context('')
        self._params = params

    def update_params(self, key, val):
        self.__params[key] = val

    def clear_failures(self):
        self.__failures = 0

    def get_failures(self):
        return self.__failures

    def set_context(self, context):
        self.__context = context
        # results for letter 'a' as approximation of total pages indexed
        self.__total = self.results('a', context)

    def get_base(self):
        return self.__base

    def results_total(self):
        return self.__total

    def __add_quotes(self, str):
        if str.find(' ') != -1 and len(str)>0 and str[0]!='"' and str[-1]!='"':
            return '"' + str + '"'
        else:
            return str

    # quotes are not implicit in context, but are in string
    def results(self, string, context=''):
        
        if context!=self.__context:
            self.set_context(context)
        res = self.results_list([string, context])
        return res 

    # avoid unescaped double quotes in string
    def results_query(self, string):
        # first check cache
        if string in self.__cache.keys():
            return self.__cache[string]
        ms = self.matches_query(string)
        if len(ms) == 0:
            res = 0
            self.__failures += 1
            print 'FAILURE!!!'
        else:
            res = long(ms[0])
        self.__cache[string] = res
        print res
        return res

    # avoid unescaped double quotes in string
    def matches_query(self, string):
        print string
        url_string = string
        self.__params[self.__qparam] = url_string
        url_params = urllib.urlencode(self.__params)
        ret = []
        self.conn = httplib.HTTPConnection(self.__url)
        bla = """User-Agent: Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)
Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5
Accept-Language: es-ar,es;q=0.8,en-us;q=0.5,en;q=0.3
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
Keep-Alive: 300
Connection: keep-alive
Referer: http://www.google.com/search?q=a++&num=1
Cookie: PREF=ID=e227d6a6270e25f0:LD=en:CR=2:TM=1189105984:LM=1189155519:GM=1:S=M4gEFmlnpxCOG__F; AnalyticsLocale=en; TZ=180; GMAIL_RTT=205; GMAIL_LOGIN=T1192629883541/1192629883541/1192629886550; S=sorry=SgXgDIQwVFNYEp6ERRjljw; GDSESS=ID=e227d6a6270e25f0:EX=1192678260:S=QrMjUQbPPM0p45e0
"""
        
        self.conn.request("GET", self.__get + url_params)
#        self.conn = httplib.HTTPConnection('192.168.254.254',80)

 #       self.conn.request("GET", 'http://' + self.__url + self.__get + url_params)
        print 'http://' + self.__url + self.__get + url_params 

        r1 = self.conn.getresponse()        
        p = r1.read()
#        print p
        iterator = re.finditer(self.__regex, p)
        for match in iterator:
            ret.append(self.__strip(match))
        return ret

    # avoid unescaped double quotes in string
    def snippets(self, string, context=''):
        if context!=self.__context:
            self.set_context(context)
        print string
        url_string = string
        self.__params[self.__qparam] = url_string
        url_params = urllib.urlencode(self.__params)
        ret = []
        self.conn = httplib.HTTPConnection(self.__url)
        bla = """User-Agent: Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)
Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5
Accept-Language: es-ar,es;q=0.8,en-us;q=0.5,en;q=0.3
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
Keep-Alive: 300
Connection: keep-alive
Referer: http://www.google.com/search?q=a++&num=1
Cookie: PREF=ID=e227d6a6270e25f0:LD=en:CR=2:TM=1189105984:LM=1189155519:GM=1:S=M4gEFmlnpxCOG__F; AnalyticsLocale=en; TZ=180; GMAIL_RTT=205; GMAIL_LOGIN=T1192629883541/1192629883541/1192629886550; S=sorry=SgXgDIQwVFNYEp6ERRjljw; GDSESS=ID=e227d6a6270e25f0:EX=1192678260:S=QrMjUQbPPM0p45e0
"""
        
        self.conn.request("GET", self.__get + url_params)
#        self.conn = httplib.HTTPConnection('192.168.254.254',80)

 #       self.conn.request("GET", 'http://' + self.__url + self.__get + url_params)
        print 'http://' + self.__url + self.__get + url_params 

        r1 = self.conn.getresponse()        
        p = r1.read()
#        print p
        iterator = re.finditer(self.__snippet_regex, p)
        for match in iterator:
            ret.append(self.__snippet_strip(match))
        return ret

    def results_list(self, list):
        string = ''
        for s in list:
            string += self.__add_quotes(s) + ' '
        return self.results_query(string)

    # quotes are not implicit in context, but are in x and y.
    def distance(self, (x, y), context=''):
        if context!=self.__context:
            self.set_context(context)
        x_res = self.results(x, context)
        y_res = self.results(y, context)
        # x,y results as a set, not concatenation
        xy_res = self.results_list([x,y,context])
        
        if x_res==0 and y_res==0:
            return None
        if xy_res==0:
            return 2.00 # infinite
        # use base 2 logs to compute final value
        base = self.__base
        numerator = max( math.log(x_res,base), math.log(y_res,base) ) - math.log(xy_res,base)
        denominator = math.log(self.__total,base) - min( math.log(x_res,base), math.log(y_res,base) )

        ret = numerator / denominator
#         if ret < 0.0:
#             ret = 0.0
#         elif ret > 1.0:
#             ret = 1.0
        print ret
        return ret

    def distances(self, pairs, context='', use_threads=True):
        if use_threads:
            return self.__fast_distances(pairs, context)
        else:
            dists = {}
            for p in pairs:
                dists[p] = self.distance(p,context)
            return dists

    def __fast_distances(self, pairs, context=''):

       dists = {}
       threads = 8
       size = 8

       partial = 0
       while partial < len(pairs):

           threadlist = []
           thread_count = 0
           while thread_count < threads and partial < len(pairs):
               thread_instance = NSED(self.__url, self.__get, self.__regex, self.__strip, self.__params, self.__qparam, self.__cache)
               current = NSEDThread(thread_instance, pairs[partial:partial+size], context)
               partial += size
               threadlist.append(current)
               current.start()
               thread_count += 1

           for thread in threadlist:
               thread.join()
               dists.update(thread.distances)

       return dists
               
   
        
