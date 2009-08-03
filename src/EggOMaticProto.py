
import cherrypy
from cherrypy.lib.static import serve_file
import re, os, time, math, sys

from EggOMatic import EggOMatic
from Utils import rank_dist_ksim, rank_dist_osim

from PorterStemmer import PorterStemmer
        
class EggHelper:
    
    __begin_top_many_users = 1
    __end_top_many_users = 10
    # exponential step 2, 4 ,8 16
    __step_top_many_users = 2
    
    __batch_show = 10

    
    def __init__(self, debug, max_per_rank, q_types, index_url='http://127.0.0.1:8080'):
        self.__index_url = index_url
        self.__debug = debug
        self.__max_per_rank = max_per_rank
        self.__q_types = q_types
    
    def set_index_url(self, index_url):
        self.__index_url = index_url
    
    def header(self, last_tags='', last_serv='youtube', last_user='', last_q_type='all'):
        

        if last_serv == 'youtube':
            fst, snd = 'selected', ''
        elif last_serv == 'flickr':
            fst, snd = '', 'selected'
        else:
            raise Exception('bad last service for header().')
        if last_q_type == 'all':
            fst_q_type, snd_q_type = 'selected', ''
        elif last_q_type == 'all_simult':
            fst_q_type, snd_q_type = '', 'selected'
        else:
            raise Exception('bad last service for header().')
        
        out = '<center><img src="name2.png" alt="Egg-O-Matic" align="middle"/>'
        #out += '<img src="logo.jpg" alt="ChickenLogo"/>'
        out += '''
        <html>
<head>
<title>Egg-O-Matic (Web 0.2)</title>
</head>
<body>
<br/>
Faceted <i>Ranking</i> of <i>Egos</i> in Collaborative Tagging Systems (i.e. <i>Folksonomies</i>)  <br/>	
<font size=2>  Jose I. Orlicki (1)(2), J. Ignacio Alvarez-Hamelin (1), Pablo Fierens (1) </font> <BR/>
(1)<a href="http://www.itba.edu.ar"><img src="itba.png" alt="ITBA" align="center"></a>
(2)<a href="http://www.coresecurity.com"><img src="core2.gif" alt="CORE" align="center"></a> 

        '''
        out += '''<br/><TABLE border="0"
          summary=""><td><tr><th>
<form name="input" action="query"
method="get">

          <select NAME="service">
               <option %s VALUE="youtube">youtube
               <option %s VALUE="flickr">flickr
          </select>
<th>
<font size=2>Tags</font> 
<input type="text" name="tags" value="%s" size="32" maxlength="256">
          <select NAME="q_type">
               <option %s VALUE="all">all tags, any content
               <option %s VALUE="all_simult">all tags, same content
          </select>
<input type="submit" value="Query">
</form>
''' % (fst, snd, last_tags, fst_q_type, snd_q_type)
        out += '''<form name="input" action="query_user"
method="get">
<font size=2>  </font><th><tr><th>
          <select NAME="service">
               <option %s VALUE="youtube">youtube
               <option %s VALUE="flickr">flickr
          </select>


<th><font size=2>User</font> 
<input type="text" name="user" value= "%s" size="54" maxlength="256">&nbsp;
<input type="submit" value="Query">
</form><th> </TABLE><HR></center>
''' % (fst, snd, last_user)
        return out

    def end(self):
        out = '''
</body>
</html>
'''
        return out
    
    def errors(self, ranks):
        out = ''

    def cluster2url(self, cluster, service, user):
	if service == 'youtube':
		tags_url = '+'.join(cluster)
		return 'http://www.youtube.com/results?search_query=%s+%s&as=1&and_queries=%s+%s&exact_query=&or_queries=&negative_queries=&search_duration=&search_hl=&search_category_type=all&search_sort=video_avg_rating&uploaded=' % (user, tags_url, user,  tags_url)
	elif service == 'flickr':
		tags_url = '+'.join(cluster)
#		return 'http://www.flickr.com/search/?q=%s+%s' % (user, tags_url)
		return 'http://www.flickr.com/photos/%s/tags/%s' % (user, cluster[0])
    
    def __user_ranks_line(self, user_ranks, service, q_type, begin='other'):
        out = ''
        out += '<TR><TD><FONT SIZE=2> %s ' % begin
        for cluster, pagerank, pos in user_ranks:
            url_cluster = '+'.join(cluster)
            view_cluster = '_'.join(cluster)
            if self.__debug:                                
#                out += '<b>#%d</b>\t%f\t<a href="%s/query?tags=d%s&clustering=0">%s</a><br/><br/>' % (pos,pagerank, self.__index_url, url_cluster, view_cluster)
                out += '#%d\t<a href="%s/query?service=%s&tags=%s&q_type=%s">%s</a> ' % (pos,self.__index_url, service, url_cluster, q_type, view_cluster)
        return out + '</FONT>'
    
    def rank2html(self, ranks, cluster, service, q_type, eggomatic, begin, end):
        out ='''
<TABLE border="0"
          summary="">
'''        
        if q_type == self.__q_types[0]:
            rank = ranks[0]
        elif q_type == self.__q_types[1]:
            rank = ranks[1]
        else:
            raise Exception('bad query type in rank2html.')
        # partial slice
        batchs = math.ceil(float(len(rank))/self.__batch_show) 
        rank = rank[begin:end]        
        for name, pagerank, pos in rank:
            url = self.cluster2url(cluster, service, name)
            out += '<TR><TD> <FONT SIZE=4><b>#%d</b>\t<a href="%s/query_user?service=%s&user=%s">%s</a></FONT> <i><a href="%s">*</a></i>' % (pos, self.__index_url, service, name, name, url)
#           
            if len(cluster) > 1: # add individual tags rankings
                indiv_user_ranks = eggomatic.user_ranks(name, cluster, 500, False)
                out += self.__user_ranks_line(indiv_user_ranks, service, q_type, '')     
            user_ranks = eggomatic.user_ranks(name, None, 10)
            out += self.__user_ranks_line(user_ranks, service, q_type, 'other')
            out += '<TR><TR><TR><TR><TR>'
                
        out += '</TABLE>'
        out += '<p align=center>'
        for i in range(batchs):
            out += '<a href=%d ' % (i+1)
            out += ' <a href="%s/query?service=%s&tags=%s&q_type=%s&begin=%d&end=%d">%d</a> ' % (self.__index_url, service, '+'.join(cluster), q_type, i*self.__batch_show,(i+1)*self.__batch_show,i+1)
        out += '... '
        out += ' <a href="%s/query?service=%s&tags=%s&q_type=%s&begin=%d&end=%d">Next</a> ' % (self.__index_url, service, '+'.join(cluster), q_type, begin+self.__batch_show,end+self.__batch_show)
        out += '</p>'
        return out
    
    def rank2html_user(self, rank, service, user, eggomatic):
        out = ''
        rank = rank[:self.__max_per_rank]
        for cluster, pagerank, pos in rank:
            url_cluster = '+'.join(cluster)
            view_cluster = '_'.join(cluster)
            tag = cluster[0]
            tag_weight = eggomatic.tag_weight(tag)
            f_size = (7 - int(1.0 / self.__max_per_rank * 7 * pos) - 0) * tag_weight 
            if f_size <= 0:
                f_size = 0
            out += '<font size="%d"> #%d <a href="%s/query?service=%s&tags=%s&q_type=all">%s</a>\t' % (f_size, pos,self.__index_url, service, url_cluster, view_cluster)
            out += '<a href="%s">*</a></font>' % (self.cluster2url(cluster, service, user))

        return out
    
    def bad_input(self, tags=None):
        out = ''
        out += '<b>Bad input tags!</b> only alphanumeric, spaces and dashes are valid.'
        return self.header() + out + self.end()            

    def bad_input_user(self, tags):
        out = ''
        out += '<b>Bad input user!</b> only alphanumeric and dashes are valid.'
        return self.header() + out + self.end()            

    def bad_tag(self, tag, tags, service, q_type):
        out = ''
        out += 'Inexistant tag: <b>%s</b>' % tag
        return self.header(' '.join(tags), service, '', q_type) + out + self.end()            

    def bad_user(self, user, service):
        out = ''
        out += 'Inexistant user: <b>%s</b>' % user
        return self.header('', service, user) + out + self.end()            

    def cluster(self, cluster, service, q_type):
        return ''
        out = ''
        if len(cluster) == 0:
            out += 'Using all tags.'
        elif len(cluster) == 1:
            out += 'Using tag: '
        else:
            out += 'Using tags: '
        for tag in cluster:
#            out += '<a href="%s/query?tags=%s&clustering=0">%s</a> ' % (self.__index_url, tag, tag)
            if service == 'youtube':
                out += '<a href="%s/query?service=%s&tags=%s&q_type=%s">%s</a> ' % (self.__index_url, service, tag, q_type, tag)
            elif service == 'flickr':
                out += '<a href="%s/query?service=%s&tags=%s&q_type=%s">%s</a> ' % (self.__index_url, service, tag, q_type, tag)
            else:
                raise Exception('bad service in cluster().')
            #out += '<a href="%s">*</a></font>' % (self.cluster2url(, service, user))
            
        out += ''
        return out

    def cluster_users(self, cluster, service):
        out = ''
        if len(cluster) == 0:
            out += 'Rankings for user: '
        elif len(cluster) == 1:
            out += 'View '
        else:
            out += 'Using tag cluster: '
        for user in cluster:
            #out += '<a href="%s/query_user?service=%s&user=%s">%s</a> ' % (self.__index_url, service, user, user)
            if service == 'youtube':
                out += '%s\'s <i><a href="http://youtube.com/user/%s">page</a></i>.' % (user,user)
            elif service == 'flickr':
                out += '%s\'s <i><a href="http://flickr.com/photos/%s">page</a></i>.' % (user,user)
            else:
                raise Exception('bad service in cluster_users().')
            
#            out += '(<a href="%s/query_user?user=%s&clustering=0">no tag clustering</a>) ' % (self.__index_url, user)
        out += '<br><br>'
        return out

    def stats_user(self, rank, total, partial_tags, total_tags, clustering):
        out = ''
        out += ''
        if not clustering:
            out += 'User reputation results:  %d of %d tags (%d of %d users)' % ( partial_tags, total_tags, len(rank),total)
        else:
            out += 'User reputation results:  %d of %d tag clusters (%d of %d users)' % ( partial_tags, total_tags, len(rank),total)
        out += '<br><br>'
        return out

    def stats(self, ranks, total, partial_tags, total_tags, q_time, user=False):
        out = ''
        out += ''
        if not user:
            out += '<p align=right><font size=2>Ranking results:  %d  of %d users | %d of %d tags | %.3f seconds</font></p>' % (len(ranks[0]), total, partial_tags, total_tags, q_time)
        else:
            out += '<p align=right><font size=2>Ranking results:  %d of %d tags | %.3f seconds</font></p>' % (partial_tags, total_tags, q_time)
        out += ''        
        return out
            
        

    def complete_page(self, ranks, cluster, total, total_tags, service, q_type, eggomatic, q_time, begin, end):
        return self.header(' '.join(cluster), service, '', q_type) + self.cluster(cluster, service, q_type) + self.stats(ranks, total, len(cluster), total_tags, q_time) + self.rank2html(ranks, cluster, service, q_type, eggomatic, begin, end)  + self.end()

    def complete_page_user(self, rank, cluster, total, total_tags, clustering, service, q_time, eggomatic):
        return self.header('',service,cluster[0]) + self.stats(cluster, total, len(rank), total_tags, q_time, True) + self.cluster_users(cluster,service)  + self.rank2html_user(rank, service, cluster[0], eggomatic)  + self.end()


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
    __services = ['youtube','flickr']
    __q_types = ['all','all_simult']
    
    def __init__(self, datasets, compute_ranks, compute_mono_rank, build_indexes, max_per_rank=500, index_url='http://127.0.0.1:8080', debug=False, current_dir=None):
        self.__debug = debug
        self.__current_dir = current_dir
        self.__index_url = index_url
#        self.__eggomatic = EggOMatic(dataset, compute_ranks, compute_mono_rank, build_indexes)
        self.__eggomatics = map(lambda x: EggOMatic(x, compute_ranks, compute_mono_rank, build_indexes, max_per_rank), datasets)
#	self.__eggomatic = self.__eggomatics[0]
        self.__html_helper = EggHelper(self.__debug, max_per_rank, self.__q_types, self.__index_url)
        self.__html_helper.set_index_url(index_url)
        self.__max_per_rank = max_per_rank
        
        self.__stemmer = PorterStemmer()
        
    def set_index_url(self, index_url):
        self.__html_helper.set_index_url(index_url)
        
    def set_debug(self, flag):
        self.__debug = flag
        
    def index(self):
        return self.__html_helper.header() + self.__html_helper.end()
    index.exposed = True

    def __set_eggomatic(self, service):
        self.__eggomatic = None
        for db_service,eggomatic in zip(self.__services, self.__eggomatics):
            if service == db_service:
                self.__eggomatic = eggomatic
        if not eggomatic:
            raise Exception('mismatch between services available and servies loaded.')

    def query(self, service, tags, q_type, begin=0, end=10):
        self.__service = service
        self.__q_type = q_type
        if not service in self.__services or not q_type in self.__q_types:
            return self.__html_helper.bad_input()
        if tags == '':
            return self.index()
        try:
            begin = int(begin)
            if begin < 0 or begin > self.__max_per_rank:
                raise Exception()
            end = int(end)
            if end < 0 or end > self.__max_per_rank:
                raise Exception()
        except:
            return self.__html_helper.bad_input()        

        init_time = time.time()
        self.__set_eggomatic(service)
        clustering='0'
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
        else:
            correct_tags = []
            for tag in tags:
                #tag = self.__stemmer.stem(tag, 0, len(tag)-1)
                if not self.__eggomatic.good_tag(tag):
                    tag = self.__eggomatic.best_tag(tag)
                    #return self.__html_helper.bad_tag(tag, tags, service, q_type)
                correct_tags.append(tag)
            tags = correct_tags
            ranks = self.__eggomatic.rank_by_tags_fast(tags)
        cluster = tags
        return self.__html_helper.complete_page(ranks, cluster, self.__eggomatic.total_users(), self.__eggomatic.total_tags(), service, q_type, self.__eggomatic, time.time()-init_time, begin, end)
    query.exposed = True

    def query_user(self, service, user):
        self.__service = service
        clustering = '0'
        clustering = clustering == '1'
        user = user.strip() #.lower()
        match = re.search('[A-Za-z0-9\-\_]+', user)
        if len(user) == 0:
            return self.index()        
        if (not match or len(match.group()) != len(user)):
            return self.__html_helper.bad_input_user(user)
        self.__set_eggomatic(service)
        if not self.__eggomatic.good_user(user):
            return self.__html_helper.bad_user(user, service)

        init_time = time.time()
        if clustering:
            rank = self.__eggomatic.user_ranks_clustering(user)            
        else:        
            rank = self.__eggomatic.user_ranks(user, None, self.__max_per_rank, sorting=True)            
        return self.__html_helper.complete_page_user(rank, [user], self.__eggomatic.total_users(), self.__eggomatic.total_tags(), clustering, service, time.time() - init_time, self.__eggomatic)
    query_user.exposed = True



    def default(self, param):
        print 'default'
        param = param.lower()
        match = re.search('[a-z\-_]+', param)
        if not match:
            return self.__error % str(param)
        
        param = param.lower()
        tags = param.split('_')
        
        print 'default: %s' % tags
#        if len(tags) == 1:
#            rank = self.__eggomatic.rank_by_tag(tags[0])
            
        return serve_file(os.path.join(self.__current_dir + '/site', 'images', tags[0]),
                              content_type='application/jpg')
        
             
        
    default.exposed = True





def main(argv=None):
    #dataset = '../data/bug'
    #dataset = '../data/ejemplo'
    #dataset = '../data/rpoland--2000'
    #dataset = '../data/jcl5m--39370'
    #dataset = '../data/ejemplo'
    #dataset = '../data/MIX'
    #dataset = '../data/flickr_med'
    #dataset = '../data/youtube'
    
#    datasets = ['../data/yt_nd_mini', '../data/fr_nd_mini']
#    datasets = ['../data/yt', '../data/fr']
#    datasets = ['../data/yt_nd', '../data/fr_nd']

    print str(sys.argv)
    if len(sys.argv) > 1:
        do_all = bool(int(sys.argv[1]))
    else:
	raise Exception('argument missing argv[1], 0 or 1 acccording to not indexing everything or yes')

    if len(sys.argv) > 2:
        datasets = sys.argv[2]
    else:
	raise Exception('argument missing argv[2], file with list of datasets')

    if len(sys.argv) > 3:
        ip = sys.argv[3]
    else:
        ip = '127.0.0.1'
	#raise Exception('argument missing argv[2], site main url')

    datasets = filter(lambda x: len(x)>0, map(lambda x:x.strip(), open(datasets).readlines()))
    print str(datasets)
#    do_all = True

    compute_ranks = do_all
    compute_mono_rank = do_all
    build_indexes = do_all
    
    max_per_rank = 500
    debug = True
    #ip = '192.168.1.102'
    #ip = '172.17.55.150'
    #ip = '172.17.54.223'
    #ip = '127.0.0.1'
    port = 80

    index_url = 'http://%s:%d' % (ip,port)    
#    cherrypy.config.update({'server.socket_port':port, 
#                            'server.socket_host':ip})
    current_dir = os.path.dirname(os.path.abspath(__file__))
    configfile_path = current_dir + '/cherrypy.config'
    #cherrypy.config.update(configfile_path)


    #cherrypy.tree.mount(EggOMaticWeb(datasets, compute_ranks, compute_mono_rank, build_indexes, max_per_rank, index_url, debug), '/', configfile_path)

    cherrypy.quickstart(EggOMaticWeb(datasets, compute_ranks, compute_mono_rank, build_indexes, max_per_rank, index_url, debug, current_dir), '/', configfile_path)

if __name__ == '__main__':
    main()


