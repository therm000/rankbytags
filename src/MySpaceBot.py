

from mechanize_ import Browser
import urllib, urllib2
import re

class MySpaceBot:

    __name_regex = 'href="http://profile.myspace.com/index.cfm?fuseaction=user.viewprofile&friendID=[0-9]+" linkindex='
    __contact_regex = 'href="http://profile.myspace.com/index.cfm\?fuseaction=user.viewprofile&friendid=[0-9]+" id="ctl[0-9]+_Main_ctl[0-9]+_UserFriends1_FriendRepeater_ctl[0-9]+_friendLink">[^\n]+</a>'
    
    __complete_name_regex = 'friendLink">[^\n]+</a>'
    __complete_name_prefix = 'friendLink">'
    __complete_name_sufix = '</a>'
    
    __url_regex = 'href="http://profile.myspace.com/index.cfm\?fuseaction=user.viewprofile&friendid=[0-9]+" id'
    __url_prefix = 'href="'
    __url_sufix = '" id'

    def __init__(self, proxies_per_proto={}, debug=False):
        self.__br = Browser()
        self.__br.set_proxies(proxies_per_proto)
        self.__br.set_debug_http(debug)
        #  no sign in
        pass
    
    def search(self, query):
        br = self.__br
        q_field = urllib.urlencode({'f_first_name': query})
        url = 'http://searchresults.myspace.com/index.cfm?fuseaction=find.search&searchType=network&interesttype=&country=&searchBy=Display&%s&Submit=Find&SearchBoxID=FindAFriend' % q_field
        br.open(url)
        links_urls = []
        for link in br.links(url_regex='profile.myspace.com/index.cfm\?fuseaction=user.viewprofile'):#self.__name_regex):
            if not link.url in links_urls:
                links_urls.append(link.url)
        return links_urls

    def __strip_complete_name(self, html_match):
        match = re.search(self.__complete_name_regex, html_match)
        match = match.group()[len(self.__complete_name_prefix):-len(self.__complete_name_sufix)]
        return match

    def __strip_url(self, html_match):
        match = re.search(self.__url_regex, html_match)
        match = match.group()[len(self.__url_prefix):-len(self.__url_sufix)]
        return match

    # search for display name "name" and retrieves contact as tuples (display_name, url).
    def contacts(self, name):
        br = self.__br
        # check if name exists.
        results = self.search(name)
        if len(results) == 0:
            raise Exception('display name "%s" doesn\'t exist in MySpace' % name)
        # assume the first person that matches
        name_link = results[0]
        # retrieve the first n (20?) contacts as tuples (complete_name, twitter_url).
        resp = self.__br.open(name_link)
        cont =  resp.read()
        matches = re.findall(self.__contact_regex, cont)
        complete_names  = map(self.__strip_complete_name, matches)
        urls            = map(self.__strip_url, matches)
        return zip(complete_names, urls)


proxies_per_proto = {"http": "192.168.254.254:80",
                "https": "192.168.254.254:80"}
myspace = MySpaceBot(proxies_per_proto, False)

print 'testing:'
try:
    print '"john garofalo" contacs:'
    conts = myspace.contacts('john garofalo')
    for c in conts:
        print c
except Exception, e:
    print 'Exception' + str(e.args)
print ''
try:
    print '"tom jones" contacs:'
    conts = myspace.contacts('tom jones')
    for c in conts:
        print c
except Exception, e:
    print 'Exception' + str(e.args)
print ''



