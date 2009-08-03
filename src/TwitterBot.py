

from mechanize import Browser
import urllib2
import re

class TwitterBot:

    __contact_regex = '<a href="http://twitter.com/[a-zA-Z_]+" rel="contact"><img alt=".*" class='
    
    __complete_name_regex = 'alt=".*" class='
    __complete_name_prefix = 'alt="'
    __complete_name_sufix = '" class='
    
    __url_regex = 'href=".*" rel'
    __url_prefix = 'href="'
    __url_sufix = '" rel'


    def __init__(self, user='zarasa123', passw='zarasa123', proxies_per_proto={}, debug=False):
        self.__br = Browser()
        self.__br.set_proxies(proxies_per_proto)
        self.__br.set_debug_http(debug)

        # sign in
        self.__br.open("http://twitter.com/")
        forms = self.__br.forms()
        form = forms.next()
        self.__br.select_form(nr=0)
        self.__br['username_or_email'] = user
        self.__br['password'] = passw
        resp = self.__br.submit()

    def search(self, query):
        br = self.__br
        self.__br.select_form(name='user_search_form')
        self.__br['q'] = query
        resp = self.__br.submit()
        links_urls = []
        for link in br.links(url_regex="twitter.com/[a-zA-Z_]+"):
            if  not 'index.php' in link.url and \
                not 'twitter.com/blog' in link.url and \
                not 'twitter.com/home' in link.url:
                links_urls.append(link.url)
        br.back()
        return links_urls

    def __strip_complete_name(self, html_match):
        match = re.search(self.__complete_name_regex, html_match)
        match = match.group()[len(self.__complete_name_prefix):-len(self.__complete_name_sufix)]
        return match

    def __strip_url(self, html_match):
        match = re.search(self.__url_regex, html_match)
        match = match.group()[len(self.__url_prefix):-len(self.__url_sufix)]
        return match


    def contacts(self, name):
        br = self.__br
        # check if name exists.
        results = self.search(name)
        if len(results) == 0:
            raise Exception('name "%s" doesn\'t exist in Twitter' % name)
        # assume the first person that matches
        name_link = results[0]
        # retrieve the first n (20?) contacts as tuples (complete_name, twitter_url).
        resp = self.__br.open(name_link + '/friends')
        cont =  resp.read()
        matches = re.findall(self.__contact_regex, cont)
        complete_names = map(self.__strip_complete_name, matches)
        urls = map(self.__strip_url, matches)
        return zip(complete_names, urls)


proxies_per_proto = {"http": "192.168.254.254:80"}
twitter = TwitterBot('zarasa123', 'zarasa123', proxies_per_proto)

print 'testing:'
try:
    print '"john garofalo" contacs:'
    conts = twitter.contacts('john garofalo')
    for c in conts:
        print c
except Exception, e:
    print 'Exception' + str(e.args)
print ''
try:
    print '"tom jones" contacs:'
    conts = twitter.contacts('guillermo castro')
    for c in conts:
        print c
except Exception, e:
    print 'Exception' + str(e.args)
print ''



