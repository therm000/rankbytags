

from mechanize import Browser
import time

#from mechanize_ import Browser
import urllib, urllib2
import re

#from PersistentLIFO import PersistentLIFO
#from PersistentFIFO import PersistentFIFO

class YouTubeBot:

    #__name_regex = 'href="http://profile.myspace.com/index.cfm?fuseaction=user.viewprofile&friendID=[0-9]+" linkindex='

    # use favorite authors as contacts.
    __contact_regex = 'http://www.youtube.com/profile\?user=[a-zA-Z_0-9]+'

    __complete_name_regex = 'http://www.youtube.com/profile\?user=[a-zA-Z_0-9]+'
    __complete_name_prefix = 'http://www.youtube.com/profile?user='
    __complete_name_sufix = ''

    __favorite_regex = 'http://www.youtube.com/watch\?v=[a-zA-Z_0-9\-]+'

    __favorite_regex = 'http://www.youtube.com/watch\?v=[a-zA-Z_0-9\-]+'
    __favorite_prefix = 'http://www.youtube.com/watch\?v='
    __favorite_sufix = ''

    __tag_regex = ' term=\'[a-zA-Z_0-9\-]+\'/>'

    __tag_regex = ' term=\'[a-zA-Z_0-9\-]+\'/>'
    __tag_prefix = ' term=\''
    __tag_sufix = '\'/>'

    __forb_tags = ['the', 'and', 'their', 'at', 'is', 'in', 'of', 
                   'a', 'on', 'for', 'an', 'with', 'to']    

    def __init__(self, proxies_per_proto={}, debug=False):
        self.__br = Browser()
        self.__br.set_proxies(proxies_per_proto)
        self.__br.set_debug_http(debug)
        # no respect for robots.txt
        self.__br.set_handle_robots(False)
        self.__sleep_secs = 0.0
        self.__sleep_module = 9999999
        self.__sleep_failure = 120.0
        self.__gets = 0
        #  no sign in
        # but i have a dummy user
        # user: zarasa12345@mailinator.com
        # password: zarasa123
        pass

    def set_sleep_secs(self, secs):
        self.__sleep_secs = float(secs)

    def set_sleep_module(self, iterations):
        self.__sleep_module = iterations

    def set_sleep_failure(self, secs):
        self.__sleep_failure = float(secs)        

    def __try_sleep(self):
        self.__gets += 1
        if self.__gets % self.__sleep_module == 0:
            print 'Sleeping for %f seconds, every %d GETs' % (self.__sleep_secs, self.__sleep_module)
            time.sleep(self.__sleep_secs)

    #most_viewed
    #top_rated
    #recently_featured
    #watch_on_mobile
    def seeds(self, type='most_viewed'):
        self.__try_sleep()
        resp = self.__br.open('http://gdata.youtube.com/feeds/standardfeeds/' + type)
        cont = resp.read()
        matches = re.findall(self.__contact_regex, cont)
        featured_users  = map(self.__strip_complete_name, matches)
        return featured_users

    def search(self, query):

        br = self.__br
        # check if name exists.
        try:
            print 'http://gdata.youtube.com/feeds/users/%s/favorites' % query
            self.__try_sleep()
            resp = self.__br.open('http://gdata.youtube.com/feeds/users/%s/favorites' % query)
        except Exception, e:
            if str(e) == 'HTTP Error 404: Not Found':
                return []
            else:
                raise e
        return [resp.read()]

    def __strip_complete_name(self, html_match):
        match = re.search(self.__complete_name_regex, html_match)
        match = match.group()[len(self.__complete_name_prefix):]
        return match

    def __strip_url(self, html_match):
        match = re.search(self.__favorite_regex, html_match)
        match = match.group()[len(self.__favorite_prefix)-1:]
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
            raise Exception('name "%s" doesn\'t exist in YouTube' % name)

##        # assume the name is a valid user
##        name_link = name
##        # retrieve the first n (20?) contacts as tuples (complete_name, twitter_url).
##        print 'http://gdata.youtube.com/feeds/users/%s/favorites' % name_link
##        self.__try_sleep()
##        resp = self.__br.open('http://gdata.youtube.com/feeds/users/%s/favorites' % name_link)
##        cont =  resp.read()

        cont = results[0]
        # favorite authors as contacts.
        matches = re.findall(self.__contact_regex, cont)
        complete_names  = map(self.__strip_complete_name, matches)
        # favorite videos to extract tags of relation.
        matches = re.findall(self.__favorite_regex, cont)
        favorite_videos  = map(self.__strip_url, matches)
        # remove repetitions
        aux = []
        for fav in favorite_videos:
            if not fav in aux:
                aux.append(fav)
        favorite_videos = aux
        #http://gdata.youtube.com/feeds/videos/MtwO0InjCdM
        # retrieve tags for each video
        tags_videos = []
        for fav in favorite_videos:
            print 'http://gdata.youtube.com/feeds/videos/%s' % fav
            self.__try_sleep()
            resp = self.__br.open('http://gdata.youtube.com/feeds/videos/%s' % fav)
            cont =  resp.read()
            matches = re.findall(self.__tag_regex, cont)
            tags  = map(self.__strip_tag, matches)
            tags_videos.append(tags)
        
        return zip(complete_names, tags_videos)

    def __normalize_tags(self, tags):
        #forb_regexs = ['\$[^\n\$]+\$']
        tags = map(lambda x: x.lower(), tags)        
        tags = filter(lambda x: x not in self.__forb_tags, tags)        
        return tags

    def __lifo_pop(self, stack):
        return stack.pop()

    def __fifo_pop(self, stack):
        return stack.pop(0)

    def __lifo_retrieve(self, stack, item):
        stack.append(item)

    def __fifo_retrieve(self, stack, item):
        stack = [item] + stack
        
    # harvest a sequence of (Alice, Bob, tags_in_Bobs_favorite_video_of_Alice)
    # modes are 'BFS' of 'DFS'
    def harvest(self, seeds, max_nodes=3, mode='DFS' ):

        out_file_name = '%s--%d.tagged_graph' % ('-'.join(seeds), max_nodes)
        out = open(out_file_name, 'w')
        out.close()

        failures = 0        
        if mode=='BFS':
            pop = self.__fifo_pop
            retrieve = self.__fifo_retrieve
        elif mode=='DFS':
            pop = self.__lifo_pop
            retrieve = self.__lifo_retrieve
        
        stack = []
        visited = set([])
        for seed in seeds:
            stack.append(seed)       
        n = len(stack)
        while n < max_nodes and len(stack) > 0:
            # use special pop operation
            node = pop(stack)
            print 'nodes expanded -> %d' % len(visited)
            print 'nodes in stack -> %d' % len(stack)
            print 'nodes harvested -> %d of %d' % (n,max_nodes)            
            if not node in visited:
                visited.add(node)              
            else:
                continue
            
            contacts= []
            
            try:
                contacts = self.contacts(node)
            except:
                failures += 1
                print 'FAILURE: #%d at %d people' % (failures, n)
                print '#GETs: %d' % self.__gets
#                if failures >= 100:
#                   
#                    print 'breaking at 100 failures'
#                    break
#                else:
                print 'sleep %f seconds after failure' % self.__sleep_failure
                time.sleep(self.__sleep_failure)
                retrieve(stack, node)                
                    
            contact_tags = {}
            for contact, tags in contacts:
                if contact != node:
                    print str(contact) + ': ' + str(tags)
                    if not contact in contact_tags.keys():
                        contact_tags[contact] = set([])
                    tags = self.__normalize_tags(tags)
                    contact_tags[contact] = contact_tags[contact].union(set(tags))
                    if not contact in visited and not contact in stack  \
			and len(visited)+len(stack) < max_nodes:                            
                            stack.append(contact)
                            n += 1
                            if n >= max_nodes:
                                break
                    
            # write node connections in file
            out = open(out_file_name, 'a')
            for contact, total_tags in contact_tags.iteritems():
                out.write('%s\t\t%s\t\t%s\n' % (node,contact,'|'.join(total_tags)))
            out.close()
            del contact_tags
                   
        print 'nodes expanded -> %d' % len(visited)
        print 'nodes in stack -> %d' % len(stack)
     	print 'nodes harvested -> %d' % n
        return n






proxies_per_proto = {"http": "192.168.254.254:80",
                "https": "192.168.254.254:80"}
youtube = YouTubeBot(proxies_per_proto, False)

##print 'testing:'
##try:
##    print '"johngarofalocho" contacs:'
##    conts = []
##    conts = youtube.contacts('johngarofalocho')
##    for c in conts:
##        print c
##except Exception, e:
##    print 'Exception: ' + str(e)
##print ''
##try:
##    print '"psychedelicum" contacs:'
##    conts = []
##    conts = youtube.contacts('psychedelicum')
##    for c in conts:
##        print c
##except Exception, e:
##    print 'Exception: ' + str(e)
##print ''



f = open('debug-%s.txt' % time.ctime().replace(' ', '_').replace(':','-'), 'w')

f.write('%s\n' % time.ctime())
# top of youtube.com
top_rated = youtube.seeds('top_rated')
print top_rated
#one_top_rated = top_rated[2:3]
one_top_rated = ['jcl5m'] #['catlovercaro']#['DarthAbercrombie'] #['jcl5m']
print 'choosing from top_rated --> %s' % str(one_top_rated)
#most_viewed = youtube.seeds('most_viewed')
#print most_viewed
#most_viewed = most_viewed[3:4]
#print 'choosing from most_viewed --> %s' % str(most_viewed)
#recently_featured = youtube.seeds('recently_featured')
#print recently_featured
#recently_featured = recently_featured[5:6]
#print 'choosing from recently_featured --> %s' % str(recently_featured)

# 1000 nodes each, and 1 seconds between queries
#sleep_module = 60
#sleep_module_secs = 0
#youtube.set_sleep_secs(sleep_module_secs)
#youtube.set_sleep_module(sleep_module)

sleep_failure = 20
youtube.set_sleep_failure(sleep_failure)
desired_total = 600
crawl_order = 'BFS' # 'DFS'
f.write('desired total: %d\n\n' % desired_total )

f.write('total = youtube.harvest(top_rated, desired_total) seed: %s\n' % str(one_top_rated))
f.write('choosed from top rated: %s\n' % str(top_rated))
total = youtube.harvest(one_top_rated, desired_total)
f.write('harvested: %d\n' % total)
f.write('%s\n' % time.ctime())

#f.write('total = youtube.harvest(most_viewed, desired_total) seed: %s\n' % str(most_viewed))
#total = youtube.harvest(most_viewed, desired_total)
#f.write('harvested: %d\n' % total)
#f.write('%s\n' % time.ctime())

#f.write('total = youtube.harvest(recently_featured, desired_total) seed: %s\n' % str(recently_featured))
#total = youtube.harvest(recently_featured, desired_total)
#f.write('harvested: %d\n' % total)
#f.write('%s\n' % time.ctime())

f.close

# TODO

