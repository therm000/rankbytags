
import pickle, re, copy

from ExtractTags import Tags
from pagerank import PageRank
from RankByTags import RankerByTags, TagBooleanFormula, TagBooleanConjunction, TagBooleanAtom
from Utils import and_rank, and_rank2, and_rank3, and_rank4, and_rank6, and_rank0_gold1, and_rank5_gold2, snd_cmp

def add_pos(rank):
    return [(name,pagerank,pos) for (name, pagerank), pos in zip(rank, range(1,len(rank)+1))] 

class EggOUserTagranksDict:
    
    def __init__(self, dataset):
        self.__dataset = dataset
        self.__len = len(open(self.__dataset + '.tagged_graph.ranks/all.users').readlines())

    def __contains__(self, user):
        try:
            f = open(self.__dataset + '.tagged_graph.ranks/%s.user.ranks' % user)
            return True
        except:
            return False
        
        
        
    def __getitem__(self, user, max=-1):
        f = open(self.__dataset + '.tagged_graph.ranks/%s.user.ranks' % user)
        lines = []
        for i in range(max):
            lines.append(f.readline())
        f.close()
        return map(lambda l: tuple(l.strip().split(' ')), filter(lambda x: len(x.strip())>0, lines))

    def __len__(self):
        return self.__len

class EggOTagUserrankDict:
    
    def __init__(self, dataset):
        self.__dataset = dataset

    def __contains__(self, tag):
        try:
            f = open(self.__dataset + '.tagged_graph.ranks/%s.graph.rank' % tag)
            return True
        except:
            return False
        
    def __getitem__(self, tag):
        f = open(self.__dataset + '.tagged_graph.ranks/%s.graph.rank' % tag)
        lines = f.readlines()
        f.close()
        return add_pos(map(lambda l: (l.strip().split(' ')[0],float(l.strip().split(' ')[1])), lines))

class EggOTagUserDict:
    
    def __init__(self, dataset):
        self.__dataset = dataset

    def __contains__(self, tag):
        try:
            f = open(self.__dataset + '.tagged_graph.ranks/%s.graph.rank' % tag)
            return True
        except:
            return False
        
    def __getitem__(self, tag):
        f = open(self.__dataset + '.tagged_graph.ranks/%s.graph.rank' % tag)
        lines = f.readlines()
        f.close()
        return set(map(lambda l: l.strip().split(' ')[0], lines))


class EggOMatic:
    
    def __build_map_user_tags(self):
        
        return EggOUserTagranksDict(self.__dataset)
        
#        map = {}
#
#        filename = self.__dataset + '.tagged_graph'
#        f = open(filename, 'r')
#        lines = f.readlines()
#        f.close()        
#        total_tags = []
#        pairs = 0
#        
#        i = 0
#        for line in lines:
#            if i % 10000 == 0:
#                print '%d lines read of %d'%(i,len(lines))
#            i += 1
#            cols = line.split('\t\t')
#            if len(cols) < 3:
#                continue
#            src = cols[0]
#            dst = cols[1]
#            cols[2] = cols[2].strip().lower()
#            tags = cols[2].split('|')
#                        
#            if not src in map:
#                map[src] = copy.deepcopy(tags)
#            else:
#                map[src] += copy.deepcopy(tags)
#
#            if not dst in map:
#                map[dst] = tags
#            else:
#                map[dst] += tags
#                
#            total_tags += tags
#        return map
    
    def __build_map_tag_users(self):
        
        return EggOTagUserDict(self.__dataset)
                
#        map = {}
#        i = 0        
#        for tag, userrank in self.__tag_userrank.iteritems():
#            if i % 1000 == 0:
#                print '%d users read of %d'%(i,len(self.__map_user_tags.keys()))
#            i += 1
#            #print 'user: %s  tags: %s' % (user,tags)
#            users = map(lambda x:x[0], userrank)
#            map[tag] = set(users)
#        return map

    
    def __build_map_tag_userrank(self):
 
        #return self.__load_obj('.tagged_graph.all_tags_ranks')
        return EggOTagUserrankDict(self.__dataset)       
        

    def __read_rank(self):
        return self.__map_tag_userrank['']
        
#        f = open(self.__dataset+'.tagged_graph-.graph.rank', 'r')
#        lines = f.readlines()
#        f.close()
#        return [(l.strip().split(' ')[0],float(l.strip().split(' ')[1])) for l in lines]

    def __read_tags(self):
        f = open(self.__dataset+ '.tagged_graph.ranks/all.tags', 'r')
        lines = f.readlines()
        f.close()
        return map(lambda line:line.strip().split(' ')[0], lines)

    def __read_clusters(self, clust_limit=5):
        clusters = list(self.__tags)
        return clusters

    def __build_map_tag_clusters(self):
        
        map = {}
        map[''] = ['']
        
        for tag in self.__tags:
            map[tag] = [tag]
            
        return map
        

    
    def __dump_obj(self, extension, obj):
        filename = self.__dataset + extension
        f = open(filename, 'w')
        pickle.dump(obj, f)
        f.close()
    
    def __load_obj(self, extension):
        filename = self.__dataset + extension
        f = open(filename, 'r')
        obj = pickle.load(f)
        f.close()
        return obj

    def __build_user_index(self):
        filename = self.__dataset + '.tagged_graph'
        tags_filename = filename + '.ranks/all.tags'
        f = open(tags_filename)
        lines = f.readlines()
        f.close()
        self.__users = set([])
        for line in lines:
                if line.strip() == '':
                    continue
                tag = line.strip().split(' ')[0]
                if len(tag) >= 64:
                    continue
                try: # some tags may be missing if we only rank top_tags
                    u_lines = open(filename + '.ranks/%s.graph.rank' % tag)
                    users = map(lambda line: line.strip().split(' ')[0], u_lines)
                    for user, pos in zip(users,range(1,len(users)+1)):
                        u_file = open(filename + '.ranks/%s.user.ranks' % user, 'aw')
                        u_file.write('%s %d\n' % (tag,pos))
                        u_file.close()
                        self.__users.add(user)
                except:
                    pass
        # sort user better ranks by position.
        users_file = open(filename + '.ranks/all.users','w')
        for user in self.__users:
            lines = open(filename + '.ranks/%s.user.ranks' % user).readlines()
            user_ranks = map(lambda x: tuple(x.strip().split(' ')), filter(lambda x:len(x.strip())>0, lines))
            user_ranks = map(lambda (tag,pos): (tag,int(pos)), user_ranks)
            user_ranks.sort(snd_cmp)
            u_file = open(filename + '.ranks/%s.user.ranks' % user, 'w')
            for tag, pos in user_ranks:
                u_file.write('%s %d\n' % (tag,pos))
            u_file.close()
            users_file.write('%s\n' % user)
        users_file.close()
    
    def __init__(self, dataset, compute_ranks=True, compute_mono_rank=False, build_index=False, max_per_rank=10000000000, top_tags=None):
        
        self.__max_per_rank = max_per_rank        
        self.__dataset = dataset
        self.__ranker = RankerByTags()
        self.__ranker.load(dataset + '.tagged_graph')
        self.__compute_ranks = compute_ranks
        self.__compute_mono_rank = compute_mono_rank

        filename = dataset + '.tagged_graph'            
        if self.__compute_ranks or self.__compute_mono_rank:
            self.__ranker.all_ranks(filename, compute_ranks, compute_mono_rank, top_tags)        
            self.__build_user_index()
    

        print 'loading map tag userrank'
        self.__map_tag_userrank = self.__build_map_tag_userrank()
        print 'loading rank'
        self.__rank = self.__read_rank()
        print 'loading tags'
        self.__tags = self.__read_tags()
        print 'loading map tag users'
        self.__map_tag_users = self.__build_map_tag_users()            
        print 'loading map user tags'
        self.__map_user_tags = self.__build_map_user_tags()            


        if build_index:
            
            
#            print 'saving pickles'
#            print 'saving tag userrank'
#            self.__dump_obj('.eggomatic_map_tag_userrank', self.__map_tag_userrank)
#            print 'saving rank'
#            self.__dump_obj('.eggomatic_rank', self.__rank)
#            print 'saving tags'
#            self.__dump_obj('.eggomatic_tags', self.__tags)
#            print 'saving map tag users'
#            self.__dump_obj('.eggomatic_map_tag_users', self.__map_tag_users)
#            print 'saving map user tags'
#            self.__dump_obj('.tagged_graph.ranks/eggomatic_map.user_tags', self.__map_user_tags)
            pass
        
        else: # used pickled objects

#            print 'loading pickles'
#            print 'loading map user tags'
#            self.__map_user_tags = self.__load_obj('.tagged_graph.ranks/eggomatic_map.user_tags')
            pass
        
        print 'finish EggOMatic initialization.'
        
    def good_tag(self, tag):
        return tag in self.__map_tag_userrank
        #return tag in self.__tags
        
    def best_tag(self, tag):
        return self.__ranker.best_tag(tag)
        
    def tag_weight(self, tag):
        return self.__ranker.tag_weight(tag)
        
    def has_bigger_cluster(self, tag):       
        return False 
#        for cluster in self.__map_tag_clusters[tag]:
#            if len(cluster) > 1:
#                return True
#        return False
        
    def has_many_clusters(self, tag):        
        return len(self.__map_tag_clusters[tag]) > 1
        
    def clusters(self, tag):
        return self.__map_tag_clusters[tag]
        
    def rank_by_tag(self, tag='', use_cluster=False, cluster_number=0):
#        if not tag in self.__tags:
#            return []
        if use_cluster:
            cluster = self.clusters(tag)[cluster_number]
            return self.rank_by_tags(cluster)
        rank = self.__map_tag_userrank[tag][:self.__max_per_rank]
        return rank, self.__merge_rank_and_monolitic([tag]), rank, rank, rank, rank, rank 
    
    def rank_by_tags(self, tags):
        
        if len(tags)==0:
            return []
        tags = list(tags)
        rank0, mono_rank, rank, rank2, rank3, rank4, rank6 = self.rank_by_tag(tags[0])        
        for tag in tags[1:]:            
            rank = self.__merge_rank_and(rank, self.rank_by_tag(tag)[2], '1')
            rank2 = self.__merge_rank_and(rank2, self.rank_by_tag(tag)[3], '2')
            rank3 = self.__merge_rank_and(rank3, self.rank_by_tag(tag)[4], '3')        
            rank4 = self.__merge_rank_and(rank4, self.rank_by_tag(tag)[5], '4', tag)
            rank6 = self.__merge_rank_and(rank6, self.rank_by_tag(tag)[6], '6')
        and_rank0 = add_pos(and_rank0_gold1(tags, self.__ranker))        
        and_rank5 = add_pos(and_rank5_gold2(tags, self.__ranker))
        mono_rank = self.__merge_rank_and_monolitic(tags)
        return and_rank0, mono_rank, rank, rank2, rank3, rank4, and_rank5, rank6

    def rank_by_tag_fast(self, tag='', use_cluster=False, cluster_number=0):
        rank = self.__map_tag_userrank[tag][:self.__max_per_rank]
	return rank, rank
    
    def rank_by_tags_fast(self, tags):
        
        if len(tags)==0:
            return []
        tags = list(tags)
        rank1, rank3  = self.rank_by_tag_fast(tags[0])        
        for tag in tags[1:]:            
            rank1 = self.__merge_rank_and(rank1, self.rank_by_tag_fast(tag)[0], '1')
            rank3 = self.__merge_rank_and(rank3, self.rank_by_tag_fast(tag)[1], '3')        
        return rank1, rank3

    def __merge_rank_and_monolitic(self, tags):
        users = self.__map_tag_users[tags[0]]
        for tag in tags[1:]:
            users = users.intersection(self.__map_tag_users[tag])
        mono_rank = []        
        for name, pagerank, pos in self.__rank:
            if name in users:
                mono_rank.append((name,pagerank))
                if self.__max_per_rank <= len(mono_rank):
                    break
        mono_rank = PageRank.normalize(mono_rank)
        return add_pos(mono_rank)
                                    

    def __merge_rank_and(self, rank1, rank2, and_type='1', tag=None):
        rank1_no_pos = [(name,pagerank) for name, pagerank, pos in rank1]
        rank2_no_pos = [(name,pagerank) for name, pagerank, pos in rank2]
        if and_type=='1':
            new_rank = and_rank(rank1_no_pos, rank2_no_pos)
        elif and_type=='2':
            new_rank = and_rank2(rank1_no_pos, rank2_no_pos)
        elif and_type=='3':
            new_rank = and_rank3(rank1_no_pos, rank2_no_pos)
        elif and_type=='4':
            new_rank = and_rank4(rank1_no_pos, rank2_no_pos, self.__ranker, tag, self.__max_per_rank)
        elif and_type=='6':
            new_rank = and_rank6(rank1_no_pos, rank2_no_pos)
        else:
            raise Exception('bad and_type in __merge_rank_and')
        new_rank_pos = add_pos(new_rank)
        return new_rank_pos

    def __merge_rank_or(self, rank1, rank2):
        
        pos = 0
        present_pagerank = -3.0
        rank = []
        index1, index2 = 0, 0
        while index1 < len(rank1) and index2 < len(rank2) and len(rank) < self.__max_per_rank:
            if rank1[index1][1] > rank2[index2][1] or (rank1[index1][1] == rank2[index2][1] and rank1[index1][0] <= rank2[index2][0]):
                name, pagerank, old_pos1 = rank1[index1]
                index1 += 1
            else:
                name, pagerank, old_pos2 = rank2[index2]
                index2 += 1
            if pagerank != present_pagerank:
                pos += 1
                present_pagerank = pagerank
            if len(rank)==0 or rank[-1][0] != name:
                rank.append((name,pagerank,pos))    

        if index1 < len(rank1):
            for name, pagerank, old_pos1 in rank1[index1:]:
                if pagerank != present_pagerank:
                    pos += 1
                    present_pagerank = pagerank
                if len(rank) >= self.__max_per_rank:
                    break
                if len(rank)==0 or rank[-1][0] != name:
                    rank.append((name,pagerank,pos))   
        elif index2 < len(rank2):
            for name, pagerank, old_pos2 in rank1[index2:]:
                if pagerank != present_pagerank:
                    pos += 1
                    present_pagerank = pagerank
                if len(rank) >= self.__max_per_rank:
                    break
                if len(rank)==0 or rank[-1][0] != name:
                    rank.append((name,pagerank,pos))   
                
        return rank
    
    def total_users(self):
        return len(self.__map_user_tags)        
        
    def total_tags(self):
        return len(self.__tags)
    
    def good_user(self, user):
        return user in self.__map_user_tags
    
    def __cmp_fst(self, A, B):
        if A[0][0] < B[0][0]:
            return -1
        elif A[0][0] > B[0][0]:
            return 1
        else:
            return 0
    
    def __sort_inside_pos(self, ranks):
        if len(ranks) == 0:
            return []
        ret = []
        aux, aux_pos = [ranks[0]], ranks[0][2]
        for tags, pr, pos in ranks[1:]:
            if pos == aux_pos:
                aux.append((tags,pr,pos))
            else:
                aux.sort(self.__cmp_fst)
                ret += aux
                aux, aux_pos = [(tags,pr,pos)], pos
        aux.sort()
        ret += aux
        return ret            
    
    def user_ranks(self, user, filter_set=None, max_per=500, sorting=True):
        user_ranks = self.__map_user_tags.__getitem__(user, max_per)
        ranks = map(lambda (tag, pos): ([tag], 0.0, int(pos)), user_ranks)
        if sorting:
            ranks = self.__sort_inside_pos(ranks)
        if filter_set:
            ranks = filter(lambda (tags,pr,pos): tags[0] in filter_set, ranks)
        return ranks
#        good_tags = []
#        ranks = []
#        for tag in tags:
#            tag_rank = self.__map_tag_userrank[tag]
#            for rank_user, pagerank, pos in tag_rank:
#                if rank_user == user:
#                    ranks.append((tag, pagerank, pos))
#        ranks = list(set(ranks))
#        ranks = map(lambda (tag, pr, pos): ([tag], pr, pos), ranks)        
#        ranks.sort(thrd_fst_cmp)
#        return ranks
    
    def user_ranks_clustering(self, user):        
        good_tags = []
        ranks = []
        added_clusters = set([])
        for cluster in self.__clusters:
            rank = self.rank_by_tags(cluster)
            for rank_user, pagerank, pos in rank:
                if rank_user == user and not '|'.join(cluster) in added_clusters:
                    ranks.append((cluster, pagerank, pos))
                    added_clusters.add('|'.join(cluster))        
        ranks.sort(thrd_fst_cmp)
        return ranks
    
            
        
def thrd_fst_cmp(A, B):     
     ret = A[2] - B[2]
     if ret < 0:
         return -1
     elif ret > 0:
         return 1
     else:         
         if str(A)[0] > str(B)[0]:
             return -1
         elif str(A)[0] < str(B)[0]:
             return 1
         else:
             return 0       
    
        
if __name__ == '__main__':
        
    #dataset = '../data/rpoland--2000'
    dataset = '../data/jcl5m--39370'
    
    eggomatic = EggOMatic(dataset, True, True)
    
    tag = 'beatles'
    print 'good tag: ' + tag
    print eggomatic.good_tag(tag)
    print 'has_bigger_cluster: ' + tag
    print eggomatic.has_bigger_cluster(tag)
    print 'has_many_clusters: ' + tag
    print eggomatic.has_many_clusters(tag)
    print 'rank_by_tag: ' + tag
    print eggomatic.rank_by_tag(tag)
    
