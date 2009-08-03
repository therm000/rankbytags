from nsed import NSED

# Normalized Msn Distance
class NMD(NSED):

    def __msn_strip(self, match):
        results = match.group()[len('<span id="count">'):-len('</span>')].replace('.','')
        results = int(results.split(' ')[2])
        return results
        #1-10 de 7.630.000.000
        
    def __msn_snippet_strip(self, match):
        snippet = match.group()[len('/a></h3><p>'):-len('</p><ul class="metaData">')]
        snippet = snippet.replace('<strong>','').replace('</strong>','')
        return snippet

    #def __init__(self, proxy=None):
    def __init__(self):
        url = 'search.live.com'
        get = '/results.aspx?'
        
        #regex = 'Page 1 of .* results</h5>'
        regex = '<span id="count">[a-zA-Z0-9.\- ]+</span>'
        strip = self.__msn_strip
        params = {}
        qparam = 'q'
        snippet_regex = '/a></h3><p>[^&]*<strong>[^&]*</strong>[^&]*</p><ul class="metaData">'
        #snippet_regex = '<p>([a-zA-Z\? -]*(<strong>)*[a-zA-Z\? -]*(</strong>)*[a-zA-Z\? -]*)+</p>'
        snippet_strip = self.__msn_snippet_strip
        super(NMD,self).__init__(url, get, regex, strip, snippet_regex, snippet_strip, params, qparam, {})
#             def __init__(self, url, get, regex, strip, snippet_strip, params, qparam, cache={}):
#, url, get, regex, strip, params, qparam, cache={}        
         
        #snippet = '<p>2fast4u -- <strong>how</strong> <strong>old</strong> <strong>are</strong> <strong>you</strong>? marcolopez -- ok do you need wheel chair? 2fast4u -- yep ... osvaldo -- decime 2fast4u como es que entrstes a este <strong>chat</strong> 2fast4u -- Disculpe.No ... </p>'
        #self.__set_snippet_regex(snippet_regex)

if __name__=='__main__':
    
    proxy = {'192.168.254.254':80}
    dist = NMD()    
#    print dist.distance(('blublu', 'bloblo'))
    print dist.snippets('how are you', 'chat transcripts')



