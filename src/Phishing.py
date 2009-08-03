
from http_email_address_grabber import search_email_address_grabber
from distance import NGD

#an email is "egutesman", "jorlicki", "ivan.arce", "info", etc.
#a name is "ivan arce" or "esther goris"
# types are 'domain2name&email' 'email2name&email' 'name2email&domain'
##emails.initialize('coresecurity.com', 'domain2name&email')

# probar con jkohen, ivan.arce, juliano

#emails.initialize('Gerardo Richarte', 'name2email&domain')
emails = search_email_address_grabber()
emails.initialize('itba.edu.ar', 'domain2name&email')
emails.targetRun()
email_list = emails.finalize()
print '--------------------------------------------------------------------------------'
for e in email_list:
    print str(e)

emails_with_name = {}
name_with_email = {}
for (e,n) in email_list:
    print e
    print n
    if n != '':
        emails_with_name[e] = n
        name_with_email[n] = e
print '--------------------------------------------------------------------------------'
print 'emails with name'
print str(emails_with_name)

def good_mail(mail):
    s = mail.split('@')
    return len(s) > 1 and '.' in s[1] and not '..' in s[1]

# now we retrieve non-domain emails.
mails_per_name = {}
mails_hits = {}
ngd = NGD()
for e, n in emails_with_name.iteritems():
    mails_per_name[n] = []
    emails = search_email_address_grabber()
    emails.initialize(n, 'name2email&domain')
    emails.targetRun()
    email_list = emails.finalize()
    for e2, n2 in email_list:
        if e2 != e and good_mail(e2):
            mails_per_name[n].append(e2)
            mails_hits[e2] = ngd.results(e2)

for n, l in mails_per_name.iteritems():
    print n
    print str(l)
    print '--------'

contexts = ['', 'machine', 'gadget', 'photo', 'video', 'song', 'album', 'computer', 'goal', 'site', 'shoes', 'post', 'article', 'paper']
# now we calculate the distance
name_best_match = {}
for n1 in mails_per_name.keys():
    best_match_dist = 3.0
    best_match = ('','')
    for context in contexts:
        tuples = []
        n2s = []
        for n2 in mails_per_name.keys():
            if n1 != n2:
                tuples.append((n1,n2))
                n2s.append(n2)
        dists = ngd.distances(tuples, context)
        for (n1,n2),dist in dists.iteritems():
            if dist < best_match_dist:
                best_match_dist = dist
                best_match = (n2,context)
                
    name_best_match[n1] = best_match
    
print '------------------------'
print 'best_matches'
for n,(n2,context) in name_best_match.iteritems():
    if n2 != '':
        # use the non-domain email with the best hits
        best = ''
        best_hits = -1
        for m in mails_per_name[n2]:
            if mails_hits[m] > best_hits:
                best_hits = mails_hits[m]
                best = m
        if best != '':
            print '%s %s will receive a phishing email from %s %s about %s' % (n, name_with_email[n], n2, best, context)


##best_matches @coresecurity.com
##force team fteam@force.coresecurity.com will receive a phishing email from ivan
##arce iarce@core-sdi.com about gadget
##juan vera juan@coresecurity.com will receive a phishing email from javier kohen
##jkohen@users.sourceforge.net about gadget
##ivan arce ivan.arce@coresecurity.com will receive a phishing email from technolo
##gies advisories  about machine
##javier kohen jkohen@coresecurity.com will receive a phishing email from technolo
##gies advisories  about site
##technologies advisories advisories@coresecurity.com will receive a phishing emai
##l from adrian manrique  about shoes
##ezequiel gutesman egutesman@coresecurity.com will receive a phishing email from
##technologies advisories  about site
##adrian manrique adrian@coresecurity.com will receive a phishing email from techn
##ologies advisories  about shoes
