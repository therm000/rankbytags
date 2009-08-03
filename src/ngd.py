
from nsed import NSED

class NGD(NSED):


    def __init__(self, proxy):
        url = 'www.google.com'
        #get = '/search?q=%s&num=1'
        get = '/search?'
        #regex = 'of about <b>[0-9,]+</b> for <b>'  
        regex = 'about <b>[0-9,]+</b>'
        #regex = 'about'
        
        def google_strip(match):
            return match.group()[len('about <b>'):-len('</b>')].replace(',','')
        
        strip = google_strip
        params = {'num':1}
        qparam = 'q'        
        super(NGD,self).__init__(url, get, regex, strip, params, qparam, {}, proxy)
        
if __name__=='__main__':
    
    proxy = {'192.168.254.254':80}
    dist = NGD(proxy)    
#    print dist.distance(('quantum', 'rock'))





        
