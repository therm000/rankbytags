

from mechanize import Browser
import time

#from mechanize_ import Browser
import urllib, urllib2
import re

from PersistentFIFO import PersistentFIFO

class FlickrBot:

    # use favorite authors as contacts.
    __url = 'http://www.flickr.com'

    __favorites_url = 'http://www.flickr.com/photos/%s/favorites'

    __favorite_regex = '/photos/[a-zA-Z_0-9@]+/[0-9]+/'
    __favorite_prefix = ''
    __favorite_sufix = ''

    __contact_regex = __favorite_regex

    __complete_name_regex = __contact_regex
    __complete_name_prefix ='/photos/' 
    __complete_name_sufix = '/'

    __tag_regex = '/photos/tags/[a-zA-Z_0-9\-]+/'

    __tag_prefix = '/photos/tags/'
    __tag_sufix = '/'

    __forb_tags = ['the', 'and', 'their', 'at', 'is', 'in', 'of', 'a', 'on', 'for', 'an', 'with']    

    def __init__(self, proxies_per_proto={}, debug=False):
        self.__br = Browser()
        self.__br.set_proxies(proxies_per_proto)
        self.__br.set_debug_http(debug)
        # no respect for robots.txt
        self.__br.set_handle_robots(False)
        self.__sleep_secs = 0
        self.__sleep_module = 1
        self.__gets = 0
        #  no sign in
        # but i have a dummy user
        # user: zarasa12345@mailinator.com
        # password: zarasa123
        pass

    def set_sleep_secs(self, secs):
        self.__sleep_secs = secs

    def set_sleep_module(self, iterations):
        self.__sleep_module = iterations

    def __try_sleep(self):
        self.__gets += 1
        if self.__gets % self.__sleep_module == 0:
            print 'Sleeping for %f seconds, every %d GETs' % (self.__sleep_secs, self.__sleep_module)
            time.sleep(self.__sleep_secs)

    #most_viewed
    #top_rated
    #recently_featured
    #watch_on_mobile
    def seeds(self):
        self.__try_sleep()
        resp = self.__br.open('http://www.flickr.com/')        
        cont = resp.read()
        matches = re.findall(self.__contact_regex, cont)
        users  = map(self.__strip_complete_name, matches)
        return users

    def search(self, query):

        br = self.__br
        # check if name exists.
        try:
            url = 'http://www.flickr.com/photos/%s/favorites/' % query
            print url            
            self.__try_sleep()
            resp = self.__br.open(url)
            cont =  resp.read()
            if not 'favorites' in cont:
                return []
        except Exception, e:
            if str(e) == 'HTTP Error 404: Not Found':
                return []
            else:
                raise e
        return [cont]

    def __strip_complete_name(self, html_match):
        return html_match.split('/')[2]

    def __strip_url(self, html_match):
        match = re.search(self.__favorite_regex, html_match)
        match = match.group()[len(self.__favorite_prefix):]
        return match

    def __strip_tag(self, html_match):
        match = re.search(self.__tag_regex, html_match)
        match = match.group()[len(self.__tag_prefix):-len(self.__tag_sufix)]
        return match

    # search for display name "name" and retrieves contact as tuples (display_name, url).
    # precondition: self.exists(user)
    def contacts(self, name):
        br = self.__br
                # check if name exists.
        results = self.search(name)
        if len(results) == 0:
            raise Exception('user "%s" doesn\'t exist in Flickr' % name)

##        # assume the name is a valid user
##        name_link = name
##        # retrieve the first n (20?) contacts as tuples (complete_name, twitter_url).
##        print self.__favorites_url % name_link
##        self.__try_sleep()
##        resp = self.__br.open(self.__favorites_url % name_link)
##        cont =  resp.read()

        cont = results[0]
        
        # favorite videos to extract tags of relation.
        matches = re.findall(self.__favorite_regex, cont)
                # remove repetitions
        favorite_videos  = list(set(matches))
        # favorite authors as contacts.
        complete_names = map(lambda x: x.split('/')[2], favorite_videos)

        # retrieve tags for each photo
        tags_videos = []
        for fav in favorite_videos:
            url = self.__url + fav
            print url
            self.__try_sleep()
            resp = self.__br.open(url)
            cont =  resp.read()
            matches = re.findall(self.__tag_regex, cont)
            tags  = map(self.__strip_tag, matches)
            # uniques
            tags = list(set(tags))
            tags_videos.append(tags)
        
        return zip(complete_names, tags_videos)

    def __normalize_tags(self, tags):
        #forb_regexs = ['\$[^\n\$]+\$']
        tags = map(lambda x: x.lower(), tags)
        tags = filter(lambda x: x not in self.__forb_tags, tags)
        return tags

    # harvest a sequence of (Alice, Bob, tags_in_Bobs_favorite_video_of_Alice)
    def harvest(self, seeds, max_nodes=3 ):

        out_file_name = '%s--%d.tagged_graph' % ('-'.join(seeds), max_nodes)
        out = open(out_file_name, 'w')
        out.close()

        failures = 0        
        stack = PersistentFIFO(out_file_name)
        visited = PersistentFIFO(out_file_name + '.visited')
        for seed in seeds:
            stack.push(seed)        
        n = stack.size()
        while n < max_nodes and stack.size() > 0:
            node = stack.pop()
            print 'nodes expanded -> %d' % visited.size()
            print 'nodes in stack -> %d' % stack.size()
            print 'nodes harvested -> %d of %d' % (n,max_nodes)            
            if not visited.has(node):
                visited.push(node)              
            else:
                continue
            
            contacts= []
            
            try:
                contacts = self.contacts(node)
            except:
                failures += 1
                print 'FAILURE: #%d at %d people' % (failures, n)
                if failures >= 100:
                   
                    print 'breaking at 100 failures'
                    break
                else:
                    print 'sleep 60 seconds after failure'
                    time.sleep(60)
                    stack.push(node)
                    
            contact_tags = {}
            for contact, tags in contacts:
                if contact != node:
                    print str(contact) + ': ' + str(tags)
                    if not contact in contact_tags.keys():
                        contact_tags[contact] = set([])
                    tags = self.__normalize_tags(tags)
                    contact_tags[contact] = contact_tags[contact].union(set(tags))
                    if not visited.has(contact) and not stack.has(contact)  \
			and visited.size()+stack.size() < max_nodes:                            
                            stack.push(contact)
                            n += 1
                            if n >= max_nodes:
                                break
                    
            # write node connections in file
            out = open(out_file_name, 'a')
            for contact, total_tags in contact_tags.iteritems():
                out.write('%s\t\t%s\t\t%s\n' % (node,contact,'|'.join(total_tags)))
            out.close()
            del contact_tags
                   
        print 'nodes expanded -> %d' % visited.size()
        print 'nodes in stack -> %d' % stack.size()
     	print 'nodes harvested -> %d' % n
        return n






proxies_per_proto = {"http": "192.168.254.254:80",
                "https": "192.168.254.254:80"}
flickr = FlickrBot(proxies_per_proto, False)

#print 'testing:'
#try:
#    user = 'johngarofalo'
#    print '"%s" contacs:' % user
#    conts = []
#    conts = flickr.contacts(user)
#    for c in conts:
#        print c
#except Exception, e:
#    print 'Exception: ' + str(e)
#print ''
#try:
#    user = 'jam343'
#    print '"%s" contacs:' % user
#    conts = []
#    conts = flickr.contacts(user)
#    for c in conts:
#        print c
#except Exception, e:
#    print 'Exception: ' + str(e)
#print ''



f = open('debug-%s.txt' % time.ctime().replace(' ', '_').replace(':','-'), 'w')

f.write('%s\n' % time.ctime())
# featured of flickr.com
#featured_user = flickr.seeds()
featured_user = ['pmorgan']
print featured_user
print 'choosing from featured_user --> %s' % str(featured_user)

# 1000 nodes each, and 1 seconds between queries
sleep_module = 10
flickr.set_sleep_secs(float(sleep_module)/1.3)
flickr.set_sleep_module(sleep_module)
desired_total = 1000000
f.write('desired total: %d\n\n' % desired_total )

f.write('total = flickr.harvest(top_rated, desired_total) seed: %s\n' % str(featured_user))
total = flickr.harvest(featured_user, desired_total)
f.write('harvested: %d\n' % total)
f.write('%s\n' % time.ctime())

f.close

# TODO

