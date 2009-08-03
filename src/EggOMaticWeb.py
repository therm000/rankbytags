import cherrypy
import re

from EggOMatic import EggOMatic
from Utils import rank_dist_ksim, rank_dist_osim

        
class EggHelper:
    
    __begin_top_many_users = 1
    __end_top_many_users = 10
    # exponential step 2, 4 ,8 16
    __step_top_many_users = 2

    
    def __init__(self, debug, max_per_rank):
        self.__index_url = 'http://127.0.0.1:8080'
        self.__debug = debug
	self.__max_per_rank = max_per_rank
    
    def set_index_url(self, index_url):
        self.__index_url = index_url
    
    def header(self):
        #<img src="logo.jpg" alt="ChickenLogo">
        out = '''
        <html>
<head>
<title>Egg-O-Matic (Web 0.2)</title>
</head>
<body>
Egg-O-Matic <br/><br/>
        '''
        out += '''<form name="input" action="query"
method="get">
YouTube tags: 
<input type="text" name="tags" size="64" maxlength="256">
<input type="submit" value="Query">
</form>
'''
        out += '''<form name="input" action="query_user"
method="get">
YouTube channel: 
<input type="text" name="user" size="64" maxlength="256">
<input type="submit" value="Query">
</form> <br/>
'''
        return out

    def end(self):
        out = '''
</body>
</html>
'''
        return out
    
    def errors(self, ranks):
        out = ''
    
    def rank2html(self, ranks):
        out ='''
<TABLE border="1"
          summary="">
<TR> <TD> <b>OFFLINE1 (AND graph)</b> <TD> <b>MONO (filter 1 rank)</b> <TD> <b>ONLINE1 (PR product)</b><TD> <b>ONLINE3 (pos. sum)</b><TD> <b>ONLINE4 (asim. filter and)</b> <TD> <b>OFFLINE2 (OR graph + intersec)</b> 
'''        
        max_len = max(map(len,ranks))
        for rank in ranks:
            for i in range(len(rank), max_len):
                rank.append(('', 0.0, i+1))
        for i in range(min(max_len,self.__max_per_rank)):
            name0, pagerank0, pos0 = ranks[0][i]
            name_mono, pagerank_mono, pos_mono = ranks[1][i]
            name1, pagerank1, pos1 = ranks[2][i]
            name2, pagerank2, pos2 = ranks[3][i]
            name3, pagerank3, pos3 = ranks[4][i]
            name4, pagerank4, pos4 = ranks[5][i]
            name5, pagerank5, pos5 = ranks[6][i]
            if self.__debug:
                out += '<TR><TD> <b>#%d</b>\t%.3f\t<a href="%s/query_user?user=%s">%s</a> <i>(<a href="http://youtube.com/user/%s">c</a>)</i>' % (pos0, pagerank0, self.__index_url, name0, name0, name0)                
                out += '<TD> <b>#%d</b>\t%.3f\t<a href="%s/query_user?user=%s">%s</a> <i>(<a href="http://youtube.com/user/%s">c</a>)</i>' % (pos_mono, pagerank_mono, self.__index_url, name_mono, name_mono, name_mono)
                out += '<TD> <b>#%d</b>\t%.3f\t<a href="%s/query_user?user=%s">%s</a> <i>(<a href="http://youtube.com/user/%s">c</a>)</i>' % (pos1, pagerank1, self.__index_url, name1, name1, name1)
                #out += '<TD> <b>#%d</b>\t%.3f\t<a href="%s/query_user?user=%s">%s</a> <i>(<a href="http://youtube.com/user/%s">c</a>)</i>' % (pos2, pagerank2, self.__index_url, name2, name2, name2)
                out += '<TD> <b>#%d</b>\t%.3f\t<a href="%s/query_user?user=%s">%s</a> <i>(<a href="http://youtube.com/user/%s">c</a>)</i>' % (pos3, pagerank3, self.__index_url, name3, name3, name3)
                out += '<TD> <b>#%d</b>\t%.3f\t<a href="%s/query_user?user=%s">%s</a> <i>(<a href="http://youtube.com/user/%s">c</a>)</i>' % (pos4, pagerank4, self.__index_url, name4, name4, name4)
                out += '<TD> <b>#%d</b>\t%.3f\t<a href="%s/query_user?user=%s">%s</a> <i>(<a href="http://youtube.com/user/%s">c</a>)</i>' % (pos5, pagerank5, self.__index_url, name5, name5, name5)
            else:
                out += '<b>#%d</b>\t<a href="%s/query_user?user=%s">%s</a> <i>(<a href="http://youtube.com/user/%s">channel</a>)</i><br/><br/>' % (pos, self.__index_url, name, name, name)
        out += '</TABLE>'
        return out
    
    def rank2html_user(self, rank):
        out = ''
        for cluster, pagerank, pos in rank:
            url_cluster = '+'.join(cluster)
            view_cluster = '_'.join(cluster)
            if self.__debug:                                
#                out += '<b>#%d</b>\t%f\t<a href="%s/query?tags=d%s&clustering=0">%s</a><br/><br/>' % (pos,pagerank, self.__index_url, url_cluster, view_cluster)
                out += '<b>#%d</b>\t%f\t<a href="%s/query?tags=%s">%s</a><br/><br/>' % (pos,pagerank, self.__index_url, url_cluster, view_cluster)

            else:                
#                out += '<b>#%d</b>\t<a href="%s/query?tags=%s&clustering=0">%s</a><br/><br/>' % (pos,self.__index_url,url_cluster, view_cluster)
                out += '<b>#%d</b>\t<a href="%s/query?tags=%s">%s</a><br/><br/>' % (pos,self.__index_url,url_cluster, view_cluster)
        return out
    
    def bad_input(self, tags):
        out = ''
        out += 'Bad input: only [a-z0-9\- ]+ is valid.'
        return self.header() + out + self.end()            

    def bad_input_user(self, tags):
        out = ''
        out += 'Bad input! only [A-Za-z0-9\-]+ is valid.'
        return self.header() + out + self.end()            

    def bad_tag(self, tag):
        out = ''
        out += 'Inexistant tag: <b>%s</b>' % tag
        return self.header() + out + self.end()            

    def bad_user(self, user):
        out = ''
        out += 'Inexistant user: <b>%s</b>' % user
        return self.header() + out + self.end()            

    def cluster(self, cluster):
        out = ''
        if len(cluster) == 0:
            out += 'Using all tags.'
        elif len(cluster) == 1:
            out += 'Using tag: '
        else:
            out += 'Using tag cluster: '
        for tag in cluster:
#            out += '<a href="%s/query?tags=%s&clustering=0">%s</a> ' % (self.__index_url, tag, tag)
            out += '<a href="%s/query?tags=%s">%s</a> ' % (self.__index_url, tag, tag)
        out += '<br><br>'
        return out

    def cluster_users(self, cluster):
        out = ''
        if len(cluster) == 0:
            out += 'Ranking for user: '
        elif len(cluster) == 1:
            out += 'Ranking for user: '
        else:
            out += 'Using tag cluster: '
        for user in cluster:
            out += '<a href="%s/query_user?user=%s">%s</a> ' % (self.__index_url, user, user)
            out += '<i>(<a href="http://youtube.com/user/%s">channel</a>)</i>' % (user)
#            out += '(<a href="%s/query_user?user=%s&clustering=0">no tag clustering</a>) ' % (self.__index_url, user)
        out += '<br><br>'
        return out

    def stats_user(self, rank, total, partial_tags, total_tags, clustering):
        out = ''
        out += ''
        if not clustering:
            out += 'Channel reputation results:  %d of %d tags (%d of %d channels)' % ( partial_tags, total_tags, len(rank),total)
        else:
            out += 'Channel reputation results:  %d of %d tag clusters (%d of %d channels)' % ( partial_tags, total_tags, len(rank),total)
        out += '<br><br>'
        return out

    def stats(self, ranks, total, partial_tags, total_tags, onlines=[1,2,4,5], dists=['osim', 'ksim']):
        out = ''
        out += ''
        out += 'Channel reputation results:  %d total channels (%d of %d tags)' % (total, partial_tags, total_tags)
        out +='''
<TABLE border="1"
          summary="">
<TR> <TD> <b>OFFLINE1 (AND graph)</b> <TD> <b>MONO (filter 1 rank)</b> <TD> <b>ONLINE1 (PR product)</b><TD> <b>ONLINE3 (pos. sum)</b><TD> <b>ONLINE4 (asim. filter and)</b> <TD> <b>OFFLINE2 (OR graph + intersec)</b> 
'''        
        
        out += '<TR><TD>Matching: %d' % len(ranks[0])
        out += '<TD>Matching: %d' % len(ranks[1])
        out += '<TD>Matching: %d' % len(ranks[2])
        out += '<TD>Matching: %d' % len(ranks[4])
        out += '<TD>Matching: %d' % len(ranks[5])
        out += '<TD>Matching: %d' % len(ranks[6])

        out += '<TR><TD><b>EXPERIMENT'
        out += '<TD><b>COMPARING'
        out += '<TD><b>WITH'
        out += '<TD><b>OFFLINE1'
        out += '<TD><b>filter AND graph'
        out += '<TD>'


        for top_many_users in [self.__step_top_many_users**i for i in range(self.__begin_top_many_users,self.__end_top_many_users)]:
            out += '<TR><TD> OSim | KSim'        
            offline1 = ranks[0]
            for online in onlines:
                out += '<TD>' #0.000 | 0.000'
                for dist in dists:
                    error, info_val = eval('rank_dist_%s(offline1,ranks[online], top_many_users)' % dist)
                    if info_val >= 0:
                        out += ' %f |' % error
                    else:
                        out += ' NOTHING |'
                out = out[:-2]                            
            out += '<TD> TOP: %d' % top_many_users

        out += '<TR><TD><b>EXPERIMENT'
        out += '<TD><b>COMPARING'
        out += '<TD><b>WITH'
        out += '<TD><b>OFFLINE2'
        out += '<TD><b>filter OR graph'
        out += '<TD><b>and then intersec'

        for top_many_users in [self.__step_top_many_users**i for i in range(self.__begin_top_many_users,self.__end_top_many_users)]:
            out += '<TR><TD> TOP: %d' % top_many_users
            offline2 = ranks[6]
            for online in onlines:
                out += '<TD>' #0.000 | 0.000'
                for dist in dists:
                    error, info_val = eval('rank_dist_%s(offline2,ranks[online],top_many_users)' % dist)
                    if info_val >= 0:
                        out += ' %f |' % error
                    else:
                        out += ' NOTHING |'
                out = out[:-2]            
            out += '<TD> OSim | KSim'

        
        out += '</TABLE>'
        out += '<br>'        
        return out
            
        

    def complete_page(self, ranks, cluster, total, total_tags):
        return self.header() + self.cluster(cluster) + self.stats(ranks, total, len(cluster), total_tags) + self.rank2html(ranks)  + self.end()

    def complete_page_user(self, rank, cluster, total, total_tags, clustering):
        return self.header() + self.cluster_users(cluster) + self.stats_user(cluster, total, len(rank), total_tags, clustering) + self.rank2html_user(rank)  + self.end()


    def choose_cluster_page(self, clusters, total_users, total_tags):
        out = ''
        out += self.header()
        out += 'Disambiguate your query, choose a tag cluster: <br><br>'
        for cluster in clusters:
            cluster = list(cluster)
            cluster.sort()
            url_cluster = '+'.join(cluster)
            view_cluster = ' '.join(cluster)
            out += '  <a href="%s/query?tags=%s">%s</a> <br><br>' % (self.__index_url, url_cluster, view_cluster)
        return out




class EggOMaticWeb(object):
    
    __error = 'ERROR: bad URL, clean your nose -> %s'
    
    def __init__(self, dataset, compute_ranks, compute_mono_rank, build_indexes, max_per_rank=100, index_url='http://127.0.0.1:8080', debug=False):
        self.__debug = debug
        self.__index_url = index_url
        self.__eggomatic = EggOMatic(dataset, compute_ranks, compute_mono_rank, build_indexes)
        self.__html_helper = EggHelper(self.__debug, max_per_rank)
        self.__html_helper.set_index_url(index_url)
        self.__max_per_rank = max_per_rank
        
    def set_index_url(self, index_url):
        self.__html_helper.set_index_url(index_url)
        
    def set_debug(self, flag):
        self.__debug = flag
        
    def index(self):
        return self.__html_helper.header() + self.__html_helper.end()
    index.exposed = True

    def query(self, tags, clustering='0'):
        clustering = clustering == '1'                
        tags = tags.strip().lower()
        match = re.search('[a-z0-9\- ]+', tags)
        if len(tags) > 0 and (not match or len(match.group()) != len(tags)):
            return self.__html_helper.bad_input(tags)
        tags = map(lambda x:x.strip(),tags.split(' '))
        cluster, rank = [], []
        print 'TAGS: %s' % tags
        if not tags or len(tags) == 0 or (len(tags)==1 and tags[0]==''):
            rank = self.__eggomatic.rank_by_tag('')
        elif len(tags) > 1:
            for tag in tags:
                if not self.__eggomatic.good_tag(tag):
                    return self.__html_helper.bad_tag(tag)
            ranks = self.__eggomatic.rank_by_tags(tags)
            for tag in tags:
                if self.__eggomatic.good_tag(tag):
                    cluster.append(tag)
        else: # len(tags) == 1:
            if not self.__eggomatic.good_tag(tags[0]):
                return self.__html_helper.bad_tag(tags[0])
            elif self.__eggomatic.has_bigger_cluster(tags[0]):
                cluster_number = 0
                if clustering:
                    if not self.__eggomatic.has_many_clusters(tags[0]):
                        cluster = self.__eggomatic.clusters(tags[0])[0]
                    else:
                        clusters = self.__eggomatic.clusters(tags[0])
                        return self.__html_helper.choose_cluster_page(clusters, self.__eggomatic.total_users(), self.__eggomatic.total_tags())
                else:
                    cluster = [tags[0]]
                ranks = self.__eggomatic.rank_by_tag(tags[0], clustering, cluster_number)
            else:
                cluster = [tags[0]]
                ranks = self.__eggomatic.rank_by_tag(tags[0])
                # TODO ask if has more than one cluster.
#        else:
#            return self.__html_helper.header() + self.__html_helper.end()
        cluster = list(cluster)
        cluster.sort()
        return self.__html_helper.complete_page(ranks, cluster, self.__eggomatic.total_users(), self.__eggomatic.total_tags())
    query.exposed = True

    def query_user(self, user, clustering='0'):
        
        clustering = clustering == '1'
        user = user.strip() #.lower()
        match = re.search('[A-Za-z0-9\-]+', user)
        if len(user) == 0:
            return self.index()        
        if (not match or len(match.group()) != len(user)):
            return self.__html_helper.bad_input_user(user)
        if not self.__eggomatic.good_user(user):
            return self.__html_helper.bad_user(user)
        
        if clustering:
            rank = self.__eggomatic.user_ranks_clustering(user)            
        else:        
            rank = self.__eggomatic.user_ranks(user)            
        return self.__html_helper.complete_page_user(rank, [user], self.__eggomatic.total_users(), self.__eggomatic.total_tags(), clustering)
    query_user.exposed = True



    def default(self, param):
        print 'default'
        param = param.lower()
        match = re.search('[a-z\-_]+', param)
        if not match:
            return self.__error % str(param)
        
        param = param.lower()
        tags = param.split('_')
        
        if len(tags) == 1:
            rank = self.__eggomatic.rank_by_tag(tags[0])
        
             
        
    default.exposed = True




if __name__ == '__main__':

    #dataset = '../data/bug'
    #dataset = '../data/ejemplo'
    #dataset = '../data/rpoland--2000'
    #dataset = '../data/jcl5m--39370'
    #dataset = '../data/ejemplo'
    #dataset = '../data/MIX'
    #dataset = '../data/flickr_med'
    dataset = '../data/youtube'
    
    # DFS
    #dataset = '../data/jcl5m--593'
    # BFS
    #dataset = '../data/jcl5m--600'

    compute_ranks = False
    compute_mono_rank = True
    build_indexes = True
    max_per_rank = 500
    debug = True
    #ip = '192.168.1.102'
    #ip = '172.17.55.150'
    #ip = '172.17.54.223'
    ip = '127.0.0.1'
    port = 8080

    index_url = 'http://%s:%d' % (ip,port)    
    cherrypy.config.update({'server.socket_port':port, 
                            'server.socket_host':ip})


    cherrypy.quickstart(EggOMaticWeb(dataset, compute_ranks, compute_mono_rank, build_indexes, max_per_rank, index_url, debug))

