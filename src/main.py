
from distance import NGD, NMD, NYD

import time

google = NGD()
msn = NMD()
yahoo = NYD()

def compare( a, b , google, msn, yahoo):

    g = google.distance(a,b)
    m = msn.distance(a,b)
    y = yahoo.distance(a,b)

    print 'for "%s" "%s"' % (a,b)
    print 'google: %f msn: %f yahoo: %f' % (g,m,y)
    print ''

pairs = [('by','with'), ('quantum','physics'), ('quantum', 'football')]

print time.ctime()
b = time.time()
#print google.distances((pairs*30)[:21])
a = time.time()
print time.ctime()
print 'took %d seconds' % (a-b)
b = time.time()
print google.distances((pairs*30)[:65], True)
a = time.time()
print time.ctime()
print 'took %d seconds' % (a-b)
